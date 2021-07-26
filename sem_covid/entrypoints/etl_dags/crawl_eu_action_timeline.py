import hashlib
import logging
from datetime import datetime, timedelta
from json import loads, dumps

from airflow import DAG
from airflow.operators.python import PythonOperator
from scrapy.crawler import CrawlerProcess
from tika import parser

import sem_covid.services.crawlers.scrapy_crawlers.settings as crawler_config
from sem_covid import config
from sem_covid.services.crawlers.scrapy_crawlers.spiders.eu_timeline_spider import EUTimelineSpider
from sem_covid.services.store_registry import store_registry

VERSION = '0.2.5'
DATASET_NAME = "eu_timeline"
DAG_TYPE = "etl"
DAG_NAME = DAG_TYPE + '_' + DATASET_NAME + '_' + VERSION
TIKA_FILE_PREFIX = 'tika/'
CONTENT_PATH_KEY = 'detail_content'
logger = logging.getLogger(__name__)


def extract_settings_from_module(module):
    settings = dict()
    for config in dir(crawler_config):
        if config.isupper():
            settings[config] = getattr(module, config)

    return settings


def start_crawler_callable():
    logger.info('start crawler')
    minio = store_registry.minio_object_store(config.EU_TIMELINE_BUCKET_NAME)
    minio.empty_bucket(object_name_prefix=None)
    settings = extract_settings_from_module(crawler_config)
    settings['config.SPLASH_URL'] = config.SPLASH_URL
    process = CrawlerProcess(settings=settings)
    process.crawl(EUTimelineSpider, filename=config.EU_TIMELINE_JSON, storage_adapter=minio)
    process.start()


def extract_document_content_with_tika_callable():
    logger.info(f'Using Apache Tika at {config.APACHE_TIKA_URL}')
    logger.info(f'Loading resource files from {config.EU_TIMELINE_JSON}')
    minio = store_registry.minio_object_store(config.EU_TIMELINE_BUCKET_NAME)
    json_content = loads(minio.get_object(config.EU_TIMELINE_JSON))
    eu_action_timeline_items_count = len(json_content)

    counter = {
        'general': 0,
        'success': 0
    }

    for index, item in enumerate(json_content):
        identifier = item['title']
        logger.info(f'[{index + 1}/{eu_action_timeline_items_count}] Processing {identifier}')

        if CONTENT_PATH_KEY in item:
            counter['general'] += 1
            parse_result = parser.from_buffer(item[CONTENT_PATH_KEY], config.APACHE_TIKA_URL)
            if 'content' in parse_result:
                counter['success'] += 1
                item[CONTENT_PATH_KEY] = parse_result['content']

        manifestation = item.get('detail_link') or item['title']
        filename = hashlib.sha256(manifestation.encode('utf-8')).hexdigest()
        minio.put_object(TIKA_FILE_PREFIX + filename, dumps(item))

    minio.put_object(config.EU_TIMELINE_JSON, dumps(json_content))

    logger.info(f"Parsed a total of {counter['general']} files, of which successfully {counter['success']} files.")


def upload_processed_documents_to_elasticsearch_callable():
    es_adapter = store_registry.es_index_store()

    logger.info(
        f'Using ElasticSearch at {config.ELASTICSEARCH_HOST_NAME}:{config.ELASTICSEARCH_PORT}')
    logger.info(f'Loading files from {config.MINIO_URL}')

    minio = store_registry.minio_object_store(config.EU_TIMELINE_BUCKET_NAME)
    objects = minio.list_objects(TIKA_FILE_PREFIX)

    object_count = 0
    for obj in objects:
        try:
            logger.info(
                f'Sending to ElasticSearch ( {config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME} ) the object {obj.object_name}')
            es_adapter.index(index_name=config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                             document_id=obj.object_name.split("/")[1],
                             document_body=loads(minio.get_object(obj.object_name).decode('utf-8')))
            object_count += 1
        except Exception as ex:
            logger.exception(ex)
            raise ex

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

with DAG(DAG_NAME, default_args=default_args, schedule_interval="@once", max_active_runs=1, concurrency=1) as dag:
    start_crawler = PythonOperator(
        task_id=f'Crawl',
        python_callable=start_crawler_callable, retries=1, dag=dag)

    extract_content_with_tika_task = PythonOperator(
        task_id=f'Tika',
        python_callable=extract_document_content_with_tika_callable, retries=1, dag=dag)

    upload_to_elastic_task = PythonOperator(
        task_id=f'Elasticsearch',
        python_callable=upload_processed_documents_to_elasticsearch_callable, retries=1, dag=dag)

    start_crawler >> extract_content_with_tika_task >> upload_to_elastic_task

start_crawler_callable()
