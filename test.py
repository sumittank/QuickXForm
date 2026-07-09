from pymongo import MongoClient

uri = ""

client = MongoClient(uri)

try:
    client.admin.command("ping")
    print("Connected!")
except Exception as e:
    print(e)