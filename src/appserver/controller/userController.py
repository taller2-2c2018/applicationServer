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
