from flask import request, Blueprint

from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.service.UserService import UserService

LOGGER = LoggerFactory().get_logger('userController')
userEndpoint = Blueprint('userEndpoint', __name__)


@userEndpoint.route("/register", methods=['POST'])
@monitor
def register_user():
    LOGGER.info('Registering a new user')
    request_json = request.get_json()
    return_value = UserService().register_new_user(request_json)
    return return_value


@userEndpoint.route("/authenticate", methods=['POST'])
@monitor
def authenticate_user():
    LOGGER.info('Authenticating user')
    request_json = request.get_json()
    return_value = UserService().authenticate_user(request_json)
    return return_value


@userEndpoint.route("/friendship", methods=['POST'])
@monitor
def send_friendship():
    LOGGER.info('Sending new friendship request')
    request_json = request.get_json()
    return_value = UserService().send_user_friendship_request(request_json)
    return return_value


@userEndpoint.route("/friendship", methods=['GET'])
@monitor
def get_friendship_requests_for_user():
    LOGGER.info('Getting all requests for given user')
    request_header = request.headers
    return_value = UserService().get_friendship_requests(request_header)
    return return_value
