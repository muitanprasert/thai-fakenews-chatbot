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

# ------- RESPONSE: functions for constructing a response to the user's input ------- #

def evaluate(msg):
    # retrieve search results from google
    results = search(msg + " antifakenewscenter.com", tld='com', num=10, pause=0.5)
    url = ""
    other_url = ""
    blacklist = ["/report-form", "/tag", '/category', '/คำถามที่พบบ่อย', '/ถามตอบ', '/เข้าสู่ระบบ']
    for r in results:
        if other_url=="" and "antifakenewscenter.com" not in r:    # keep url in another website just in case
            other_url = r
        if url=="" and "antifakenewscenter.com" in r and len(r) > 36 and sum(b in r for b in blacklist) == 0:
            url = r
    if url == "":
        return get_approximation(msg, other_url)

    # get title, date and verifying agency
    entry = get_raw(url)
    from_index = entry.find('<div class="title-post-news">')
    to_index = entry.find('<div class="tag-post-news">')
    if from_index == -1 or to_index == -1:   # just in case the html retrieved doesn't have expected fields
        return get_approximation(msg, other_url)
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
    if verifier == "" or  (wcount > 3 and sim <= 0.7):   # verifier is only found in report articles
        return get_approximation(msg, other_url)
    url = unquote(url)
    detail = "\"" + title + "\" ยืนยัน" + date + verifier + "\n\nอ่านรายละเอียดได้ที่ " + url
    header = ""
    if wcount <= 3:
        header = "เนื่องจากคำค้นหาสั้นเกินไป ระบบจะแสดงข่าวที่เกี่ยวข้องกับคำค้นหาของคุณมากที่สุด โปรดตรวจสอบความถูกต้องด้วยตนเองอีกครั้ง\n\n"
    if "เป็นข้อมูลเท็จ" in entry:
        return header + "ข่าวปลอม: " + detail
    if "เป็นข้อมูลบิดเบือน" in entry:
        return header + "ข่าวบิดเบือน: " + detail
    return header + "ข่าวจริง: " + detail

def get_raw(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    return r.text

def removetags(raw_html):
    cleanr = cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def similarity(msg, html):
    from pythainlp.tag import pos_tag
    from pythainlp.tokenize import word_tokenize

    # tokenize and keep only words with "key" pos tags
    tokens = word_tokenize(msg, engine='newmm-safe', keep_whitespace=False)
    tuples = pos_tag(tokens, corpus='')
    key_tags = ['N', 'VACT', 'VATT', 'XVBB', 'XVMM', 'DCNM', 'DONM', 'CMTR', 'JCMP', 'RPRE', 'PROPN']
    words = []
    for (word,tag) in tuples:
       if tag in key_tags or len(tag)==0 or tag[0] in key_tags:
          words.append(word)

    # count no. words that appear in the article
    appear = sum(w in html for w in words)
    appear_ratio = appear/len(words)
    return len(tuples), appear_ratio

def get_approximation(msg, url):
    if len(url) > 0:
        html = get_raw(url)
        wcount, sim = similarity(msg, html)
        if sim > 0.6:
            return "ไม่พบข่าวดังกล่าวในฐานข้อมูลที่ตรวจสอบแล้ว นี่คือบทความที่อาจเกี่ยวข้องกับคำค้นหาของคุณแต่ยังไม่ได้รับการตรวจสอบ: "+unquote(url)
    return "ไม่พบข่าวดังกล่าวในฐานข้อมูล"

if __name__ == '__main__':
    app.run(debug=True)


# ------- UNUSED: saved code for predictor models that exceed heroku memory limit ------- #
def get_features(input_text, extractor):
    # REMINDER: uncomment dependencies in requirements.txt needed for the feature extractor

    if extractor=='wangchanberta':
        # import transformers
        from tqdm.auto import tqdm
        from transformers import CamembertTokenizer, pipeline

        # create tokenizer & feature extractor
        tokenizer = CamembertTokenizer.from_pretrained(
                                        'airesearch/wangchanberta-base-att-spm-uncased',
                                        revision='main')
        tokenizer.additional_special_tokens = ['<s>NOTUSED', '</s>NOTUSED', '<_>']

        feature_extractor = pipeline(task='feature-extraction',
                tokenizer=tokenizer,
                model = f'airesearch/wangchanberta-base-att-spm-uncased',
                revision = 'main')

        # get features from last 4 states
        input_text = input_text[:415]
        last_k = 4
        hidden_states = feature_extractor(input_text)[0]
        last_k_layers = [hidden_states[i] for i in [-i for i in range(1,last_k+1)]]
        cat_hidden_states = np.array(sum(last_k_layers, []))
        return cat_hidden_states[None,:]

    else:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('paraphrase-xlm-r-multilingual-v1')
        return model.encode(input)

def guess(input, extractor):
    import pickle
    from sklearn.linear_model import LogisticRegression
    inputX = get_features(input) 
    model = pickle.load(open('/detector/logist-'+extractor+'.sav', 'rb'))
    pred = 100-(model.predict_proba(inputX)[0][0]*100)
    if pred >= 50:
        return "ไม่พบข่าวนี้ในฐานข้อมูล แต่โมเดลปัญญาประดิษฐ์ของเราประเมินว่ามีโอกาส %d%% ที่ข่าวนี้จะเป็นความจริง" % pred
    else:
        return "ไม่พบข่าวนี้ในฐานข้อมูล แต่โมเดลปัญญาประดิษฐ์ของเราประเมินว่ามีโอกาส %d%% ที่ข่าวนี้จะเป็นความเท็จ" % (100-pred)