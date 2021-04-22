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


class IrishGovItem(scrapy.Item):
    # this field might be irrelevant
    keyword = scrapy.Field()
    page_type = scrapy.Field()
    page_link = scrapy.Field()
    department_data = scrapy.Field()
    published_date = scrapy.Field()
    updated_date = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    content_links = scrapy.Field()
    campaigns_links = scrapy.Field()
    part_of_links = scrapy.Field()
    policies_links = scrapy.Field()
    documents = scrapy.Field()
