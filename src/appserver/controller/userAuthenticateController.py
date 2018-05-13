from flask import request
from flask_restful import Resource
from appserver.logger import LoggerFactory
from appserver.service.UserService import UserService

LOGGER = LoggerFactory().get_logger('UserAuthenticateResource')


class UserAuthenticateResource(Resource):

    def post(self):
        LOGGER.info('Authenticating user')
        request_json = request.get_json()
        return_value = UserService().authenticate_user(request_json)
        return return_value
