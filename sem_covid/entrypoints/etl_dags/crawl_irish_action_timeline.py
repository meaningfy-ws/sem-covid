#!/usr/bin/python3

# crawl_irish_action_timeline.py
# Date:  13/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
import logging

import airflow

from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.etl_dags.crawl_pipeline import CrawlDagPipeline
from sem_covid.services.crawlers.scrapy_crawlers.spiders.irish_gov import IrishGovCrawler
from sem_covid.services.store_registry import store_registry

logger = logging.getLogger(__name__)
logger.debug(f"This line is important for DAG discovery because the *airflow module* "
             f"shall be imported here. Otherwise it does not discover DAGs in this "
             f"module. Airflow version {airflow.__version__}")

CONTENT_PATH_KEY = 'content'
DAG_TYPE = 'etl'
DATASET_NAME = "ireland_timeline"
MAJOR = 2
MINOR = 9

DAG_NAME = dag_name(category=DAG_TYPE, name=DATASET_NAME, version_major=MAJOR,
                    version_minor=MINOR)

crawl_dag_pipeline = CrawlDagPipeline(
    store_registry=store_registry,
    file_name=config.IRELAND_TIMELINE_JSON,
    bucket_name=config.IRELAND_TIMELINE_BUCKET_NAME,
    elasticsearch_index_name=config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
    content_path_key=CONTENT_PATH_KEY,
    scrapy_crawler=IrishGovCrawler)

dag = DagFactory(
    dag_pipeline=crawl_dag_pipeline, dag_name=DAG_NAME).create_dag(schedule_interval="@once",
                                                                   max_active_runs=1, concurrency=1)
