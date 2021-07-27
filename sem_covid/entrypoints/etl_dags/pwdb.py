#!/usr/bin/python3

# main.py
# Date:  22/02/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
import hashlib
import json
import logging
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid import config
from sem_covid.adapters.dag.base_etl_dag_pipeline import BaseMasterPipeline
from sem_covid.entrypoints.etl_dags.pwdb_worker import DAG_NAME as SLAVE_DAG_NAME
from sem_covid.services.sc_wrangling.json_transformer import transform_pwdb
from sem_covid.services.store_registry import store_registry, StoreRegistryABC

VERSION = '0.01'
DATASET_NAME = "pwdb"
DAG_TYPE = "etl"
DAG_NAME = DAG_TYPE + '_' + DATASET_NAME + '_' + VERSION
CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
CONTENT_LANGUAGE = "language"
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
FIELD_DATA_PREFIX = "field_data/"
logger = logging.getLogger(__name__)


class PWDBMasterDag(BaseMasterPipeline):
    def __init__(self, store_registry: StoreRegistryABC, minio_url: str, bucket_name: str,
                 dataset_url: str, dataset_local_filename: str, ) -> None:
        self.store_registry = store_registry
        self.minio_url = minio_url
        self.bucket_name = bucket_name
        self.dataset_url = dataset_url
        self.dataset_local_filename = dataset_local_filename

    def select_assets(self, *args, **kwargs) -> None:
        response = requests.get(self.dataset_url, stream=True, timeout=30)
        response.raise_for_status()
        minio = self.store_registry.minio_object_store(self.bucket_name)
        for prefix in [None, RESOURCE_FILE_PREFIX, TIKA_FILE_PREFIX, FIELD_DATA_PREFIX]:
            minio.empty_bucket(object_name_prefix=prefix)
        transformed_json = transform_pwdb(json.loads(response.content))
        uploaded_bytes = minio.put_object(self.dataset_local_filename, json.dumps(transformed_json).encode('utf-8'))
        logger.info('Uploaded ' + str(uploaded_bytes) + ' bytes to bucket [' + self.bucket_name + '] at ' + self.minio_url)

        list_count = len(transformed_json)
        current_item = 0
        logger.info("Start splitting " + str(list_count) + " items.")
        for field_data in transformed_json:
            current_item += 1
            filename = FIELD_DATA_PREFIX + hashlib.sha256(field_data['title'].encode('utf-8')).hexdigest() + ".json"
            logger.info(
                '[' + str(current_item) + ' / ' + str(list_count) + '] - '
                    + field_data['title'] + " saved to " + filename)
            minio.put_object(filename, json.dumps(field_data))

    def trigger_workers(self, **context) -> None:
        minio = self.store_registry.minio_object_store(self.bucket_name)
        field_data_objects = minio.list_objects(FIELD_DATA_PREFIX)

        for field_data_object in field_data_objects:
            TriggerDagRunOperator(
                task_id='trigger_slave_dag____' + field_data_object.object_name.replace("/", "_"),
                trigger_dag_id=SLAVE_DAG_NAME,
                conf={"filename": field_data_object.object_name}).execute(context)


# def download_and_split_callable():
#     response = requests.get(config.PWDB_DATASET_URL, stream=True, timeout=30)
#     response.raise_for_status()
#     minio = StoreRegistry.minio_object_store(config.PWDB_COVID19_BUCKET_NAME)
#     for prefix in [None, RESOURCE_FILE_PREFIX, TIKA_FILE_PREFIX, FIELD_DATA_PREFIX]:
#         minio.empty_bucket(object_name_prefix=prefix)
#
#     transformed_json = transform_pwdb(json.loads(response.content))
#
#     uploaded_bytes = minio.put_object(config.PWDB_DATASET_LOCAL_FILENAME,
#                                       json.dumps(transformed_json).encode('utf-8'))
#     logger.info('Uploaded ' + str(uploaded_bytes) + ' bytes to bucket [' + config.PWDB_COVID19_BUCKET_NAME
#                 + '] at ' + config.MINIO_URL)
#
#     list_count = len(transformed_json)
#     current_item = 0
#     logger.info("Start splitting " + str(list_count) + " items.")
#     for field_data in transformed_json:
#         current_item += 1
#         filename = FIELD_DATA_PREFIX + hashlib.sha256(field_data['title'].encode('utf-8')).hexdigest() + ".json"
#         logger.info(
#             '[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['title'] + " saved to " + filename)
#         minio.put_object(filename, json.dumps(field_data))
#
#
# def execute_worker_dags_callable(**context):
#     minio = StoreRegistry.minio_object_store(config.PWDB_COVID19_BUCKET_NAME)
#     field_data_objects = minio.list_objects(FIELD_DATA_PREFIX)
#
#     for field_data_object in field_data_objects:
#         TriggerDagRunOperator(
#             task_id='trigger_slave_dag____' + field_data_object.object_name.replace("/", "_"),
#             trigger_dag_id=SLAVE_DAG_NAME,
#             conf={"filename": field_data_object.object_name}
#         ).execute(context)

pwdb_master = PWDBMasterDag(
    store_registry=store_registry,
    minio_url=config.MINIO_URL,
    bucket_name=config.PWDB_COVID19_BUCKET_NAME,
    dataset_url=config.PWDB_DATASET_URL,
    dataset_local_filename=config.PWDB_DATASET_LOCAL_FILENAME
)

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
                                   python_callable=pwdb_master.select_assets, retries=1, dag=dag)

    execute_worker_dags = PythonOperator(task_id='execute_worker_dags',
                                         python_callable=pwdb_master.trigger_workers, retries=1, dag=dag, )

    download_task >> execute_worker_dags
