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
from jq import compile
from tika import parser

from sem_covid.adapters.minio_adapter import MinioAdapter

logger = logging.getLogger(__name__)

VERSION = '0.10.0'

# TODO: rely on the project configs for these variables: both environment or Airflow vars

URL: str = Variable.get('EURLEX_SPARQL_URL')
APACHE_TIKA_URL = Variable.get('APACHE_TIKA_URL')

ELASTICSEARCH_INDEX_NAME: str = Variable.get('EURLEX_ELASTIC_SEARCH_INDEX_NAME')
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

EURLEX_JSON = Variable.get('EURLEX_JSON')
MINIO_URL = Variable.get("MINIO_URL")
MINIO_BUCKET = Variable.get('EURLEX_BUCKET_NAME')
MINIO_ACCESS_KEY = Variable.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = Variable.get("MINIO_SECRET_KEY")

transformation = '''{
work: .work.value,
title: .title.value,
cdm_types: .cdm_types.value | split("| "),
cdm_type_labels: .cdm_type_labels.value | split("| "),
resource_types: .resource_types.value | split("| "),
resource_type_labels: .resource_type_labels.value | split("| "),
eurovoc_concepts: .eurovoc_concepts.value | split("| "),
eurovoc_concept_labels: .eurovoc_concept_labels.value | split("| "),
subject_matters: .subject_matters.value | split("| "),
subject_matter_labels: .subject_matter_labels.value | split("| "),
directory_codes: .directory_codes.value | split("| "),
directory_codes_labels: .directory_codes_labels.value | split("| "),
celex_numbers: .celex_numbers.value | split("| "),
legal_elis: .legal_elis.value | split("| "),
id_documents: .id_documents.value | split("| "),
same_as_uris: .same_as_uris.value | split("| "),
authors: .authors.value | split("| "),
author_labels: .author_labels.value | split("| "),
full_ojs: .full_ojs.value | split("| "),
oj_sectors: .oj_sectors.value | split("| "),
internal_comments: .internal_comments.value | split("| "),
is_in_force: .is_in_force.value | split("| "),
dates_document: .dates_document.value | split("| "),
dates_created: .dates_created.value | split("| "),
legal_dates_entry_into_force: .legal_dates_entry_into_force.value | split("| "),
legal_dates_signature: .legal_dates_signature.value | split("| "),
manifs_pdf: .manifs_pdf.value | split("| "),
manifs_html: .manifs_html.value | split("| "),
pdfs_to_download: .pdfs_to_download.value | split("| "),
htmls_to_download: .htmls_to_download.value | split("| ")
}'''

SEARCH_RULE = ".[] | "


def get_transformation_rules(rules: str, search_rule: str = SEARCH_RULE):
    return (search_rule + rules).replace("\n", "")


def make_request(query):
    wrapper = SPARQLWrapper(URL)
    wrapper.setQuery(query)
    wrapper.setReturnFormat(JSON)

    return wrapper.query().convert()


def get_covid19_items():
    logger.info('Start retrieving EURLex Covid 19 items')
    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET)
    minio.empty_bucket(object_name_prefix=None)
    minio.empty_bucket(object_name_prefix=RESOURCE_FILE_PREFIX)
    minio.empty_bucket(object_name_prefix=TIKA_FILE_PREFIX)

    query = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX lang: <http://publications.europa.eu/resource/authority/language/>
    PREFIX res_type: <http://publications.europa.eu/resource/authority/resource-type/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    
    SELECT DISTINCT
        ?work ?title
    
        (group_concat(DISTINCT ?cdm_type; separator="| ") as ?cdm_types)
        (group_concat(DISTINCT ?cdm_type_label; separator="| ") as ?cdm_type_labels)
    
        (group_concat(DISTINCT ?resource_type; separator="| ") as ?resource_types)
        (group_concat(DISTINCT ?resource_type_label; separator="| ") as ?resource_type_labels)
    
        (group_concat(DISTINCT ?eurovoc_concept; separator="| ") as ?eurovoc_concepts)
        (group_concat(DISTINCT ?eurovoc_concept_label; separator="| ") as ?eurovoc_concept_labels)
    
        (group_concat(DISTINCT ?subject_matter; separator="| ") as ?subject_matters)
        (group_concat(DISTINCT ?subject_matter_label; separator="| ") as ?subject_matter_labels)
    
        (group_concat(DISTINCT ?directory_code; separator="| ") as ?directory_codes)
        (group_concat(DISTINCT ?directory_code_label; separator="| ") as ?directory_codes_labels)
    
        (group_concat(DISTINCT ?celex; separator="| ") as ?celex_numbers)
        (group_concat(DISTINCT ?legal_eli; separator="| ") as ?legal_elis)
        (group_concat(DISTINCT ?id_document; separator="| ") as ?id_documents)
        (group_concat(DISTINCT ?same_as_uri; separator="| ") as ?same_as_uris)
    
        (group_concat(DISTINCT ?author; separator="| ") as ?authors)
        (group_concat(DISTINCT ?author_label; separator="| ") as ?author_labels)
    
        (group_concat(DISTINCT ?full_oj; separator="| ") as ?full_ojs)
        (group_concat(DISTINCT ?oj_sector; separator="| ") as ?oj_sectors)
        (group_concat(DISTINCT ?internal_comment; separator="| ") as ?internal_comments)
        (group_concat(DISTINCT ?in_force; separator="| ") as ?is_in_force)
    
        (group_concat(DISTINCT ?date_document; separator="| ") as ?dates_document)
        (group_concat(DISTINCT ?date_created; separator="| ") as ?dates_created)
        (group_concat(DISTINCT ?legal_date_entry_into_force; separator="| ") as ?legal_dates_entry_into_force)
        (group_concat(DISTINCT ?legal_date_signature; separator="| ") as ?legal_dates_signature)
    
        (group_concat(DISTINCT ?manif_pdf; separator="| ") as ?manifs_pdf)
        (group_concat(DISTINCT ?manif_html; separator="| ") as ?manifs_html)
        (group_concat(DISTINCT ?pdf_to_download; separator="| ") as ?pdfs_to_download)
        (group_concat(DISTINCT ?html_to_download; separator="| ") as ?htmls_to_download)
    WHERE {
        # selector criteria
        VALUES ?expr_lang { lang:ENG}
        ?work cdm:resource_legal_comment_internal ?comment .
        FILTER (regex(str(?comment),'COVID19'))
        FILTER NOT EXISTS { ?work cdm:work_embargo [] . }
    
        # metadata - classification criteria
        OPTIONAL {
            ?work a ?cdm_type .
            OPTIONAL {
                ?cdm_type skos:prefLabel ?cdm_type_label .
                FILTER (lang(?cdm_type_label)="en")
            }
        }
        OPTIONAL {
            ?work cdm:work_has_resource-type ?resource_type .
            OPTIONAL {
                ?resource_type skos:prefLabel ?resource_type_label .
                FILTER (lang(?resource_type_label)="en")
            }
        }
        OPTIONAL {
            ?work cdm:resource_legal_is_about_subject-matter ?subject_matter .
            OPTIONAL {
                ?subject_matter skos:prefLabel ?subject_matter_label .
                FILTER (lang(?subject_matter_label)="en")
            }
        }
        OPTIONAL {
            ?work cdm:resource_legal_is_about_concept_directory-code ?directory_code .
            OPTIONAL {
                ?directory_code skos:prefLabel ?directory_code_label .
                FILTER (lang(?directory_code_label)="en")
            }
        }
        OPTIONAL {
            ?work cdm:work_is_about_concept_eurovoc ?eurovoc_concept .
            OPTIONAL {
                ?eurovoc_concept skos:prefLabel ?eurovoc_concept_label .
                FILTER (lang(?eurovoc_concept_label)="en")
            }
        }
    
        # metadata - descriptive criteria
        OPTIONAL {
            ?work cdm:work_created_by_agent ?author .
            OPTIONAL {
                ?author skos:prefLabel ?author_label .
                FILTER (lang(?author_label)="en")
            }
        }
        OPTIONAL {
            ?work cdm:resource_legal_in-force ?in_force .
        }
        OPTIONAL {
            ?work cdm:resource_legal_id_sector ?oj_sector .
        }
        OPTIONAL {
            ?work cdm:resource_legal_published_in_official-journal ?full_oj .
        }
        OPTIONAL {
            ?work cdm:resource_legal_comment_internal ?internal_comment .
        }
        OPTIONAL {
            ?work cdm:work_date_document ?date_document .
        }
        OPTIONAL {
            ?work cdm:work_date_creation ?date_created .
        }
        OPTIONAL {
            ?work cdm:resource_legal_date_signature ?legal_date_signature .
        }
        OPTIONAL {
            ?work cdm:resource_legal_date_entry-into-force ?legal_date_entry_into_force .
        }
    
        # metadata - identification properties
        OPTIONAL {
            ?work cdm:resource_legal_id_celex ?celex .
        }
        OPTIONAL {
            ?work cdm:resource_legal_eli ?legal_eli .
        }
        OPTIONAL {
            ?work cdm:work_id_document ?id_document .
        }
        OPTIONAL {
            ?work owl:sameAs ?same_as_uri .
        }
    
        # diving down FRBR structure for the title and the content
        OPTIONAL {
            ?exp cdm:expression_belongs_to_work ?work ;
                 cdm:expression_uses_language ?expr_lang ;
                 cdm:expression_title ?title .
    
            OPTIONAL {
                ?manif_pdf cdm:manifestation_manifests_expression ?exp ;
                           cdm:manifestation_type ?type_pdf .
                FILTER (str(?type_pdf) in ('pdf', 'pdfa1a', 'pdfa2a', 'pdfa1b', 'pdfx'))
            }
            OPTIONAL {
                ?manif_html cdm:manifestation_manifests_expression ?exp ;
                            cdm:manifestation_type ?type_html .
                FILTER (str(?type_html) in ('html', 'xhtml'))
            }
        }
        BIND(IRI(concat(?manif_pdf,"/zip")) as ?pdf_to_download)
        BIND(IRI(concat(?manif_html,"/zip")) as ?html_to_download)
    }
    GROUP BY ?work ?title
    ORDER BY ?work ?title"""

    response = make_request(query)['results']['bindings']
    transformed_json = compile(get_transformation_rules(transformation)).input(response).all()
    uploaded_bytes = minio.put_object(EURLEX_JSON, dumps(transformed_json).encode('utf-8'))

    logger.info(f'Save query result to {EURLEX_JSON}')
    logger.info('Uploaded ' + str(uploaded_bytes) + ' bytes to bucket [' + MINIO_BUCKET + '] at ' + MINIO_URL)


def download_file(source: dict, location_details: str, file_name: str, minio: MinioAdapter):
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


def download_covid19_items():
    logger.info(f'Enriched fragments will be saved locally to the bucket {MINIO_BUCKET}')

    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET)

    eurlex_json = loads(minio.get_object(EURLEX_JSON).decode('utf-8'))
    eurlex_items_count = len(eurlex_json)
    logger.info(f'Found {eurlex_items_count} EURLex COVID19 items.')

    counter = {
        'html': 0,
        'pdf': 0
    }

    for index, item in enumerate(eurlex_json):
        item[CONTENT_PATH_KEY] = list()
        if item.get('manifs_html'):
            for html_manifestation in item.get('htmls_to_download'):
                filename = hashlib.sha256(html_manifestation.encode('utf-8')).hexdigest()

                logger.info(
                    f"[{index + 1}/{eurlex_items_count}] Downloading HTML manifestation for {item['title']}")

                html_file = filename + '_html.zip'
                if download_file(item, html_manifestation, html_file, minio):
                    counter['html'] += 1
        elif item.get('manifs_pdf'):
            for pdf_manifestation in item.get('pdfs_to_download'):

                filename = hashlib.sha256(pdf_manifestation.encode('utf-8')).hexdigest()

                logger.info(
                    f"[{index + 1}/{eurlex_items_count}] Downloading PDF manifestation for {item['title']}")

                pdf_file = filename + '_pdf.zip'
                if download_file(item, pdf_manifestation, pdf_file, minio):
                    counter['pdf'] += 1
        else:
            logger.exception(f"No manifestation has been found for {item['title']}")

    minio.put_object_from_string(EURLEX_JSON, dumps(eurlex_json))

    logger.info(f"Downloaded {counter['html']} HTML manifestations and {counter['pdf']} PDF manifestations.")


def extract_document_content_with_tika():
    logger.info(f'Using Apache Tika at {APACHE_TIKA_URL}')
    logger.info(f'Loading resource files from {EURLEX_JSON}')
    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET)
    eurlex_json = loads(minio.get_object(EURLEX_JSON))
    eurlex_items_count = len(eurlex_json)

    counter = {
        'general': 0,
        'success': 0
    }

    for index, item in enumerate(eurlex_json):
        valid_sources = 0
        identifier = item['title']
        logger.info(f'[{index + 1}/{eurlex_items_count}] Processing {identifier}')
        item[CONTENT_KEY] = list()

        if FAILURE_KEY in item:
            logger.info(
                f'Will not process source <{identifier}> because it failed download with reason <{item[FAILURE_KEY]}>')
        else:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    for content_path in item[CONTENT_PATH_KEY]:
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
                            parse_result = parser.from_file(str(content_file), APACHE_TIKA_URL)

                            if 'content' in parse_result:
                                # logger.info(f'Parse result (first 100 characters): {dumps(parse_result)[:100]}')
                                item[CONTENT_KEY].append(parse_result['content'])
                                counter['success'] += 1

                                valid_sources += 1
                            else:
                                logger.warning(
                                    f'Apache Tika did NOT return a valid content for the source {Path(content_file).name}')
            except Exception as e:
                logger.exception(e)
        if valid_sources:
            manifestation = item.get('manifs_html', [None])[0] or item.get('manifs_pdf', [None])[0]
            filename = hashlib.sha256(manifestation.encode('utf-8')).hexdigest()
            minio.put_object_from_string(TIKA_FILE_PREFIX + filename, dumps(item))

    minio.put_object_from_string(EURLEX_JSON, dumps(eurlex_json))

    logger.info(f"Parsed a total of {counter['general']} files, of which successfully {counter['success']} files.")


def upload_processed_documents_to_elasticsearch():
    elasticsearch_client = Elasticsearch(
        [
            f'{ELASTICSEARCH_PROTOCOL}://{ELASTICSEARCH_USER}:{ELASTICSEARCH_PASSWORD}@{ELASTICSEARCH_HOSTNAME}:{ELASTICSEARCH_PORT}'])

    logger.info(f'Using ElasticSearch at {ELASTICSEARCH_PROTOCOL}://{ELASTICSEARCH_HOSTNAME}:{ELASTICSEARCH_PORT}')

    logger.info(f'Loading files from {MINIO_URL}')

    minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET)
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
    "start_date": datetime(2021, 2, 16),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500)
}

dag = DAG(
    'EURLex_COVID19_ver_' + VERSION,
    default_args=default_args,
    schedule_interval="@once",
    max_active_runs=1,
    concurrency=1
)

get_eurlex_json_task = PythonOperator(
    task_id=f'Download',
    python_callable=get_covid19_items, retries=1, dag=dag)

download_documents_and_enrich_eurlex_json_task = PythonOperator(
    task_id=f'Enrich',
    python_callable=download_covid19_items, retries=1, dag=dag)

extract_content_with_tika_task = PythonOperator(
    task_id=f'Tika',
    python_callable=extract_document_content_with_tika, retries=1, dag=dag)

upload_to_elastic_task = PythonOperator(
    task_id=f'Elasticsearch',
    python_callable=upload_processed_documents_to_elasticsearch, retries=1, dag=dag)

get_eurlex_json_task >> download_documents_and_enrich_eurlex_json_task >> extract_content_with_tika_task >> upload_to_elastic_task
