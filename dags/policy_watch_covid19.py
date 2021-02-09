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

logger = logging.getLogger('lam-fetcher')
version = '0.7'


def enrich_policy_watch(covid19db_json_location: pathlib.Path = None,
                        covid19_enriched_fragments_output_path: pathlib.Path = None):
    if covid19db_json_location is None:
        covid19db_json_location = pathlib.Path(os.path.dirname(os.path.realpath(__file__))) / pathlib.Path(
            'covid19db.json')
    logger.info('Looking for covid19db.json in ' + str(covid19db_json_location))

    if covid19_enriched_fragments_output_path is None:
        covid19_enriched_fragments_output_path = pathlib.Path(
            os.path.dirname(os.path.realpath(__file__))) / pathlib.Path('fragments')
    logger.info('Enriched fragments will be saved locally to ' + str(covid19_enriched_fragments_output_path))

    # TODO: Following line does not work. Permission denied.
    covid19_enriched_fragments_output_path.mkdir(parents=True, exist_ok=True)

    logging.info('Starting the enrichment...')
    with open(covid19db_json_location, encoding='utf-8') as covid19db:
        covid19json = json.loads(covid19db.read())

    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        logger.info('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['fieldData']['title'])

        for source in field_data['portalData']['sources']:
            __download_source(source)
            with open(covid19_enriched_fragments_output_path / hashlib.sha256(
                    source['sources::url'].encode('utf-8')).hexdigest(), 'w') as enriched_fragment_file:
                json.dump(source, enriched_fragment_file)
        break


def __download_source(source):
    try:
        url = source['sources::url'] if source['sources::url'].startswith('http') else (
                'http://' + source['sources::url'])
        request = requests.get(url, allow_redirects=True)

        source['content'] = str(request.content)
    except Exception as ex:
        source['failure_reason'] = str(ex)

    return source


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 7),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('PolicyWatch_DB_Enrich_DAG_version_' + version, default_args=default_args,
          schedule_interval=timedelta(minutes=1000))

python_task = PythonOperator(task_id='PolicyWatch_DB_Enrich_task_version_' + version,
                             python_callable=enrich_policy_watch, retries=1, dag=dag)
