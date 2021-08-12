#!/usr/bin/python3

# pwdb_master.py
# Date:  10.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.etl_dags.pwdb_master import PWDBMasterDag
from sem_covid.entrypoints.etl_dags.pwdb_worker import PWDBDagWorker
from sem_covid.services.store_registry import store_registry

VERSION = '0.01'
DATASET_NAME = "pwdb"
DAG_TYPE = "etl"
MAJOR = 0
MINOR = 2
MASTER_DAG_NAME = dag_name(category=DAG_TYPE, name=DATASET_NAME + "_master", version_major=MAJOR,
                           version_minor=MINOR)

WORKER_DAG_NAME = dag_name(category=DAG_TYPE, name=DATASET_NAME + "_worker", version_major=MAJOR,
                           version_minor=MINOR)

pwdb_master = PWDBMasterDag(
    store_registry=store_registry,
    minio_url=config.MINIO_URL,
    bucket_name=config.PWDB_COVID19_BUCKET_NAME,
    dataset_url=config.PWDB_DATASET_URL,
    dataset_local_filename=config.PWDB_DATASET_LOCAL_FILENAME,
    worker_dag_name=WORKER_DAG_NAME
)

pwdb_worker = PWDBDagWorker(
    store_registry=store_registry,
    bucket_name=config.PWDB_COVID19_BUCKET_NAME,
    apache_tika_url=config.APACHE_TIKA_URL,
    elasticsearch_host_name=config.ELASTICSEARCH_HOST_NAME,
    elasticsearch_port=config.ELASTICSEARCH_PORT,
    elasticsearch_index_name=config.PWDB_ELASTIC_SEARCH_INDEX_NAME
)

# Create pwdb_master DAG

master_dag = DagFactory(
    dag_pipeline=pwdb_master, dag_name=MASTER_DAG_NAME).create_dag(schedule_interval="@once",
                                                                   max_active_runs=1, concurrency=1)

# Create pwdb_worker DAG

worker_dag = DagFactory(
    dag_pipeline=pwdb_worker, dag_name=WORKER_DAG_NAME).create_dag(schedule_interval="@once",
                                                                   max_active_runs=128, concurrency=128)
