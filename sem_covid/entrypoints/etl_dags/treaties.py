#!/usr/bin/python3

# legal_initiatives.py
# Date:  18/05/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
import hashlib
import json
import logging
from datetime import datetime, timedelta

from SPARQLWrapper import SPARQLWrapper, JSON
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid import config
from sem_covid.adapters.minio_adapter import MinioAdapter
from sem_covid.entrypoints.etl_dags.treaties_worker import DAG_NAME as SLAVE_DAG_NAME

VERSION = '0.001'
DATASET_NAME = "treaties"
DAG_TYPE = "etl"
DAG_NAME = DAG_TYPE + '_' + DATASET_NAME + '_' + VERSION
CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
FIELD_DATA_PREFIX = "field_data/"
logger = logging.getLogger(__name__)


def make_request(query):
    wrapper = SPARQLWrapper(config.TREATIES_SPARQL_URL)
    wrapper.setQuery(query)
    wrapper.setReturnFormat(JSON)
    return wrapper.query().convert()


def download_and_split_callable():
    logger.info(f'Start retrieving works of treaties..')
    minio = MinioAdapter(config.TREATIES_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    minio.empty_bucket(object_name_prefix=None)
    minio.empty_bucket(object_name_prefix=RESOURCE_FILE_PREFIX)
    minio.empty_bucket(object_name_prefix=TIKA_FILE_PREFIX)
    minio.empty_bucket(object_name_prefix=FIELD_DATA_PREFIX)
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

    treaties_json = make_request(query)['results']['bindings']
    result = json.dumps(treaties_json)

    uploaded_bytes = minio.put_object_from_string(config.TREATIES_JSON, str(result.encode('utf-8')))
    logger.info('Uploaded ' + str(
        uploaded_bytes) + ' bytes to bucket [' + config.TREATIES_BUCKET_NAME + '] at ' + config.MINIO_URL)

    list_count = len(treaties_json)
    current_item = 0
    logger.info("Start splitting " + str(list_count) + " items.")
    for field_data in treaties_json:
        current_item += 1
        filename = FIELD_DATA_PREFIX + hashlib.sha256(field_data['work']['value'].encode('utf-8')).hexdigest() + ".json"
        logger.info(
            '[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['work'][
                'value'] + " saved to " + filename)
        minio.put_object_from_string(filename, json.dumps(field_data))


def execute_worker_dags_callable(**context):
    minio = MinioAdapter(config.TREATIES_BUCKET_NAME, config.MINIO_URL, config.MINIO_ACCESS_KEY,
                         config.MINIO_SECRET_KEY)
    field_data_objects = minio.list_objects(FIELD_DATA_PREFIX)
    count = 0

    for field_data_object in field_data_objects:
        TriggerDagRunOperator(
            task_id='trigger_slave_dag____' + field_data_object.object_name.replace("/", "_"),
            trigger_dag_id=SLAVE_DAG_NAME,
            conf={"filename": field_data_object.object_name}
        ).execute(context)
        count += 1

    logger.info("Created " + str(count) + " DAG runs")


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
with DAG(DAG_NAME, default_args=default_args, schedule_interval="@once", max_active_runs=1, concurrency=4) as dag:
    download_task = PythonOperator(task_id='download_and_split',
                                   python_callable=download_and_split_callable, retries=1, dag=dag)

    execute_worker_dags = PythonOperator(task_id='execute_worker_dags',
                                         python_callable=execute_worker_dags_callable, retries=1, dag=dag,
                                         provide_context=True)

    download_task >> execute_worker_dags
