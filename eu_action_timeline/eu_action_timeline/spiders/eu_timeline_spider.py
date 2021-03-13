import scrapy
from scrapy_splash import SplashRequest

from ..items import EuActionTimelineItem


class EUTimelineSpider(scrapy.Spider):
    name = 'eu-timeline'
    url = 'https://ec.europa.eu/info/live-work-travel-eu/coronavirus-response/timeline-eu-action_en'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse_main_page, headers=self.headers)

    def parse_main_page(self, response):
        data = {}
        timeline_data = response.xpath(
            '//div[@class="field field-name-field-core-timelines field--field-core-timelines"]/div["field__items"]/*[ @class !="clearfix"]')
        month_name = ''
        for index, block in enumerate(timeline_data):
            if not index % 2:
                self.logger.info(f'Processing data for {month_name}.')

                month_name = block.xpath('*//h2/text()').get()

            else:
                month_timeline = block.xpath('*//li')
                for month in month_timeline:
                    date = month.xpath('*[@class="timeline__list__item__title"]/text()').get()
                    title = month.xpath('*//h4/text() | *//h4/strong/text()').get()
                    body = ' '.join(month.xpath('*//p[string-length(text()) > 0]').extract())

                    presscorner_base_url = 'https://ec.europa.eu/commission/presscorner/detail'
                    presscorner_links = [link.attrib['href'] for link in month.xpath('*//p//a') if
                                         presscorner_base_url in link.attrib['href']]

                    for presscorner_link in presscorner_links:
                        self.logger.info(f'Processing data for this link: {presscorner_link}.')
                        meta = {}
                        meta['month_name'] = month_name
                        meta['date'] = date
                        meta['title'] = title
                        meta['excerpt'] = body
                        meta['presscorner_links'] = presscorner_links
                        meta['all_links'] = [link.attrib['href'] for link in month.xpath('*//p//a')]
                        yield SplashRequest(url=presscorner_link, callback=self.parse_presscorner_page,
                                            args={'wait': 5},
                                            meta=meta)

    def parse_presscorner_page(self, response):
        meta = response.meta
        item = EuActionTimelineItem()
        item['month_name'] = meta['month_name']
        item['date'] = meta['date']
        item['title'] = meta['title']
        item['excerpt'] = meta['excerpt']
        item['presscorner_links'] = meta['presscorner_links']
        item['all_links'] = meta['all_links']
        item['article_content'] = response.xpath('//div[@class="ecl-paragraph"]').get()
        item['detail_title'] = response.xpath(
            '//h1[@class="ecl-heading ecl-heading--h1 ecl-u-color-white"]//text()').extract()

        detail_links_start = response.xpath('//p[contains(., "For More Information")]')
        if detail_links_start:
            item['for_more_information_links'] = [link.attrib['href'] for link in
                                                  detail_links_start[0].xpath('following-sibling::p/a')]
        item['detail_pdf_link'] = response.xpath('//a[contains(@class, "ecl-button--file ecl-file__download")]').attrib[
            'href']

        item['press_contacts'] = list()
        press_contacts = response.xpath('//ul[@class="ecl-listing"]/li')
        for press_contact in press_contacts:
            item['press_contacts'].append({
                'name': press_contact.xpath('*//div/h4/text()').get(),
                'phone': press_contact.xpath('*//div/div[@class="ecl-field__body"]/text()').get(),
                'email': press_contact.xpath('*//div/div[@class="ecl-field__body"]/a/text()').get()
            })

        yield item
