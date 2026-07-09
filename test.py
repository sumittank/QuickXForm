from pymongo import MongoClient

uri = "mongodb+srv://sumittank77756_db_user:1Z3lYz3H5MudMseY@cluster0.ezg0jgd.mongodb.net/?appName=Cluster0"

client = MongoClient(uri)

try:
    client.admin.command("ping")
    print("Connected!")
except Exception as e:
    print(e)