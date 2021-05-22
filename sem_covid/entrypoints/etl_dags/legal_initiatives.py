#!/usr/bin/python3

# legal_initiatives.py
# Date:  18/05/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import hashlib
import json
import logging
from datetime import datetime, timedelta
from json import dumps

from SPARQLWrapper import SPARQLWrapper, JSON
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid import config
from sem_covid.entrypoints.etl_dags.legal_initiatives_worker import DAG_NAME as SLAVE_DAG_NAME
from sem_covid.services.sc_wrangling import json_transformer
from sem_covid.services.store_registry import StoreRegistry

VERSION = '0.002'
DATASET_NAME = "legal_initiatives"
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
    wrapper = SPARQLWrapper(config.EU_CELLAR_SPARQL_URL)
    wrapper.setQuery(query)
    wrapper.setReturnFormat(JSON)

    return wrapper.query().convert()


def download_and_split_callable():
    logger.info('Start retrieving EURLex Covid 19 items')
    minio = StoreRegistry.minio_object_store(config.LEGAL_INITIATIVES_BUCKET_NAME)
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

        # properties specific to legal initiatives
        (group_concat(DISTINCT ?part_of_dossier; separator="| ") as ?part_of_dossiers)
        (group_concat(DISTINCT ?work_sequence; separator="| ") as ?work_sequences)
        (group_concat(DISTINCT ?related_to_work; separator="| ") as ?related_to_works)

        # properties from the template
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

        ?work cdm:work_id_document ?idd .
        FILTER (strStarts(str(?idd),"pi_com" ) )

        # metadata - specific to legal initiatives

        OPTIONAL {
            ?work cdm:work_part_of_dossier|^cdm:dossier_contains_work  ?part_of_dossier .
        }
        OPTIONAL {
            ?work cdm:work_sequence ?work_sequence .
        }
        OPTIONAL {
            ?work cdm:cdm:work_related_to_work ?related_to_work .
        }

        # metadata from the template
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
    transformed_json = json_transformer.transform_legal_initiatives(response)
    uploaded_bytes = minio.put_object(config.LEGAL_INITIATIVES_JSON,
                                      dumps(transformed_json).encode('utf-8'))

    logger.info(f'Save query result to {config.LEGAL_INITIATIVES_JSON}')
    logger.info('Uploaded ' + str(
        uploaded_bytes) + ' bytes to bucket [' + config.LEGAL_INITIATIVES_BUCKET_NAME + '] at ' + config.MINIO_URL)

    list_count = len(transformed_json)
    current_item = 0
    logger.info("Start splitting " + str(list_count) + " items.")
    for field_data in transformed_json:
        current_item += 1
        filename = FIELD_DATA_PREFIX + hashlib.sha256(field_data['work'].encode('utf-8')).hexdigest() + ".json"
        logger.info(
            '[' + str(current_item) + ' / ' + str(list_count) + '] - ' + (
                    field_data['title'] or field_data['work']) + " saved to " + filename)
        minio.put_object_from_string(filename, json.dumps(field_data))


def execute_worker_dags_callable(**context):
    minio = StoreRegistry.minio_object_store(config.LEGAL_INITIATIVES_BUCKET_NAME)
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
