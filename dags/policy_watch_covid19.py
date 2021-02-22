#!/usr/bin/python3

# main.py
# Date:  22/02/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import hashlib
import io
import json
import logging
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from elasticsearch import Elasticsearch
from minio import Minio
from minio.deleteobjects import DeleteObject
from tika import parser

apache_tika_url = Variable.get("APACHE_TIKA_URL")
elasticsearch_index_name = Variable.get("PWDB_ELASTIC_SEARCH_INDEX_NAME")
elasticsearch_protocol: str = Variable.get("ELASTICSEARCH_PROTOCOL")
elasticsearch_hostname: str = Variable.get("ELASTICSEARCH_URL")
elasticsearch_port: int = Variable.get("ELASTICSEARCH_PORT")
elasticsearch_user: str = Variable.get("ELASTICSEARCH_USERNAME")
elasticsearch_password: str = Variable.get("ELASTICSEARCH_PASSWORD")
dataset_url = Variable.get("PWDB_DATASET_URL")
dataset_local_filename = Variable.get("PWDB_DATASET_LOCAL_FILENAME")
minio_url = Variable.get("MINIO_URL")
minio_pwdb_bucket = Variable.get("PWDB_COVID19_BUCKET_NAME")
minio_acces_key = Variable.get("MINIO_ACCESS_KEY")
minio_secret_key = Variable.get("MINIO_SECRET_KEY")

logger = logging.getLogger('lam-fetcher')
version = '1.0'


def initialize_minio() -> Minio:
    logger.info('Connecting to Minio instance on ' + minio_url)

    minio_client = Minio(
        minio_url,
        access_key=minio_acces_key,
        secret_key=minio_secret_key,
        secure=False
    )
    logger.info('...done.')

    if minio_client.bucket_exists(minio_pwdb_bucket):
        logger.info('Bucket ' + minio_pwdb_bucket + ' already exists.')
    else:
        logger.info('Bucket ' + minio_pwdb_bucket + ' does not exist. Creating...')
        minio_client.make_bucket(minio_pwdb_bucket)
        logger.info('...done.')

    return minio_client


def empty_bucket(minio_client: Minio):
    logger.info('Clearing the ' + minio_pwdb_bucket + ' bucket...')
    objects = minio_client.list_objects(minio_pwdb_bucket)
    objects_to_delete = [DeleteObject(x.object_name) for x in objects]
    for error in minio_client.remove_objects(minio_pwdb_bucket, objects_to_delete):
        logger.error("Deletion error: {}".format(error))


def download_policy_dataset():
    response = requests.get(dataset_url, stream=True, timeout=30)
    response.raise_for_status()
    minio_client = initialize_minio()
    empty_bucket(minio_client)
    raw_content = io.BytesIO(response.content)
    raw_content_size = raw_content.getbuffer().nbytes
    minio_client.put_object(minio_pwdb_bucket, dataset_local_filename, raw_content, raw_content_size)
    logger.info('Uploaded ' + str(raw_content_size) + ' bytes to bucket [' + minio_pwdb_bucket + '] at ' + minio_url)


def download_policy_watch_resources():
    logging.info('Starting the download...')

    minio_client = initialize_minio()
    with minio_client.get_object(minio_pwdb_bucket, dataset_local_filename) as response:
        covid19json = json.loads(response.read().decode('utf-8'))

    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        logger.info('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['fieldData']['title'])

        if not field_data['fieldData']['d_endDate']:
            field_data['fieldData']['d_endDate'] = None  # Bozo lives here

        for source in field_data['portalData']['sources']:
            download_single_source(source, minio_client)

    raw_content = io.BytesIO(json.dumps(covid19json).encode())
    raw_content_size = raw_content.getbuffer().nbytes
    minio_client.put_object(minio_pwdb_bucket, dataset_local_filename, raw_content, raw_content_size)

    logger.info("...done downloading.")


def download_single_source(source, minio_client: Minio):
    try:
        url = source['sources::url'] if source['sources::url'].startswith('http') else (
                'http://' + source['sources::url'])
        filename = str('res.' + hashlib.sha256(source['sources::url'].encode('utf-8')).hexdigest())

        with requests.get(url, allow_redirects=True, timeout=30) as response:
            raw_content = io.BytesIO(response.content)
            raw_content_size = raw_content.getbuffer().nbytes
            minio_client.put_object(minio_pwdb_bucket, filename, raw_content, raw_content_size)

        source['content_path'] = filename
    except Exception as ex:
        source['failure_reason'] = str(ex)

    return source


def process_using_tika():
    logger.info('Using Apache Tika at ' + apache_tika_url)

    minio_client = initialize_minio()
    with minio_client.get_object(minio_pwdb_bucket, dataset_local_filename) as response:
        covid19json = json.loads(response.read().decode('utf-8'))

    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        valid_sources = 0
        logger.info('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['fieldData']['title'])

        try:
            for source in field_data['portalData']['sources']:
                if 'failure_reason' in source:
                    logger.info('Will not process source <' +
                                source['sources::title'] +
                                '> because it failed download with reason <' +
                                source['failure_reason'] + '>')
                else:
                    with minio_client.get_object(minio_pwdb_bucket, source['content_path']) as response:
                        parse_result = parser.from_buffer(response.read().decode('utf-8'), apache_tika_url)
                    logger.info('RESULT IS ' + json.dumps(parse_result))
                    if 'content' in parse_result:
                        source['content'] = parse_result['content']
                        valid_sources += 1
                    else:
                        logger.warning('Apache Tika did NOT return a valid content for the source ' +
                                       source['sources::title'])

            if valid_sources > 0:
                raw_content = io.BytesIO(json.dumps(field_data).encode())
                raw_content_size = raw_content.getbuffer().nbytes
                minio_client.put_object(minio_pwdb_bucket, 'tika.' + hashlib.sha256(
                    field_data['fieldData']['title'].encode('utf-8')).hexdigest(), raw_content,
                                        raw_content_size)
            else:
                logger.warning('Field ' + field_data['fieldData']['title'] + ' had no valid or processable sources.')
        except Exception as ex:
            logger.exception(ex)


def put_elasticsearch_documents():
    elasticsearch_client = Elasticsearch([elasticsearch_protocol +
                                          '://' +
                                          elasticsearch_user +
                                          ':' +
                                          elasticsearch_password +
                                          '@' +
                                          elasticsearch_hostname +
                                          ':' +
                                          str(elasticsearch_port)])

    logger.info('Using ElasticSearch at ' + elasticsearch_protocol + '://' + elasticsearch_hostname + ':' + str(
        elasticsearch_port))

    minio_client = initialize_minio()
    objects = minio_client.list_objects(minio_pwdb_bucket, prefix='tika.')
    object_count = 0

    for obj in objects:
        try:
            logger.info('Sending to ElasticSearch (  ' +
                        elasticsearch_index_name +
                        ' ) the file ' +
                        obj.object_name)

            with minio_client.get_object(minio_pwdb_bucket, obj.object_name) as response:
                elasticsearch_client.index(index=elasticsearch_index_name,
                                           body=json.loads(response.read().decode('utf-8')))
            object_count += 1
        except Exception as ex:
            logger.exception(ex)

    logger.info('Sent ' + str(object_count) + ' object(s) to ElasticSearch.')


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 22),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=3600)
}
dag = DAG('PolicyWatchDB_ver_' + version,
          default_args=default_args,
          schedule_interval="@once",
          max_active_runs=1,
          concurrency=1)

download_task = PythonOperator(task_id='Download',
                               python_callable=download_policy_dataset, retries=1, dag=dag)

enrich_task = PythonOperator(task_id='Enrich',
                             python_callable=download_policy_watch_resources, retries=1, dag=dag)

tika_task = PythonOperator(task_id='Tika',
                           python_callable=process_using_tika, retries=1, dag=dag)

elasticsearch_task = PythonOperator(task_id='ElasticSearch',
                                    python_callable=put_elasticsearch_documents, retries=1, dag=dag)

enrich_task.set_upstream(download_task)
tika_task.set_upstream(enrich_task)
elasticsearch_task.set_upstream(tika_task)
