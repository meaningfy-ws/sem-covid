#!/usr/bin/python3

# pwdb_master.py
# Date:  10.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import hashlib
import json
import requests
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid.adapters.dag.base_etl_dag_pipeline import BaseMasterPipeline
from sem_covid.services.sc_wrangling.json_transformer import transform_pwdb
from sem_covid.services.store_registry import StoreRegistryABC
import logging

CONTENT_KEY = 'content'
CONTENT_LANGUAGE = "language"
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
FIELD_DATA_PREFIX = "field_data/"
logger = logging.getLogger(__name__)


class PWDBMasterDag(BaseMasterPipeline):
    def __init__(self, store_registry: StoreRegistryABC, minio_url: str, bucket_name: str,
                 dataset_url: str, dataset_local_filename: str,
                 worker_dag_name: str
                 ) -> None:
        self.store_registry = store_registry
        self.minio_url = minio_url
        self.bucket_name = bucket_name
        self.dataset_url = dataset_url
        self.dataset_local_filename = dataset_local_filename
        self.worker_dag_name = worker_dag_name

    def select_assets(self, *args, **kwargs) -> None:
        response = requests.get(self.dataset_url, stream=True,timeout=30)
        response.raise_for_status()
        minio = self.store_registry.minio_object_store(self.bucket_name)
        for prefix in [None, RESOURCE_FILE_PREFIX, TIKA_FILE_PREFIX, FIELD_DATA_PREFIX]:
            minio.empty_bucket(object_name_prefix=prefix)
        transformed_json = transform_pwdb(json.loads(response.content))
        uploaded_bytes = minio.put_object(self.dataset_local_filename, json.dumps(transformed_json).encode('utf-8'))
        logger.info(
            'Uploaded ' + str(uploaded_bytes) + ' bytes to bucket [' + self.bucket_name + '] at ' + self.minio_url)

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
                trigger_dag_id=self.worker_dag_name,
                conf={"filename": field_data_object.object_name}).execute(context)
