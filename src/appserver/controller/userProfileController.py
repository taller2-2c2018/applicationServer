from flask import request
from flask_restful import Resource
from appserver.logger import LoggerFactory
from appserver.service.UserService import UserService
from appserver.monitor.monitor import monitor


LOGGER = LoggerFactory().get_logger('UserProfileResource')


class UserProfileResource(Resource):

    @monitor
    def post(self):
        LOGGER.info('Adding new profile to user')
        request_json = request.get_json()
        request_header = request.headers
        return_value = UserService().create_user_profile(request_json, request_header)
        return return_value

    @monitor
    def get(self, username):
        LOGGER.info('Getting profile of ' + username)
        return_value = UserService().get_user_profile(username)
        return return_value