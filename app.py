import os
from flask import Flask
from pymongo import MongoClient
from flask_pymongo import PyMongo
import pprint

MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017/applicationServerDB"

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URL
mongoDB = PyMongo(app)

mongoClient = MongoClient('localhost', 27017)
dataBase = mongoClient.applicationServerDB
table = dataBase.table



@app.route('/')
def hello_world():
    app.logger.info('Logging info before setting into database')
    mongoDB.db.collection.insert({"key":"PEPOTE"})
    return 'Inserted key value!'

@app.route('/get')
def getValues():
    got_table = mongoDB.db.collection.find({"key":"value"})
    pprint.pprint(mongoDB.db.collection.find_one())
    table_string = str(got_table)

    app.logger.warn('%s', table_string)
    return pprint.pformat(mongoDB.db.collection.find_one())



if __name__ == '__main__':
    app.run()
