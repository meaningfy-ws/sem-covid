import scrapy
from ..items import EuActionTimelineItem
from scrapy_selenium import SeleniumRequest


class EUTimelineSpider(scrapy.Spider):
    name = 'eu-timeline'
    url = 'https://ec.europa.eu/info/live-work-travel-eu/coronavirus-response/timeline-eu-action_en'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }
    json_file = 'parsed.json'

    def process_request(self, request, spider):
        driver = webdriver.PhantomJS()
        driver.get(request.url)

        body = driver.page_source
        return SeleniumRequest(driver.current_url, body=body, encoding='utf-8', request=request)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse_main_page, headers=self.headers)

    def parse_main_page(self, response, **kwargs):
        data = {}
        timeline_data = response.xpath(
            '//div[@class="field field-name-field-core-timelines field--field-core-timelines"]/div["field__items"]/*[ @class !="clearfix"]')
        month_name = ''
        for index, block in enumerate(timeline_data[:2]):
            if not index % 2:
                self.logger.info(f'Processing data for {month_name}.')

                month_name = block.xpath('*//h2/text()').get()
                data[month_name] = list()

            else:
                month_timeline = block.xpath('*//li')
                for month in month_timeline:
                    date = month.xpath('*[@class="timeline__list__item__title"]/text()').get()
                    title = month.xpath('*//h4/text()').get()
                    body = ' '.join(month.xpath('*//p[string-length(text()) > 0]').extract())

                    base_url = 'https://ec.europa.eu/commission/presscorner/detail'
                    presscorner_links = [link.attrib['href'] for link in month.xpath('*//p//a') if
                                         base_url in link.attrib['href']]
                    data[month_name].append({
                        'date': str(date),
                        'title': str(title),
                        'excerpt': str(body),
                        'presscorner_links': presscorner_links,
                        'links': [link.attrib['href'] for link in month.xpath('*//p//a')]
                    })

                    for presscorner_link in presscorner_links:
                        self.logger.info(f'Processing data for this link: {presscorner_link}.')
                        meta = {}
                        meta['month_name'] = month_name
                        meta['date'] = date
                        meta['title'] = title
                        meta['excerpt'] = body
                        meta['presscorner_links'] = presscorner_links
                        meta['all_links'] = [link.attrib['href'] for link in month.xpath('*//p//a')]
                        yield SeleniumRequest(url=presscorner_link, callback=self.parse_presscorner_page,
                                              headers=self.headers,
                                              wait_time=25,
                                              meta=meta)

    def parse_presscorner_page(self, response, **kwargs):
        import time
        time.sleep(5)
        meta = response.meta
        item = EuActionTimelineItem()
        item['month_name'] = meta['month_name']
        item['date'] = meta['date']
        item['title'] = meta['title']
        item['excerpt'] = meta['excerpt']
        item['presscorner_links'] = meta['presscorner_links']
        item['all_links'] = meta['all_links']
        item['detail_body'] = response.body.decode()
        item['detail_title'] = response.xpath(
            '//h1[@class="ecl-heading ecl-heading--h1 ecl-u-color-white"]//text()').extract()
        yield item
