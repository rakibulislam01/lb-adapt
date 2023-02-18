# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2


class AdaptPipeline(object):
    """
    Company index pipeline
    """

    def __init__(self):
        # Database name, connection to this machine MySQL, port number, MySQL user name, MySQL user password
        db = 'lbadapt'
        host = 'localhost'
        port = 3306
        user = 'lbadapt'
        passwd = 'lbadapt'

        # Open database connection
        self.db_conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=passwd)
        # Create cursor object
        self.db_cur = self.db_conn.cursor()

    def process_item(self, item, spider):
        """
        :param item:
        :param spider:
        :return:
        """
        # SQL Statement
        insert_sql = """
                insert into company_index(company_name,source_url,tag) VALUES(%s,%s,%s)
                """
        # Execute the SQL statement and submit it to the database for execution
        self.db_cur.execute(insert_sql, (item['company_name'], item['source_url'], item['tag']))
        self.db_conn.commit()
        print("Insert finished")
        # return item for the next Pipeline class
        return item


class CompanyProfilePipeline(object):
    """
    Company profile pipeline
    """

    def __init__(self):
        # Database name, connection to this machine MySQL, port number, MySQL user name, MySQL user password
        db = 'lbadapt'
        host = 'localhost'
        port = 5432
        user = 'lbadapt'
        passwd = 'lbadapt'

        # Open database connection
        self.db_conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=passwd)
        # Create cursor object
        self.db_cur = self.db_conn.cursor()

    def process_item(self, item, spider):
        """
        :param item:
        :param spider:
        :return:
        """
        # SQL Statement
        insert_sql_company_profile = """
                insert into company_profile(company_name,company_location,company_website, company_webdomain, company_industry, company_employee_size, company_revenue) VALUES(%s,%s,%s,%s,%s,%s,%s)
                """
        # Execute the SQL statement and submit it to the database for execution
        self.db_cur.execute(insert_sql_company_profile, (item['company_name'], item['company_location'], item['company_website'], item['company_webdomain'], item['company_industry'], item['company_employee_size'], item['company_revenue']))
        self.db_conn.commit()
        print("Insert finished")

        for detail in item['contact_details']:
            # SQL Statement
            insert_sql_contact_details = """
                    insert into contact_details(contact_name,contact_jobtitle,contact_email_domain, contact_department, company_id) VALUES(%s,%s,%s,%s,(select id from company_profile where company_name=%s))
                    """
            # Execute the SQL statement and submit it to the database for execution
            self.db_cur.execute(insert_sql_contact_details, (detail['contact_name'], detail['contact_jobtitle'], detail['contact_email_domain'], detail['contact_department'], item['company_name']))
            self.db_conn.commit()
            print("Insert finished")
        # return item for the next Pipeline class
        return item
