#!/usr/bin/python3

# main.py
# Date:  22/02/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import hashlib
import json
import logging
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from tika import parser

from sem_covid import config
from sem_covid.adapters.es_adapter import ESAdapter
from sem_covid.adapters.minio_adapter import MinioAdapter

VERSION = '0.01'
DATASET_NAME = "pwdb_worker"
DAG_TYPE = "etl"
DAG_NAME = DAG_TYPE + '_' + DATASET_NAME + '_' + VERSION
CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
CONTENT_LANGUAGE = "Language"
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
logger = logging.getLogger(__name__)


def download_single_source(source, minio: MinioAdapter):
    try:
        logger.info("Now downloading source " + str(source))
        url = source['url'] if source['url'].startswith('http') else ('http://' + source['url'])
        filename = str(RESOURCE_FILE_PREFIX + hashlib.sha256(source['url'].encode('utf-8')).hexdigest())

        with requests.get(url, allow_redirects=True, timeout=30) as response:
            minio.put_object(filename, response.content)

        source[CONTENT_PATH_KEY] = filename
    except Exception as ex:
        source['failure_reason'] = str(ex)

    return source


def download_policy_watch_resources(**context):
    if "filename" not in context['dag_run'].conf:
        logger.error(
            "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    filename = context['dag_run'].conf['filename']
    logging.info('Processing the file ' + filename)

    minio = MinioAdapter(config.PWDB_COVID19_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    field_data = json.loads(minio.get_object(filename).decode('utf-8'))

    if not field_data['end_date']:
        field_data['end_date'] = None  # Bozo lives here

    for source in field_data['sources']:
        download_single_source(source, minio)

    minio.put_object_from_string(filename, json.dumps(field_data))

    logger.info("...done downloading.")


def process_using_tika(**context):
    if "filename" not in context['dag_run'].conf:
        logger.error(
            "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    filename = context['dag_run'].conf['filename']
    logging.info('Processing the file ' + filename)
    logger.info('Using Apache Tika at ' + config.APACHE_TIKA_URL)

    minio = MinioAdapter(config.PWDB_COVID19_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    field_data = json.loads(minio.get_object(filename).decode('utf-8'))

    valid_sources = 0

    try:
        for source in field_data['sources']:
            if 'failure_reason' in source:
                logger.info('Will not process source <' +
                            source['title'] +
                            '> because it failed download with reason <' +
                            source['failure_reason'] + '>')
            else:
                logger.info(f'content path is: {source[CONTENT_PATH_KEY]}')
                parse_result = parser.from_buffer(minio.get_object(source[CONTENT_PATH_KEY]),
                                                  config.APACHE_TIKA_URL)

                logger.info('RESULT IS ' + json.dumps(parse_result))
                if CONTENT_KEY in parse_result and parse_result[CONTENT_KEY]:
                    source[CONTENT_KEY] = parse_result[CONTENT_KEY].replace('\n', '')
                    source[CONTENT_LANGUAGE] = (
                            parse_result["metadata"].get("Content-Language")
                            or
                            parse_result["metadata"].get("content-language")
                            or
                            parse_result["metadata"].get("language"))
                    valid_sources += 1
                else:
                    logger.warning('Apache Tika did NOT return a valid content for the source ' +
                                   source['title'])

        if valid_sources > 0:
            logger.info('Field ' + field_data['title'] + ' had ' + str(valid_sources) + ' valid sources.')
        else:
            logger.warning('Field ' + field_data['title'] + ' had no valid or processable sources.')

        minio.put_object_from_string(TIKA_FILE_PREFIX + hashlib.sha256(
            (str(field_data['identifier'] +
                 field_data['title'])).encode('utf-8')).hexdigest(), json.dumps(field_data))
    except Exception as ex:
        logger.exception(ex)


def put_elasticsearch_documents(**context):
    if "filename" not in context['dag_run'].conf:
        logger.error(
            "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    filename = context['dag_run'].conf['filename']
    logging.info('Processing the file ' + filename)

    es_adapter = ESAdapter(config.ELASTICSEARCH_HOST_NAME,
                           config.ELASTICSEARCH_PORT,
                           config.ELASTICSEARCH_USERNAME,
                           config.ELASTICSEARCH_PASSWORD)
    logger.info('Using ElasticSearch at ' + config.ELASTICSEARCH_HOST_NAME + ':' + str(
        config.ELASTICSEARCH_PORT))

    minio = MinioAdapter(config.PWDB_COVID19_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    original_field_data = json.loads(minio.get_object(filename).decode('utf-8'))
    tika_filename = TIKA_FILE_PREFIX + hashlib.sha256(
        (str(original_field_data['identifier'] + original_field_data['title'])).encode('utf-8')).hexdigest()
    logger.info("Tika-processed filename is " + tika_filename)
    tika_field_data = json.loads(minio.get_object(tika_filename).decode('utf-8'))

    logger.info('Sending to ElasticSearch (  ' +
                config.PWDB_ELASTIC_SEARCH_INDEX_NAME +
                ' ) the file ' +
                tika_filename)
    es_adapter.index(index_name=config.PWDB_ELASTIC_SEARCH_INDEX_NAME,
                     document_id=tika_filename.split("/")[1],
                     document_body=tika_field_data)

    logger.info('Sent ' + tika_filename + '  to ElasticSearch.')


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


with DAG(DAG_NAME, default_args=default_args, schedule_interval=None, max_active_runs=4, concurrency=4) as dag:
    enrich_task = PythonOperator(task_id='Enrich',
                                 python_callable=download_policy_watch_resources, retries=1, dag=dag, provide_context=True)

    tika_task = PythonOperator(task_id='Tika',
                               python_callable=process_using_tika, retries=1, dag=dag, provide_context=True)

    elasticsearch_task = PythonOperator(task_id='ElasticSearch',
                                        python_callable=put_elasticsearch_documents, retries=1, dag=dag,
                                        provide_context=True)

    enrich_task >> tika_task >> elasticsearch_task
