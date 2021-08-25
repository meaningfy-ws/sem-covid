
import scrapy

from ..items import TestCrawlerItem
from tests.unit.conftest import fake_response_from_file, call_mock_publication


class TestCrawler(scrapy.Spider):
    name = "test-crawler"
    fake_response = fake_response_from_file(call_mock_publication()).url

    def start_requests(self):
        yield scrapy.Request(url=self.fake_response, callback=self.parse)

    def parse(self, response):
        items = TestCrawlerItem()
        title = response.css('div[reboot-header]').css('h1::text').get()
        items['title'] = title

        yield items

