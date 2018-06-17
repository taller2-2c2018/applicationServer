from functools import wraps
from flask import request
from appserver.logger import LoggerFactory
from appserver import app
from appserver.datastructure.ApplicationResponse import ApplicationResponse
import time

LOGGER = LoggerFactory.get_logger(__name__)
user_collection = app.database.user


def secure(method):
    @wraps(method)
    def check_authorization(*args, **kwargs):
        token = request.headers.get('Authorization')
        facebook_id = request.headers.get('facebookUserId')
        user = user_collection.find_one({'facebookUserId': facebook_id})

        if user is None:
            return ApplicationResponse.unauthorized('Missing facebookUserId header')

        if (token != user['token']) and (app.skip_auth is False):
            return ApplicationResponse.unauthorized('User token is invalid')

        timestamp_now = int(time.time())
        if (timestamp_now > int(user['expires_at'])) and (app.skip_auth is False):
            return ApplicationResponse.unauthorized('Provided token expired')

        return method()

    return check_authorization
