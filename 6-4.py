# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 13:46:03 2019

@author: aaaaa
"""

from __future__ import print_function
import time
from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import schedule
import datetime
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

now = datetime.datetime.now().strftime("%Y%m%d")
array =['1101.TW', '1102.TW', '1103.TW', '1104.TW', '1108.TW', '1109.TW', '1110.TW']

# 先與網站請求抓到價格
def getstock(stocknumber='2002'):
    url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=' + now + '&stockNo=' + stocknumber
    list_req = requests.get(url)
    soup = BeautifulSoup(list_req.content, "html.parser")
    getjson=json.loads(soup.text)
    
    # 判斷請求是否成功
    if getjson['stat'] != '很抱歉，沒有符合條件的資料!': 
        return [getjson['data']]
    else:
        return [] # 請求失敗回傳空值

# 開始計算股票的平均以及標準差
def Standard_Deviation(stocknumber='2002'):
    stocklist = getstock(stocknumber)
    
    # 判斷是否為空值
    if len(stocklist) != 0:
        # 把json資料丟進DataFrame
        stockdf = pd.DataFrame(stocklist[0],columns=["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"])
        stockAverage = pd.to_numeric(stockdf['收盤價']).mean() #計算平均數
        stockSTD = pd.to_numeric(stockdf['收盤價']).std() #計算標準差
        
        # 看看這隻股票現在是否便宜（平均-兩倍標準差）
        buy='很貴不要買'
        if pd.to_numeric(stockdf['收盤價'][-1:]).values[0] < stockAverage - (2*stockSTD):
            buy = '這隻股票現在很便宜喔！'
            
        # 顯示結果
        get='收盤價 ＝ ' + stockdf['收盤價'][-1:].values[0]
        get=get+'\n中間價 ＝ ' + str(stockAverage)
        get=get+'\n線距 ＝ ' + str(stockSTD)
        get=get+buy
    else:
        get='請求失敗，請檢查您的股票代號'
    line_bot_api.push_message(yourid, TextSendMessage(text=get))


def job():
#把股票一個一個塞進去        
    for i in array:
       Standard_Deviation(i[:4])
second_5_j = schedule.every().day.at("8:00").do(job)

# 無窮迴圈
while True: 
    schedule.run_pending()
    time.sleep(1)
