from appserver.datastructure.validationResponse import ValidationResponse
from appserver.logger import LoggerFactory


LOGGER = LoggerFactory().get_logger('JsonValidator')


class JsonValidator(object):

    @staticmethod
    def validate_user_authenticate(json):
        LOGGER.info("Validating user authentication json.")
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity(json, "username", validation_response)
        validation_response = JsonValidator.__check_validity(json, "password", validation_response)
        validation_response = JsonValidator.__check_validity(json, "facebookAuthToken", validation_response)

        return validation_response

    @staticmethod
    def validate_user_friendship_post(json):
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity(json, "mRequesterUsername", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mTargetUsername", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mDescription", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mPicture", validation_response)

        return validation_response

    @staticmethod
    def validate_profile_datafields(json):
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity(json, "mFirstName", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mLastName", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mBirthDate", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mPicture", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mFacebookUrl", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mSex", validation_response)

        return validation_response

    @staticmethod
    def validate_story_datafields(json):
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity(json, "mTitle", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mDescription", validation_response)
        validation_response = JsonValidator.__check_validity(json, "mPicture", validation_response)

        return validation_response

    @staticmethod
    def validate_header_has_username(json):
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity(json, "mUsername", validation_response)

        return validation_response

    @staticmethod
    def __check_validity(json, field_name, validation_response):
        if field_name not in json or json[field_name] is '':
            validation_response.message += "Json must have " + field_name + " field and must not be empty. "
            validation_response.hasErrors = True
        return validation_response

    @staticmethod
    def validate_shared_server_register_user(shared_server_response):
        LOGGER.info("Validating shared server response:" + shared_server_response.text)
        status_code = shared_server_response.status_code
        if status_code == 200 or status_code == 201:
            return ValidationResponse(False)
        return ValidationResponse(True, "Failed the communication with shared server user registration. "
                                        "Got a status code: " + str(status_code))
