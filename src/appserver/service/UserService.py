from appserver.validator.jsonValidator import JsonValidator
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.repository.userRepository import UserRepository
from appserver.repository.friendshipRepository import FriendshipRepository
from appserver.logger import LoggerFactory
from appserver.datastructure.ApplicationResponse import ApplicationResponse

LOGGER = LoggerFactory().get_logger('UserService')


class UserService(object):
    @staticmethod
    def register_new_user(request_json):
        validation_response = JsonValidator.validate_user_authenticate(request_json)
        if validation_response.hasErrors:
            return validation_response.message
        LOGGER.info("Json is valid.")
        shared_server_response = SharedServer.register_user(request_json)
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
        validation_response = JsonValidator.validate_user_friendship_get(request_header)
        if validation_response.hasErrors:
            return validation_response.message
        username = request_header["mUsername"]
        friendship_list = FriendshipRepository.get_friendship_requests_of_username(username)
        return ApplicationResponse.get_success(friendship_list)
