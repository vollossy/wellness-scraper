# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WellnessItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    item_url = scrapy.Field()
    name = scrapy.Field()
    business_name = scrapy.Field()
    street = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zip = scrapy.Field()
    primary_speciality = scrapy.Field()
    #staff must be array, because it can contain list of different people
    staff = scrapy.Field()
    years = scrapy.Field()
    #rating - number of stars
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    website = scrapy.Field()
