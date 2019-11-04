# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 11:38:09 2019

@author: Admin
"""

from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor
from bs4 import BeautifulSoup

def get_webservice(stock):
    url = "http://61.220.30.176/WebOrder/GVETransacs.asmx/QueryQuote5Price?compcode=" + stock
    list_req = requests.get(url)
    soup = BeautifulSoup(list_req.content)
    r = soup.find('string').text
    return r


def getPrice(stock):
    client = get_webservice(stock)
    try:
        import xml.etree.cElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET
        
    #price = client.service.QueryQuote5Price(stock, )
    r = ET.fromstring(client)
    r_new = "您查詢的股價為:\n"+"成交價:"+str(r[0][0].text)+\
                                "\n"+"成交量:"+str(r[0][1].text)+\
                                "\n"+"委買價:"+str(r[0][2].text)+\
                                "\n"+"委買量:"+str(r[0][22].text)+\
                                "\n"+"委賣價:"+str(r[0][12].text)+\
                                "\n"+"委賣量:"+str(r[0][23].text)+\
                                "\n"+"昨收價:"+str(r[0][24].text)+\
                                "\n"+"漲停價:"+str(r[0][25].text)+\
                                "\n"+"跌停價:"+str(r[0][26].text)+"\n"
    return r_new