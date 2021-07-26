#!/usr/bin/python3

# crawl_pipeline.py
# Date:  26/07/2021
# Author: Dan Chiriac
# Email: dan.chiriac1453@gmail.com

""" """

import hashlib
import logging
import uuid
from json import loads, dumps

from scrapy.crawler import CrawlerProcess
from tika import parser

import sem_covid.services.crawlers.scrapy_crawlers.settings as crawler_config
from sem_covid import config
from sem_covid.services.store_registry import StoreRegistry

TIKA_FILE_PREFIX = 'tika/'
SPLASH_URL_CONFIG = 'config.SPLASH_URL'
CONTENT_PATH_KEY = 'content'

logger = logging.getLogger(__name__)


def extract_settings_from_module(module) -> dict:
    settings = dict()
    for setting_config in dir(crawler_config):
        if setting_config.isupper():
            settings[setting_config] = getattr(module, setting_config)

    return settings


class CrawlDagPipeline:
    """
        Pipeline for data crawling
    """
    def __init__(self, file_name: str, bucket_name: str, elasticsearch_index_name: str,
                 content_path_key: str, scrapy_crawler) -> None:
        self.file_name = file_name
        self.bucket_name = bucket_name
        self.elasticsearch_index_name = elasticsearch_index_name
        self.content_path_key = content_path_key
        self.scrapy_crawler = scrapy_crawler

    def start_crawler(self) -> None:
        """
            This step includes data crawling from the sources
        """
        logger.info('start crawler')
        minio = StoreRegistry.minio_object_store(self.bucket_name)
        minio.empty_bucket(object_name_prefix=None)
        settings = extract_settings_from_module(crawler_config)
        settings[SPLASH_URL_CONFIG] = config.SPLASH_URL
        process = CrawlerProcess(settings=settings)
        process.crawl(self.scrapy_crawler, filename=self.file_name, storage_adapter=minio)
        process.start()

    def extract_document_content_with_tika(self) -> None:
        """
            Using Apache Tika, it loads files from the source and extracts the content.
            After that, it stores into MinIO bucket.
        """
        logger.info(f'Using Apache Tika at {config.APACHE_TIKA_URL}')
        logger.info(f'Loading resource files from {self.file_name}')
        minio = StoreRegistry.minio_object_store(self.bucket_name)
        json_content = loads(minio.get_object(self.file_name))

        for index, item in enumerate(json_content):
            identifier = item['title']
            logger.info(f'[{index + 1}/{len(json_content)}] Processing {identifier}')

            if self.content_path_key in item:
                parse_result = parser.from_buffer(item[self.content_path_key], config.APACHE_TIKA_URL)

                if 'content' in parse_result:
                    item[self.content_path_key] = parse_result['content']

            manifestation = item.get('detail_link') or item['title']
            if manifestation is None:
                manifestation = "no title ( " + str(uuid.uuid4()) + " )"
            filename = hashlib.sha256(manifestation.encode('utf-8')).hexdigest()
            minio.put_object(TIKA_FILE_PREFIX + filename, dumps(item))

        minio.put_object(self.file_name, dumps(json_content))

    def upload_processed_documents_to_elasticsearch(self) -> None:
        """
            Uploads extracted documents into Elasticsearch
        """
        es_adapter = StoreRegistry.es_index_store()
        logger.info(
            f'Using ElasticSearch at {config.ELASTICSEARCH_HOST_NAME}:{config.ELASTICSEARCH_PORT}')
        logger.info(f'Loading files from {config.MINIO_URL}')

        minio = StoreRegistry.minio_object_store(self.bucket_name)
        objects = minio.list_objects(TIKA_FILE_PREFIX)

        for item in objects:
            try:
                logger.info(
                    f'Sending to ElasticSearch ( {self.elasticsearch_index_name} ) the object {item.object_name}')
                es_adapter.index(index_name=self.elasticsearch_index_name,
                                 document_id=item.object_name.split("/")[1],
                                 document_body=loads(minio.get_object(item.object_name).decode('utf-8')))
            except Exception as exception:
                logger.exception(exception)
                raise exception

