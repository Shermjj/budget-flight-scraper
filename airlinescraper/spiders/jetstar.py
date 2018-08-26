# -*- coding: utf-8 -*-
import scrapy
import pickle
from bs4 import BeautifulSoup
from airlinescraper.items import PriceItem
import json
import re
import logging

# Guide:
# 0.
#    This is built on the scrapy framework. See below for explanation of the bug.
#    Other than that, works as expected.
#    The server may at times block the ip adress for a period of time if the requests
#    exceeds a certain number.
#    
#
# 1. Bug : (On the scrapy version)
#          Sometimes, we end up with an empty page with a 200 code. Then it leads to to
#          wrong prices for subsequent request (somehow the prices are for another origin/dest?) 
#          Are these two phenomenon related? Seems to be...
#
#   Solution: Use a custom script instead of relying on the scrapy framework. 
#             Tried - Turning off cookies, turning off concurrent downloads, increasing download delay
#
#
# 2. For every requests, it returns 18 days worth of prices. So segment the dates into 18 days.
#
# 4. This program requires the use of a form payload .

class JetstarSpider(scrapy.Spider):
    VIEWSTATE = '''/wEPDwUBMGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFJ01lbWJlckxvZ2luU2VhcmNoVmlldyRtZW1iZXJfUmVtZW1iZXJtZaXQj/rtlZ1hPS0zPQj+skvkM9qtml4xeXxQQ8y8k6xx'''
    name = 'jetstar'
    url_main = "https://book.jetstar.com"
    #URL to hit if we want to do the next page
    #url_next = "https://book.jetstar.com/CalendarSelect.aspx"
    dates = ['25/08/2018']
    #,'25/08/2018','10/09/2018','25/09/2018','10/10/2018','25/10/2018','10/11/2018','25/11/2018','10/12/2018','25/12/2018']

    # The origin_destination list is a tuple of two lists, the origin and destination respectively.
    # origin_destination_list = (['Singapore (SIN)'],["Nha Trang (CXR)","Da Nang (DAD)","Da Lat (DLI)","Hanoi (HAN)"])
    origin_destination_list = (['Singapore (SIN)'],["Phnom Penh (PNH)","Siem Reap (REP)","Jakarta (CGK)","Bali (Denpasar) (DPS)",
               "Medan - Kualanamu  (KNO)","Pekanbaru (PKU)","Palembang (PLM)","Surabaya (SUB)",
               "Kuala Lumpur (KUL)","Penang (PEN)","Yangon (RGN)","Clark (CRK)",
               "Manila (MNL)","Bangkok (BKK)","Hat Yai (HDY)","Phuket (HKT)",
               "Nha Trang (CXR)","Da Nang (DAD)","Da Lat (DLI)","Hanoi (HAN)",
               "Hai Phong (HPH)","Hue (HUI)","Phu Quoc (PQC)","Pleiku (PXU)",
               "Ho Chi Minh City (SGN)","Chu Lai (VCL)","Vinh (VII)"])

    def start_requests(self):
        """
        Ensure that the form (a dictionary object) that is required to make the POST request is available
        Returns all the formrequest that will be made
        """
        with open('post_form_jetstar.p','rb') as fp:
            form_payload = pickle.load(fp)
        #Nice piece of list comprehension generates all the combination of dates, origins and destination
        #for all sets of origin -> destination and destination -> origin
        payload_list = [self._format_payload(form_payload,origin=a,destination=b,date=d)
                            for d in self.dates 
                                for i in range(2) 
                                    for a in self.origin_destination_list[i] 
                                        for b in self.origin_destination_list[1-i]]

        for p in payload_list:
             yield scrapy.FormRequest(url=self.url_main,formdata=p[0],dont_filter=True,callback=self.parse,meta={'origin':p[1],'destination':p[2],'payload':p[0]})

        
    def _format_payload(self,payload,origin,destination,date):
        """
        Sets the origin, destination and date for the payload
        Returns a tuple (*payload with settings*, *origin(abv.)*, *destination(abv.)*)
        """
        payload['__VIEWSTATE'] = self.VIEWSTATE
        payload['ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin1'] = origin
        payload['ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination1'] = destination
        payload['ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureDate1'] = date
        #Need to give a copy of the payload, otherwise it will reference the object which will be further modified...
        return (dict(payload),re.findall(r'\((.*?)\)',origin)[-1],re.findall(r'\((.*?)\)',destination)[-1])
        

    def parse(self, response):
        """
        Returns an item
        """
        soup = BeautifulSoup(response.text,'lxml')
        try:
            currency = soup.find('div',class_='legend-currency').text.split(':')[1].strip()
            li_list = soup.find('div',class_='low-fare-selector').findAll('li')
            for li in li_list:
                jitem = PriceItem()
                jitem['provider'] = self.name
                jitem['date'] = li['data-date']
                jitem['price'] = li['data-price']
                jitem['currency'] = currency
                jitem['origin'] = response.meta['origin']
                jitem['destination'] = response.meta['destination']
                yield jitem
        except AttributeError as e:
            print(e)
            print(response.meta['origin'] + ' to ' + response.meta['destination'])
            logging.error('NoneType issue for ' + response.meta['origin'] + ' to ' + response.meta['destination'])