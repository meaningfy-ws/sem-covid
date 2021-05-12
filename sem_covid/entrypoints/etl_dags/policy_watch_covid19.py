#!/usr/bin/python3

# main.py
# Date:  22/02/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import hashlib
import json
import logging
from datetime import datetime, timedelta
import random

import requests
from airflow import DAG, AirflowException
from airflow.operators.python import PythonOperator
from tika import parser

from sem_covid import config
from sem_covid.adapters.es_adapter import ESAdapter
from sem_covid.adapters.minio_adapter import MinioAdapter
from sem_covid.services.sc_wrangling.json_transformer import transform_pwdb

VERSION = '0.10.14'
DATASET_NAME = "pwdb"
DAG_TYPE = "etl"
DAG_NAME = DAG_TYPE + '_' + DATASET_NAME + '_' + VERSION
CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
CONTENT_LANGUAGE = "Tika detected language"
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
logger = logging.getLogger(__name__)
exception_list = []


def download_policy_dataset():
    response = requests.get(config.PWDB_DATASET_URL, stream=True, timeout=30)
    response.raise_for_status()
    minio = MinioAdapter(config.PWDB_COVID19_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    minio.empty_bucket(object_name_prefix=None)
    minio.empty_bucket(object_name_prefix=RESOURCE_FILE_PREFIX)
    minio.empty_bucket(object_name_prefix=TIKA_FILE_PREFIX)

    transformed_json = transform_pwdb(json.loads(response.content))

    uploaded_bytes = minio.put_object(config.PWDB_DATASET_LOCAL_FILENAME, json.dumps(transformed_json).encode('utf-8'))
    logger.info(
        'Uploaded ' + str(
            uploaded_bytes) + ' bytes to bucket [' + config.PWDB_COVID19_BUCKET_NAME + '] at ' + config.MINIO_URL)


def download_single_source(source, minio: MinioAdapter):
    try:
        logger.info("Now downloading source " + str(source))
        url = source['url'] if source['url'].startswith('http') else ('http://' + source['url'])
        filename = str(RESOURCE_FILE_PREFIX + hashlib.sha256(source['url'].encode('utf-8')).hexdigest())

        with requests.get(url, allow_redirects=True, timeout=30) as response:
            minio.put_object(filename, response.content)

        source[CONTENT_PATH_KEY] = filename

        raise Exception("Ahahahah")
    except Exception as ex:
        exception_list.append(ex)
        logger.info(str(len(exception_list)))
        source['failure_reason'] = str(ex)

    return source


def download_policy_watch_resources():
    logging.info('Starting the download...')

    minio = MinioAdapter(config.PWDB_COVID19_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    covid19json = json.loads(minio.get_object(config.PWDB_DATASET_LOCAL_FILENAME).decode('utf-8'))
    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        logger.info('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['title'])

        if not field_data['end_date']:
            field_data['end_date'] = None  # Bozo lives here

        for source in field_data['sources']:
            download_single_source(source, minio)
        if current_item == 10:
            break

    minio.put_object_from_string(config.PWDB_DATASET_LOCAL_FILENAME, json.dumps(covid19json))
    logger.info("...done downloading.")
    logger.info(str(len(exception_list)))
    return exception_list


def process_using_tika():
    logger.info('Using Apache Tika at ' + config.APACHE_TIKA_URL)

    minio = MinioAdapter(config.PWDB_COVID19_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    covid19json = json.loads(minio.get_object(config.PWDB_DATASET_LOCAL_FILENAME).decode('utf-8'))
    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        valid_sources = 0
        logger.info('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['title'])

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
                logger.info('Field ' + field_data['title'] + ' had ' + str(valid_sources) + 'valid sources.')
            else:
                logger.warning('Field ' + field_data['title'] + ' had no valid or processable sources.')

            minio.put_object_from_string(TIKA_FILE_PREFIX + hashlib.sha256(
                (str(field_data['identifier'] +
                     field_data['title'])).encode('utf-8')).hexdigest(), json.dumps(field_data))
        except Exception as ex:
            exception_list.append(ex)
            logger.exception(ex)


def put_elasticsearch_documents():
    es_adapter = ESAdapter(config.ELASTICSEARCH_HOST_NAME,
                           config.ELASTICSEARCH_PORT,
                           config.ELASTICSEARCH_USERNAME,
                           config.ELASTICSEARCH_PASSWORD)
    logger.info('Using ElasticSearch at ' + config.ELASTICSEARCH_HOST_NAME + ':' + str(
        config.ELASTICSEARCH_PORT))

    minio = MinioAdapter(config.PWDB_COVID19_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    objects = minio.list_objects(TIKA_FILE_PREFIX)
    object_count = 0

    for obj in objects:
        try:
            logger.info('Sending to ElasticSearch (  ' +
                        config.PWDB_ELASTIC_SEARCH_INDEX_NAME +
                        ' ) the file ' +
                        obj.object_name)
            es_adapter.index(index_name=config.PWDB_ELASTIC_SEARCH_INDEX_NAME,
                             document_id=obj.object_name.split("/")[1],
                             document_body=json.loads(minio.get_object(obj.object_name).decode('utf-8')))
            object_count += 1
        except Exception as ex:
            exception_list.append(ex)
            logger.exception(ex)

    logger.info('Sent ' + str(object_count) + ' object(s) to ElasticSearch.')


def summarize_exceptional_conditions():
    logger.info("There have been " + str(len(exception_list)) + " exceptions recorded.")
    for ex in exception_list:
        logger.exception(ex)
    if len(exception_list) > 0:
        raise AirflowException("DAG execution failed.")


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
dag = DAG(DAG_NAME,
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

summary_task = PythonOperator(task_id='Summary',
                              python_callable=summarize_exceptional_conditions, retries=1, dag=dag)

download_task >> enrich_task >> tika_task >> elasticsearch_task >> summary_task
