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


app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

config = configparser.ConfigParser()
config.read('config.ini')
username = urllib.parse.quote_plus(config.get("mongodb-atlas", "username"))
password = urllib.parse.quote_plus(config.get("mongodb-atlas", "password"))
myclient = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")



line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))     # 確認 token 是否正確
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))            # 確認 secret 是否正確
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
myclient = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")



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
        payload['replyToken'] = replyToken                   # 常用的變數 ->存在payload字典
        msg = events[0]['message']
        # 如果格式是訊息
        if events[0]["type"] == "message":
            if events[0]["message"]["type"] == "text":
                text = events[0]["message"]["text"]

                if text == "這隻貓叫作什麼名字?":
                    payload["messages"] = [openCamera()]          # 回傳messge格式
                    replyMessage(payload)                         # 呼叫回傳訊息
                    print(type(payload))
                    print('payload------->'+payload)

                elif text == "111":
                    flexmessage(replyToken)




                # 都沒有觸發回應的文字就echo回他
                else:
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]

        if events[0]["message"]["type"] == "image":
            local_save = saveimg(msg['id'])                 # 呼叫存照片功能得到照片儲存路徑
            whatscat(local_save, replyToken, msg['id'])

    # # 如果格式是postback
    # elif events[0]["type"] == "postback":
    #     if msg["type"] == "image":                        # 如果用戶傳照片
    #         local_save = saveimg(msg['id'])               # 呼叫存照片功能得到照片儲存路徑
    #         whatscat(local_save, replyToken, msg['id'])   # 呼叫這隻貓叫做什麼? 功能

    return 'OK'                                             # 驗證 Webhook 使用，不能省略





def replyMessage(payload):
    response = requests.post('https://api.line.me/v2/bot/message/reply', headers=HEADER, json=payload)
    return 'OK'



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




def flexmessage(replyToken):
    # FlexMessage = json.load(open('./flexmessage_template/跩哥Malfoy_flexmessage.json', 'r', encoding='utf-8'))
    try:
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                'type': 'bubble',
                'direction': 'ltr',
                'hero': {
                    'type': 'image',
                    'url': 'https://example.com/cafe.jpg',
                    'size': 'full',
                    'aspectRatio': '20:13',
                    'aspectMode': 'cover',
                    'action': {'type': 'uri', 'uri': 'http://example.com', 'label': 'label'}
                }
            }
        )
        line_bot_api.reply_message(replyToken, flex_message)

    except:
        line_bot_api.reply_message(replyToken, TextSendMessage(text='發生錯誤！'))




# 儲存用戶傳來的照片
def saveimg(message_id):
    SendImage = line_bot_api.get_message_content(message_id)
    local_save = './static/' + message_id + '.jpg'
    with open(local_save, 'wb') as file:
        for chenk in SendImage.iter_content():
            file.write(chenk)
    return local_save


# 這隻貓叫做什麼功能
def whatscat(local_save, replyToken, message_id):
    with open('detect_args.json', newline='') as jsonfile:                     # 載入需要餵進detect.py的Json參數
        opt = json.load(jsonfile)
        opt["source"] = local_save                                             # 將傳入照片來源改成flask預設圖片目錄  改雲端方案時要更變
        result, result_img_path = detect(opt, temp_userid)                     # 呼叫detect.py detect功能
        result_img = result_img_path[20:]
        cat_name = result[:-5]
        print(cat_name)
        # originalContentUrl = end_point + "/static/result_photo/" + result_img
        # print(originalContentUrl)
        cat_data = gomongodb(cat_name)                                        # 呼叫gomongodb 查這隻貓的資料
        print('-'*50)
        print(type(cat_data))
        cat_data = str(cat_data)
        # print('-----------'+ cat_data)
        try:
            message = [  # 串列
                TextSendMessage(  # 傳送文字
                    text= cat_data,
                ),
                TextSendMessage(  # 傳送文字
                    text= result,
                ),
                ImageSendMessage(  # 傳送圖片
                    original_content_url=end_point + "/static/result_photo/" + message_id+ ".jpg",
                    preview_image_url=end_point + "/static/result_photo/" + message_id + ".jpg"
                )
            ]
            line_bot_api.reply_message(replyToken, message)
        except:
            line_bot_api.reply_message(replyToken, TextSendMessage(text='發生錯誤！'))



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
    app.run()
