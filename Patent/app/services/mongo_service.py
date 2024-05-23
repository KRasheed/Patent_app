import os
from pymongo import MongoClient


def get_mongo_connection():
    client = MongoClient(os.environ["MONGO_URI"])
    return client["kofi-aninakwa"]


def close_mongo_connection(client):
    client.close()
