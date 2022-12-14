import pymongo
import urllib.parse
import configparser

from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
import requests
import json

from detect import detect
from views_template import Carousel_Template

app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'

# 為何這樣就出錯
# app = Flask(__name__, static_url_path='/static/user_cats_photo/', static_folder='static/user_cats_photo/')
# UPLOAD_FOLDER = './static/user_cats_photo/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'HEIC', 'HEIF'])

config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get(
    'line-bot', 'channel_access_token'))  # 確認 token 是否正確
handler = WebhookHandler(config.get(
    'line-bot', 'channel_secret'))  # 確認 secret 是否正確
my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}

# 與mongodb atlas做連線
username = urllib.parse.quote_plus(config.get("mongodb-atlas", "username"))
password = urllib.parse.quote_plus(config.get("mongodb-atlas", "password"))
myclient = pymongo.MongoClient(
    f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")

# 全域變數
StrF = ""  # 用戶尚未收集的貓咪


@app.route("/", methods=['POST', 'GET'])
def linebot():
    if request.method == 'GET':
        return 'ok'
    body = request.json  # 可觀察印出來的訊息JSON格式
    events = body["events"]

    if "replyToken" in events[0]:
        payload = dict()
        replyToken = events[0]["replyToken"]
        payload['replyToken'] = replyToken  # 回應憑證的格式 進入Line-server的基本資格
        source = events[0]["source"]  # 產生event的來源與userID
        userId = source["userId"]
        db_landing_user(userId)  # 建立用戶資料到mongodb

        if events[0]["type"] == "message":  # 如果events類型是訊息
            if events[0]["message"]["type"] == "text":
                text = events[0]["message"]["text"]

                if text == "這隻貓叫作什麼名字?":
                    payload["messages"] = [openCamera()]  # 打開相機/打開相簿
                    replyMessage(payload)  # 呼叫回傳訊息功能


                elif text == "附近景點":
                    payload["messages"] = [Carousel_Template()]  # 回應景點Carousel_Template
                    replyMessage(payload)

                elif text == "我收集到哪些貓咪?":
                    payload["messages"] = db_user_collection(userId)
                    replyMessage(payload)

                elif text == "查詢尚未收集到的貓咪們":
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": StrF
                        }
                    ]

                    replyMessage(payload)



                else:  # 都沒有觸發回應的文字就echo回他
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                    replyMessage(payload)

            if events[0]["message"]["type"] == "image":  # 當用戶傳送照片時
                local_save = get_user_content(events[0]["message"]["id"])  # 呼叫存照片功能得到照片儲存路徑
                cat_name = whatscat(local_save, userId)  # 呼叫功能一: 這隻貓叫作什麼名字

                if cat_name:  # 能夠辨認貓咪回傳貓咪卡片
                    payload["messages"] = [flexmessage(cat_name),
                                           reply_detect_img(end_point, events[0]["message"]["id"])]
                    replyMessage(payload)
                    db_update_collection(cat_name, userId)

                else:  # 當模法無法辨認貓咪時回應
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": "無法辦認是哪隻貓咪\n可以再拍一張嗎?"
                        }
                    ]
                    replyMessage(payload)
    return 'OK'  # 驗證 Webhook 使用，不能省略


# 回傳訊息功能
def replyMessage(payload):
    response = requests.post('https://api.line.me/v2/bot/message/reply', headers=HEADER, json=payload)
    return 'OK'


# template 訊息: 選擇拍照/挑選照片
def openCamera():
    message = {
        "type": "template",
        "altText": "拍張猴硐貓村的貓咪貓咪照吧~",
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
def get_user_content(message_id):
    res = requests.get(f'https://api-data.line.me/v2/bot/message/{message_id}/content', headers=HEADER)
    message_content = res.content

    local_save = './static/user_cats_photo/' + message_id + '.jpg'
    with open(local_save, 'wb') as fd:
        for chunk in res.iter_content():
            fd.write(chunk)
    return local_save


# 這隻貓叫作什麼名字(進detect.py)
def whatscat(local_save, userId):
    with open('detect_args.json', newline='') as jsonfile:  # 載入需要餵進detect.py的Json參數
        opt = json.load(jsonfile)
        opt["source"] = local_save
        try:
            result, result_img_path = detect(opt)  # 呼叫detect.py detect功能
            if result:
                label_name = result[:-5]
        except:  # 回傳不能辨認
            label_name = ""

        return label_name


# FlexMessage 貓咪卡片
def flexmessage(cat_name):
    flex_contents = f"./flexmessage_template/{cat_name}_flexmessage.json"
    with open(flex_contents, 'rb') as f:
        contents = json.load(f)
        message = dict()
        message = {
            "type": "flex",
            "altText": "猴硐貓村附近景點推薦給您~",
            "contents": contents
        }
        return message


# 貓咪偵測框選結果照片
def reply_detect_img(end_point, message_id):
    message = {
        "type": "image",
        "originalContentUrl": end_point + "/static/result_photo/" + message_id + ".jpg",
        "previewImageUrl": end_point + "/static/result_photo/" + message_id + ".jpg"
    }
    return message


# 登入用戶資料到mongoDB
def db_landing_user(userId):
    cats_dict = dict()
    db = myclient["meow_cat_data"]

    cursor = db.user_test3.find({"_id": userId})

    x = dict()
    for i in cursor:
        x.update(i)

    if not x:
        try:
            print("查不到這個用戶, 所以新增此用戶")
            db.user_test3.insert_one({"_id": userId})
            for x in db.cat_data.find({}, {"name": 1}):
                print(x["name"])
                cats_dict[x["name"]] = False
            print(cats_dict)
            myquery = {"_id": userId}
            newvalues = {"$set": cats_dict}
            db.user_test3.update_one(myquery, newvalues)
            cursor = db.user_test3.find()
            print(list(cursor))
        except:
            print("error無法新增這個新用戶")
    else:
        print("此用戶之前新增過, 所以不用再新增")
        pass


# 更新貓咪收集情況
def db_update_collection(cat_name, userId):
    db = myclient["meow_cat_data"]
    cursor = db.user_test3.find({"_id": userId})
    x = dict()
    for i in cursor:
        x.update(i)

    if x:
        cat_dict = {cat_name: True}
        myquery = {"_id": userId}
        newvalues = {"$set": cat_dict}
        db.user_test3.update_one(myquery, newvalues)


# 查詢mongoDB貓咪收集情況
def db_user_collection(userId):
    global StrF  # 用戶尚未收集的貓咪
    db = myclient["meow_cat_data"]
    cursor = db.user_test3.find({"_id": userId})
    x = dict()
    T_cats = []  # 已收集的貓咪
    F_cats = []  # 未收集的貓咪
    StrT = ""
    StrF = ""  # 每次先清空上次的查詢在更新

    for i in cursor:
        x.update(i)

    if x:  # 查詢此用戶的收集情況 新用戶T_cats為空
        for key, value in x.items():
            if str(value) == "True":
                T_cats.append(key)
            elif str(value) == "False":
                F_cats.append(key)
            else:
                pass

        for i in T_cats:  # T_cats轉字串做✅修飾
            StrT += "✅  " + str(i) + "\n"

        for i in F_cats:
            StrF += "🔰 " + str(i) + "\n"

        if not T_cats:  # 新用戶第先按"收集貓貓"的回應
            message = [
                {
                    "type": "text",
                    "text": "打開相機開始收集吧~。📸"
                },
                {
                    "type": "text",
                    "text": "小提示😆小貓咪們都在圈圈處🐈"
                },
                {
                    "type": "image",
                    "originalContentUrl": end_point + "/static/element/" + "cats_map.jpg",
                    "previewImageUrl": end_point + "/static/element/" + "cats_map.jpg"
                }
            ]
            return message

        elif len(T_cats) == 22:
            message = [
                {
                    "type": "text",
                    "text": "🎉🎉🎉🎉🎉🎉\n您太厲害了!所有貓咪們都收集完了🎉🎉🎉🎉🎉🎉"
                }
            ]
            return message

        if T_cats:  # 舊用戶回應"收集貓貓"
            message = [
                {
                    "type": "text",
                    "text": "您已收集到的貓咪🐈:\n\n" + StrT
                },
                {
                    "type": "text",
                    "text": f"還有🐈{len(F_cats)}隻貓咪\n尚未收集到😅"
                },
                {
                    "type": "image",
                    "originalContentUrl": end_point + "/static/element/" + "cats_map.jpg",
                    "previewImageUrl": end_point + "/static/element/" + "cats_map.jpg"
                },
                {
                    "type": "template",
                    "altText": "This is a buttons template",
                    "template": {
                        "type": "buttons",
                        "text": "查詢尚未收集到的貓咪們🐈",
                        "actions": [
                            {
                                "type": "message",
                                "label": "查詢貓咪們",
                                "text": "查詢尚未收集到的貓咪們"
                            }
                        ]
                    }
                }
            ]
            return message


if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0', 5000, debug=True)