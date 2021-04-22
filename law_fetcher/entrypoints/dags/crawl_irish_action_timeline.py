#!/usr/bin/python3

# crawl_irish_action_timeline.py
# Date:  13/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from json import loads, dumps

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from elasticsearch.client import Elasticsearch
from scrapy.crawler import CrawlerProcess
from tika import parser

import law_fetcher.entrypoints.crawlers.scrapy_crawlers.settings as crawler_config
from law_fetcher.adapters.minio_adapter import MinioAdapter
from law_fetcher.entrypoints.crawlers.scrapy_crawlers.spiders.irish_gov import IrishGovCrawler

logger = logging.getLogger('lam-fetcher')
VERSION = '0.1.2'

APACHE_TIKA_URL = Variable.get('APACHE_TIKA_URL')
ELASTICSEARCH_INDEX_NAME: str = Variable.get('IRISH_ACTION_TIMELINE_ELASTIC_SEARCH_INDEX_NAME')
ELASTICSEARCH_PROTOCOL: str = Variable.get('ELASTICSEARCH_PROTOCOL')
ELASTICSEARCH_HOSTNAME: str = Variable.get('ELASTICSEARCH_URL')
ELASTICSEARCH_PORT: int = Variable.get('ELASTICSEARCH_PORT')
ELASTICSEARCH_USER: str = Variable.get('ELASTICSEARCH_USERNAME')
ELASTICSEARCH_PASSWORD: str = Variable.get('ELASTICSEARCH_PASSWORD')

SPLASH_URL: str = Variable.get('SPLASH_URL')
TIKA_FILE_PREFIX = 'tika/'

IRISH_ACTION_TIMELINE_JSON = Variable.get('IRISH_ACTION_TIMELINE_JSON')
MINIO_URL = Variable.get("MINIO_URL")
MINIO_BUCKET = Variable.get('IRISH_ACTION_TIMELINE_BUCKET_NAME')
MINIO_ACCESS_KEY = Variable.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = Variable.get("MINIO_SECRET_KEY")

CONTENT_PATH_KEY = 'content'


def extract_settings_from_module(module):
    settings = dict()
    for config in dir(crawler_config):
        if config.isupper():
            settings[config] = getattr(module, config)

    return settings


def start_crawler():
    logger.info('start crawler')
    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET)
    minio.empty_bucket(object_name_prefix=None)
    settings = extract_settings_from_module(crawler_config)
    settings['SPLASH_URL'] = SPLASH_URL
    process = CrawlerProcess(settings=settings)
    process.crawl(IrishGovCrawler, filename=IRISH_ACTION_TIMELINE_JSON, storage_adapter=minio)
    process.start()


def extract_document_content_with_tika():
    logger.info(f'Using Apache Tika at {APACHE_TIKA_URL}')
    logger.info(f'Loading resource files from {IRISH_ACTION_TIMELINE_JSON}')
    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET)
    irish_action_timeline_json = loads(minio.get_object(IRISH_ACTION_TIMELINE_JSON))
    irish_action_timeline_items_count = len(irish_action_timeline_json)

    counter = {
        'general': 0,
        'success': 0
    }

    for index, item in enumerate(irish_action_timeline_json):
        identifier = item['title']
        logger.info(f'[{index + 1}/{irish_action_timeline_items_count}] Processing {identifier}')

        if CONTENT_PATH_KEY in item:
            counter['general'] += 1
            parse_result = parser.from_buffer(item[CONTENT_PATH_KEY], APACHE_TIKA_URL)
            if 'content' in parse_result:
                counter['success'] += 1
                item[CONTENT_PATH_KEY] = parse_result['content']

        manifestation = item.get('detail_link') or item['title']
        if manifestation is None:
            manifestation = "no title ( " + str(uuid.uuid4()) + " )"
        filename = hashlib.sha256(manifestation.encode('utf-8')).hexdigest()
        minio.put_object_from_string(TIKA_FILE_PREFIX + filename, dumps(item))

    minio.put_object_from_string(IRISH_ACTION_TIMELINE_JSON, dumps(irish_action_timeline_json))

    logger.info(f"Parsed a total of {counter['general']} files, of which successfully {counter['success']} files.")


def upload_processed_documents_to_elasticsearch():
    elasticsearch_client = Elasticsearch(
        [
            f'{ELASTICSEARCH_PROTOCOL}://{ELASTICSEARCH_USER}:{ELASTICSEARCH_PASSWORD}@{ELASTICSEARCH_HOSTNAME}:{ELASTICSEARCH_PORT}'])

    logger.info(f'Using ElasticSearch at {ELASTICSEARCH_PROTOCOL}://{ELASTICSEARCH_HOSTNAME}:{ELASTICSEARCH_PORT}')

    logger.info(f'Loading files from {MINIO_URL}')

    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET)
    objects = minio.list_objects(TIKA_FILE_PREFIX)
    object_count = 0
    for obj in objects:
        try:
            logger.info(f'Sending to ElasticSearch ( {ELASTICSEARCH_INDEX_NAME} ) the object {obj.object_name}')
            elasticsearch_client.index(index=ELASTICSEARCH_INDEX_NAME, id=obj.object_name.split("/")[1],
                                       body=loads(minio.get_object(obj.object_name).decode('utf-8')))
            object_count += 1
        except Exception as ex:
            logger.exception(ex)

    logger.info(f'Sent {object_count} file(s) to ElasticSearch.')


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 16),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500)
}

dag = DAG(
    'Crawl_Irish_Action_Timeline_' + VERSION,
    default_args=default_args,
    schedule_interval="@once",
    max_active_runs=1,
    concurrency=1
)

start_crawler = PythonOperator(
    task_id=f'Crawl',
    python_callable=start_crawler, retries=1, dag=dag)

extract_content_with_tika_task = PythonOperator(
    task_id=f'Tika',
    python_callable=extract_document_content_with_tika, retries=1, dag=dag)

upload_to_elastic_task = PythonOperator(
    task_id=f'Elasticsearch',
    python_callable=upload_processed_documents_to_elasticsearch, retries=1, dag=dag)

start_crawler >> extract_content_with_tika_task >> upload_to_elastic_task
