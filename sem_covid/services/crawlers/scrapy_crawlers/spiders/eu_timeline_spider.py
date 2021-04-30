from json import dumps

import scrapy
import pandas as pd
from sem_covid import config
from scrapy_splash import SplashRequest

from ..items import EuActionTimelineItem


class EUTimelineSpider(scrapy.Spider):
    name = 'eu-timeline'
    url = 'https://ec.europa.eu/info/live-work-travel-eu/coronavirus-response/timeline-eu-action_en'
    presscorner_base_url = 'https://ec.europa.eu/commission/presscorner/detail'

    def __init__(self, filename, *args, storage_adapter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage_adapter = storage_adapter
        self.filename = filename
        self.data = list()
        self.logger.debug(self.storage_adapter)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse_main_page)

    def closed(self, reason):
        self.logger.info(self.data)
        uploaded_bytes = self.storage_adapter.put_object(self.filename, dumps(self.data).encode('utf-8'))
        self.logger.info(f'Uploaded {uploaded_bytes}')

    def parse_main_page(self, response):
        timeline_data = response.xpath(
            '//div[@class="field field-name-field-core-timelines field--field-core-timelines"]/div["field__items"]/*[ @class !="clearfix"]')
        month_name = ''
        for index, block in enumerate(timeline_data):
            if not index % 2:
                self.logger.info(f'Processing data for {month_name}.')
                month_name = block.xpath('*/h2/text()').get()

            else:
                month_timeline = block.xpath('*//li[@class="timeline__list__item"]')
                for month in month_timeline:
                    date = month.xpath('*[@class="timeline__list__item__title"]/text()').get()
                    title = month.xpath('*//h4//text()').get()
                    body = ' '.join(month.xpath('*//p[string-length(text()) > 0]').extract())

                    presscorner_links = [link.attrib['href'] for link in month.xpath('*//p//a') if
                                         self.presscorner_base_url in link.attrib.get('href', '')]
                    meta = dict()
                    meta['month_name'] = month_name
                    meta['date'] = date
                    meta['title'] = title
                    meta['abstract'] = body
                    meta['presscorner_links'] = presscorner_links
                    meta['all_links'] = [link.attrib['href'] for link in month.xpath('*//p//a')]
                    if presscorner_links:
                        for presscorner_link in presscorner_links:
                            self.logger.info(f'Processing data for link: {presscorner_link}.')
                            yield SplashRequest(url=presscorner_link, callback=self.parse_presscorner_page,
                                                args={'wait': 5},
                                                dont_filter=True,
                                                meta=meta)
                    else:
                        self.data.append(meta)

    def _get_topics_by_spoke_person_name(self, spoke_person_name: str) -> list:
        df_spoke_person = pd.read_json(config.CRAWLER_EU_TIMELINE_SPOKEPERSONS)
        if spoke_person_name in df_spoke_person['Name'].values:
            return df_spoke_person[df_spoke_person['Name'] == spoke_person_name]['Topics'][0]
        return []

    def parse_presscorner_page(self, response):
        meta = response.meta
        item = EuActionTimelineItem(
            month_name=meta['month_name'],
            date=meta['date'],
            title=meta['title'],
            abstract=meta['abstract'],
            presscorner_links=meta['presscorner_links'],
            all_links=meta['all_links'],
            detail_link=response.url
        )

        metadata = response.xpath('//span[contains(@class, "ecl-meta__item")]//text()')
        item['detail_metadata'] = {
            'type': metadata[0].get(),
            'date': metadata[1].get(),
            'location': metadata[2].get()
        }
        item['detail_content'] = response.xpath('//div[@class="ecl-paragraph"]').get()
        item['detail_title'] = response.xpath(
            '//h1[@class="ecl-heading ecl-heading--h1 ecl-u-color-white"]//text()').extract()

        detail_links_start = response.xpath('//p[contains(., "For More Information")]')
        if detail_links_start:
            item['for_more_information_links'] = [link.attrib.get('href') for link in
                                                  detail_links_start[0].xpath('following-sibling::p/a')]
        item['detail_pdf_link'] = response.xpath(
            '//a[contains(@class, "ecl-button--file ecl-file__download")]').attrib.get(
            'href')

        item['press_contacts'] = list()
        item['topics'] = list()
        press_contacts = response.xpath('//ul[@class="ecl-listing"]/li')
        for press_contact in press_contacts:
            document_spoke_person_name = press_contact.xpath('*//div/h4/text()').get()
            item['topics'] += self.get_topics_by_spoke_person_name(document_spoke_person_name)
            item['press_contacts'].append({
                'name': document_spoke_person_name,
                'phone': press_contact.xpath('*//div/div[@class="ecl-field__body"]/text()').get(),
                'email': press_contact.xpath('*//div/div[@class="ecl-field__body"]/a/text()').get()
            })
        item['topics'] = list(set(item['topics']))
        self.logger.info(f'Push data from: {response.url}.')
        self.data.append(dict(item))
