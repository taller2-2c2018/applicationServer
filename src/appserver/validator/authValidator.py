import time

from flask import request
from functools import wraps

from appserver import app
from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.logger import LoggerFactory
from appserver.repository.userRepository import UserRepository
from appserver.threading.RunAsync import run_async

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
        except Exception as e:
            LOGGER.info('User was not authenticated. Reason: ' + str(e))
            return ApplicationResponse.bad_request('Missing request header Authorization')

        timestamp_now = int(time.time())
        if (timestamp_now > int(user['expires_at'])) and (app.skip_auth is False):
            return ApplicationResponse.unauthorized('Provided token expired')

        update_firebase_id_for_user(facebook_id, request.headers.get('firebaseId'))

        return method(*args, **kwargs)

    return check_authorization


@run_async
def update_firebase_id_for_user(facebook_id, firebase_id):
    if firebase_id is not None and firebase_id is not '':
        UserRepository.update_firebase_id(facebook_id, firebase_id)
