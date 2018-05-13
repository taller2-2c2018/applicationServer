from flask import request
from flask_restful import Resource
from appserver.logger import LoggerFactory
from appserver.service.UserService import UserService

LOGGER = LoggerFactory().get_logger('UserResource')


class UserRegisterResource(Resource):

    def post(self):
        LOGGER.info('Registering a new user')
        requestJson = request.get_json()
        return_value = UserService().register_new_user(requestJson)
        return return_value
