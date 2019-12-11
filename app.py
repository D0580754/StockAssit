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
line_bot_api = LineBotApi('b2ZZ5S9d8Uvtl6CqAQiSS2ykRn4fBehUEnj0i1PitOEe2bN+yPW7XbnZyZaYj6asN/pinquk9P2+7evxROlazavRnRUmS1NVqmvW9OVCFOTM28Pz71e7bKjbTlHTMS60pR/6TrkDjEgs1kHXLSF7HQdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('991b83b3b7aa95da15660991d0248a3a')

#line_bot_api.push_message('Uc52a42025be949ba1b1e0654d6536122', TextSendMessage(text='開始'))

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
        line_bot_api.push_message(uid, TextSendMessage(usespeak[0:4]+'儲存成功'))
        return 0 
    elif re.match('刪除[0-9]{4}',usespeak): # 刪除存在資料庫裡面的股票
        mongodb.delete_user_stock_fountion(stock=usespeak[2:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak[2:]+'刪除成功'))
        return 0
    elif re.match('[0-9]{4}[.][TW]',usespeak):
        answer = search.getPrice(usespeak)
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('取消委託',usespeak):#取消委託
        answer = order.cancelOrder(usespeak[4:])
        line_bot_api.push_message(uid, TextSendMessage(answer))
    elif re.match('[B|S]',usespeak): #下單
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
        line_bot_api.push_message(uid, TextSendMessage('熱門股Top10\n'+answer))
    elif re.match('漲幅排行',usespeak):#查詢單日漲幅排行
        name ='up'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage('漲幅排行Top10\n'+answer))
    elif re.match('跌幅排行',usespeak):#查詢單日跌幅排行
        name ='down'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage('跌幅排行Top10\n'+answer))
    elif re.match('當沖指標排行',usespeak):#查詢當沖指標排行
        name ='pdis'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage('當沖指標排行Top10\n'+answer))
    elif usespeak =='成交價排行':#查詢成交價排行
        name ='pri'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage('成交價排行Top10\n'+answer))
    elif usespeak =='成交值排行':#查詢成交值排行
        name ='amt'
        answer = choice.techface(name)
        line_bot_api.push_message(uid, TextSendMessage('成交值排行Top10\n'+answer)) 
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
    elif usespeak =='殖利率排行':
        answer = choice.y_ield()
        line_bot_api.push_message(uid, TextSendMessage('殖利率排行Top25\n'+answer))
    elif usespeak =='股價便宜':
        answer = choice.EPSBPR()
        line_bot_api.push_message(uid, TextSendMessage('股價偏便宜的股票\n'+answer))
    elif event.message.text == "台股網站":
        line_bot_api.reply_message(event.reply_token, imagemap_message())
    elif event.message.text == "虛擬下單":
        line_bot_api.reply_message(event.reply_token, buttons_template())
    elif event.message.text == "選股":
        line_bot_api.reply_message(event.reply_token, carousel_template())
    elif event.message.text == "股票小學堂":
        line_bot_api.reply_message(event.reply_token, buttons2_template())
    elif event.message.text == "股票交易基本流程": 
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='https://imgur.com/VHAAgdU.png', preview_image_url='https://imgur.com/VHAAgdU.png'))
    elif event.message.text == "股票交易基本規則":
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='https://imgur.com/NTFTH3d.png', preview_image_url='https://imgur.com/o8WuFjh.png'))
    elif event.message.text == "選股知識":
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='https://imgur.com/JGCG0MP.png', preview_image_url='https://imgur.com/JGCG0MP.png'))
    elif event.message.text == "技術指標":
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='https://imgur.com/IGKydqq.png', preview_image_url='https://imgur.com/IGKydqq.png'))
    elif event.message.text == "使用教學":
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='https://imgur.com/BrhlwQr.png', preview_image_url='https://imgur.com/BrhlwQr.png'))
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
            alt_text='虛擬下單功能',
            template=ButtonsTemplate(
                    title='請選擇服務功能',
                    text='股票助理提供以下功能',
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
                actions=[
                     MessageTemplateAction(
                        label='下單',
                        text='請依範例格式輸入下單資料\nB/S->買賣類型\n2330.TW->股票代碼\nLMT/MKT->委託類型\n1000->委託數量\n300.5->委託價'
                    ), 
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
                    )  
                ]
            )
    ) 
    return buttons
def buttons2_template(): #尚未更正: 其他使用者看不到請輸入..
    buttons2 = TemplateSendMessage(
            alt_text='股票小學堂',
            template=ButtonsTemplate(
                    title='股票小學堂',
                    text='請選擇想了解的項目',
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
                actions=[
                     MessageTemplateAction(
                        label='股票交易基本流程',
                        text='股票交易基本流程'
                    ), 
                     MessageTemplateAction(
                        label='股票交易基本規則',
                        text='股票交易基本規則'
                    ),
                     MessageTemplateAction(
                        label='選股知識',
                        text='選股知識'
                    ),
                     MessageTemplateAction(
                        label='技術指標',
                        text='技術指標'
                    )  
                ]
            )
    ) 
    return buttons2
def  carousel_template():
    carousel = TemplateSendMessage(
        alt_text='選股',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
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
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
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
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
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
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
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
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
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
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
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
                thumbnail_image_url='https://i.imgur.com/CCohubT.jpg',
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
                    ),
                    MessageTemplateAction(
                        label='X',
                        text='X'
                    )
                ]
            )


        ]
    )
    )
    return carousel      

if __name__ == '__main__':
    app.run(debug=True)