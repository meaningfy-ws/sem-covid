#!/usr/bin/python3

# main.py
# Date:  04/03/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import hashlib
import logging
import tempfile
import zipfile
from datetime import datetime, timedelta
from itertools import chain
from json import dumps, loads
from pathlib import Path

import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from elasticsearch import Elasticsearch
from tika import parser

from sem_covid.adapters.minio_adapter import MinioAdapter

logger = logging.getLogger(__name__)
VERSION = '0.9.0'

# TODO: rely on the project configs for these variables: both environment or Airflow vars

URL: str = Variable.get('TREATIES_SPARQL_URL')
APACHE_TIKA_URL = Variable.get('APACHE_TIKA_URL')

ELASTICSEARCH_INDEX_NAME: str = Variable.get('TREATIES_ELASTIC_SEARCH_INDEX_NAME')
ELASTICSEARCH_PROTOCOL: str = Variable.get('ELASTICSEARCH_PROTOCOL')
ELASTICSEARCH_HOSTNAME: str = Variable.get('ELASTICSEARCH_URL')
ELASTICSEARCH_PORT: int = Variable.get('ELASTICSEARCH_PORT')
ELASTICSEARCH_USER: str = Variable.get('ELASTICSEARCH_USERNAME')
ELASTICSEARCH_PASSWORD: str = Variable.get('ELASTICSEARCH_PASSWORD')

CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'

TREATIES_JSON = Variable.get('TREATIES_JSON')
MINIO_URL = Variable.get("MINIO_URL")
TREATIES_BUCKET = Variable.get('TREATIES_BUCKET_NAME')
MINIO_ACCESS_KEY = Variable.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = Variable.get("MINIO_SECRET_KEY")


def make_request(query):
    wrapper = SPARQLWrapper(URL)
    wrapper.setQuery(query)
    wrapper.setReturnFormat(JSON)
    return wrapper.query().convert()


def get_treaty_items():
    logger.info(f'Start retrieving works of treaties..')
    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, TREATIES_BUCKET)
    minio.empty_bucket(object_name_prefix=None)
    minio.empty_bucket(object_name_prefix=RESOURCE_FILE_PREFIX)
    minio.empty_bucket(object_name_prefix=TIKA_FILE_PREFIX)
    query = """prefix cdm: <http://publications.europa.eu/ontology/cdm#>
                prefix lang: <http://publications.europa.eu/resource/authority/language/>

                select
                distinct ?work
                ?doc_id
                ?title
                ?comment
                group_concat(distinct ?eurovocConcept; separator=", ") as ?eurovocConcepts
                group_concat(distinct ?subjectMatter; separator=", ") as ?subjectMatters
                group_concat(distinct ?directoryCode; separator=", ") as ?directoryCodes
                ?dateCreated
                ?dateDocument
                ?legalDateSignature
                ?legalDateEntryIntoForce
                ?legalIdCelex
                ?oj_sector
                group_concat(distinct ?legalEli; separator=", ") as ?legalElis
                group_concat(?createdBy; separator=", ") as ?authors
                ?pdf_to_download
                ?html_to_download
                {
                    ?work a cdm:treaty;
                            cdm:work_id_document ?doc_id.
                    OPTIONAL
                    {
                        ?work cdm:resource_legal_id_sector ?oj_sector
                    }
                    optional {
                    ?work cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/TREATY>
                    }
                    optional {
                    ?work cdm:resource_legal_in-force "true"^^<http://www.w3.org/2001/XMLSchema#boolean>.
                    }
                    optional {
                        ?expression cdm:expression_belongs_to_work ?work. 
                        ?expression cdm:expression_title ?title.
                        ?expression cdm:expression_uses_language lang:ENG.

                        OPTIONAL
                        {
                            ?manif_pdf cdm:manifestation_manifests_expression ?expression.
                            ?manif_pdf cdm:manifestation_type ?type_pdf.
                            FILTER(str(?type_pdf) in ('pdf', 'pdfa1a', 'pdfa2a', 'pdfa1b', 'pdfx'))
                        }

                        OPTIONAL
                        {
                            ?manif_html cdm:manifestation_manifests_expression ?expression.
                            ?manif_html cdm:manifestation_type ?type_html.
                            FILTER(str(?type_html) in ('html', 'xhtml'))
                        }

                        BIND(IRI(concat(?manif_pdf,"/zip")) as ?pdf_to_download)
                        BIND(IRI(concat(?manif_html,"/zip")) as ?html_to_download)
                    }
                    optional {
                    ?work cdm:resource_legal_comment_internal ?comment .
                    }
                    optional {
                    ?work cdm:work_is_about_concept_eurovoc ?eurovocConcept 
                    }
                    optional {
                    ?work cdm:resource_legal_is_about_subject-matter ?subjectMatter 
                    }
                    optional {
                    ?work cdm:resource_legal_is_about_concept_directory-code ?directoryCode 
                    }
                    optional {
                    ?work cdm:work_created_by_agent ?createdBy .
                    }
                    optional {
                    ?work cdm:work_date_creation ?dateCreated .
                    }
                    optional {
                    ?work cdm:work_date_document ?dateDocument .
                    }
                    optional {
                    ?work cdm:resource_legal_date_signature ?legalDateSignature .
                    }
                    optional {
                    ?work cdm:resource_legal_date_entry-into-force ?legalDateEntryIntoForce .
                    }
                    optional {
                    ?work cdm:resource_legal_id_celex ?legalIdCelex .
                    }
                    optional {
                    ?work cdm:resource_legal_eli ?legalEli .
                    }
                    filter not exists{?work a cdm:fragment_resource_legal}.
                    filter not exists {?work cdm:work_embargo [].}
                    FILTER EXISTS {?manif cdm:manifestation_manifests_expression ?expression}
                }
                ORDER BY ?dateDocument"""

    uploaded_bytes = minio.put_object_from_string(TREATIES_JSON, dumps(make_request(query)))
    logger.info(f'Save query result to the {TREATIES_JSON} bucket')
    logger.info('Uploaded ' + str(uploaded_bytes) + ' bytes to bucket [' + TREATIES_BUCKET + '] at ' + MINIO_URL)


def download_file(source: dict, location_details: dict, file_name: str, minio: MinioAdapter):
    try:
        url = location_details['value'] if location_details['value'].startswith('http') \
            else 'http://' + location_details['value']
        request = requests.get(url, allow_redirects=True, timeout=30)
        minio.put_object(RESOURCE_FILE_PREFIX + file_name, request.content)
        source[CONTENT_PATH_KEY] = file_name
        return True

    except Exception as e:
        source[FAILURE_KEY] = str(e)
        return False


def download_treaties_items():
    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, TREATIES_BUCKET)
    treaties_json = loads(minio.get_object(TREATIES_JSON).decode('utf-8'))
    logger.info(dumps(treaties_json)[:100])
    treaties_json = treaties_json['results']['bindings']
    treaties_items_count = len(treaties_json)
    logger.info(f'Found {treaties_items_count} treaties items.')

    counter = {
        'html': 0,
        'pdf': 0
    }

    for index, item in enumerate(treaties_json):
        if item.get('html_to_download') and item['html_to_download']['value'] != '/zip':
            filename = hashlib.sha256(item['html_to_download']['value'].encode('utf-8')).hexdigest()

            logger.info(
                f"[{index + 1}/{treaties_items_count}] Downloading HTML file for {item['title']['value']}")

            html_file = filename + '_html.zip'
            if download_file(item, item['html_to_download'], html_file, minio):
                counter['html'] += 1
        elif item.get('pdf_to_download') and item['pdf_to_download']['value'] != '/zip':
            filename = hashlib.sha256(item['pdf_to_download']['value'].encode('utf-8')).hexdigest()

            logger.info(
                f"[{index + 1}/{treaties_items_count}] Downloading PDF file for {item['title']['value']}")

            pdf_file = filename + '_pdf.zip'
            if download_file(item, item['pdf_to_download'], pdf_file, minio):
                counter['pdf'] += 1
        else:
            logger.exception(f"No treaties files has been found for {item['title']['value']}")

    updated_treaties_json = loads(minio.get_object(TREATIES_JSON).decode('utf-8'))
    updated_treaties_json['results']['bindings'] = treaties_json
    minio.put_object_from_string(TREATIES_JSON, dumps(updated_treaties_json))

    logger.info(f"Downloaded {counter['html']} HTML manifestations and {counter['pdf']} PDF manifestations.")


def extract_document_content_with_tika():
    logger.info(f'Using Apache Tika at {APACHE_TIKA_URL}')
    logger.info(f'Loading resource files from {TREATIES_JSON}')
    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, TREATIES_BUCKET)
    treaties_json = loads(minio.get_object(TREATIES_JSON))['results']['bindings']
    treaties_items_count = len(treaties_json)

    counter = {
        'general': 0,
        'success': 0
    }

    for index, item in enumerate(treaties_json):
        valid_sources = 0
        identifier = item['title']['value']
        logger.info(f'[{index + 1}/{treaties_items_count}] Processing {identifier}')
        item['content'] = list()

        if FAILURE_KEY in item:
            logger.info(
                f'Will not process source <{identifier}> because it failed download with reason <{item[FAILURE_KEY]}>')
        else:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    current_zip_location = Path(temp_dir) / Path(item[CONTENT_PATH_KEY])
                    with open(current_zip_location, 'wb') as current_zip:
                        content_bytes = bytearray(minio.get_object(RESOURCE_FILE_PREFIX + item[CONTENT_PATH_KEY]))
                        current_zip.write(content_bytes)
                    with zipfile.ZipFile(current_zip_location, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    logger.info(f'Processing each file from {item[CONTENT_PATH_KEY]}:')
                    for content_file in chain(Path(temp_dir).glob('*.html'), Path(temp_dir).glob('*.pdf')):
                        logger.info(f'Parsing {Path(content_file).name}')
                        counter['general'] += 1
                        parse_result = parser.from_file(str(content_file), APACHE_TIKA_URL)

                        if 'content' in parse_result:
                            # logger.info(f'Parse result (first 100 characters): {dumps(parse_result)[:100]}')
                            item['content'].append(parse_result['content'])
                            counter['success'] += 1

                            valid_sources += 1
                        else:
                            logger.warning(
                                f'Apache Tika did NOT return a valid content for the source {Path(content_file).name}')
            except Exception as e:
                logger.exception(e)
        if valid_sources:
            filename = hashlib.sha256(item['html_to_download']['value'].encode('utf-8')).hexdigest()
            minio.put_object_from_string(TIKA_FILE_PREFIX + filename, dumps(item))

    updated_treaties_json = loads(minio.get_object(TREATIES_JSON).decode('utf-8'))
    updated_treaties_json['results']['bindings'] = treaties_json
    minio.put_object_from_string(TREATIES_JSON, dumps(updated_treaties_json))

    logger.info(f"Parsed a total of {counter['general']} files, of which successfully {counter['success']} files.")


def upload_processed_documents_to_elasticsearch():
    elasticsearch_client = Elasticsearch(
        [
            f'{ELASTICSEARCH_PROTOCOL}://{ELASTICSEARCH_USER}:{ELASTICSEARCH_PASSWORD}@{ELASTICSEARCH_HOSTNAME}:{ELASTICSEARCH_PORT}'])

    logger.info(f'Using ElasticSearch at {ELASTICSEARCH_PROTOCOL}://{ELASTICSEARCH_HOSTNAME}:{ELASTICSEARCH_PORT}')

    logger.info(f'Loading files from {MINIO_URL}')

    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, TREATIES_BUCKET)
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
    "start_date": datetime(2021, 2, 21),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500)
}

dag = DAG('Treaty_Items_DAG_version_' + VERSION, default_args=default_args,
          schedule_interval="@once",
          max_active_runs=1)

get_treaties_json_task = PythonOperator(task_id='Treaty_Items_task_version_' + VERSION,
                                        python_callable=get_treaty_items, retries=1, dag=dag)

download_documents_from_treaties_json_task = PythonOperator(
    task_id=f'get_treaties_documents_task_version_{VERSION}',
    python_callable=download_treaties_items, retries=1, dag=dag)

extract_content_with_tika_task = PythonOperator(
    task_id=f'treaties_extract_content_task_version_{VERSION}',
    python_callable=extract_document_content_with_tika, retries=1, dag=dag)

upload_to_elastic_task = PythonOperator(
    task_id=f'treaties_elastic_upload_task_version_{VERSION}',
    python_callable=upload_processed_documents_to_elasticsearch, retries=1, dag=dag)

get_treaties_json_task >> download_documents_from_treaties_json_task >> extract_content_with_tika_task >> upload_to_elastic_task
