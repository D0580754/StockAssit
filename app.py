# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 01:00:17 2018

@author: linzino
"""


from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import mongodb
import re

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
    ### 抓到顧客的資料 ###
    #message = TextSendMessage(text="你說的是不是"+event.message.text)
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
    elif event.message.text == "台股網站":
        line_bot_api.reply_message(event.reply_token, imagemap_message())
    elif event.message.text == "功能選單":
        line_bot_api.reply_message(event.reply_token, buttons_template())

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

def buttons_template():
    buttons = TemplateSendMessage(
            alt_text='功能選單',
            template=ButtonsTemplate(
                    title='請選擇功能',
                    text='股票助理提供以下功能',
                thumbnail_image_url='https://i.imgur.com/R6gvyxC.png',
                actions=[
                     MessageTemplateAction(
                        label='選股功能',
                        text='你已點選選股功能'
                    ),
                     MessageTemplateAction(
                        label='指標回測',
                        text='你已點選指標回測功能'
                    ),
                     MessageTemplateAction(
                        label='虛擬交易',
                        text='你已點選虛擬交易功能'
                    ),
                    MessageTemplateAction(
                        label='查詢功能',
                        text='你已點選查詢功能'
                    )
                ]
            )
    ) 
    return buttons
if __name__ == '__main__':
    app.run(debug=True)