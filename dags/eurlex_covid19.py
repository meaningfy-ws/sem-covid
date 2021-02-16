import hashlib
import logging
import os
from json import dumps, loads
from pathlib import Path
from datetime import datetime, timedelta
from typing import Union

import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger('lam-fetcher')
VERSION = '0.1.10'

URL = 'http://publications.europa.eu/webapi/rdf/sparql'
EURLEX_JSON_LOCATION = Path(os.path.dirname(os.path.realpath(__file__))) / Path('eurlex.json')
EURLEX_DOWNLOAD_LOCATION = Path(os.path.dirname(os.path.realpath(__file__))) / Path('eurlex')


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


def download_file(source: dict, location: Union[str, Path], file_name: str):
    try:
        url = source['value'] if source['value'].startswith('http') else 'http://' + source['value']
        request = requests.get(url, allow_redirects=True)

        (Path(location) / file_name).write_bytes(request.content)
        source['content_path'] = file_name
        return True

    except Exception as e:
        source['failure_reason'] = str(e)
        return False


def download_covid19_items():
    download_location = EURLEX_DOWNLOAD_LOCATION
    download_location.mkdir()
    logger.info(f'Enriched fragments will be saved locally to {download_location}')

    eurlex_json = loads(EURLEX_JSON_LOCATION.read_text())['results']['bindings']
    eurlex_items_count = len(eurlex_json)
    logger.info(f'Found {eurlex_items_count} EURLex COVID19 items.')

    counter = {
        'html': 0,
        'pdf': 0
    }

    for index, item in enumerate(eurlex_json[:40]):
        if item.get('manifestation_html'):
            filename = hashlib.sha256(item['manifestation_html']['value'].encode('utf-8')).hexdigest()

            logger.info(f"[{index+1}/{eurlex_items_count}] Downloading HTML manifestation for {item['processed_title']['value']}")

            html_file = filename + '_html.zip'
            if download_file(item['html_to_download'], download_location, html_file):
                counter['html'] += 1
        elif item.get('manifestation_pdf'):
            filename = hashlib.sha256(item['manifestation_pdf']['value'].encode('utf-8')).hexdigest()

            logger.info(f"[{index+1}/{eurlex_items_count}] Downloading PDF manifestation for {item['processed_title']['value']}")

            html_file = filename + '_pdf.zip'
            if download_file(item['pdf_to_download'], download_location, html_file):
                counter['pdf'] +=1
        else:
            logger.exception(f"No manifestation has been found for {item['processed_title']['value']}")

    updated_eurlex_json = loads(EURLEX_JSON_LOCATION.read_text())
    updated_eurlex_json['results']['bindings'] = eurlex_json
    EURLEX_JSON_LOCATION.write_text(dumps(updated_eurlex_json))

    logger.info(f"Downloaded {counter['html']} HTML manifestations and {counter['pdf']} PDF manifestations.")

# check if more than 1 file in zip
def process_eurlex_items():
    covid19_items = get_covid19_items()
    download_covid19_items()


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

get_eurlex_json_task = PythonOperator(task_id=f'EURLex_COVID19_get_json_task_version_{VERSION}',
                                      python_callable=get_covid19_items, retries=1, dag=dag)

download_documents_and_enrich_eurlex_json_task = PythonOperator(task_id=f'EURLex_COVID19_get_documents_task_version_{VERSION}',
                                            python_callable=download_covid19_items, retries=1, dag=dag)

download_documents_and_enrich_eurlex_json_task.set_upstream(get_eurlex_json_task)
