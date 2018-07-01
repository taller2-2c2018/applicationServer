from appserver.datastructure.validationResponse import ValidationResponse
from appserver.logger import LoggerFactory
from appserver.repository.userRepository import UserRepository

LOGGER = LoggerFactory().get_logger('DatabaseValidator')


class DatabaseValidator(object):

    @staticmethod
    def validate_is_existing_user(request_json):
        facebook_user_id = request_json['facebookUserId']
        if UserRepository.username_exists(facebook_user_id):
            return ValidationResponse(True, 'User already registered.')
        return ValidationResponse(False)
