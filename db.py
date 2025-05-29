from pymongo import MongoClient

from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_database(Config.MONGO_DB)
anime_db = client.get_database(Config.MONGO_ANIME_DB)

anime_mapping = anime_db.get_collection(Config.MONGO_ANIME_MAP)
