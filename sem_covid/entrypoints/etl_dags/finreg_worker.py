import hashlib
import json
import logging
import tempfile
import zipfile
from datetime import datetime, timedelta
from itertools import chain
from pathlib import Path

import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from airflow import DAG
from airflow.operators.python import PythonOperator
from tika import parser

from sem_covid import config
from sem_covid.entrypoints import dag_name
from sem_covid.services.sc_wrangling import json_transformer
from sem_covid.services.store_registry import StoreRegistry

logger = logging.getLogger(__name__)

DAG_NAME = dag_name(category="etl",
                    name="finreg_cellar",
                    role="worker",
                    version_patch=2)
CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
CONTENT_LANGUAGE = "language"
FIELD_DATA_PREFIX = "works/"

QUERY = '''PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX lang: <http://publications.europa.eu/resource/authority/language/>
PREFIX res_type: <http://publications.europa.eu/resource/authority/resource-type/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX subj_mat: <http://publications.europa.eu/resource/authority/subject-matter/>

PREFIX ev: <http://eurovoc.europa.eu/>

PREFIX fd_030: <http://publications.europa.eu/resource/authority/fd_030/>

SELECT DISTINCT
    ?work
    (group_concat(DISTINCT ?_title; separator="| ") as ?title)
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
    VALUES ?expr_lang { lang:ENG }
    VALUES ?work { <%WORK_ID%> }

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

    OPTIONAL {
        ?exp cdm:expression_belongs_to_work ?work ;
            cdm:expression_uses_language ?expr_lang ;
            cdm:expression_title ?_title .

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
GROUP BY ?work'''


def make_request(query):
    wrapper = SPARQLWrapper(config.EU_CELLAR_SPARQL_URL)
    wrapper.setQuery(query)
    wrapper.setReturnFormat(JSON)
    return wrapper.query().convert()


def get_single_item(query, json_file_name):
    minio = StoreRegistry.minio_object_store(config.EU_FINREG_CELLAR_BUCKET_NAME)
    response = make_request(query)['results']['bindings']
    content = json_transformer.transform_eurlex(response)
    logger.info(response)
    content = content[0]
    uploaded_bytes = minio.put_object(json_file_name, json.dumps(content).encode('utf-8'))
    logger.info(f'Saving query result to {json_file_name}')
    logger.info('Uploaded ' +
                str(uploaded_bytes) +
                ' bytes to bucket [' +
                config.EU_FINREG_CELLAR_BUCKET_NAME + '] at ' +
                config.MINIO_URL)
    return content


def extract_content_with_tika_callable(**context):
    if "work" not in context['dag_run'].conf:
        logger.error(
            "Could not find the work in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    work = context['dag_run'].conf['work']
    json_file_name = FIELD_DATA_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
    logger.info(f'Using Apache Tika at {config.APACHE_TIKA_URL}')
    logger.info(f'Loading resource files from {json_file_name}')
    minio = StoreRegistry.minio_object_store(config.EU_FINREG_CELLAR_BUCKET_NAME)
    json_content = json.loads(minio.get_object(json_file_name))

    counter = {
        'general': 0,
        'success': 0
    }

    valid_sources = 0
    identifier = json_content['work']
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

    minio.put_object(json_file_name, json.dumps(json_content))

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
    if "work" not in context['dag_run'].conf:
        logger.error(
            "Could not find the work in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    work = context['dag_run'].conf['work']
    logger.info(f'Enriched fragments will be saved locally to the bucket {config.EU_FINREG_CELLAR_BUCKET_NAME}')

    minio = StoreRegistry.minio_object_store(config.EU_FINREG_CELLAR_BUCKET_NAME)
    json_filename = FIELD_DATA_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
    json_content = get_single_item(QUERY.replace("%WORK_ID%", work), json_filename)

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
        logger.warning(f"No manifestation has been found for {(json_content['title'] or json_content['work'])}")

    minio.put_object(json_filename, json.dumps(json_content))

    logger.info(f"Downloaded {counter['html']} HTML manifestations and {counter['pdf']} PDF manifestations.")


def upload_to_elastic_callable(**context):
    if "work" not in context['dag_run'].conf:
        logger.error(
            "Could not find the work in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    work = context['dag_run'].conf['work']
    json_file_name = FIELD_DATA_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
    es_adapter = StoreRegistry.es_index_store()
    logger.info(f'Using ElasticSearch at {config.ELASTICSEARCH_HOST_NAME}:{config.ELASTICSEARCH_PORT}')

    logger.info(f'Loading files from {config.MINIO_URL}')

    minio = StoreRegistry.minio_object_store(config.EU_FINREG_CELLAR_BUCKET_NAME)
    json_content = json.loads(minio.get_object(json_file_name).decode('utf-8'))
    try:
        logger.info(
            f'Sending to ElasticSearch ( {config.EU_FINREG_CELLAR_ELASTIC_SEARCH_INDEX_NAME} ) the file {json_file_name}')
        es_adapter.index(index_name=config.EU_FINREG_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                         document_id=hashlib.sha256(work.encode('utf-8')).hexdigest(),
                         document_body=json_content)
    except Exception as ex:
        logger.exception(ex)

    logger.info(f'Sent {json_file_name} file(s) to ElasticSearch.')


def callback_subdag_clear(context):
    """Clears a subdag's tasks on retry.
        Sources:
            https://gist.github.com/camilomartinez/84c5a8bb41ad687ef0b32369a030cdc0
            https://stackoverflow.com/questions/49008716/how-can-you-re-run-upstream-task-if-a-downstream-task-fails-in-airflow-using-su
    """
    dag_id = "{}.{}".format(
        context['dag'].dag_id,
        context['ti'].task_id,
    )
    execution_date = context['execution_date']

    task = context['task']
    sdag = task.subdag
    if sdag is None:
        raise Exception("Can't find dag {}".format(dag_id))
    else:
        logging.info("Clearing SubDag: {} {}".format(dag_id, execution_date))

    sdag.clear(
        start_date=execution_date,
        end_date=execution_date,
        only_failed=False,
        only_running=False,
        confirm_prompt=False,
        include_subdags=False)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 16),
    "email": ["infro@meaningfy.ws"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(seconds=5)
}

with DAG(DAG_NAME, default_args=default_args, schedule_interval=None, max_active_runs=10, concurrency=20) as dag:
    download_documents_and_enrich_json = PythonOperator(
        task_id=f'Enrich',
        python_callable=download_documents_and_enrich_json_callable, retries=1, dag=dag,
        on_retry_callback=callback_subdag_clear,
    )

    extract_content_with_tika = PythonOperator(
        task_id=f'Tika',
        python_callable=extract_content_with_tika_callable, retries=1, dag=dag,
        on_retry_callback=callback_subdag_clear,
    )

    upload_to_elastic = PythonOperator(
        task_id=f'Elasticsearch',
        python_callable=upload_to_elastic_callable, retries=1, dag=dag,
        on_retry_callback=callback_subdag_clear,
    )

    download_documents_and_enrich_json >> extract_content_with_tika >> upload_to_elastic
