import os
from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
from .controller.userController import UserResource
import pprint
from appserver.logger import LoggerFactory

MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017/applicationServerDB"

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URL
mongoDB = PyMongo(app)
api = Api(app)
api.add_resource(UserResource, '/user/')
LOGGER = LoggerFactory.get_logger(__name__)


class Configuration(object):
    def get_database(self):
        return mongoDB.db


@app.route('/')
def hello_world():
    LOGGER.info('Logging info before setting into database')
    mongoDB.db.collection.insert({"key":"value"})
    return 'Inserted key value!'


@app.route('/get')
def getValues():
    pprint.pprint(mongoDB.db.collection.find_one())

    return pprint.pformat(mongoDB.db.collection.find_one())


if __name__ == '__main__':
    app.run()
