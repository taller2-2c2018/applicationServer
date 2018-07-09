import time

from flask import request
from functools import wraps

from appserver import app
from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.logger import LoggerFactory
from appserver.repository.userRepository import UserRepository

LOGGER = LoggerFactory.get_logger(__name__)
user_collection = app.database.user


def secure(method):
    @wraps(method)
    def check_authorization(*args, **kwargs):
        try:
            facebook_id = request.headers.get('facebookUserId')
            user = user_collection.find_one({'facebookUserId': facebook_id})

            if user is None:
                return ApplicationResponse.unauthorized('facebookUserId missing or value not valid')
        except:
            return ApplicationResponse.bad_request('Missing request header with facebookUserId')

        try:
            token = request.headers.get('Authorization')
            if (token != user['token']) and (app.skip_auth is False):
                return ApplicationResponse.unauthorized('User token is invalid')
        except:
            return ApplicationResponse.bad_request('Missing request header Authorization')

        timestamp_now = int(time.time())
        if (timestamp_now > int(user['expires_at'])) and (app.skip_auth is False):
            return ApplicationResponse.unauthorized('Provided token expired')

        firebase_id = request.headers.get('firebaseId')
        if firebase_id is not None and firebase_id is not '':
            UserRepository.update_firebase_id(facebook_id, firebase_id)

        return method(*args, **kwargs)

    return check_authorization
