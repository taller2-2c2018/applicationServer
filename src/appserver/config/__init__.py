import os
from flask_pymongo import PyMongo
from redis import Redis
from dotenv import load_dotenv, find_dotenv
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger('ConfigurationInit')


class Configuration(object):
    def set_up_environment(self):
        is_dev = os.environ.get('DEVELOPMENT', None)
        if is_dev:
            LOGGER.info('Loading environment variables from .env files')
            load_dotenv(find_dotenv())

    def set_up_mongodb(self, app):
        # Mongo DB config
        MONGO_URL = os.environ.get('MONGO_URL')
        if not MONGO_URL:
            MONGO_URL = "mongodb://database:27017/applicationServerDB"
            # TODO remove this and find a better way to test with db also we need to run 'sudo mongod' before tests
            # MONGO_URL = "mongodb://localhost:27017/"
        app.config['MONGO_URI'] = MONGO_URL
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
        return os.getenv("SHARED_SERVER_HOST")

    @staticmethod
    def get_server_user():
        return os.getenv("SERVER_USER")

    @staticmethod
    def get_server_password():
        return os.getenv("SERVER_PASSWORD")

    @staticmethod
    def get_server_password():
        return os.getenv("SERVER_PASSWORD")

    @staticmethod
    def get_android_app_token():
        return os.getenv("ANDROID_APP_TOKEN")
