import pymongo
import urllib.parse
import configparser

from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.models import *
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import requests
import json

from detect import detect
from views_template import Carousel_Template


app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

config = configparser.ConfigParser()
config.read('config.ini')
username = urllib.parse.quote_plus(config.get("mongodb-atlas", "username"))
password = urllib.parse.quote_plus(config.get("mongodb-atlas", "password"))
myclient = pymongo.MongoClient(
    f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")


line_bot_api = LineBotApi(config.get(
    'line-bot', 'channel_access_token'))                        # 確認 token 是否正確
handler = WebhookHandler(config.get(
    'line-bot', 'channel_secret'))                              # 確認 secret 是否正確
my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}

# 與mongodb atlas做連線
username = urllib.parse.quote_plus(config.get("mongodb-atlas", "username"))
password = urllib.parse.quote_plus(config.get("mongodb-atlas", "password"))
myclient = pymongo.MongoClient(
    f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")


user_collection = {}
temp_userid = ""


@app.route("/", methods=['POST', 'GET'])
def linebot():
    if request.method == 'GET':
        return 'ok'
    body = request.json                                   # body data type 是 dict
    # print(body)
    # print(type(body))
    events = body["events"]
    # print(events)

    if "replyToken" in events[0]:
        payload = dict()
        replyToken = events[0]['replyToken']
        # 常用的變數 ->存在payload字典
        payload['replyToken'] = replyToken
        msg = events[0]['message']
        print("msg=events[0]['message']" + str(msg))
        print('payload ------->' + str(payload))
        # 如果格式是訊息
        if events[0]["type"] == "message":
            if events[0]["message"]["type"] == "text":
                text = events[0]["message"]["text"]

                if text == "這隻貓叫作什麼名字?":
                    # Line-sever 接受的訊息格式
                    payload["messages"] = [openCamera()]
                    replyMessage(payload)                         # 呼叫回傳訊息
   

                elif text == "附近景點":
                    payload["messages"] = [Carousel_Template()]
                    replyMessage(payload) 

                # 都沒有觸發回應的文字就echo回他
                else:
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]

            if events[0]["message"]["type"] == "image":
                local_save = saveimg(events[0]["message"]["id"])                 # 呼叫存照片功能得到照片儲存路徑
                cat_name = whatscat(local_save)     # 呼叫功能一: 這隻貓叫作什麼名字
                payload["messages"] = [flexmessage(cat_name), reply_detect_img(end_point, events[0]["message"]["id"])]
                replyMessage(payload)

    return 'OK'                                                                 # 驗證 Webhook 使用，不能省略


# 回傳訊息功能
def replyMessage(payload):
    response = requests.post(
        'https://api.line.me/v2/bot/message/reply', headers=HEADER, json=payload)
    return 'OK'


# template 訊息: 行動呼籲用戶選擇拍照/挑選照片
def openCamera():
    message = {
        "type": "template",
        "altText": "this is a confirm template",
        "template": {
            "type": "confirm",
            "text": "拍張猴硐貓村的貓咪照📸",
            "actions": [
                {
                    "type": "camera",
                    "label": "打開相機"
                },
                {
                    "type": "cameraRoll",
                    "label": "挑選照片"
                }
            ]
        }
    }
    return message


# 儲存用戶傳來的照片
def saveimg(message_id):
    SendImage = line_bot_api.get_message_content(
        message_id)     # message_id 用戶傳訊息的訊息ID
    local_save = './static/' + message_id + '.jpg'
    with open(local_save, 'wb') as file:
        for chenk in SendImage.iter_content():
            file.write(chenk)
    return local_save


# 這隻貓叫作什麼名字
def whatscat(local_save):
    with open('detect_args.json', newline='') as jsonfile:                     # 載入需要餵進detect.py的Json參數
        opt = json.load(jsonfile)
        # 將傳入照片來源改成flask預設圖片目錄  改雲端方案時要更變
        opt["source"] = local_save
        # 呼叫detect.py detect功能
        result, result_img_path = detect(opt)
        result_img = result_img_path[20:]
        cat_name = result[:-5]
        print(cat_name)
        return cat_name



# Flexmessage 貓咪卡片
def flexmessage(cat_name):
    flex_contents = f"./flexmessage_template/{cat_name}_flexmessage.json"
    with open(flex_contents, 'rb') as f:
        contents = json.load(f)
        message = dict()
        message = {
            "type": "flex",
            "altText": "this is a flex message",
            "contents": contents
        }
        return message



def reply_detect_img(end_point, message_id):
    message = {
        "type": "image",
        "originalContentUrl": end_point + "/static/result_photo/" + message_id + ".jpg",
        "previewImageUrl": end_point + "/static/result_photo/" + message_id + ".jpg"
    }
    return message


def gomongodb(cat_name):
    db = myclient["meow_cat_data"]
    collection = db["cat_data"]
    myquery = {'name': cat_name}
    data = list(collection.find(myquery))
    print(data)
    print(type(data))
    return data



if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0', 5000, debug=True)
