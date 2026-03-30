from mongoengine import connect

def connect_db():
    connect(
            db = "corAI_database",
            host = "mongodb://localhost:27017/corAI_database"
            )
