
import hashlib
import json

import sem_covid.services.crawlers.scrapy_crawlers.settings as crawler_config
from sem_covid.entrypoints.etl_dags.crawl_pipeline import extract_settings_from_module
from sem_covid.entrypoints.etl_dags.crawl_pipeline import CrawlDagPipeline
from tests.unit.test_crawler.test_crawler.spiders.test_spider import TestCrawler
from tests.fake_store_registry import FakeStoreRegistry


fake_store_registry = FakeStoreRegistry()
fake_filename = 'fake_file.json'
fake_bucket_name = 'fake-bucket-name'
fake_es_index_name = 'fake_index_name'
fake_content_path_key = 'title'
TIKA_FILE_PREFIX = 'tika/'
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


def test_crawl_dag_pipeline(get_crawl_result):
    crawler_pipeline = CrawlDagPipeline(
                            store_registry=fake_store_registry,
                            file_name=fake_filename,
                            bucket_name=fake_bucket_name,
                            elasticsearch_index_name=fake_es_index_name,
                            content_path_key=fake_content_path_key,
                            scrapy_crawler=fake_crawler
    )

    crawler_pipeline.extract()
    minio = fake_store_registry.minio_object_store(fake_bucket_name)
    minio.empty_bucket(object_name_prefix=None)
    minio.put_object(fake_filename, json.dumps(get_crawl_result))
    tika_hashed_file = hashlib.sha256(fake_filename.encode('utf-8')).hexdigest()
    assert '9716b040dd1a7256757a99412a419c5238551c3bf49777c092c40c4e59daa425' == tika_hashed_file
    minio.put_object(TIKA_FILE_PREFIX + tika_hashed_file, json.dumps(get_crawl_result))

    crawler_pipeline.transform_content()
    assert 'title' == crawler_pipeline.content_path_key

    crawler_pipeline.transform_structure()
    crawler_pipeline.load()
