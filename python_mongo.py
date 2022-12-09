import pymongo
import urllib.parse
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
username = urllib.parse.quote_plus(config.get("mongodb-atlas", "username"))
password = urllib.parse.quote_plus(config.get("mongodb-atlas", "password"))

myclient = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")





# 查詢user_test2桶子的所有資料
# db = myclient["meow_cat_data"]
# cursor = db.user_test3.find()
#
# x = dict()
# for i in cursor:
#     x.update(i)
#
# if len(x) != 0:
#     print(x)
# else:
#     print("查不到這筆資料")
    





# # 查詢此user的這支貓咪蒐集情況
# userId = "U3f0ce81f0c841994bffc95b23053c492"
# cat_name = "萱萱Xuan_Xuan"
# db = myclient["meow_cat_data"]
# cursor = db.user_test3.find({"_id": userId})

# x = dict()
# for i in cursor:
#     x.update(i)

# print(x)








# # 刪除user_test2桶子的所有資料
db = myclient["meow_cat_data"]
db.user_test3.delete_many({})

cursor = db.user_test3.find()
x = dict()
for i in cursor:
    x.update(i)
print(x)


























