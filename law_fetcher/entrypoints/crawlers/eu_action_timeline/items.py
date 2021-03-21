# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EuActionTimelineItem(scrapy.Item):
    month_name = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    detail_title = scrapy.Field()
    detail_link = scrapy.Field()
    detail_content = scrapy.Field()
    detail_metadata = scrapy.Field()
    excerpt = scrapy.Field()
    presscorner_links = scrapy.Field()
    pdf_links = scrapy.Field()
    detail_for_more_information_links = scrapy.Field()
    press_contacts = scrapy.Field()
    all_links = scrapy.Field()
    for_more_information_links = scrapy.Field()
    detail_pdf_link = scrapy.Field()
