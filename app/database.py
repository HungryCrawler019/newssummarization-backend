from pymongo import mongo_client
from dotenv import load_dotenv
import os

load_dotenv()

client = mongo_client.MongoClient(
    os.getenv('DATABASE_URL'), serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect to the MongoDB server.")

db = client[os.getenv('MONGO_INITDB_DATABASE')]