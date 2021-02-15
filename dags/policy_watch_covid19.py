"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
import hashlib
import json
import logging
import os
import pathlib
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from elasticsearch import Elasticsearch

from tika import parser

# Most of the following should be loaded from Airflow variables, like this: var_name = Variable.get("APACHE_TIKA_URL")

dataset_url = 'http://static.eurofound.europa.eu/covid19db/data/covid19db.json'
dataset_local_filename = 'covid19db.json'
covid19db_json_location = pathlib.Path(os.path.dirname(os.path.realpath(__file__))) / pathlib.Path(
    dataset_local_filename)
covid19_resources = pathlib.Path(os.path.dirname(os.path.realpath(__file__))) / pathlib.Path(
    'covid19-resources')
logger = logging.getLogger('lam-fetcher')
version = '0.04'

apache_tika_url = 'http://apache-tika:9998'

elasticsearch_url = 'http://elasticsearch:9200'
elasticsearch_index_name = 'pwdb-index'
elasticsearch_protocol: str = 'http'
elasticsearch_hostname: str = 'elasticsearch'
elasticsearch_port: int = 9200
elasticsearch_user: str = 'elastic'
elasticsearch_password: str = 'changeme'


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

    input_path = covid19_resources / pathlib.Path('tika')
    logger.info('Loading files from ' + str(input_path))

    file_count = 0

    for file in os.listdir(str(input_path)):
        try:
            full_input_file_name = str(input_path / pathlib.Path(file))
            logger.info('Sending to ElasticSearch (  ' +
                        elasticsearch_index_name +
                        ' ) the file ' +
                        full_input_file_name)

            with open(full_input_file_name, encoding='utf-8') as json_file:
                elasticsearch_client.index(index=elasticsearch_index_name, body=json_file.read())
            file_count += 1
        except Exception as ex:
            logger.exception(ex)

    logger.info('Sent ' + str(file_count) + ' file(s) to ElasticSearch.')


def download_policy_dataset():
    response = requests.get(dataset_url)
    response.raise_for_status()

    with open(covid19db_json_location, 'wb') as local_dataset_file:
        local_dataset_file.write(response.content)


def download_policy_watch_resources():
    logger.info('Downloaded resources will be saved locally to ' + str(covid19_resources))
    logging.info('Starting the download...')
    with open(covid19db_json_location, encoding='utf-8') as covid19db:
        covid19json = json.loads(covid19db.read())

    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        logger.info('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['fieldData']['title'])

        if not field_data['fieldData']['d_endDate']:
            field_data['fieldData']['d_endDate'] = None  # Bozo lives here

        for source in field_data['portalData']['sources']:
            __download_source(source)

    with open(covid19_resources / pathlib.Path(dataset_local_filename), 'w') as processed_covid19db:
        json.dump(covid19json, processed_covid19db)

    logger.info("...done downloading.")


def __download_source(source):
    try:
        url = source['sources::url'] if source['sources::url'].startswith('http') else (
                'http://' + source['sources::url'])
        filename = str(covid19_resources / pathlib.Path(
            hashlib.sha256(source['sources::url'].encode('utf-8')).hexdigest() + '.res'))

        request = requests.get(url, allow_redirects=True)

        with open(filename, 'wb') as resource_file:
            resource_file.write(request.content)

        source['content_path'] = filename
    except Exception as ex:
        source['failure_reason'] = str(ex)

    return source


def process_using_tika():
    logger.info('Using Apache Tika at ' + apache_tika_url)

    input_path = covid19_resources
    logger.info('Loading resource files from ' + str(input_path))

    output_path = covid19_resources / pathlib.Path('tika')
    logger.info('Saving Tika processed fragments to ' + str(output_path))

    with open(str(covid19_resources / pathlib.Path(dataset_local_filename)), encoding='utf-8') as covid19db:
        covid19json_with_resources = json.loads(covid19db.read())

    list_count = len(covid19json_with_resources)
    current_item = 0

    for field_data in covid19json_with_resources:
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
                    parse_result = parser.from_file(source['content_path'], apache_tika_url)
                    logger.info('RESULT IS ' + json.dumps(parse_result))
                    if 'content' in parse_result:
                        source['content'] = parse_result['content']
                        valid_sources += 1
                    else:
                        logger.warning('Apache Tika did NOT return a valid content for the source ' +
                                       source['sources::title'])

            if valid_sources > 0:
                with open(output_path / hashlib.sha256(
                        field_data['fieldData']['title'].encode('utf-8')).hexdigest(), 'w') as processed_tika_file:
                    json.dump(field_data, processed_tika_file)
            else:
                logger.warning('Field ' + field_data['fieldData']['title'] + ' had no valid or processable sources.')
        except Exception as ex:
            logger.exception(ex)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 14),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5000)
}

dag = DAG('PolicyWatch_DB_Enrich_DAG_version_' + version,
          default_args=default_args,
          schedule_interval=timedelta(minutes=5000),
          max_active_runs=1)

download_task = PythonOperator(task_id='PolicyWatch_DB_Download_task_version_' + version,
                               python_callable=download_policy_dataset, retries=1, dag=dag)

enrich_task = PythonOperator(task_id='PolicyWatch_DB_Enrich_task_version_' + version,
                             python_callable=download_policy_watch_resources, retries=1, dag=dag)

tika_task = PythonOperator(task_id='PolicyWatch_DB_Tika_task_version_' + version,
                           python_callable=process_using_tika, retries=1, dag=dag)

elasticsearch_task = PythonOperator(task_id='PolicyWatch_DB_ElasticSearch_task_version_' + version,
                                    python_callable=put_elasticsearch_documents, retries=1, dag=dag)

enrich_task.set_upstream(download_task)
tika_task.set_upstream(enrich_task)
elasticsearch_task.set_upstream(tika_task)
