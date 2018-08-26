# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PriceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    date = scrapy.Field()
    origin = scrapy.Field()
    destination = scrapy.Field()
    provider = scrapy.Field()
    price_converted = scrapy.Field()
