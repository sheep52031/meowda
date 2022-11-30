import pymongo
import urllib.parse
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
username = urllib.parse.quote_plus(config.get("mongodb-atlas", "username"))
password = urllib.parse.quote_plus(config.get("mongodb-atlas", "password"))

myclient = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.fv5ng2z.mongodb.net/?retryWrites=true&w=majority")


db = myclient["meow_cat_data"]
collection = db["cat_data"]
myquery = {'name': '麻糬Mochi'}
data = list(collection.find(myquery))
print(data)
