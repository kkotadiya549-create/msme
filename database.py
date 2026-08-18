import os
from motor.motor_asyncio import AsyncIOMotorClient

client = None
db = None

def connect_db():
    global client, db
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        print("CRITICAL ERROR: MONGODB_URI not found.")
        return
    client = AsyncIOMotorClient(uri)
    db = client.get_database() # Uses database name from URI

def get_db():
    return db
