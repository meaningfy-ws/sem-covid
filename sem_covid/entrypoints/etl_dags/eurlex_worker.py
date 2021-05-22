import hashlib
import json
import logging
import tempfile
import zipfile
from datetime import datetime, timedelta
from itertools import chain
from pathlib import Path

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from tika import parser

from sem_covid import config
from sem_covid.services.store_registry import StoreRegistry

logger = logging.getLogger(__name__)

VERSION = '0.006'
DATASET_NAME = "eu_cellar_worker"
DAG_TYPE = "etl"
DAG_NAME = DAG_TYPE + '_' + DATASET_NAME + '_' + VERSION
CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
CONTENT_LANGUAGE = "language"


def extract_content_with_tika_callable(**context):
    if "filename" not in context['dag_run'].conf:
        logger.error(
            "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    json_file_name = context['dag_run'].conf['filename']
    logger.info(f'Using Apache Tika at {config.APACHE_TIKA_URL}')
    logger.info(f'Loading resource files from {json_file_name}')
    minio = StoreRegistry.minio_object_store(config.EU_CELLAR_BUCKET_NAME)
    json_content = json.loads(minio.get_object(json_file_name))

    counter = {
        'general': 0,
        'success': 0
    }

    valid_sources = 0
    identifier = (json_content['title'] or json_content['work'])
    logger.info(f'Processing {identifier}')
    json_content[CONTENT_KEY] = list()

    if FAILURE_KEY in json_content:
        logger.info(
            f'Will not process source <{identifier}> because it failed download with reason <{json_content[FAILURE_KEY]}>')
    else:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                for content_path in json_content[CONTENT_PATH_KEY]:
                    current_zip_location = Path(temp_dir) / Path(content_path)
                    with open(current_zip_location, 'wb') as current_zip:
                        content_bytes = bytearray(minio.get_object(RESOURCE_FILE_PREFIX + content_path))
                        current_zip.write(content_bytes)
                    with zipfile.ZipFile(current_zip_location, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    logger.info(f'Processing each file from {content_path}:')
                    for content_file in chain(Path(temp_dir).glob('*.html'), Path(temp_dir).glob('*.pdf')):
                        logger.info(f'Parsing {Path(content_file).name}')
                        counter['general'] += 1
                        parse_result = parser.from_file(str(content_file), config.APACHE_TIKA_URL)

                        if 'content' in parse_result:
                            json_content[CONTENT_KEY].append(parse_result['content'])
                            json_content[CONTENT_LANGUAGE] = (
                                    parse_result["metadata"].get("Content-Language")
                                    or
                                    parse_result["metadata"].get("content-language")
                                    or
                                    parse_result["metadata"].get("language"))
                            counter['success'] += 1

                            valid_sources += 1
                        else:
                            logger.warning(
                                f'Apache Tika did NOT return a valid content for the source {Path(content_file).name}')
                    json_content[CONTENT_KEY] = " ".join(json_content[CONTENT_KEY])
        except Exception as e:
            logger.exception(e)

    minio.put_object_from_string(json_file_name, json.dumps(json_content))

    logger.info(f"Parsed a total of {counter['general']} files, of which successfully {counter['success']} files.")


def download_file(source: dict, location_details: str, file_name: str, minio):
    try:
        url = location_details if location_details.startswith('http') \
            else 'http://' + location_details
        request = requests.get(url, allow_redirects=True, timeout=30)
        minio.put_object(RESOURCE_FILE_PREFIX + file_name, request.content)
        source[CONTENT_PATH_KEY].append(file_name)
        return True

    except Exception as e:
        source[FAILURE_KEY] = str(e)
        return False


def download_documents_and_enrich_json_callable(**context):
    if "filename" not in context['dag_run'].conf:
        logger.error(
            "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    json_file_name = context['dag_run'].conf['filename']
    logger.info(f'Enriched fragments will be saved locally to the bucket {config.EU_CELLAR_BUCKET_NAME}')

    minio = StoreRegistry.minio_object_store(config.EU_CELLAR_BUCKET_NAME)

    json_content = json.loads(minio.get_object(json_file_name).decode('utf-8'))

    counter = {
        'html': 0,
        'pdf': 0
    }

    json_content[CONTENT_PATH_KEY] = list()
    if json_content.get('manifs_html'):
        for html_manifestation in json_content.get('htmls_to_download'):
            filename = hashlib.sha256(html_manifestation.encode('utf-8')).hexdigest()

            logger.info(f"Downloading HTML manifestation for {(json_content['title'] or json_content['work'])}")

            html_file = filename + '_html.zip'
            if download_file(json_content, html_manifestation, html_file, minio):
                counter['html'] += 1
    elif json_content.get('manifs_pdf'):
        for pdf_manifestation in json_content.get('pdfs_to_download'):

            filename = hashlib.sha256(pdf_manifestation.encode('utf-8')).hexdigest()

            logger.info(f"Downloading PDF manifestation for {(json_content['title'] or json_content['work'])}")

            pdf_file = filename + '_pdf.zip'
            if download_file(json_content, pdf_manifestation, pdf_file, minio):
                counter['pdf'] += 1
    else:
        logger.exception(f"No manifestation has been found for {json_content['title']}")

    minio.put_object_from_string(json_file_name, json.dumps(json_content))

    logger.info(f"Downloaded {counter['html']} HTML manifestations and {counter['pdf']} PDF manifestations.")


def upload_to_elastic_callable(**context):
    if "filename" not in context['dag_run'].conf:
        logger.error(
            "Could not find the file name in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    json_file_name = context['dag_run'].conf['filename']
    es_adapter = StoreRegistry.es_index_store()
    logger.info(f'Using ElasticSearch at {config.ELASTICSEARCH_HOST_NAME}:{config.ELASTICSEARCH_PORT}')

    logger.info(f'Loading files from {config.MINIO_URL}')

    minio = StoreRegistry.minio_object_store(config.EU_CELLAR_BUCKET_NAME)
    json_content = json.loads(minio.get_object(json_file_name).decode('utf-8'))
    try:
        logger.info(
            f'Sending to ElasticSearch ( {config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME} ) the file {json_file_name}')
        es_adapter.index(index_name=config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                         document_id=json_file_name.split("/")[1],
                         document_body=json_content)
    except Exception as ex:
        logger.exception(ex)

    logger.info(f'Sent {json_file_name} file(s) to ElasticSearch.')


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

with DAG(DAG_NAME, default_args=default_args, schedule_interval=None, max_active_runs=4, concurrency=4) as dag:
    download_documents_and_enrich_json = PythonOperator(
        task_id=f'Enrich',
        python_callable=download_documents_and_enrich_json_callable, retries=1, dag=dag, provide_context=True)

    extract_content_with_tika = PythonOperator(
        task_id=f'Tika',
        python_callable=extract_content_with_tika_callable, retries=1, dag=dag, provide_context=True)

    upload_to_elastic = PythonOperator(
        task_id=f'Elasticsearch',
        python_callable=upload_to_elastic_callable, retries=1, dag=dag)

    download_documents_and_enrich_json >> extract_content_with_tika >> upload_to_elastic
