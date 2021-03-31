from pathlib import Path

import re
from datetime import datetime, date
from typing import Optional

import scrapy
from scrapy_splash import SplashRequest


class IrishGovCrawler(scrapy.Spider):
    name = 'irish-gov'
    url = 'https://www.gov.ie/en/publications/?q=&sort_by=published_date&page=1800'
    earliest_date = date(2004, 8, 29)
    date_format = '%d %B %Y'
    date_format_re = r'\d{1,2} \w+ \d{4}'

    def __init__(self, *args, storage_adapter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_searches = ['covid']
        self.storage_adapter = storage_adapter
        self.filename = 'filename'
        self.data = list()

    def start_requests(self):
        for text_search in self.text_searches:
            yield SplashRequest(url=self.url, callback=self.parse_list_page, args={'wait': 5})

    #
    # def closed(self, reason):
    #     self.logger.info(self.data)
    #     uploaded_bytes = self.storage_adapter.put_object(self.filename, dumps(self.data).encode('utf-8'))
    #     self.logger.info(f'Uploaded {uploaded_bytes}')

    def parse_list_page(self, response):
        page_links = response.css('ul[reboot-site-list]').css('li')
        for page_link in page_links:
            date_match = self._extract_date(page_link.css('p::text').get()) or ''
            if self._is_in_range(date_match):
                yield SplashRequest(url='https://www.gov.ie/' + page_link.css('a::attr(href)').get(),
                                    callback=self.parse_detail_page,
                                    args={'wait': 5})

    def parse_detail_page(self, response):
        file_path = Path.cwd() / f'{response.css("h1::text").get()}.html'
        file_path.write_bytes(response.body)

    def _extract_date(self, text: str) -> Optional[str]:
        date_match = re.search(self.date_format_re, text)
        if date_match:
            return date_match.group()

    def _is_in_range(self, date_string: str) -> bool:
        return datetime.strptime(date_string, self.date_format).date() >= self.earliest_date
