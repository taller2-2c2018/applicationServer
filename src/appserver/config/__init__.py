import os
from flask_pymongo import PyMongo


class Configuration(object):
    def set_up_mongodb(self, app):
        # Mongo DB config
        MONGO_URL = os.environ.get('MONGO_URL')
        if not MONGO_URL:
            MONGO_URL = "mongodb://database:27017/applicationServerDB"
        app.config['MONGO_URI'] = MONGO_URL
        return PyMongo(app)
