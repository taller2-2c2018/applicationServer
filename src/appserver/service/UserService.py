from appserver.validator.jsonValidator import JsonValidator
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.repository.userRepository import UserRepository
from appserver.repository.friendshipRepository import FriendshipRepository


class UserService(object):
    @staticmethod
    def register_new_user(request_json):
        validation_response = JsonValidator.validate_user_authenticate(request_json)
        if validation_response.hasErrors:
            return validation_response.message
        shared_server_response = SharedServer.registerUser(request_json)
        shared_server_response_validation = JsonValidator.validate_shared_server_register_user(shared_server_response)
        if shared_server_response_validation.hasErrors:
            return shared_server_response_validation.message
        UserRepository.insert(request_json)
        return shared_server_response

    @staticmethod
    def authenticate_user(request_json):
        validation_response = JsonValidator.validate_user_authenticate(request_json)
        if validation_response.hasErrors:
            return validation_response.message
        return SharedServer.authenticate_user(request_json)

    @staticmethod
    def send_user_friendship_request(request_json):
        validation_response = JsonValidator.validate_user_friendship(request_json)
        if validation_response.hasErrors:
            return validation_response.message
        FriendshipRepository.insert(request_json)
        return "The request has been sent successfully"

