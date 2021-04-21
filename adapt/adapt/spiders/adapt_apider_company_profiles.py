import scrapy
from ..items import CompanyProfileItem
import re
from urllib.parse import urlparse


class AdaptSpider(scrapy.Spider):
    name = "company_profile"
    download_delay = 1

    custom_settings = {
        'ITEM_PIPELINES': {
            'adapt.pipelines.CompanyProfilePipeline': 300,
        }
    }

    def start_requests(self):
        urls = [
            'https://www.adapt.io/directory/industry/telecommunications/A-1',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # def parse_(self, response):
    #     # collect all company link alphabetically from [A-Z]
    #     company_source = response.css('.DirectoryTopInfo_linkItemWrapper__2MyQQ a')
    #     for source in company_source:
    #         source_url = source.css('::attr(href)').extract_first()
    #         yield scrapy.Request(source_url, callback=self.company_link)

    def parse(self, response):
        company_source = response.css('.DirectoryList_linkItemWrapper__3F2UE a')
        for source in company_source:
            source_url = source.css('::attr(href)').extract_first()
            yield response.follow(source_url, callback=self.company_profile)
        # Collect all company link from each alphabet
        # next_page = response.css('.undefined ::attr(href)').extract_first()
        # if next_page:
        #     yield response.follow(next_page, callback=self.company_link)

    def company_profile(self, response):
        company_profile = CompanyProfileItem()
        company_name = response.css('h1 ::text').extract_first()
        company_location = response.css(
            '.CompanyTopInfo_addressIcon__hQdTR+ .CompanyTopInfo_contentWrapper__2Jkic .CompanyTopInfo_infoValue__27_Yo ::text').extract()
        company_website = response.css('.CompanyTopInfo_websiteUrl__13kpn ::text').extract_first()
        company_webdomain = urlparse(company_website).netloc
        company_webdomain = company_webdomain.replace('www.', '') if company_webdomain else ''
        company_industry = response.css(
            '.CompanyTopInfo_industryIcon__1hhPC+ .CompanyTopInfo_contentWrapper__2Jkic .CompanyTopInfo_infoValue__27_Yo ::text').extract_first()
        company_revenue = response.css(
            '.CompanyTopInfo_revenueIcon__1acbf+ .CompanyTopInfo_contentWrapper__2Jkic .CompanyTopInfo_infoValue__27_Yo ::text').extract_first()
        company_employee_size = response.css(
            '.CompanyTopInfo_headCountIcon__1-4b-+ .CompanyTopInfo_contentWrapper__2Jkic .CompanyTopInfo_infoValue__27_Yo ::text').extract_first()
        company_profile['company_name'] = company_name
        company_profile['company_location'] = ''.join(company_location)
        company_profile['company_website'] = company_website
        company_profile['company_webdomain'] = company_webdomain
        company_profile['company_industry'] = company_industry
        company_profile['company_employee_size'] = company_employee_size
        company_profile['company_revenue'] = company_revenue

        contact_list_link = response.xpath('//*[@id="__next"]/div/main/div[2]/div[2]/div[1]//a/@href').extract()

        con = 'https://www.adapt.io/company/abr-telecom'
        request = scrapy.Request(con, callback=self.contact_link)
        request.meta['company_profile'] = company_profile
        request.meta['contact_list_link'] = contact_list_link
        request.meta['contact_detail'] = []
        request.meta['contact_detail_len'] = len(contact_list_link)
        yield request

    def contact_link(self, response):
        company_profile = response.meta['company_profile']
        contact_list_link = response.meta['contact_list_link']
        contact_detail = response.meta['contact_detail']
        contact_detail_len = response.meta['contact_detail_len']
        if contact_detail is None:
            contact_detail = []

        for link in contact_list_link:
            request = scrapy.Request(link, callback=self.contact_details)
            request.meta['company_profile'] = company_profile
            request.meta['contact_list_link'] = contact_list_link
            request.meta['contact_detail'] = contact_detail
            request.meta['contact_detail_len'] = contact_detail_len
            yield request

    def contact_details(self, response):
        company_profile = response.meta['company_profile']
        contact_list_link = response.meta['contact_list_link']
        contact_detail = response.meta['contact_detail']
        contact_detail_len = response.meta['contact_detail_len']

        if contact_detail is None:
            contact_detail = []

        contact_name = response.xpath(
            '//*[@id="__next"]/div/main/div[2]/div[1]/div/div[1]/div[1]/div[1]/h1/text()').extract()
        contact_jobtitle = response.xpath(
            '//*[@id="__next"]/div/main/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/text()').extract()
        contact_email_domain = response.css(
            '.ContactTopInfo_infoItemActionWrap__26Kcj .ContactTopInfo_infoValue__DNIWM ::text').extract_first()
        contact_department = response.css(
            '.ContactTopInfo_departmentIcon__1DBtX+ .ContactTopInfo_contentWrapper__3VEQ2 .ContactTopInfo_infoValue__DNIWM , .ContactTopInfo_jobTitle__1Psvw ::text').extract_first()
        contact_name = contact_name[0] if contact_name else ''
        contact_jobtitle = contact_jobtitle[0] if contact_jobtitle else ''
        try:
            contact_email_domain = re.search('@.*', contact_email_domain).group()
        except:
            contact_email_domain = response.css('.ContactTopInfo_emailBorderIcon__Ld4fh+ .ContactTopInfo_contentWrapper__3VEQ2 .ContactTopInfo_infoValue__DNIWM ::text').extract_first()
            contact_email_domain = re.search('@.*', contact_email_domain).group()
            contact_email_domain = contact_email_domain if contact_email_domain else ''

        contact_details = [{
            "contact_name": contact_name,
            "contact_jobtitle": contact_jobtitle,
            "contact_email_domain": contact_email_domain,
            "contact_department": contact_department
        }]
        contact_detail.extend(contact_details)

        con = 'https://www.adapt.io/company/abr-telecom'
        if response.url in contact_list_link: contact_list_link.remove(response.url)

        if contact_detail_len == len(contact_detail):
            company_profile['contact_details'] = contact_detail
            yield company_profile
        else:
            yield response.follow(con, callback=self.contact_link,
                                  meta={'company_profile': company_profile,
                                        'contact_list_link': contact_list_link,
                                        'contact_detail': contact_detail,
                                        'contact_detail_len': contact_detail_len})
