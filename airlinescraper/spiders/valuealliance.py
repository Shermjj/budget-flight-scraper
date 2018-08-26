# -*- coding: utf-8 -*-
import scrapy
import re
from string import Template
from airlinescraper.items import PriceItem 
import json
# To get token, make a get request to token url
# with header: Abb-Sponsor:value_alliance
# Date format: 03-Aug-2018
class ValueallianceSpider(scrapy.Spider):
    name = 'valuealliance'
    start_urls = ['https://meta.valuealliance.com/shopping_range/']
    origin_destination_list = ['Bacolod (BCD)','Butuan (BXU)','Cagayan De Oro (CGY)','Caticlan (Boracay) (MPH)',
                    'Cauayan (CYZ)','Daniel Z Romualdez (TAC)','Davao (DVO)','Dumaguete (DGT)','General Santos (GES)',
                    'Iloilo (ILO)','Legazpi (LGP)','Pagadian (PAG)','Puerto Princesa (PPS)','Roxas Airport (RXS)','Tagbilaran (TAG)',
                    'Tuguegarao (TUG)','Virac (VRC)','Buri Ram (BFV)','Chiang Rai (CEI)','Chumphon (CJM)','Khon Kaen (KKC)','Lampang (LPT)',
                    'Loei (LOE)','Mae Sot (MAQ)''Nakhon Phanom (KOP)','Nan (NNT)','Phitsanulok (PHS)','Phrae (PRH)','Ranong (UNN)','Roi Et (ROI)',
                    'Ubon Ratchathani (UBP)','Udon Thani (UTH)']
    # token_url = 'https://vac.api.amber.airblackbox.com/v1/token'
    payload = '''{"type":"oneway","traveller_count":1,"journeys":[{"order":1,"origin":"$origin","destination":"$destination","date":"$date"}],"plus_days":30,"min_days":7}'''
    headers = {"Content-Type":"application/json",
                "abb-sponsor":"value_alliance",
                "abb-booking-token":"fb2faf71-8b4d-408c-ad68-b4935ac199c3"}
    dates = ["07-Aug-2018","07-Sep-2018","07-Oct-2018","07-Nov-2018","07-Dec-2018"]
    # ,"03-Sep-2018"]

    def start_requests(self):
        IATA_country_list = (['SIN'],[re.findall(r'\((.*?)\)',s)[-1] for s in self.origin_destination_list])
        payload_list = [Template(self.payload).substitute(origin=a,destination=b,date=d) for d in self.dates for i in range(2) for a in IATA_country_list[i] for b in IATA_country_list[1-i]]
        for payload in payload_list:
            yield scrapy.Request(url=self.start_urls[0],callback=self.parse,method='POST',headers=self.headers,body=payload)

    def parse(self, response):
        j = json.loads(response.text)
        for price in j['journeys']:
            vitem = PriceItem()
            vitem['provider'] = self.name
            vitem['currency'] = j['currency']
            vitem['price'] = price['price']
            vitem['origin'] = price['origin']
            vitem['destination'] = price['destination']
            vitem['date'] = price['date']
            yield vitem
