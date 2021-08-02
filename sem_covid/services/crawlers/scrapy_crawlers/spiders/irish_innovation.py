from datetime import datetime, date
import re
from typing import Optional, List
from urllib.parse import urlparse

import scrapy
from parsel import SelectorList
from scrapy_splash import SplashRequest
# from ..items import IrishGovItem


class IrishInnovationSpider(scrapy.Spider):
    name = 'irish_innovation'
    base_url = 'https://www.gov.ie'
    start_urls = ['https://gov.ie/en/publications/?q=innovation']
    earliest_date = date(2020, 2, 1)
    date_format = '%d %B %Y'
    date_format_re = r'\d{1,2} \w+ \d{4}'

    def parse(self, response):
        links = response.css('ul[reboot-site-list]').css('li')
        next_page_link = self._build_link(response.css('a[aria-label="next"]::attr(href)').get())

        for link in links:
            date_match = self._extract_date(link.css('p::text').get())
            if self._is_in_range(date_match):
                yield SplashRequest(url=self._build_link(link.css('a::attr(href)').get()),
                                    callback=self.parse, meta=response.meta)

        if next_page_link:
            yield response.follow(url=next_page_link, callback=self.parse)

    # def parse_detail_page(self, response):
    #     item = IrishGovItem()
    #     item['title'] = response.css("h1::text").get()
    #     item['content'] = response.css('div[reboot-content]').get()
    #     item['content_links'] = self._extract_links(response.css('div[reboot-content]').css('a'))

    def _build_link(self, extracted_link: str) -> str:
        if extracted_link:
            return extracted_link if urlparse(extracted_link).netloc else self.base_url + extracted_link

    def _extract_date(self, text: str) -> Optional[str]:
        if text:
            date_match = re.search(self.date_format_re, str(text))
            try:
                if date_match:
                    return date_match.group()
            except ValueError:
                self.logger.error(f'data {date_match} does not match format {self.date_format}')

    def _is_in_range(self, date_string: str) -> bool:
        if not date_string:
            return False

        return datetime.strptime(date_string, self.date_format).date() >= self.earliest_date

    def _extract_links(self, link_list_nodes: SelectorList) -> List[dict]:
        return [{
            'link': self._build_link(link.css('::attr(href)').get()),
            'text': self._remove_whitespace(link.css('::text').get())
        } for link in link_list_nodes if link.css('::attr(href)')]

    @staticmethod
    def _remove_whitespace(text: str) -> str:
        if text:
            return text.replace('\n', '').strip()
        else:
            return ''
