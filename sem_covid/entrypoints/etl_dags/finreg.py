#!/usr/bin/python3

# main.py
# Date:  24/05/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
import json
import logging
from datetime import datetime, timedelta

from SPARQLWrapper import SPARQLWrapper, JSON
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid import config
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.etl_dags.finreg_worker import DAG_NAME as SLAVE_DAG_NAME
from sem_covid.services.store_registry import StoreRegistry

logger = logging.getLogger(__name__)

DAG_NAME = dag_name(category="etl",
                    name="finreg_cellar",
                    role="main",
                    version_major="1",
                    version_minor="1",
                    version_patch="0")
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
WHERE {
    VALUES ?expr_lang { lang:ENG }
    VALUES ?eurovoc_concept {
        ev:1005
        ev:1021
        ev:1129
        ev:1488
        ev:1804
        ev:2002
        ev:4585
        ev:616
        ev:1452
        ev:3246
        ev:5868
        ev:1476
        ev:1638
        ev:504
        ev:5455
        ev:1281
        ev:189
        ev:4195
        ev:8469
        ev:1052
        ev:1132
        ev:935
        ev:2098
        ev:554
        ev:1310
        ev:2216
        ev:365
        ev:408
        ev:4392
        ev:549
        ev:6029
        ev:8468
        ev:248
        ev:3878
        ev:4347
        ev:4646
        ev:766
        ev:1095
        ev:1676
        ev:2264
        ev:5157
        ev:635
        ev:1234
        ev:1630
        ev:2463
        ev:4763
        ev:7942
        ev:1156
        ev:1164
        ev:561
        ev:6342
        ev:4493
        ev:2805
        ev:521
        ev:3951
        ev:2150
        ev:2386
        ev:1328
        ev:2220
        ev:871
        ev:1497
        ev:5090
        ev:57
        ev:924
        ev:3240
        ev:3942
        ev:1130
        ev:1326
        ev:5156
        ev:5645
        ev:6343
        ev:1971
        ev:2149
        ev:2831
        ev:4115
        ev:1459
        ev:560
        ev:1972
        ev:5964
        ev:4250
        ev:5465
        ev:5598
        ev:170
        ev:2839
        ev:4491
        ev:6362
        ev:728
        ev:1787
        ev:834
        ev:3148
        ev:4855
        ev:2219
        ev:5566
        ev:c_406ad4cc
        ev:c_dcc650ef
        ev:c_3e6af2e7
        ev:c_8f89faac
        ev:c_96124aaf
        ev:c_b499ede2
        ev:c_a18525ab
        ev:c_e749c083
        ev:c_dd52c1e9
        ev:c_dcf3f7c0
        ev:c_a3b85311
        ev:1000
        ev:1460
        ev:2497
        ev:2900
        ev:4838
        ev:2504
        ev:1448
        ev:4190
        ev:6751
        ev:165
        ev:2607
        ev:1492
        ev:5389
        ev:5218
        ev:3543
        ev:3233
        ev:1801
        ev:1815
        ev:4703
        ev:2162
        ev:55
        ev:3119
        ev:1491
        ev:115
        ev:524
        ev:1490
        ev:822
        ev:4406
        ev:3235
        ev:c_14d71455
        ev:c_7f2d2214
        ev:c_d08207d1
        ev:1313
        ev:4279
    }
    VALUES ?resource_type {
        res_type:REG
        fd_030:REGL
        res_type:DIR
        res_type:REG_IMPL
        res_type:REG_DEL
        fd_030:DIRECTIVE
        fd_030:REGIMP
        fd_030:REGDEL
        res_type:DIR_DEL
        res_type:DIR_IMPL
        res_type:REG_FINANC
        fd_030:DIRDEL
        fd_030:DIRIMP
        fd_030:DIR
        fd_030:REG
    }

    ?work cdm:work_is_about_concept_eurovoc ?eurovoc_concept ;
        cdm:work_has_resource-type|cdm:resource_legal_has_type_act_concept_type_act ?resource_type .
    OPTIONAL {
        ?exp cdm:expression_belongs_to_work ?work ;
            cdm:expression_uses_language ?expr_lang ;
            cdm:expression_title ?_title .
    }
}
GROUP BY ?work'''


def make_request(query, wrapperSPARQL):
    wrapperSPARQL.setQuery(query)
    wrapperSPARQL.setReturnFormat(JSON)
    return wrapperSPARQL.query().convert()


def get_single_item(query, json_file_name, wrapperSPARQL, minio):
    response = make_request(query, wrapperSPARQL)['results']['bindings']
    uploaded_bytes = minio.put_object(json_file_name, json.dumps(response).encode('utf-8'))
    logger.info(f'Save query result to {json_file_name}')
    logger.info('Uploaded ' +
                str(uploaded_bytes) +
                ' bytes to bucket [' +
                config.EU_FINREG_CELLAR_BUCKET_NAME + '] at ' +
                config.MINIO_URL)
    return response


def download_and_split_callable():
    # TODO: use triple store adapter
    wrapperSPARQL = SPARQLWrapper(config.EU_CELLAR_SPARQL_URL)
    minio = StoreRegistry.minio_object_store(config.EU_FINREG_CELLAR_BUCKET_NAME)
    minio.empty_bucket(object_name_prefix=None)
    minio.empty_bucket(object_name_prefix=RESOURCE_FILE_PREFIX)
    minio.empty_bucket(object_name_prefix=TIKA_FILE_PREFIX)
    minio.empty_bucket(object_name_prefix=FIELD_DATA_PREFIX)

    get_single_item(QUERY, config.EU_FINREG_CELLAR_JSON, wrapperSPARQL, minio)


def execute_worker_dags_callable(**context):
    minio = StoreRegistry.minio_object_store(config.EU_FINREG_CELLAR_BUCKET_NAME)
    works = json.loads(minio.get_object(config.EU_FINREG_CELLAR_JSON).decode('utf-8'))
    for count, work in enumerate(works):
        TriggerDagRunOperator(
            task_id='trigger_slave_dag_finreg_' + str(count),
            trigger_dag_id=SLAVE_DAG_NAME,
            conf={"work": work['work']['value']}
        ).execute(context)
    logger.info(f"Launched {SLAVE_DAG_NAME} DAG {len(works)} times for each extracted Work URI.")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 22),
    "email": ["info@meaningfy.ws"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=30)
}

with DAG(DAG_NAME, default_args=default_args, schedule_interval="@once", max_active_runs=1, concurrency=4) as dag:
    download_task = PythonOperator(task_id='download_and_split',
                                   python_callable=download_and_split_callable, retries=1, dag=dag)

    execute_worker_dags = PythonOperator(task_id='execute_worker_dags',
                                         python_callable=execute_worker_dags_callable, retries=1, dag=dag)
    download_task >> execute_worker_dags
