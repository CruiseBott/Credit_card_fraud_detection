from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client["fraud_detection"]
users = db["users"]
transactions = db["transactions"]
contact_collection = db["contact"]
