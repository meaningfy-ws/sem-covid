#!/usr/bin/python3

# main.py
# Date:  22/02/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import hashlib
import json
import logging
from datetime import datetime, timedelta
from json import dumps, loads

import requests
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from elasticsearch import Elasticsearch
from jq import compile
from tika import parser

from law_fetcher.adapters.minio_adapter import MinioAdapter

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
minio_bucket = Variable.get("PWDB_COVID19_BUCKET_NAME")
minio_acces_key = Variable.get("MINIO_ACCESS_KEY")
minio_secret_key = Variable.get("MINIO_SECRET_KEY")

CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'

logger = logging.getLogger(__name__)
VERSION = '0.10.0'

transformation = '''{
identifier: .recordId,
title: .fieldData.title,
title_national_language: .fieldData.title_nationalLanguage,
country: .fieldData.calc_country,
start_date: .fieldData.d_startDate,
end_date: .fieldData.d_endDate,
date_type: .fieldData.dateType,
type_of_measure: .fieldData.calc_type,
status_of_regulation: .fieldData.statusOfRegulation,
category: .fieldData.calc_minorCategory,
subcategory: .fieldData.calc_subMinorCategory,
creation_date: .fieldData.calc_creationDay,
background_info_description: .fieldData.descriptionBackgroundInfo,
content_of_measure_description: .fieldData.descriptionContentOfMeasure,
use_of_measure_description: .fieldData.descriptionUseOfMeasure,
involvement_of_social_partners_description: .fieldData.descriptionInvolvementOfSocialPartners,
social_partner_form: .fieldData.socialPartnerform,
social_partner_role: .fieldData.socialPartnerrole,
is_sector_specific: .fieldData.isSector,
private_or_public_sector: .fieldData.sector_privateOrPublic,
is_occupation_specific: .fieldData.isOccupation,
actors: [.portalData.actors[] | ."actors::name" ],
target_groups: [.portalData.targetGroups[] | ."targetGroups::name"],
funding: [.portalData.funding[] | ."funding::name" ],
sectors: [.portalData.sectors[] | ."sectors::name" ],
occupations: [.portalData.occupations[] | .],
sources: [.portalData.sources[] | { url: ."sources::url", title: ."sources::title"}]
}'''

SEARCH_RULE = ".[] | "


def get_transformation_rules(rules: str, search_rule: str = SEARCH_RULE):
    return (search_rule + rules).replace("\n", "")


def download_policy_dataset():
    response = requests.get(dataset_url, stream=True, timeout=30)
    response.raise_for_status()
    minio = MinioAdapter(minio_url, minio_acces_key, minio_secret_key, minio_bucket)
    minio.empty_bucket()
    transformed_json = compile(get_transformation_rules(transformation)).input(loads(response.content)).all()
    uploaded_bytes = minio.put_object(dataset_local_filename, dumps(transformed_json).encode('utf-8'))
    logger.info('Uploaded ' + str(uploaded_bytes) + ' bytes to bucket [' + minio_bucket + '] at ' + minio_url)


def download_single_source(source, minio: MinioAdapter):
    try:
        url = source['url'] if source['url'].startswith('http') else ('http://' + source['url'])
        filename = str(RESOURCE_FILE_PREFIX + hashlib.sha256(source['url'].encode('utf-8')).hexdigest())

        with requests.get(url, allow_redirects=True, timeout=30) as response:
            minio.put_object(filename, response.content)

        source[CONTENT_PATH_KEY] = filename
    except Exception as ex:
        source['failure_reason'] = str(ex)

    return source


def download_policy_watch_resources():
    logging.info('Starting the download...')

    minio = MinioAdapter(minio_url, minio_acces_key, minio_secret_key, minio_bucket)
    covid19json = json.loads(minio.get_object(dataset_local_filename).decode('utf-8'))
    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        logger.info('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['title'])

        if not field_data['end_date']:
            field_data['end_date'] = None  # Bozo lives here

        for source in field_data['sources']:
            download_single_source(source, minio)

    minio.put_object_from_string(dataset_local_filename, json.dumps(covid19json))
    logger.info("...done downloading.")


def process_using_tika():
    logger.info('Using Apache Tika at ' + apache_tika_url)

    minio = MinioAdapter(minio_url, minio_acces_key, minio_secret_key, minio_bucket)
    covid19json = json.loads(minio.get_object(dataset_local_filename).decode('utf-8'))
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
                    parse_result = parser.from_buffer(minio.get_object(source[CONTENT_PATH_KEY]), apache_tika_url)

                    logger.info('RESULT IS ' + json.dumps(parse_result))
                    if CONTENT_KEY in parse_result:
                        logger.info(f"content type: {type(parse_result['content'])}")
                        source[CONTENT_KEY] = parse_result['content'].replace('\n', '')
                        valid_sources += 1
                    else:
                        logger.warning('Apache Tika did NOT return a valid content for the source ' +
                                       source['title'])

            if valid_sources > 0:
                minio.put_object_from_string(TIKA_FILE_PREFIX + hashlib.sha256(
                    field_data['title'].encode('utf-8')).hexdigest(), json.dumps(field_data))
            else:
                logger.warning('Field ' + field_data['title'] + ' had no valid or processable sources.')
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

    minio = MinioAdapter(minio_url, minio_acces_key, minio_secret_key, minio_bucket)
    objects = minio.list_objects(TIKA_FILE_PREFIX)
    object_count = 0

    for obj in objects:
        try:
            logger.info('Sending to ElasticSearch (  ' +
                        elasticsearch_index_name +
                        ' ) the file ' +
                        obj.object_name)
            elasticsearch_client.index(index=elasticsearch_index_name,
                                       body=json.loads(minio.get_object(obj.object_name).decode('utf-8')))
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
dag = DAG('PolicyWatchDB_ver_' + VERSION,
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

download_task >> enrich_task >> tika_task >> elasticsearch_task
