import pymongo
import urllib.parse
import configparser

from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
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



line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))  # 確認 token 是否正確
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))  # 確認 secret 是否正確
my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}



username = urllib.parse.quote_plus(config.get("mongodb-atlas", "username"))
password = urllib.parse.quote_plus(config.get("mongodb-atlas", "password"))
myclient = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")

user_collection = {}
temp_userid = ""





@app.route("/", methods=['POST', 'GET'])
def linebot():
    body = request.json                                   # body data type 是 dict
    # print(body)
    # print(type(body))
    events = body["events"]
    # print(events)
    payload = dict()
    replyToken = events[0]['replyToken']
    payload['replyToken'] = replyToken                   # 常用的變數 ->存在payload字典
    message = events[0]['message']
    # print(f'id---->{message["id"]}')

    if events[0]["type"] == "message":
        if message["type"] == "image":                    # 如果用戶傳照片
            local_save = saveimg(message['id'])           # 呼叫存照片功能得到照片儲存路徑
            whatscat(local_save, replyToken, message['id'])

    return 'OK'                                           # 驗證 Webhook 使用，不能省略




def saveimg(message_id):
    SendImage = line_bot_api.get_message_content(message_id)
    local_save = './static/' + message_id + '.jpg'
    with open(local_save, 'wb') as file:
        for chenk in SendImage.iter_content():
            file.write(chenk)
    return local_save



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
        cat_data = gomongodb(cat_name)
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
