from appserver.datastructure.validationResponse import ValidationResponse
from appserver.logger import LoggerFactory


LOGGER = LoggerFactory().get_logger('JsonValidator')


class JsonValidator(object):

    @staticmethod
    def validate_user_register(json):
        LOGGER.info("Validating user authentication json.")
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity_json(json, "facebookUserId", validation_response)
        validation_response = JsonValidator.__check_validity_json(json, "facebookAuthToken", validation_response)
        return validation_response

    @staticmethod
    def validate_user_authenticate(json):
        LOGGER.info("Validating user authentication json.")
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity_json(json, "facebookUserId", validation_response)
        validation_response = JsonValidator.__check_validity_json(json, "facebookAuthToken", validation_response)

        return validation_response

    @staticmethod
    def validate_user_friendship_post(json):
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity_json(json, "mTargetUsername", validation_response)
        validation_response = JsonValidator.__check_validity_json(json, "mDescription", validation_response)

        return validation_response

    @staticmethod
    def validate_profile_datafields(json):
        if json is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity_json(json, "mFirstName", validation_response)
        validation_response = JsonValidator.__check_validity_json(json, "mLastName", validation_response)
        validation_response = JsonValidator.__check_validity_json(json, "mBirthDate", validation_response)
        validation_response = JsonValidator.__check_validity_json(json, "mEmail", validation_response)
        validation_response = JsonValidator.__check_validity_json(json, "mSex", validation_response)

        return validation_response

    @staticmethod
    def validate_story_request(request):
        validate_header = JsonValidator.validate_header_has_facebook_user_id(request.headers)
        if validate_header.hasErrors:
            return validate_header

        form = request.form
        file = request.files
        if form is None:
            return ValidationResponse(True, "Content-Type: is not application/json. Please make sure you send a json")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity_form(file, "file", validation_response)
        validation_response = JsonValidator.__check_validity_form(form, "mFileType", validation_response)
        validation_response = JsonValidator.__check_validity_form(form, "mFlash", validation_response)
        validation_response = JsonValidator.__check_validity_form(form, "mPrivate", validation_response)
        validation_response = JsonValidator.__check_validity_form(form, "mLatitude", validation_response)
        validation_response = JsonValidator.__check_validity_form(form, "mLongitude", validation_response)

        return validation_response

    @staticmethod
    def validate_header_has_facebook_user_id(header):
        if header is None:
            return ValidationResponse(True, "No values present at header.")
        validation_response = ValidationResponse(False, "")
        validation_response = JsonValidator.__check_validity_header(header, "facebookUserId", validation_response)

        return validation_response

    @staticmethod
    def __check_validity_json(json, field_name, validation_response):
        return JsonValidator.__check_validity(json, field_name, validation_response, 'Json')

    @staticmethod
    def __check_validity_form(form, field_name, validation_response):
        return JsonValidator.__check_validity(form, field_name, validation_response, 'Form')

    @staticmethod
    def __check_validity_header(header, field_name, validation_response):
        return JsonValidator.__check_validity(header, field_name, validation_response, 'Header')

    @staticmethod
    def __check_validity(request_map, field_name, validation_response, request_type):
        if field_name not in request_map or request_map[field_name] is '':
            validation_response.message += request_type + " must have " + field_name + " field and must not be empty. "
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

    @staticmethod
    def validate_shared_server_authorization(shared_server_response):
        LOGGER.info("Validating shared server response:" + str(shared_server_response))
        status_code = shared_server_response["code"]
        if status_code == 200 or status_code == 201:
            return ValidationResponse(False)
        return ValidationResponse(True, "Failed the communication with shared server user authentication. "
                                        "Got a status code: " + str(status_code))

    @staticmethod
    def validate_profile_picture(request):
        validate_header = JsonValidator.validate_header_has_facebook_user_id(request.headers)
        if validate_header.hasErrors:
            return validate_header
        if 'file' not in request.files:
            return ValidationResponse(True, 'No file in request')
        return ValidationResponse(False)
