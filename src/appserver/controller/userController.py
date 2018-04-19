from flask import request
from flask_restful import Resource
from appserver.logger import LoggerFactory
from appserver.service.userService import UserService

LOGGER = LoggerFactory().get_logger('UserResource')


class UserResource(Resource):
    def get(self):
        LOGGER.info('logging something')
        return "nada"

    def post(self):
        LOGGER.info('Trying to post new user')
        requestJson = request.get_json()
        return_value = UserService().insert_new_user(requestJson)
        return return_value
