from flask_restful import Api
from redis import Redis
from . import app
from appserver.controller.userRegisterController import UserRegisterResource
from appserver.controller.userAuthenticateController import UserAuthenticateResource
from appserver.controller.userFriendshipController import UserFriendshipResource
from appserver.controller.userFriendshipAcceptController import UserFriendshipAcceptResource
from appserver.controller.userProfileController import UserProfileResource
from appserver.controller.storyController import storiesEndpoint
from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor_controller

api = Api(app)
api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserAuthenticateResource, '/user/authenticate')
api.add_resource(UserFriendshipResource, '/user/friendship')
api.add_resource(UserFriendshipAcceptResource, '/user/friendship/accept/<username>')
api.add_resource(UserProfileResource, '/user/profile', '/user/profile/<username>')
app.register_blueprint(storiesEndpoint, url_prefix="/story")
# Redis config
redis = Redis(host='redis', port=6379)
app.register_blueprint(monitor_controller)
LOGGER = LoggerFactory.get_logger(__name__)
database = app.database

