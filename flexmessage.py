import json

import os,sys
cat_name = str('meowmeow')

json_path = "flexmessage_template/跩哥Malfoy_flexmessage.json"  #讀取貓咪的flex message 的樣式
json_path1= f'C:\Python_class\LINEBOT_GUESSWHO\{cat_name}cat_flexmessage2.json' #準備一個放新的樣式的路徑

dict={} #先準備一個放修改好的資料的字典

def get_json_data(json_path):
    with open(json_path,'rb') as f:
        message = json.load(f)
        body_message = message["body"]["contents"]
        content_message =body_message[1]['contents']
        attack_content_message = content_message[0]['contents']
        icon_list = [{'type': 'icon', 'url': 'https://i.imgur.com/VckcSY0.png'}]
        for i in range(2): #改成 貓咪的各個數值
            attack_content_message += icon_list
            i+=1
        content_message[0]['contents']=attack_content_message         # 0 攻擊力
        dict = message
    f.close()
    return dict

def write_json_data(dict):
    with open(json_path1,'w') as r:
        json.dump(dict,r)
    r.close()

the_revised_dict = get_json_data(json_path)
write_json_data(the_revised_dict)