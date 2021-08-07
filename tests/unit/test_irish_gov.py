import json
import numpy as np

from tests.unit.conftest import (fake_response_from_file, create_html_response, call_mock_article_page,
                                 call_mock_publication, call_mock_article_page_json, call_mock_publication_json,
                                 call_mock_covid_search_term_page_json)


def test_irish_gov_crawler_parsing_publication_from_the_page(call_irish_crawler):
    result = call_irish_crawler.parse_detail_page(fake_response_from_file(call_mock_publication()))
    result = call_irish_crawler.data
    call_mock_publication_json().write_text(data=json.dumps(result))


def test_irish_gov_crawler_innovation_keyword(call_irish_crawler):
    parsed_pages = call_irish_crawler.parse(fake_response_from_file(call_mock_article_page()))
    call_irish_crawler.parse_detail_page(create_html_response(list(parsed_pages)[0].url))
    output = call_irish_crawler.data
    call_mock_article_page_json().write_text(data=json.dumps(output))


def test_irish_gov_crawler_for_key_word_innovation(call_irish_crawler):
    page_numbers = np.arange(1, 9, 1)
    for page_number in page_numbers:
        url = 'https://www.gov.ie/en/publications/?q=innovation&page='
        numbered_page = url + str(page_number)
        parsed_pages = call_irish_crawler.parse(create_html_response(numbered_page))
        call_irish_crawler.parse_detail_page(create_html_response(list(parsed_pages)[0].url))
    output = call_irish_crawler.data
    call_mock_covid_search_term_page_json().write_text(data=json.dumps(output))
