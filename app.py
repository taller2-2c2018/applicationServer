from flask import Flask
from pymongo import MongoClient
import pprint

mongoClient = MongoClient('localhost', 27017)
dataBase = mongoClient.applicationServerDB
table = dataBase.table

app = Flask(__name__)


@app.route('/')
def hello_world():
    app.logger.info('Logging info before setting into database')
    table.insert({"key":"value"})
    return 'Inserted key value!'

@app.route('/get')
def getValues():
    got_table = table.find({"key":"value"})
    got_table_index_zero = got_table[0]
    pprint.pprint(table.find_one())
    table_string = str(got_table)

    app.logger.warn('%s', table_string)
    return pprint.pformat(table.find_one())



if __name__ == '__main__':
    app.run()
