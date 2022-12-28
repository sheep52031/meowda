import io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import json


CLASSES = [
'躲貓貓Hide_and_Seek','麻糬Mochi','跩哥Malfoy','瞌睡蟲Sleepy','小孤獨Lonely','阿虎Tiger','豆花Douhua','小花Flower','美女Prettygirl','膽小鬼Coward','小妖豔Shower','小淘氣Player','小煤炭Soot_Spirits','傑克Jack','麒麟Kirin','熊貓Panda','站長Station_Master','萱萱Xuan_Xuan','跳跳虎Jumping_Tiger','沃卡萊姆Vodka_Lime','馬丁尼Martini','莫希托Mojito']

url = "http://localhost:8000/predict"


with open("./test2.jpg", "rb") as image_file:        
    files = {'file': image_file}
    res = requests.post(url, files=files, stream=True)  
    pred = np.asarray(json.loads(res.json()))
    image_file.seek(0)
    image = Image.open(io.BytesIO(image_file.read()))
    

    # 畫出偵測結果框選圖片
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("simsun.ttc", 80, encoding="unic")  # 设置字体
    for x1, y1, x2, y2, conf, class_id in pred:                   # 看class_id決定第幾個標籤得到貓咪分類
        text = f"{CLASSES[int(class_id)]}  {conf:.2f}"         
        draw.rectangle(((x1-20, y1-10), (x2+20, y2+10)), outline='blue', width=15)
        draw.rectangle(((x1, y1+5), (x1+1000, y1+100)), fill='yellow')
        draw.text((x1+10, y1+10), text, fill ="red", font = font, align ="right")

    # image_bytes = io.BytesIO()
    # image.save(image_bytes, format='PNG')
    # image_bytes = image_bytes.getvalue()

    image.show()




