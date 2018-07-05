from flask import request, Blueprint

from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.validator.authValidator import secure
from appserver.service.UserService import UserService
from appserver.controller.ControllerAuditory import controller_auditory

LOGGER = LoggerFactory().get_logger('userController')
userEndpoint = Blueprint('userEndpoint', __name__)


@userEndpoint.route('/register', methods=['POST'])
@monitor
@controller_auditory
def register_user():
    LOGGER.info('Registering a new user')
    request_json = request.get_json()
    return_value = UserService().register_new_user(request_json)
    return return_value


@userEndpoint.route('/authenticate', methods=['POST'])
@monitor
@controller_auditory
def authenticate_user():
    LOGGER.info('Authenticating user')
    request_json = request.get_json()
    return_value = UserService().authenticate_user(request_json)
    return return_value


@userEndpoint.route('/friendship', methods=['POST'])
@monitor
@secure
@controller_auditory
def send_friendship():
    LOGGER.info('Sending new friendship request')
    request_json = request.get_json()
    request_header = request.headers
    return_value = UserService().send_user_friendship_request(request_json, request_header)
    return return_value


@userEndpoint.route('/friendship', methods=['GET'])
@monitor
@secure
@controller_auditory
def get_friendship_requests_for_user():
    LOGGER.info('Getting all requests for given user')
    request_header = request.headers
    return_value = UserService().get_friendship_requests(request_header)
    return return_value


@userEndpoint.route('/friends', methods=['GET'])
@monitor
@secure
@controller_auditory
def get_user_friends():
    LOGGER.info('Getting all friends of given user')
    request_header = request.headers
    return_value = UserService().get_user_friends(request_header)
    return return_value


@userEndpoint.route('/friendship/accept/<facebook_user_id>', methods=['POST'])
@monitor
@secure
@controller_auditory
def accept_user_friendship(facebook_user_id):
    LOGGER.info('Accepting friendship request')
    request_header = request.headers
    return_value = UserService().accept_friendship_request(request_header, facebook_user_id)
    return return_value


@userEndpoint.route('/friendship/reject/<facebook_user_id>', methods=['POST'])
@monitor
@secure
@controller_auditory
def reject_user_friendship(facebook_user_id):
    LOGGER.info('Rejecting friendship request')
    request_header = request.headers
    return_value = UserService().reject_friendship_request(request_header, facebook_user_id)
    return return_value


@userEndpoint.route('/profile', methods=['POST', 'PUT'])
@monitor
@secure
@controller_auditory
def modify_user_profile():
    LOGGER.info('Adding new profile to user')
    request_json = request.get_json()
    request_header = request.headers
    return_value = UserService().modify_user_profile(request_json, request_header)
    return return_value


@userEndpoint.route('/profilePictureStream', methods=['POST', 'PUT'])
@monitor
@secure
@controller_auditory
def modify_user_profile_picture():
    LOGGER.info('Adding new profile picture to user by stream')
    return_value = UserService().modify_user_profile_picture(request)
    return return_value


@userEndpoint.route('/profilePicture', methods=['POST', 'PUT'])
@monitor
@secure
@controller_auditory
def modify_user_profile_picture_json():
    LOGGER.info('Adding new profile picture to user')
    headers = request.headers
    file_json = request.get_json()
    return_value = UserService().modify_user_profile_picture_json(headers, file_json)
    return return_value


@userEndpoint.route('/profile/<facebook_user_id>', methods=['GET'])
@monitor
@secure
@controller_auditory
def get_user_profile(facebook_user_id):
    LOGGER.info('Getting profile of ' + facebook_user_id)
    return_value = UserService().get_user_profile(request, facebook_user_id)
    return return_value


@userEndpoint.route('/list', methods=['GET'])
@monitor
@secure
@controller_auditory
def get_user_list():
    LOGGER.info('Getting all users')
    return_value = UserService().get_user_list(request.headers)
    return return_value
