from flask_restful import Api

from appserver.controller.storyController import storiesEndpoint
from appserver.controller.userController import userEndpoint
from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor_controller
from . import app

api = Api(app)
app.register_blueprint(userEndpoint, url_prefix='/user')
app.register_blueprint(storiesEndpoint, url_prefix='/story')
app.register_blueprint(monitor_controller)
LOGGER = LoggerFactory.get_logger(__name__)
database = app.database

