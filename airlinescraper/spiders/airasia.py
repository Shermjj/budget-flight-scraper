# -*- coding: utf-8 -*-
import scrapy
import json
from airlinescraper.items import PriceItem
# API site available to make a GET request
#https://k.apiairasia.com/availabledates/api/v1/pricecalendar/0/0/SGD/SIN/ATQ/2018-09-01/1

class AirasiaSpider(scrapy.Spider):
    name = 'airasia'
    start_urls = ['http://airasia.com/']
    # origin_destination_list = (["SIN"], ["PNH","REP"])
    origin_destination_list = (["SIN"], ["PNH","REP","KOS","DPS","BTJ","BDO","CGK","LOP","KNO","PDG","SRG",
                        "SOC","SUB","JOG","LPQ","VTE","BTU","BKI","KUL","KCH","LGK","MYY",
                        "PEN","MDL","RGN","CEB","DVO","MNL","DMK","CNX","CEI","KKC","KBV",
                        "HKT","URT","UTH","DAD","HAN","SGN","CXR"])
    url = "https://k.apiairasia.com/availabledates/api/v1/pricecalendar/0/0/SGD/{src}/{dest}/{date}/1"
    dates = ['2018-08-01','2018-09-01','2018-10-01','2018-11-01','2018-12-01']
    # dates = ['2018-08-01','2018-09-01']
    def start_requests(self):
        """
        Starts the requests
        """
        #Fun list comprehension to generate all the permuations of SIN/<SEA country> and <SEA country>/SIN for each date
        complete_url_list = [(self.url.format(src=a,dest=b,date=d),d)
                                for d in self.dates
                                    for i in range(2)
                                        for a in self.origin_destination_list[1-i]
                                            for b in self.origin_destination_list[i]]
        for url in complete_url_list:
            yield scrapy.Request(url=url[0],callback=self.parse,meta={'date':url[1]})

    def parse(self, response):
        j = json.loads(response.text)
        currency = list(j.keys())[0].split('|')[1]
        origin= list(j.keys())[0].split('|')[0][:3]
        destination = list(j.keys())[0].split('|')[0][3:]
        
        for d,p in list(j.values())[0].items():
            aitem = PriceItem()
            aitem['provider'] = self.name
            aitem['origin'] = origin
            aitem['destination'] = destination
            aitem['currency'] = currency
            aitem['date'] = d
            aitem['price'] = p
            yield aitem
