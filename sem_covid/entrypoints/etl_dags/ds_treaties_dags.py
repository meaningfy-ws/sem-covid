#!/usr/bin/python3

# ds_treaties_dags.py
# Date:  13/07/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 


""" """

import logging

from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name, DEFAULT_DAG_ARGUMENTS
from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import CellarDagMaster
from sem_covid.entrypoints.etl_dags.etl_cellar_worker_dag import CellarDagWorker
from sem_covid.services.sparq_query_registry import QueryRegistry
from sem_covid.services.store_registry import store_registry
import airflow

logger = logging.getLogger(__name__)
logger.debug(f"This line is important for DAG discovery because the *airflow module* "
             f"shall be imported here. Otherwise it does not discover DAGs in this "
             f"module. Airflow version {airflow.__version__}")

MAJOR = 3
MINOR = 1

MASTER_DAG_NAME = dag_name(category="etl", name="treaties", role="master", version_major=MAJOR,
                           version_minor=MINOR)
WORKER_DAG_NAME = dag_name(category="etl", name="treaties", role="worker", version_major=MAJOR,
                           version_minor=MINOR)

# Creating the master DAG

master_pipeline = CellarDagMaster(
    list_of_queries=[QueryRegistry().TREATIES_SELECTOR],
    worker_dag_name=WORKER_DAG_NAME,
    sparql_endpoint_url=config.EU_CELLAR_SPARQL_URL,
    minio_bucket_name=config.TREATIES_BUCKET_NAME,
    store_registry=store_registry,
    index_name=config.TREATIES_ELASTIC_SEARCH_INDEX_NAME
)

master_dag = DagFactory(
    dag_pipeline=master_pipeline,
    dag_name=MASTER_DAG_NAME).create_dag(schedule_interval="@once", max_active_runs=1, concurrency=1)

# Creating the worker DAG

worker_pipeline = CellarDagWorker(
    sparql_query=QueryRegistry().METADATA_FETCHER,
    sparql_endpoint_url=config.EU_CELLAR_SPARQL_URL,
    minio_bucket_name=config.TREATIES_BUCKET_NAME,
    store_registry=store_registry,
    index_name=config.TREATIES_ELASTIC_SEARCH_INDEX_NAME)

worker_dag = DagFactory(
    dag_pipeline=worker_pipeline, dag_name=WORKER_DAG_NAME,
    default_dag_args=DEFAULT_DAG_ARGUMENTS).create_dag(schedule_interval=None, max_active_runs=4, concurrency=4)
