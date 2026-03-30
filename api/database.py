from mongoengine import connect
import os


def connect_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/corAI_database")
    connect(host=mongo_uri)
