import os
from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
import pprint
from appserver.controller.userController import UserResource
from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.monitor.monitor import monitor_controller

app = Flask(__name__)


# Mongo DB config
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://database:27017/applicationServerDB"
app.config['MONGO_URI'] = MONGO_URL
mongoDB = PyMongo(app)



api = Api(app)
api.add_resource(UserResource, '/user/')

LOGGER = LoggerFactory.get_logger(__name__)


class Configuration(object):
    def get_database(self):
        return mongoDB.db


app.register_blueprint(monitor_controller)

@app.route('/')
@monitor
def hello_world():
    LOGGER.info('Logging info before setting into database')
    mongoDB.db.collection.insert({"key":"value"})
    return 'Inserted key value!'


@app.route('/get')
def getValues():
    pprint.pprint(mongoDB.db.collection.find_one())

    return pprint.pformat(mongoDB.db.collection.find_one())

