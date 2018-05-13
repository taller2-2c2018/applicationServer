from flask_restful import Api
from . import app
from appserver.controller.userRegisterController import UserRegisterResource
from appserver.controller.userAuthenticateController import UserAuthenticateResource
from appserver.controller.userFriendshipController import UserFriendshipResource
from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor_controller

api = Api(app)
api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserAuthenticateResource, '/user/authenticate')
api.add_resource(UserFriendshipResource, '/user/friendship')
app.register_blueprint(monitor_controller)
LOGGER = LoggerFactory.get_logger(__name__)
collection = app.database.collection

