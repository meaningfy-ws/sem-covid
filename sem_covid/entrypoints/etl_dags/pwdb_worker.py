#!/usr/bin/python3

# main.py
# Date:  22/02/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import hashlib
import json
import logging
import requests
from tika import parser
from sem_covid.services.store_registry import StoreRegistryABC
from sem_covid.adapters.dag.base_etl_dag_pipeline import BaseETLPipeline


BUSINESSES = {'Companies providing essential services', 'Contractors of a company', 'Larger corporations',
              'One person or microenterprises', 'Other businesses', 'SMEs', 'Sector specific set of companies',
              'Solo-self-employed', 'Start-ups'}

CITIZENS = {'Children (minors)', 'Disabled', 'Migrants', 'Older citizens', 'Other groups of citizens', 'Parents',
            'People in care facilities', 'Refugees', 'Single parents', 'The COVID-19 risk group', 'Women',
            'Youth (18-25)'}

WORKERS = {'Cross-border commuters', 'Disabled workers', 'Employees in standard employment', 'Female workers',
           'Migrants in employment', 'Older people in employment (aged 55+)', 'Other groups of workers',
           'Parents in employment', 'Particular professions', 'Platform workers', 'Posted workers',
           'Refugees in employment', 'Seasonal workers', 'Self-employed', 'Single parents in employment',
           'The COVID-19 risk group at the workplace', 'Undeclared workers', 'Unemployed', 'Workers in care facilities',
           'Workers in essential services', 'Workers in non-standard forms of employment',
           'Youth (18-25) in employment'}

CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
CONTENT_LANGUAGE = "language"
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
logger = logging.getLogger(__name__)


def download_single_source(source, minio):
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


class PWDBDagWorker(BaseETLPipeline):
    def __init__(self, bucket_name: str, apache_tika_url: str, elasticsearch_host_name: str,
                 elasticsearch_port: str, elasticsearch_index_name: str, store_registry: StoreRegistryABC) -> None:
        self.store_registry = store_registry
        self.bucket_name = bucket_name
        self.apache_tika_url = apache_tika_url
        self.elasticsearch_host_name = elasticsearch_host_name
        self.elasticsearch_port = elasticsearch_port
        self.elasticsearch_index_name = elasticsearch_index_name

    def get_steps(self) -> list:
        return [self.extract,
                self.transform_content, self.load]

    def extract(self, **context) -> None:
        if "filename" not in context['dag_run'].conf:
            logger.error(
                "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
            return
        filename = context['dag_run'].conf['filename']
        logging.info('Processing the file ' + filename)
        minio = self.store_registry.minio_object_store(self.bucket_name)
        field_data = json.loads(minio.get_object(filename))

        if not field_data['end_date']:
            field_data['end_date'] = None  # Bozo lives here

        for source in field_data['sources']:
            download_single_source(source, minio)

        minio.put_object(filename, json.dumps(field_data))

        logger.info("...done downloading.")

    def transform_content(self, **context) -> None:
        if "filename" not in context['dag_run'].conf:
            logger.error(
                "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
            return

        filename = context['dag_run'].conf['filename']
        logging.info('Processing the file ' + filename)
        logger.info('Using Apache Tika at ' + self.apache_tika_url)

        minio = self.store_registry.minio_object_store(self.bucket_name)
        field_data = json.loads(minio.get_object(filename))

        valid_sources = 0

        try:
            for source in field_data['sources']:
                if 'failure_reason' in source:
                    logger.info('Will not process source <' + source['title'] +
                                '> because it failed download with reason <' + source['failure_reason'] + '>')
                else:
                    logger.info(f'content path is: {source[CONTENT_PATH_KEY]}')
                    parse_result = parser.from_buffer(minio.get_object(source[CONTENT_PATH_KEY]), self.apache_tika_url)

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

                minio.put_object(TIKA_FILE_PREFIX + hashlib.sha256(
                    (str(field_data['identifier'] +
                         field_data['title'])).encode('utf-8')).hexdigest(), json.dumps(field_data))
        except Exception as ex:
            logger.exception(ex)

    def transform_structure(self, *args, **kwargs):
        pass

    def load(self, **context) -> None:
        if "filename" not in context['dag_run'].conf:
            logger.error(
                "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
            return

        filename = context['dag_run'].conf['filename']
        logging.info('Processing the file ' + filename)

        es_adapter = self.store_registry.es_index_store()
        logger.info('Using ElasticSearch at ' + self.elasticsearch_host_name + ':' + str(
            self.elasticsearch_port))

        minio = self.store_registry.minio_object_store(self.bucket_name)
        original_field_data = json.loads(minio.get_object(filename))
        tika_filename = TIKA_FILE_PREFIX + hashlib.sha256(
            (str(original_field_data['identifier'] + original_field_data['title'])).encode('utf-8')).hexdigest()
        logger.info("Tika-processed filename is " + tika_filename)
        tika_field_data = json.loads(minio.get_object(tika_filename).decode('utf-8'))

        new_columns = {'businesses': BUSINESSES, 'citizens': CITIZENS, 'workers': WORKERS}
        target_groups_key = tika_field_data['target_groups']
        for column, class_set in new_columns.items():
            tika_field_data[column] = int(any(item for item in class_set if item in target_groups_key))

        logger.info('Sending to ElasticSearch (  ' +
                    self.elasticsearch_index_name +
                    ' ) the file ' +
                    tika_filename)
        es_adapter.index(index_name=self.elasticsearch_index_name,
                         document_id=tika_filename.split("/")[1],
                         document_body=tika_field_data)

        logger.info('Sent ' + tika_filename + '  to ElasticSearch.')
