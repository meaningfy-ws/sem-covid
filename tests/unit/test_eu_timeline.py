import json
from tests.unit.conftest import call_eu_timeline_main_page, call_eu_timeline_main_page_json, fake_response_from_file


def test_eu_timeline_crawler_parse_main_page(call_eu_timeline_crawler):
    result = call_eu_timeline_crawler.parse_main_page(fake_response_from_file(call_eu_timeline_main_page()))
    result = call_eu_timeline_crawler.data
    call_eu_timeline_main_page_json().write_text(data=json.dumps(result))

