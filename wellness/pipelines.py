# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from spiders.doctors_spider import conn

class WellnessPipeline(object):
    def process_item(self, item, spider):
        # cur = conn.cursor()
        # cur.execute("INSERT INTO results(website, rating, reviews_count, item_url, name, zip, city, primary_speciality,"
        #             " years, state, street, business_name, staff) "
        #             "VALUES (%(website)s, %(rating)s, %(reviews_count)s, %(item_url)s, %(name)s, %(zip)s, %(city)s, "
        #             "%(primary_speciality)s, %(years)s, %(state)s, %(street)s, %(business_name)s, %(staff)s)")
        return item
