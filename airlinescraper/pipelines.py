# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ConvertPricePipeline(object):
    """
    Performs the forex conversion for certain data points which are in foreign currency.
    The forex rates are fixed by the dictionary below.
    Returns the currency in SGD.
    """
    currency_conversion = {'SGD':1,'USD':0.73,'VND':17065,'MYR':3,'PHP':38.7,'THB':24.3,'IDR':10552}
    def process_item(self, item, spider):
        if item['price'] and item['currency']:
            if item['currency'] in self.currency_conversion:
                item['price_converted'] = float(item['price']) / self.currency_conversion[item['currency']]
            else:
                raise ValueError('Unknown currency')
        else:
            item['price_converted'] = ''
        return item
