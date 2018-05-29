import os
from flask_pymongo import PyMongo
from redis import Redis
from dotenv import load_dotenv, find_dotenv

class Configuration(object):
    def set_up_environment(self):
        is_dev = os.environ.get('DEVELOPMENT', None)
        if is_dev:
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

    def set_up_redis(self):
        return Redis(host=os.getenv("REDIS_HOST"), port=6379)

    def get_shared_server_host_url():
        return os.getenv("SHARED_SERVER_HOST")

    def get_server_user():
        return os.getenv("SERVER_USER")

    def get_server_password():
        return os.getenv("SERVER_PASSWORD")
