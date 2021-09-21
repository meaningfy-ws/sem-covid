import json
from tests.unit.conftest import (call_eu_timeline_main_page, call_eu_timeline_main_page_json,
                                 fake_response_from_file, create_html_response,
                                 call_eu_timeline_presscorner_page, call_eu_timeline_presscorner_page_json)


def test_eu_timeline_crawler_parse_main_page(call_eu_timeline_crawler):
    result = call_eu_timeline_crawler.parse_main_page(fake_response_from_file(call_eu_timeline_main_page()))
    call_eu_timeline_main_page_json().write_text(data=json.dumps(result))
    file = open('../test_data/crawlers/sample_eu_timeline/saved_data/eu_timeline_main_page.json')
    content = json.load(file)

    assert ['month_name', 'date', 'title', 'abstract', 'presscorner_links', 'all_links'] == list(content[0].keys())
    assert 'May 2021' == content[0]['month_name']
    assert '21 May' == content[0]['date']
    assert 'Global leaders adopt agenda to overcome COVID-19 crisis and avoid future pandemics' == content[0]['title']


def test_eu_timeline_crawler_parse_presscorner_page(call_eu_timeline_crawler):
    """To be resolved..."""
    # result = call_eu_timeline_crawler.parse_main_page(fake_response_from_file(call_eu_timeline_main_page()))
    # output = call_eu_timeline_crawler.parse_presscorner_page(create_html_response(list(result)[0].url))
    # print(output)
    # output = call_eu_timeline_crawler.data
    # print(output)
    # call_eu_timeline_presscorner_page_json().write_text(data=json.dumps(output))
    pass
