from flask_restful import Api
import pprint
from . import app
from appserver.controller.userController import UserResource
from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.monitor.monitor import monitor_controller

api = Api(app)
api.add_resource(UserResource, '/user/')
app.register_blueprint(monitor_controller)
LOGGER = LoggerFactory.get_logger(__name__)
collection = app.database.collection


@app.route('/')
@monitor
def hello_world():
    LOGGER.info('Logging info before setting into database')
    collection.insert({"key": "value"})
    return 'Inserted key value!'


@app.route('/get')
@monitor
def getValues():
    pprint.pprint(collection.find_one())
    return pprint.pformat(collection.find_one())
