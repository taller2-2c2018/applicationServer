from appserver.validator.jsonValidator import JsonValidator
from appserver.externalcommunication.sharedServer import SharedServer


class UserService(object):
    @staticmethod
    def register_new_user(request_json):
        validation_response = JsonValidator.validate_user_authenticate(request_json)
        if validation_response.hasErrors:
            return validation_response.message
        response = SharedServer.registerUser(request_json)
        # TODO here save the user if the registry was successful
        return response

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
        # TODO here save in the database the request
        return "The request has been sent successfully"

