
import sem_covid.services.crawlers.scrapy_crawlers.settings as crawler_config
from sem_covid.entrypoints.etl_dags.crawl_pipeline import extract_settings_from_module
from tests.unit.dags.conftest import get_crawl_result
from sem_covid.entrypoints.etl_dags.crawl_pipeline import CrawlDagPipeline
from tests.unit.test_crawler.test_crawler.spiders.test_spider import TestCrawler
from tests.unit.test_store.fake_store_registry import FakeStoreRegistry


fake_store_registry = FakeStoreRegistry()
fake_filename = 'fake_file.json'
fake_bucket_name = 'fake-bucket-name'
fake_es_index_name = 'fake_index_name'
fake_content_path_key = 'fake_content'
fake_crawler = TestCrawler


def test_extract_settings_from_module():
    setting_extraction = extract_settings_from_module(crawler_config)

    assert dict == type(setting_extraction)
    keys = [key for key in setting_extraction]
    assert " ".join(keys).isupper() is True
    setting_keys = ['BOT_NAME', 'DEFAULT_REQUEST_HEADERS', 'DOWNLOADER_MIDDLEWARES', 'DOWNLOAD_DELAY',
                    'DUPEFILTER_CLASS', 'HTTPCACHE_STORAGE', 'NEWSPIDER_MODULE', 'ROBOTSTXT_OBEY',
                    'SPIDER_MIDDLEWARES', 'SPIDER_MODULES', 'SPLASH_URL']
    assert setting_keys == keys


def test_crawl_dag_pipeline():
    crawler_pipeline = CrawlDagPipeline(
                            store_registry=fake_store_registry,
                            file_name=fake_filename,
                            bucket_name=fake_bucket_name,
                            elasticsearch_index_name=fake_es_index_name,
                            content_path_key=fake_content_path_key,
                            scrapy_crawler=fake_crawler
    )

    crawler_pipeline.extract()

    minio_bucket = fake_store_registry.minio_object_store(fake_bucket_name)
    minio_bucket.put_object(fake_filename, get_crawl_result())

    # crawler_pipeline.transform_structure()

    crawler_pipeline.load()
