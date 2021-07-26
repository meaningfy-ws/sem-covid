
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from sem_covid import config
from sem_covid.services.crawlers.scrapy_crawlers.spiders.eu_timeline_spider import EUTimelineSpider
from sem_covid.entrypoints.etl_dags.crawl_pipeline import CrawlDagPipeline

VERSION = '0.2.5'
DATASET_NAME = "eu_timeline"
DAG_TYPE = "etl"
DAG_NAME = DAG_TYPE + '_' + DATASET_NAME + '_' + VERSION
TIKA_FILE_PREFIX = 'tika/'
CONTENT_PATH_KEY = 'detail_content'

crawl_dag_pipeline = CrawlDagPipeline(config.EU_TIMELINE_JSON, config.EU_TIMELINE_BUCKET_NAME,
                                      config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME, CONTENT_PATH_KEY,
                                      EUTimelineSpider)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.today(),
    "email": ["dan.chiriac1453@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500)
}

dag = DAG(
    DAG_NAME,
    default_args=default_args,
    schedule_interval="@once",
    max_active_runs=1,
    concurrency=1
)

start_crawler = PythonOperator(
    task_id=f'Crawl',
    python_callable=crawl_dag_pipeline.start_crawler, retries=1, dag=dag)

extract_content_with_tika_task = PythonOperator(
    task_id=f'Tika',
    python_callable=crawl_dag_pipeline.extract_document_content_with_tika, retries=1, dag=dag)

upload_to_elastic_task = PythonOperator(
    task_id=f'Elasticsearch',
    python_callable=crawl_dag_pipeline.upload_processed_documents_to_elasticsearch, retries=1, dag=dag)

start_crawler >> extract_content_with_tika_task >> upload_to_elastic_task
