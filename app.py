#!/usr/bin/python
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
from flask import Flask, jsonify, render_template, request
import json
import numpy as np
import requests
from googlesearch import search

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__)

lineaccesstoken = '3POi0EbdigkQvu+n0ZmqdvTp/exfy6f63l17uohvB6UjI2pTpVERM55f9ZqUV142wqO7dPwo46jxK8v+0ixUQKOMpumyrbfa7T8POc7uNRyv+KE/VlWswBNSBkbsn8V513MUoVH44X4cDYMq5IxwWQdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(lineaccesstoken)

####################### new ########################
@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    no_event = len(decoded['events'])
    for i in range(no_event):
        event = decoded['events'][i]
        event_handle(event)
    return '',200


def event_handle(event):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    try:
        msgId = event["message"]["id"]
        msgType = event["message"]["type"]
    except:
        print('error cannot get msgID, and msgType')
        #sk_id = np.random.randint(1,17)
        #replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        #line_bot_api.reply_message(rtoken, replyObj)
        return ''

    if msgType == "text":
        msg = str(event["message"]["text"]) # incoming msg
        response = evaluate(msg)
        replyObj = TextSendMessage(text=response)
        line_bot_api.reply_message(rtoken, replyObj)

    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

def get_raw(url):
    r = requests.get(url)
    return r.text

def evaluate(msg):
    results = search(msg + " antifakenewscenter.com", tld='com', num=10, pause=2.0)
    url = 0
    for r in results:
        if "antifakenewscenter.com" in r:
            url = r
            break
    if url == 0:
        return "ไม่พบข่าวนี้ในฐานข้อมูล"

    entry = get_raw(url)
    if "เป็นข้อมูลเท็จ" in entry:
        return "ข่าวนี้ได้รับการยืนยันแล้วว่าเป็นข่าวปลอม อ่านรายละเอียดได้ที่ "+url
    elif "เป็นข้อมูลบิดเบือน" in entry:
        return "ข่าวนี้ได้การยืนยันแล้วว่าเป็นข่าวบิดเบือน อ่านรายละเอียดได้ที่ "+url
    return "ข่าวนี้ได้รับการยืนยันแล้วว่าเป็นความจริง อ่านรายละเอียดได้ที่ "+url

if __name__ == '__main__':
    app.run(debug=True)
