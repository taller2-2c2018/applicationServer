from appserver.datastructure.validationResponse import ValidationResponse
from appserver.logger import LoggerFactory


LOGGER = LoggerFactory().get_logger('JsonValidator')


class JsonValidator(object):

    @staticmethod
    def validate_user_authenticate(json):
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity(json, "username", validation_response)
        validation_response = JsonValidator.__check_validity(json, "password", validation_response)
        validation_response = JsonValidator.__check_validity(json, "facebookAuthToken", validation_response)

        return validation_response

    @staticmethod
    def validate_user_friendship(json):
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity(json, "requesterUser", validation_response)
        validation_response = JsonValidator.__check_validity(json, "targetUser", validation_response)

        return validation_response

    @staticmethod
    def __check_validity(json, field_name, validation_response):
        if field_name not in json or json[field_name] is '':
            validation_response.message += "Json must have " + field_name + " field and must not be empty. "
            validation_response.hasErrors = True
        return validation_response

    @staticmethod
    def validate_shared_server_register_user(shared_server_response):
        # TODO validate shared server register user response
        return ValidationResponse(False)
