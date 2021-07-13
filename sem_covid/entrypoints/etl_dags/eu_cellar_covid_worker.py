import hashlib
import json
import logging
import re
import tempfile
import zipfile
from datetime import datetime, timedelta
from itertools import chain
from pathlib import Path
import requests
from tika import parser
from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory, DagPipelineManager
from sem_covid.adapters.dag.dag_pipeline_abc import DagPipeline
from sem_covid.entrypoints import dag_name, DEFAULT_DAG_ARGUMENTS
from sem_covid.entrypoints.etl_dags.etl_cellar_worker_dag import CellarDagWorker
from sem_covid.services.sc_wrangling.data_cleaning import clean_remove_line_breaks, clean_fix_unicode, clean_to_ascii
from sem_covid.services.sparq_query_registry import QueryRegistry
from sem_covid.services.store_registry import StoreRegistryManagerABC, StoreRegistryManager

logger = logging.getLogger(__name__)

DAG_NAME = dag_name(category="etl", name="eu_cellar_covid", role="worker", version_major=1, version_minor=2)

cellar_dag_worker_pipeline = CellarDagWorker(
    sparql_query=QueryRegistry().METADATA_FETCHER,
    sparql_endpoint_url=config.EU_CELLAR_SPARQL_URL,
    minio_bucket_name=config.EU_CELLAR_BUCKET_NAME,
    store_registry=StoreRegistryManager())

worker_dag = DagFactory(
    dag_pipeline=cellar_dag_worker_pipeline, dag_name=DAG_NAME,
    default_dag_args=DEFAULT_DAG_ARGUMENTS).create_dag(schedule_interval=None, max_active_runs=128, concurrency=128)
