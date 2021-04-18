import scrapy
from ..items import AdaptItem


class AdaptSpider(scrapy.Spider):
    name = "adapt"
    download_delay = 5

    def start_requests(self):
        urls = [
            'https://www.adapt.io/directory/industry/telecommunications/A-1',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        company_source = response.css('.DirectoryTopInfo_linkItemWrapper__2MyQQ a')
        for source in company_source:
            source_url = source.css('::attr(href)').extract_first()
            yield scrapy.Request(source_url, callback=self.company_link)

    def company_link(self, response):
        company_list = []
        company_source = response.css('.DirectoryList_linkItemWrapper__3F2UE a')
        for source in company_source:
            company = AdaptItem()

            company_name = source.css('::text').extract_first()
            source_url = source.css('::attr(href)').extract_first()
            company['company_name'] = company_name
            company['source_url'] = source_url
            company['tag'] = response.url
            company_info = {
                "company_name": company_name,
                "source_url": source_url
            }
            company_list.append(company_info)
            yield company
        next_page = response.css('.undefined ::attr(href)').extract_first()
        if next_page:
            # yield scrapy.Request(url=next_page, callback=self.parse)
            yield response.follow(next_page, callback=self.company_link)
