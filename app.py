#!/usr/bin/python
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
from flask import Flask, jsonify, render_template, request
import json
import numpy as np
import requests
from googlesearch import search
import re
from urllib.parse import unquote
from tqdm.auto import tqdm
import torch
from tensorflow import keras

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

#transformers
from transformers import (
    CamembertTokenizer,
    AutoTokenizer,
    AutoModel,
    AutoModelForMaskedLM,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    pipeline,
)

#create tokenizer & feature extractor
tokenizer = CamembertTokenizer.from_pretrained(
                                'airesearch/wangchanberta-base-att-spm-uncased',
                                revision='main')
tokenizer.additional_special_tokens = ['<s>NOTUSED', '</s>NOTUSED', '<_>']

feature_extractor = pipeline(task='feature-extraction',
        tokenizer=tokenizer,
        model = f'airesearch/wangchanberta-base-att-spm-uncased',
        revision = 'main')

app = Flask(__name__)

lineaccesstoken = '3POi0EbdigkQvu+n0ZmqdvTp/exfy6f63l17uohvB6UjI2pTpVERM55f9ZqUV142wqO7dPwo46jxK8v+0ixUQKOMpumyrbfa7T8POc7uNRyv+KE/VlWswBNSBkbsn8V513MUoVH44X4cDYMq5IxwWQdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(lineaccesstoken)

####################### new ########################
@app.route('/')
def index():
    return render_template('hello.html')


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

def evaluate(msg):
    # retrieve search results from google
    results = search(msg + " antifakenewscenter.com", tld='com', num=10, pause=0.5)
    url = 0
    blacklist = ["/report-form", "/tag", '/category', '/คำถามที่พบบ่อย', '/ถามตอบ', '/เข้าสู่ระบบ']
    for r in results:
        if "antifakenewscenter.com" in r and len(r) > 36 and sum(b in r for b in blacklist) == 0:
            url = r; break
    if url == 0:
        return get_approximation(msg)

    # get title, date and verifying agency
    entry = get_raw(url)
    from_index = entry.find('<div class="title-post-news">')
    to_index = entry.find('<div class="tag-post-news">')
    if from_index == -1 or to_index == -1:
        return get_approximation(msg)
    entry = entry[from_index:to_index]
    title = removetags(entry.split("\n")[1]).strip()
    date = ""; verifier = ""
    index = entry.find("วันที่ ")
    if index > -1:
        date = "เมื่อ " + entry[index:index+30].strip()
    index = entry.find("หน่วยงานที่ตรวจสอบ ")
    if index > -1:
        chunk = entry[index:index+100]
        verifier = " โดย " + chunk[20:chunk.find('</')].strip()

    # construct and return response message
    wcount, sim = similarity(msg, entry)
    if verifier == "" or  (wcount > 3 and sim <= 0.8): # verifier is only found in report articles
        return get_approximation(msg)
    url = unquote(url)
    detail = "\"" + title + "\" ยืนยัน" + date + verifier + "\n\nอ่านรายละเอียดได้ที่ " + url
    header = ""
    if wcount <= 3:
        header = "ระบบไม่สามารถระบุเนื้อข่าวอย่างแน่นอนได้เนื่องจากคำค้นหาสั้นเกินไป นี่คือข่าวที่เกี่ยวข้องกับคำค้นหาของคุณมากที่สุด\n\n"
    if "เป็นข้อมูลเท็จ" in entry:
        return header + "ข่าวปลอม: " + detail
    if "เป็นข้อมูลบิดเบือน" in entry:
        return header + "ข่าวบิดเบือน: " + detail
    return header + "ข่าวจริง: " + detail

def get_raw(url):
    r = requests.get(url)
    return r.text

def removetags(raw_html):
    cleanr = cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def similarity(msg, html):
    url = "https://api.aiforthai.in.th/tpos"
    data = {'text':msg}
    headers = {'Apikey': "KTgCpXIQS2uRt0L6l8ZY8Q83tRFbvwwH",}
    response = requests.post(url, data=data, headers=headers)

    tuples = list(zip(response.json()['words'], response.json()['tags']))

    key_tags = ['NN', 'NR', 'CD', 'OD', 'FWN', 'ADV']
    words = []
    for (word,tag) in tuples:
       if tag in key_tags:
          words.append(word)

    appear = sum(w in html for w in words)
    appear_ratio = appear/len(words)
    return len(tuples), appear_ratio

def extract_last_k(input_text, last_k=4):
    hidden_states = feature_extractor(input_text)[0]
    last_k_layers = [hidden_states[i] for i in [-i for i in range(1,last_k+1)]]
    cat_hidden_states = sum(last_k_layers, [])
    return np.array(cat_hidden_states)

def get_approximation(input):
    inputX = extract_last_k(input[:415], last_k=4)[None,:]
    model = keras.models.load_model('/detector/base-model.h5', compile=False)
    pred = model.predict(inputX)[0][0]*100
    if pred >= 50:
        return "ไม่พบข่าวนี้ในฐานข้อมูล แต่โมเดลปัญญาประดิษฐ์ของเราประเมินว่ามีโอกาส %d%% ที่ข่าวนี้จะเป็นความจริง" % pred
    else:
        return "ไม่พบข่าวนี้ในฐานข้อมูล แต่โมเดลปัญญาประดิษฐ์ของเราประเมินว่ามีโอกาส %d%% ที่ข่าวนี้จะเป็นความเท็จ" % (100-pred)

if __name__ == '__main__':
    app.run(debug=True)
