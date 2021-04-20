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
    Company_name = scrapy.Field()
    Company_location = scrapy.Field()
    Company_website = scrapy.Field()
    Company_webdomain = scrapy.Field()
    Company_industry = scrapy.Field()
    Company_employee_size = scrapy.Field()
    Company_revenue = scrapy.Field()
    contact_details = scrapy.Field()
