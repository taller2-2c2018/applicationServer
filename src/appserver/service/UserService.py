import json

from appserver.validator.jsonValidator import JsonValidator
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.externalcommunication.facebook import Facebook
from appserver.repository.userRepository import UserRepository
from appserver.repository.friendshipRepository import FriendshipRepository
from appserver.logger import LoggerFactory
from appserver.datastructure.ApplicationResponse import ApplicationResponse
from bson.json_util import dumps


LOGGER = LoggerFactory().get_logger('UserService')


class UserService(object):
    @staticmethod
    def register_new_user(request_json):
        validation_response = JsonValidator.validate_user_authenticate(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)
        LOGGER.info("Register user Json is valid")

        facebook_token_is_valid = Facebook.user_token_is_valid(request_json)
        if not facebook_token_is_valid:
            return ApplicationResponse.bad_request(message='Invalid Facebook credentials')
        LOGGER.info("Facebook user token is valid")

        Facebook.get_user_identification(request_json)

        shared_server_response = SharedServer.register_user(request_json)
        LOGGER.info("Response from shared server: " + str(shared_server_response))
        shared_server_response_validation = JsonValidator.validate_shared_server_register_user(shared_server_response)
        if shared_server_response_validation.hasErrors:
            return ApplicationResponse.bad_request(message=shared_server_response_validation.message)
        UserRepository.insert(request_json)
        return ApplicationResponse.created(message='Created user successfully')

    @staticmethod
    def authenticate_user(request_json):
        validation_response = JsonValidator.validate_user_authenticate(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        facebook_token_is_valid = Facebook.user_token_is_valid(request_json)
        if not facebook_token_is_valid:
            return ApplicationResponse.bad_request(message='Invalid Facebook credentials')
        LOGGER.info("Facebook user token is valid")

        response = SharedServer.authenticate_user(request_json)
        LOGGER.info("Response gotten from server: " + str(response))

        shared_server_response_validation = JsonValidator.validate_shared_server_authorization(response)
        if shared_server_response_validation.hasErrors:
            return ApplicationResponse.bad_request(message=shared_server_response_validation.message)

        data = response["data"]
        facebook_id = data["facebook_id"]
        token = data["token"]
        expires_at = data["expires_at"]
        UserRepository.update_user_token(facebook_id, token, expires_at)
        response = {'message': 'Logged in successfully.', 'token': token}
        response_json = json.dumps(response)
        return ApplicationResponse.success(data=response_json)

    @staticmethod
    def send_user_friendship_request(request_json):
        validation_response = JsonValidator.validate_user_friendship_post(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)
        target_username = request_json["mTargetUsername"]
        if UserRepository.username_exists(target_username):
            FriendshipRepository.insert(request_json)
            return ApplicationResponse.success(message='Friendship request sent successfully')
        return ApplicationResponse.bad_request(message='Target username doesn\'t exist')

    @staticmethod
    def get_friendship_requests(request_header):
        validation_response = JsonValidator.validate_header_has_username(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)
        username = request_header["mUsername"]
        friendship_list = FriendshipRepository.get_friendship_requests_of_username(username)
        return ApplicationResponse.success(data=friendship_list)

    @staticmethod
    def accept_friendship_request(request_header, target_user):
        validation_response = JsonValidator.validate_header_has_username(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)
        user_that_accepts_friendship = request_header["mUsername"]
        if FriendshipRepository.friendship_exists(user_that_accepts_friendship, target_user):
            FriendshipRepository.accept_friendship(user_that_accepts_friendship, target_user)
            UserRepository.add_friendship(user_that_accepts_friendship, target_user)
            return ApplicationResponse.success(message='Friendship was accepted successfully')
        return ApplicationResponse.bad_request(message='Friendship request couldn\'t be found')

    @staticmethod
    def create_user_profile(request_json, request_header):
        validation_response = JsonValidator.validate_header_has_username(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)
        validation_response = JsonValidator.validate_profile_datafields(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)
        username = request_header["mUsername"]
        UserRepository.create_profile(username, request_json)

        return ApplicationResponse.created(message='Created profile successfully')

    @staticmethod
    def get_user_profile(username):
        profile = UserRepository.get_profile(username)

        return ApplicationResponse.success(data=dumps(profile))
