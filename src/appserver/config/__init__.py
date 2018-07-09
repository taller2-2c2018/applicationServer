import os
from dotenv import load_dotenv, find_dotenv
from flask_pymongo import PyMongo
from redis import Redis

from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger(__name__)


class Configuration(object):
    @staticmethod
    def set_up_environment():
        is_dev = os.environ.get('DEVELOPMENT', None)
        if is_dev:
            LOGGER.info('Loading environment variables from .env files')
            load_dotenv(find_dotenv())

    @staticmethod
    def set_up_mongodb(app):
        # Mongo DB config
        MONGO_URL = os.environ.get('MONGO_URL')
        if not MONGO_URL:
            MONGO_URL = 'mongodb://database:27017/applicationServerDB'
        app.config['MONGO_URI'] = MONGO_URL
        LOGGER.info('Setting up database: ' + str(MONGO_URL))
        return PyMongo(app)

    @staticmethod
    def set_up_redis():
        return Redis(
            host=os.environ.get('REDIS_HOST'),
            port=os.environ.get('REDIS_PORT'),
            password=os.environ.get('REDIS_PWD')
        )

    @staticmethod
    def get_shared_server_host_url():
        return os.getenv('SHARED_SERVER_HOST')

    @staticmethod
    def get_server_user():
        return os.getenv('SERVER_USER')

    @staticmethod
    def get_server_password():
        return os.getenv('SERVER_PASSWORD')

    @staticmethod
    def get_server_password():
        return os.getenv('SERVER_PASSWORD')

    @staticmethod
    def get_android_app_token():
        return os.getenv('ANDROID_APP_TOKEN')

    @staticmethod
    def get_skip_auth():
        return os.getenv('SKIP_AUTH') == 'True'
