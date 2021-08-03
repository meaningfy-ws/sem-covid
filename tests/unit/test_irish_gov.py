import json
import os
import pathlib

import numpy as np
import requests
from scrapy.http import Request, HtmlResponse

from sem_covid.services.crawlers.scrapy_crawlers.spiders import COVID_EUROVOC_SEARCH_TERMS
from sem_covid.services.crawlers.scrapy_crawlers.spiders.irish_gov import IrishGovCrawler
from tests.unit.test_store.fake_store_registry import FakeStoreRegistry


MOCK_ARTICLE_PAGE = '/home/daycu/Programming/Meaningfy/sem-covid/tests/test_data/crawlers/sample_ireland_gov/innovation_keyword.html'
MOCK_PUBLICATION = '/home/daycu/Programming/Meaningfy/sem-covid/tests/test_data/crawlers/sample_ireland_gov/mock_publication.html'

mock_article_page_file = pathlib.Path(__file__).parent.parent.parent / 'tests' / 'test_data' / 'crawlers' / 'sample_ireland_gov' / 'saved_data' / 'mock_article_page.json'
mock_publication_file = pathlib.Path(__file__).parent.parent.parent / 'tests' / 'test_data' / 'crawlers' / 'sample_ireland_gov' / 'saved_data' / 'mock_publication.json'
mock_covid_search_term_page_file = pathlib.Path(__file__).parent.parent.parent / 'tests' / 'test_data' / 'crawlers' / 'sample_ireland_gov' / 'saved_data' / 'mock_covid_search_term_page.json'

FAKE_FILENAME = 'fake_filename.json'
FAKE_BUCKET_NAME = 'fake-bucket-name'
KEY_WORD = ['innovation']
store_registry = FakeStoreRegistry()


def fake_response_from_file(file_name: str, url: str = None) -> HtmlResponse:
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unit testing.
    """
    if not url:
        url = 'https://www.gov.ie/en/publications/?q=innovation'
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name
    file_content = open(file_path, 'r').read()

    return HtmlResponse(url=url, request=Request(url=url), body=file_content, encoding='utf-8')


def extract_html_content_text(url: str) -> str:
    """
        Using requests library, it extracts the html page content and transform it into string type
    """
    response = requests.get(url)
    return response.text


def create_html_response(url: str) -> HtmlResponse:
    """
        It gets the inserted url and transforms it into response type for scrapy request
    """
    return HtmlResponse(url=url, request=Request(url=url), body=extract_html_content_text(url), encoding='utf-8')


def test_irish_gov_crawler_parsing_publication_from_the_page():
    irish_gov_crawler = IrishGovCrawler(
        text_searches=COVID_EUROVOC_SEARCH_TERMS[0],
        filename=FAKE_FILENAME,
        storage_adapter=store_registry.minio_object_store(FAKE_BUCKET_NAME),
        )
    result = irish_gov_crawler.parse_detail_page(fake_response_from_file(MOCK_PUBLICATION))
    result = irish_gov_crawler.data
    mock_publication_file.write_text(data=json.dumps(result))


def test_irish_gov_crawler_innovation_keyword():
    irish_gov_crawler = IrishGovCrawler(
        text_searches=KEY_WORD,
        filename=FAKE_FILENAME,
        storage_adapter=store_registry.minio_object_store(FAKE_BUCKET_NAME),
        )
    parsed_pages = irish_gov_crawler.parse(fake_response_from_file(MOCK_ARTICLE_PAGE))
    for page in list(parsed_pages):
        irish_gov_crawler.parse_detail_page(create_html_response(page.url))

    output = irish_gov_crawler.data
    mock_article_page_file.write_text(data=json.dumps(output))


def test_irish_gov_crawler_for_key_word_innovation():
    irish_gov_crawler = IrishGovCrawler(
        text_searches=COVID_EUROVOC_SEARCH_TERMS,
        filename=FAKE_FILENAME,
        storage_adapter=store_registry.minio_object_store(FAKE_BUCKET_NAME))
    page_numbers = np.arange(1, 9, 1)
    for page_number in page_numbers:
        url = 'https://www.gov.ie/en/publications/?q=innovation&page='
        numbered_page = url + str(page_number)
        parsed_pages = irish_gov_crawler.parse(create_html_response(numbered_page))
        for each_page in list(parsed_pages):
            irish_gov_crawler.parse_detail_page(create_html_response(each_page.url))
    output = irish_gov_crawler.data
    print(output)
    mock_covid_search_term_page_file.write_text(data=json.dumps(output))
