
import sem_covid.services.crawlers.scrapy_crawlers.settings as crawler_config
from sem_covid.entrypoints.etl_dags.crawl_pipeline import extract_settings_from_module


def test_extract_settings_from_module():
    setting_extraction = extract_settings_from_module(crawler_config)

    assert dict == type(setting_extraction)
    keys = [key for key in setting_extraction]
    assert " ".join(keys).isupper() is True
    setting_keys = ['BOT_NAME', 'DEFAULT_REQUEST_HEADERS', 'DOWNLOADER_MIDDLEWARES', 'DOWNLOAD_DELAY',
                    'DUPEFILTER_CLASS', 'HTTPCACHE_STORAGE', 'NEWSPIDER_MODULE', 'ROBOTSTXT_OBEY',
                    'SPIDER_MIDDLEWARES', 'SPIDER_MODULES', 'SPLASH_URL']
    assert setting_keys == keys
