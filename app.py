# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 01:00:17 2018

@author: yeh
"""


from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import mongodb
import re
import schedule
import urllib.parse
import datetime
from bs4 import BeautifulSoup
import time
import search
import order
import choice

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('0RESBNWCfsvSRF4MMUJnu5uTKCeS3MFN05XAoDkNUmLh/JwfjZZqV1hisMl8GsR6wG175trlcY/74iN0sJ1A98hLE1v2takoD7UNfNY8Fu102jM7C6agGKWOQNAqYZzKK2sEh+eZtx86OO4bhxh6kAdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('54cd451ffb3d2728924e284de5f836bd')

line_bot_api.push_message('Ud5ccf6452c79b7add21fcb8a008b0717', TextSendMessage(text='開始'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id #使用者ID
    usespeak=str(event.message.text) #使用者講的話
    if re.match('[0-9]{4}[<>][0-9]',usespeak): # 先判斷是否是使用者要用來存股票的
        mongodb.write_user_stock_fountion(stock=usespeak[0:4], bs=usespeak[4:5], price=usespeak[5:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak[0:4]+'已經儲存成功'))
        return 0 
    elif re.match('刪除[0-9]{4}',usespeak): # 刪除存在資料庫裡面的股票
        mongodb.delete_user_stock_fountion(stock=usespeak[2:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'已經刪除成功'))
        return 0
    elif re.match('[0-9]{4}[.][TW]',usespeak):
        answer = search.getPrice(usespeak)
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('取消委託',usespeak):#取消委託
        answer = order.cancelOrder(usespeak[4:])
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('[B|S]',usespeak):
        answer = order.putOrder(usespeak[0], usespeak[2:9], usespeak[10:13], usespeak[14:18], usespeak[19:])    
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif usespeak =='委託紀錄':#查詢委託
        answer = search.getOrder()
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('庫存紀錄',usespeak):#查詢庫存
        answer = search.getInStock()
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif usespeak=='成交紀錄':#查詢成交
        answer = search.getDeal()
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('熱門股',usespeak):#查詢熱門股
        name ='vol'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('漲幅排行',usespeak):#查詢單日漲幅排行
        name ='up'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('跌幅排行',usespeak):#查詢單日跌幅排行
        name ='down'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('當沖指標排行',usespeak):#查詢當沖指標排行
        name ='pdis'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif usespeak =='成交價排行':#查詢成交價排行
        name ='pri'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif usespeak =='成交值排行':#查詢成交值排行
        name ='amt'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage(answer)) 
    elif usespeak =='外資買超':#查詢外資買超排行
        name ='ZG_D'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('外資買超Top10\n'+answer))
    elif usespeak =='外資賣超':#查詢外資賣超排行
        name ='ZG_DA'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('外資賣超Top10\n'+answer))
    elif usespeak =='自營商買超':#查詢自營商買超排行
        name ='ZG_DB'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('自營商買超Top10\n'+answer))
    elif usespeak =='自營商賣超':#查詢自營商賣超排行
        name ='ZG_DC'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('自營商賣超Top10\n'+answer))
    elif usespeak =='投信買超':#查詢投信買超排行
        name ='ZG_DD'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('投信買超Top10\n'+answer))
    elif usespeak =='投信賣超':#查詢投信賣超排行
        name ='ZG_DE'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('投信賣超Top10\n'+answer))
    elif usespeak =='自營商買賣超':#查詢自營商買賣超
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('自營商買賣超Top10\n'+answer))
    elif usespeak =='投信買賣超':#查詢投信買賣超排行
        name ='ZGK_DD'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('投信買賣超Top10\n'+answer))
    elif usespeak =='主力買超':#查詢主力買超排行
        name ='ZG_F'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('主力買超Top10\n'+answer))
    elif usespeak =='主力賣超':#查詢主力賣超排行
        name ='ZG_FA'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('主力賣超Top10\n'+answer))
    elif usespeak =='主力買賣超':#查詢主力買賣超排行
        name ='ZGK_F'
        answer = choice.chipface(name)
        line_bot_api.push_message(uid, TextSendMessage('主力買賣超Top10\n'+answer))   
    elif usespeak =='營業額創新高':#最近一月營收創新高的股票
        name ='zkparse_970_NA'
        answer = choice.basicface(name)
        line_bot_api.push_message(uid, TextSendMessage('最近一月營收創新高的股票\n'+answer))
    elif usespeak =='本益比<12':#本益比<12的股票
        name ='zkparse_170_12'
        answer = choice.basicface(name)
        line_bot_api.push_message(uid, TextSendMessage('本益比<12的股票\n'+answer))
    elif usespeak =='股價淨值<1':#股價淨值<1
        name ='zkparse_160_1'
        answer = choice.basicface(name)
        line_bot_api.push_message(uid, TextSendMessage('股價淨值<1的股票\n'+answer))
    elif usespeak =='股價便宜':
        answer = choice.EPSBPR()
        line_bot_api.push_message(uid, TextSendMessage('股價偏便宜的股票\n'+answer))
    elif event.message.text == "台股網站":
        line_bot_api.reply_message(event.reply_token, imagemap_message())
    elif event.message.text == "查詢功能":
        line_bot_api.reply_message(event.reply_token, buttons_template())
    elif event.message.text == "選股":
        line_bot_api.reply_message(event.reply_token, carousel_template())
#@imagemap.add(MessageEvent, message=TextMessage)
def imagemap_message():
    message = ImagemapSendMessage(
            base_url='https://i.imgur.com/R6gvyxC.png',
            alt_text='台股網站',
            base_size=BaseSize(height=2000, width=2000),
            actions=[
                URIImagemapAction(
                    link_uri='https://www.cnyes.com/twstock/',
                    area=ImagemapArea(
                        x=0, y=0, width=1000, height=1000
                    )
                ),
                URIImagemapAction(
                    link_uri='https://tw.stock.yahoo.com/',
                    area=ImagemapArea(
                        x=1000, y=0, width=1000, height=1000
                    )
                ),
                URIImagemapAction(
                    link_uri='https://www.wantgoo.com/',
                    area=ImagemapArea(
                        x=0, y=1000, width=1000, height=1000
                    )
                ),
                URIImagemapAction(
                    link_uri='https://www.twse.com.tw/zh/',
                    area=ImagemapArea(
                        x=1000, y=1000, width=1000, height=1000
                    )
                )
            ]
    )
    return message

def buttons_template(): #尚未更正: 其他使用者看不到請輸入..
    buttons = TemplateSendMessage(
            alt_text='查詢功能',
            template=ButtonsTemplate(
                    title='請選擇查詢項目',
                    text='股票助理提供以下查詢功能',
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                actions=[
                     MessageTemplateAction(
                        label='委託紀錄',
                        text='委託紀錄'
                    ),
                     MessageTemplateAction(
                        label='庫存紀錄',
                        text='庫存紀錄'
                    ),
                     MessageTemplateAction(
                        label='成交紀錄',
                        text='成交紀錄'
                    ),
                    MessageTemplateAction(
                        label='股價查詢',
                        text='請輸入股票代碼 ex. 2330.TW'
                    )
                ]
            )
    ) 
    return buttons

def  carousel_template():
    Carousel_template = TemplateSendMessage(
        alt_text='選股',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                title='基本面選股',
                text='請選擇選股條件',
                actions=[
                    MessageTemplateAction(
                        label='最近一個月營收創新高',
                        text='營業額創新高'
                    ),
                    MessageTemplateAction(
                        label='本益比<10股價淨值比<0.7',
                        text='股價便宜'
                    ),
                    MessageTemplateAction(
                        label='殖利率排行',
                        text='殖利率排行'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                title='技術面選股',
                text='請選擇選股條件',
                actions=[
                    MessageTemplateAction(
                        label='熱門股',
                        text='熱門股'
                    ),
                    MessageTemplateAction(
                        label='漲幅排行',
                        text='漲幅排行'
                    ),
                    MessageTemplateAction(
                        label='跌幅排行',
                        text='跌幅排行'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                title='技術面選股',
                text='請選擇選股條件',
                actions=[
                    MessageTemplateAction(
                        label='當沖指標排行',
                        text='當沖指標排行'
                    ),
                    MessageTemplateAction(
                        label='成交價排行',
                        text='成交價排行'
                    ),
                    MessageTemplateAction(
                        label='成交值排行',
                        text='成交值排行'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                title='籌碼面選股',
                text='請選擇選股條件',
                actions=[
                    MessageTemplateAction(
                        label='外資買超',
                        text='外資買超'
                    ),
                    MessageTemplateAction(
                        label='外資賣超',
                        text='外資賣超'
                    ),
                    MessageTemplateAction(
                        label='自營商買超',
                        text='自營商買超'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                title='籌碼面選股',
                text='請選擇選股條件',
                actions=[
                    MessageTemplateAction(
                        label='自營商賣超',
                        text='自營商賣超'
                    ),
                    MessageTemplateAction(
                        label='投信買超',
                        text='投信買超'
                    ),
                    MessageTemplateAction(
                        label='投信賣超',
                        text='投信賣超'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                title='籌碼面選股',
                text='請選擇選股條件',
                actions=[
                    MessageTemplateAction(
                        label='主力買超',
                        text='主力買超'
                    ),
                    MessageTemplateAction(
                        label='主力賣超',
                        text='主力賣超'
                    ),
                    MessageTemplateAction(
                        label='主力買賣超',
                        text='主力買賣超'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                title='籌碼面選股',
                text='請選擇選股條件',
                actions=[
                    MessageTemplateAction(
                        label='自營商買賣超',
                        text='自營商買賣超'
                    ),
                    MessageTemplateAction(
                        label='投信買賣超',
                        text='投信買賣超'
                    )
                ]
            ),


        ]
    )
    )
    return Carousel_template      


if __name__ == '__main__':
    app.run(debug=True)