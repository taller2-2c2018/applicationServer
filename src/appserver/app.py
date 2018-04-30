import os
from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
import pprint
from appserver.controller.userController import UserResource
from appserver.logger import LoggerFactory
from redis import Redis

app = Flask(__name__)


# Mongo DB config
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://database:27017/applicationServerDB"
app.config['MONGO_URI'] = MONGO_URL
mongoDB = PyMongo(app)

# Redis config
redis = Redis(host='redis', port=6379)


api = Api(app)
api.add_resource(UserResource, '/user/')
LOGGER = LoggerFactory.get_logger(__name__)


class Configuration(object):
    def get_database(self):
        return mongoDB.db


@app.route('/')
def hello_world():
    redis.incr('hits')
    LOGGER.info('Logging info before setting into database')
    mongoDB.db.collection.insert({"key":"value"})
    return 'Inserted key value!'

@app.route('/getHits')
def get_hits():
    return redis.get('hits')

@app.route('/get')
def getValues():
    pprint.pprint(mongoDB.db.collection.find_one())

    return pprint.pformat(mongoDB.db.collection.find_one())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

