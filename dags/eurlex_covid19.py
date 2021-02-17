import hashlib
import logging
import os
import tempfile
import zipfile
from itertools import chain
from json import dumps, loads
from pathlib import Path
from datetime import datetime, timedelta
from typing import Union

import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from tika import parser
from elasticsearch import Elasticsearch

logger = logging.getLogger('lam-fetcher')

VERSION = '0.2.3'

URL: str = Variable.get('EURLEX_SPARQL_URL')
EURLEX_JSON_LOCATION = Path(os.path.dirname(os.path.realpath(__file__))) / Variable.get('EURLEX_DATASET_LOCAL_FILENAME')
EURLEX_DOWNLOAD_LOCATION = Path(os.path.dirname(os.path.realpath(__file__))) / Variable.get('EURLEX_RESOURCES')
APACHE_TIKA_URL = Variable.get('APACHE_TIKA_URL')
TIKA_LOCATION = Path(os.path.dirname(os.path.realpath(__file__))) / Path('tika')

ELASTICSEARCH_INDEX_NAME: str = Variable.get('EURLEX_ELASTIC_SEARCH_INDEX_NAME')
ELASTICSEARCH_PROTOCOL: str = Variable.get('ELASTICSEARCH_PROTOCOL')
ELASTICSEARCH_HOSTNAME: str = Variable.get('ELASTICSEARCH_URL')
ELASTICSEARCH_PORT: int = Variable.get('ELASTICSEARCH_PORT')
ELASTICSEARCH_USER: str = Variable.get('ELASTICSEARCH_USERNAME')
ELASTICSEARCH_PASSWORD: str = Variable.get('ELASTICSEARCH_PASSWORD')

CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'


def make_request(query):
    wrapper = SPARQLWrapper(URL)
    wrapper.setQuery(query)
    wrapper.setReturnFormat(JSON)

    return wrapper.query().convert()


def get_covid19_items():
    logger.info('Start retrieving EURLex Covid 19 items')
    query = """prefix cdm: <http://publications.europa.eu/ontology/cdm#>
    prefix lang: <http://publications.europa.eu/resource/authority/language/>
    
    SELECT
      DISTINCT ?processed_title 
      ?date_document
      ?celex
      ?full_oj
      ?manifestation_pdf
      ?manifestation_html
      ?pdf_to_download
      ?html_to_download
      ?oj_sector
      ?resource_type
      ?legal_date_entry_into_force
      GROUP_CONCAT(DISTINCT ?author; separator=",") as ?authors
      GROUP_CONCAT(DISTINCT ?eurovoc_concept; separator=", ") as ?eurovoc_concepts
      GROUP_CONCAT(DISTINCT ?subject_matter; separator=", ") as ?subject_matters
      GROUP_CONCAT(DISTINCT ?directory_code; separator=", ") as ?directory_codes
      GROUP_CONCAT(DISTINCT ?legal_eli; separator=", ") as ?legal_elis
    
    WHERE
    {
      ?work cdm:resource_legal_comment_internal ?comment .
      
      FILTER(regex(STR(?comment),'COVID19'))
    
      ?work cdm:work_date_document ?date_document .
      ?work cdm:work_created_by_agent ?author . 
      ?work cdm:resource_legal_id_celex ?celex .
    
      OPTIONAL {
        ?work cdm:work_is_about_concept_eurovoc ?eurovoc_concept .
      }
      OPTIONAL {
        ?work cdm:resource_legal_is_about_subject-matter ?subject_matter .
      }
      OPTIONAL {
        ?work cdm:resource_legal_is_about_concept_directory-code ?directory_code .
      }
      OPTIONAL {
        ?work cdm:resource_legal_date_entry-into-force ?legal_date_entry_into_force .
      }
      OPTIONAL {
        ?work cdm:resource_legal_eli ?legal_eli .
      }
    
      ?work cdm:resource_legal_id_sector ?oj_sector .
    
      OPTIONAL {
        ?work cdm:work_has_resource-type ?resource_type .
      }
    
      OPTIONAL {
        ?work cdm:resource_legal_published_in_official-journal ?full_oj .
      }
    
      OPTIONAL {
        ?exp cdm:expression_title ?title .
        ?exp cdm:expression_uses_language ?lang .
        ?exp cdm:expression_belongs_to_work ?work .
    
        FILTER(?lang = lang:ENG)
    
        OPTIONAL {
          ?manifestation_pdf cdm:manifestation_manifests_expression ?exp .
          ?manifestation_pdf cdm:manifestation_type ?type_pdf .
          FILTER(STR(?type_pdf) in ('pdf', 'pdfa1a', 'pdfa2a', 'pdfa1b', 'pdfx')) 
        }
    
        OPTIONAL {
          ?manifestation_html cdm:manifestation_manifests_expression ?exp .
          ?manifestation_html cdm:manifestation_type ?type_html .
          FILTER(STR(?type_html) in ('html', 'xhtml'))
        }
      }
      BIND(IF(BOUND(?title), ?title, 'The title does not exist in that language'@en) as ?processed_title)
      BIND(IRI(CONCAT(?manifestation_pdf,"/zip")) as ?pdf_to_download)
      BIND(IRI(CONCAT(?manifestation_html,"/zip")) as ?html_to_download)
    
    } ORDER by ?date_document"""

    save_location = EURLEX_JSON_LOCATION
    logger.info(f'Save query result to {EURLEX_JSON_LOCATION}')
    save_location.write_text(dumps(make_request(query)))


def download_file(source: dict, location_details: dict, location: Union[str, Path], file_name: str):
    try:
        url = location_details['value'] if location_details['value'].startswith('http') \
            else 'http://' + location_details['value']
        request = requests.get(url, allow_redirects=True)

        (Path(location) / file_name).write_bytes(request.content)
        source[CONTENT_PATH_KEY] = file_name
        return True

    except Exception as e:
        source[FAILURE_KEY] = str(e)
        return False


def download_covid19_items():
    EURLEX_DOWNLOAD_LOCATION.mkdir(exist_ok=True)
    download_location = EURLEX_DOWNLOAD_LOCATION
    logger.info(f'Enriched fragments will be saved locally to {download_location}')

    eurlex_json = loads(EURLEX_JSON_LOCATION.read_text())
    logger.info(dumps(eurlex_json)[:100])
    eurlex_json = eurlex_json['results']['bindings']
    eurlex_items_count = len(eurlex_json)
    logger.info(f'Found {eurlex_items_count} EURLex COVID19 items.')

    counter = {
        'html': 0,
        'pdf': 0
    }

    for index, item in enumerate(eurlex_json):
        if item.get('manifestation_html'):
            filename = hashlib.sha256(item['manifestation_html']['value'].encode('utf-8')).hexdigest()

            logger.info(
                f"[{index + 1}/{eurlex_items_count}] Downloading HTML manifestation for {item['processed_title']['value']}")

            html_file = filename + '_html.zip'
            if download_file(item, item['html_to_download'], download_location, html_file):
                counter['html'] += 1
        elif item.get('manifestation_pdf'):
            filename = hashlib.sha256(item['manifestation_pdf']['value'].encode('utf-8')).hexdigest()

            logger.info(
                f"[{index + 1}/{eurlex_items_count}] Downloading PDF manifestation for {item['processed_title']['value']}")

            pdf_file = filename + '_pdf.zip'
            if download_file(item, item['pdf_to_download'], download_location, pdf_file):
                counter['pdf'] += 1
        else:
            logger.exception(f"No manifestation has been found for {item['processed_title']['value']}")

    updated_eurlex_json = loads(EURLEX_JSON_LOCATION.read_text())
    updated_eurlex_json['results']['bindings'] = eurlex_json
    EURLEX_JSON_LOCATION.write_text(dumps(updated_eurlex_json))

    logger.info(f"Downloaded {counter['html']} HTML manifestations and {counter['pdf']} PDF manifestations.")


def extract_document_content_with_tika():
    logger.info(f'Using Apache Tika at {APACHE_TIKA_URL}')
    logger.info(f'Loading resource files from {EURLEX_JSON_LOCATION}')

    eurlex_json = loads(EURLEX_JSON_LOCATION.read_text())['results']['bindings']
    eurlex_items_count = len(eurlex_json)

    logger.info(f'Saving Tika processed fragments to {TIKA_LOCATION}')
    TIKA_LOCATION.mkdir(exist_ok=True)
    tika_location = TIKA_LOCATION
    counter = {
        'general': 0,
        'success': 0
    }

    for index, item in enumerate(eurlex_json):
        valid_sources = 0
        identifier = item['processed_title']['value']
        logger.info(f'[{index + 1}/{eurlex_items_count}] Processing {identifier}')
        item['content'] = list()

        if FAILURE_KEY in item:
            logger.info(
                f'Will not process source <{identifier}> because it failed download with reason <{item[FAILURE_KEY]}>')
        else:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(EURLEX_DOWNLOAD_LOCATION / item[CONTENT_PATH_KEY], 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    logger.info(f'Processing each file from {item[CONTENT_PATH_KEY]}:')
                    for content_file in chain(Path(temp_dir).glob('*.html'), Path(temp_dir).glob('*.pdf')):
                        logger.info(f'Parsing {Path(content_file).name}')
                        counter['general'] += 1
                        parse_result = parser.from_file(str(content_file), APACHE_TIKA_URL)

                        if 'content' in parse_result:
                            logger.info(f'Parse result (first 100 characters): {dumps(parse_result)[:100]}')
                            item['content'].append(parse_result['content'])
                            counter['success'] += 1

                            valid_sources += 1
                        else:
                            logger.warning(
                                f'Apache Tika did NOT return a valid content for the source {Path(content_file).name}')
            except Exception as e:
                logger.exception(e)
        if valid_sources:
            filename = hashlib.sha256(item['manifestation_html']['value'].encode('utf-8')).hexdigest()
            (tika_location / filename).write_text(dumps(item))

    updated_eurlex_json = loads(EURLEX_JSON_LOCATION.read_text())
    updated_eurlex_json['results']['bindings'] = eurlex_json
    EURLEX_JSON_LOCATION.write_text(dumps(updated_eurlex_json))

    logger.info(f"Parsed a total of {counter['general']} files, of which successfully {counter['success']} files.")


def upload_processed_documents_to_elasticsearch():
    elasticsearch_client = Elasticsearch(
        [
            f'{ELASTICSEARCH_PROTOCOL}://{ELASTICSEARCH_USER}:{ELASTICSEARCH_PASSWORD}@{ELASTICSEARCH_HOSTNAME}:{ELASTICSEARCH_PORT}'])

    logger.info(f'Using ElasticSearch at {ELASTICSEARCH_PROTOCOL}://{ELASTICSEARCH_HOSTNAME}:{ELASTICSEARCH_PORT}')

    tika_location = TIKA_LOCATION
    logger.info(f'Loading files from {tika_location}')

    file_count = 0

    for tika_file in tika_location.iterdir():
        try:
            logger.info(f'Sending to ElasticSearch ( {ELASTICSEARCH_INDEX_NAME} ) the file {tika_file}')
            logger.info(f'first 100: {tika_file.read_text()[:100]}')
            elasticsearch_client.index(index=ELASTICSEARCH_INDEX_NAME, body=tika_file.read_text())
            file_count += 1
        except Exception as ex:
            logger.exception(ex)

    logger.info(f'Sent {file_count} file(s) to ElasticSearch.')


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
    'EURLex_COVID19_DAG_version_' + VERSION,
    default_args=default_args,
    schedule_interval=timedelta(minutes=1000)
)

get_eurlex_json_task = PythonOperator(
    task_id=f'EURLex_COVID19_get_json_task_version_{VERSION}',
    python_callable=get_covid19_items, retries=1, dag=dag)

download_documents_and_enrich_eurlex_json_task = PythonOperator(
    task_id=f'EURLex_COVID19_get_documents_task_version_{VERSION}',
    python_callable=download_covid19_items, retries=1, dag=dag)

extract_content_with_tika_task = PythonOperator(
    task_id=f'EURLex_COVID19_extract_content_task_version_{VERSION}',
    python_callable=extract_document_content_with_tika, retries=1, dag=dag)

upload_to_elastic_task = PythonOperator(
    task_id=f'EURLex_COVID19_elastic_upload_task_version_{VERSION}',
    python_callable=upload_processed_documents_to_elasticsearch, retries=1, dag=dag)

get_eurlex_json_task >> download_documents_and_enrich_eurlex_json_task >> extract_content_with_tika_task >> upload_to_elastic_task
