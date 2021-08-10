from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name
from sem_covid.services.crawlers.scrapy_crawlers.spiders.eu_timeline_spider import EUTimelineSpider
from sem_covid.entrypoints.etl_dags.crawl_pipeline import CrawlDagPipeline
from sem_covid.services.store_registry import store_registry

CONTENT_PATH_KEY = 'detail_content'

MAJOR = 2
MINOR = 5
DAG_NAME = dag_name(category="etl", name="eu_timeline", version_major=MAJOR,
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
