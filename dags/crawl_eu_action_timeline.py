import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from scrapy.crawler import CrawlerProcess
import eu_action_timeline.settings as crawler_config
from eu_action_timeline.spiders.eu_timeline_spider import EUTimelineSpider

logger = logging.getLogger('lam-fetcher')
VERSION = '0.0.3'


def extract_settings_from_module(module):
    settings = dict()
    for config in dir(crawler_config):
        if config.isupper():
            settings[config] = getattr(module, config)

    return settings


def start_crawler():
    logger.info('start crawler')
    process = CrawlerProcess(settings=extract_settings_from_module(crawler_config))

    process.crawl(EUTimelineSpider)
    process.start()


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 16),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500)
}

dag = DAG(
    'Crawl_EU_Action_Timeline_' + VERSION,
    default_args=default_args,
    schedule_interval="@once",
    max_active_runs=1,
    concurrency=1
)

start_crawler = PythonOperator(
    task_id=f'Crawl',
    python_callable=start_crawler, retries=1, dag=dag)

