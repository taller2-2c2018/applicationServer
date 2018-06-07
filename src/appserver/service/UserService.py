from appserver.validator.jsonValidator import JsonValidator
from appserver.externalcommunication.sharedServer import SharedServer
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
            return validation_response.message
        LOGGER.info("Register user Json is valid.")
        shared_server_response = SharedServer.register_user(request_json)
        LOGGER.info("Response from shared server: " + str(shared_server_response))
        shared_server_response_validation = JsonValidator.validate_shared_server_register_user(shared_server_response)
        if shared_server_response_validation.hasErrors:
            return shared_server_response_validation.message
        UserRepository.insert(request_json)
        return ApplicationResponse.get_created("Created user successfully")

    @staticmethod
    def authenticate_user(request_json):
        validation_response = JsonValidator.validate_user_authenticate(request_json)
        if validation_response.hasErrors:
            return validation_response.message
        response = SharedServer.authenticate_user(request_json)
        LOGGER.info("Response gotten from server: " + str(response))
        token = response["token"]
        user = request_json["username"]
        UserRepository.update_user_token(user, token)
        return ApplicationResponse.get_success("Logged in successfully. Token: " + token["token"])

    @staticmethod
    def send_user_friendship_request(request_json):
        validation_response = JsonValidator.validate_user_friendship_post(request_json)
        if validation_response.hasErrors:
            return validation_response.message
        target_username = request_json["mTargetUsername"]
        if UserRepository.username_exists(target_username):
            FriendshipRepository.insert(request_json)
            return ApplicationResponse.get_success("Friendship request sent successfully")
        return ApplicationResponse.get_bad_request("Target username doesn't exist")

    @staticmethod
    def get_friendship_requests(request_header):
        validation_response = JsonValidator.validate_header_has_username(request_header)
        if validation_response.hasErrors:
            return validation_response.message
        username = request_header["mUsername"]
        friendship_list = FriendshipRepository.get_friendship_requests_of_username(username)
        return ApplicationResponse.get_success(friendship_list)

    @staticmethod
    def accept_friendship_request(request_header, target_user):
        validation_response = JsonValidator.validate_header_has_username(request_header)
        if validation_response.hasErrors:
            return validation_response.message
        user_that_accepts_friendship = request_header["mUsername"]
        if FriendshipRepository.friendship_exists(user_that_accepts_friendship, target_user):
            FriendshipRepository.accept_friendship(user_that_accepts_friendship, target_user)
            UserRepository.add_friendship(user_that_accepts_friendship, target_user)
            return ApplicationResponse.get_success("Friendship was accepted successfully")
        return ApplicationResponse.get_bad_request("Friendship request couldn't be found")

    @staticmethod
    def create_user_profile(request_json, request_header):
        validation_response = JsonValidator.validate_header_has_username(request_header)
        if validation_response.hasErrors:
            return validation_response.message
        validation_response = JsonValidator.validate_profile_datafields(request_json)
        if validation_response.hasErrors:
            return validation_response.message
        username = request_header["mUsername"]
        UserRepository.create_profile(username, request_json)

        return ApplicationResponse.get_created("Created profile successfully")

    @staticmethod
    def get_user_profile(username):
        profile = UserRepository.get_profile(username)

        return ApplicationResponse.get_success(dumps(profile))
