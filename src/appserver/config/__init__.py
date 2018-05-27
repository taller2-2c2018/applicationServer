import os
from flask_pymongo import PyMongo
from redis import Redis


class Configuration(object):
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
        return Redis(host='redis', port=6379)
