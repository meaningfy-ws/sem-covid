import re
from datetime import datetime, date
from json import dumps
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

import scrapy
from scrapy.selector import SelectorList
from scrapy_splash import SplashRequest

from sem_covid import config
from sem_covid.services.store_registry import store_registry
from . import COVID_EUROVOC_SEARCH_TERMS
from ..items import IrishGovItem


class IrishGovCrawler(scrapy.Spider):
    name = 'ireland-timeline'
    base_url = 'https://www.gov.ie'
    url = 'https://www.gov.ie/en/publications/?q={term}'
    earliest_date = date(2020, 2, 1)
    date_format = '%d %B %Y'
    date_format_re = r'\d{1,2} \w+ \d{4}'

    def __init__(self, *args, filename: str = config.IRELAND_TIMELINE_JSON,
                 text_searches: List[str] = COVID_EUROVOC_SEARCH_TERMS,
                 storage_adapter=store_registry.minio_object_store(config.IRELAND_TIMELINE_BUCKET_NAME),
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.text_searches = text_searches
        self.storage_adapter = storage_adapter
        self.filename = filename
        self.data = list()

    def start_requests(self):
        for text_search in self.text_searches:
            yield SplashRequest(url=self.url.format(term=text_search), callback=self.parse,
                                meta={'keyword': text_search})

    def closed(self, reason):
        if self.storage_adapter:
            self.logger.info(self.data)
            uploaded_bytes = self.storage_adapter.put_object(self.filename, dumps(self.data).encode('utf-8'))
            self.logger.info(f'Uploaded {uploaded_bytes}')
        else:
            file = Path.cwd() / self.filename
            file.write_text(dumps(self.data))

    def parse(self, response):
        page_links = response.css('ul[reboot-site-list]').css('li')
        next_page_link = self._build_link(response.css('a[aria-label="next"]::attr(href)').get())

        for page_link in page_links:
            date_match = self._extract_date(page_link.css('p::text').get())
            if self._is_in_range(date_match):
                yield SplashRequest(url=self._build_link(page_link.css('a::attr(href)').get()),
                                    callback=self.parse_detail_page, meta=response.meta)
        if next_page_link:
            yield SplashRequest(url=next_page_link, callback=self.parse, meta=response.meta)

    def parse_detail_page(self, response):
        item = IrishGovItem()
        item['keyword'] = response.meta.get('keyword')
        item['page_type'] = self._remove_whitespace(response.css('div[reboot-header]').css('span::text').get())
        item['page_link'] = response.url
        item['department_data'] = {
            'link': self._build_link(response.css('div[reboot-header]').css('p').css('a::attr(href)').get()),
            'text': response.css('div[reboot-header]').css('p').css('a::text').get()
        }
        item['published_date'] = response.css('div[reboot-header]').css('p').css('time::text')[0].get()
        item['updated_date'] = response.css('div[reboot-header]').css('p').css('time::text')[1].get()
        item['title'] = response.css("h1::text").get()
        item['content'] = response.css('div[reboot-content]').get()
        item['content_links'] = self._extract_links(response.css('div[reboot-content]').css('a'))
        item['campaigns_links'] = self._extract_links(
            response.xpath('//h3[contains(., "Campaigns")]/following-sibling::ul[1]/li/a'))
        item['part_of_links'] = self._extract_links(
            response.xpath('//h3[contains(., "Part of")]/following-sibling::ul[1]/li/a'))
        item['part_of_links'] = self._extract_links(
            response.xpath('//h3[contains(., "Policies")]/following-sibling::ul[1]/li/a'))

        item['documents'] = self._extract_document_metadata(response.css('div[reboot-markdown-document]'))

        self.data.append(dict(item))

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

    def _extract_document_metadata(self, document_list_nodes: SelectorList) -> List[dict]:
        return [{
            'title': document.css('p[reboot-markdown-document-title]::text').get(),
            'summary': document.css('p[reboot-markdown-document-summary]::text').get(),
            'link': self._build_link(document.css('a[reboot-markdown-document-link]::attr(href)').get())
        } for document in document_list_nodes]

    def _build_link(self, extracted_link: str) -> str:
        if extracted_link:
            return extracted_link if urlparse(extracted_link).netloc else self.base_url + extracted_link

    @staticmethod
    def _remove_whitespace(text: str) -> str:
        if text:
            return text.replace('\n', '').strip()
        else:
            return ''

