import logging

import airflow

from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.etl_dags.crawl_pipeline import CrawlDagPipeline
from sem_covid.services.crawlers.scrapy_crawlers.spiders.eu_timeline_spider import EUTimelineSpider
from sem_covid.services.store_registry import store_registry

logger = logging.getLogger(__name__)
logger.debug(f"This line is important for DAG discovery because the *airflow module* "
             f"shall be imported here. Otherwise it does not discover DAGs in this "
             f"module. Airflow version {airflow.__version__}")

CONTENT_PATH_KEY = 'detail_content'
DAG_TYPE = 'etl'
DATASET_NAME = "eu_timeline"
MAJOR = 3
MINOR = 15
DAG_NAME = dag_name(category=DAG_TYPE, name=DATASET_NAME, version_major=MAJOR,
                    version_minor=MINOR)

crawl_dag_pipeline = CrawlDagPipeline(
    store_registry=store_registry,
    file_name=config.EU_TIMELINE_JSON,
    bucket_name=config.EU_TIMELINE_BUCKET_NAME,
    elasticsearch_index_name=config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
    content_path_key=CONTENT_PATH_KEY,
    scrapy_crawler=EUTimelineSpider)

dag = DagFactory(
    dag_pipeline=crawl_dag_pipeline, dag_name=DAG_NAME).create_dag(schedule_interval="@once",
                                                                   max_active_runs=1, concurrency=1)
