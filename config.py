import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuration class
    """
    JSON_SORT_KEYS = False
    FLASK_HOST = os.getenv('FLASK_RUN_HOST', "localhost")
    FLASK_PORT = os.getenv('FLASK_RUN_PORT', "5000")
    SECRET_KEY = os.getenv('SECRET_KEY', "this is not a secret key")
    COMPRESS_ALGORITHM = ['gzip']
    COMPRESS_BR_LEVEL = 4
    DEBUG = os.getenv('FLASK_DEBUG', False)

    MONGO_URI = os.getenv('MONGO_URI', "")
    MONGO_DB = os.getenv('MONGO_DB', "")
    MONGO_ANIME_DB = os.getenv('MONGO_ANIME_DATABASE', "")
    MONGO_ANIME_MAP = os.getenv('MONGO_ANIME_MAP_COLLECTION', "")
