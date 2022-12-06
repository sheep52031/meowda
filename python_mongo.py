import pymongo
import urllib.parse
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
username = urllib.parse.quote_plus(config.get("mongodb-atlas", "username"))
password = urllib.parse.quote_plus(config.get("mongodb-atlas", "password"))

myclient = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")


# myquery = {'name': '麻糬 Mochi'}
# cursor = db.collection.find({}, "name")
# data = list(collection.find(myquery))



userId = "U3f0ce81f0c841994bffc95b23053c492"


cats_dict = dict()
db = myclient["meow_cat_data"]
user_dict = {"_id": userId}

cursor = db.user.find({}, {"_id": userId})

x = dict()
for i in cursor:
    x.update(i)

if not x:
    try:
        db.user.insert_one(user_dict)
        for x in db.cat_data.find({}, {"name": 1}):
            print(x["name"])
            cats_dict[x["name"]] = False
        print(cats_dict)
        myquery = {"_id": userId}
        newvalues = {"$set": cats_dict}
        db.user.update_one(myquery, newvalues)
        cursor = db.user.find()
        print(list(cursor))
    except:
        print("Couldn't insert userID")





def db_update_collection(cat_name, userId):
    db = myclient["meow_cat_data"]
    cursor = db.user.find({}, {cat_name: False})
    x = dict()
    for i in cursor:
        x.update(i)

    if x:
        cat_dict = {cat_name: True}
        myquery = {"_id": userId}
        newvalues = {"$set": cat_dict}
        db.user.update_one(myquery, newvalues)



cat_name = "傑克Jack"

db_update_collection(cat_name, userId)

