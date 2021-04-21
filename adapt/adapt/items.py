# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CompanyIndexItem(scrapy.Item):
    company_name = scrapy.Field()
    source_url = scrapy.Field()
    tag = scrapy.Field()


class CompanyProfileItem(scrapy.Item):
    company_name = scrapy.Field()
    company_location = scrapy.Field()
    company_website = scrapy.Field()
    company_webdomain = scrapy.Field()
    company_industry = scrapy.Field()
    company_employee_size = scrapy.Field()
    company_revenue = scrapy.Field()
    contact_details = scrapy.Field()
