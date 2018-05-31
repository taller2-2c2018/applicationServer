from flask import request
from flask_restful import Resource
from appserver.logger import LoggerFactory
from appserver.service.UserService import UserService
from appserver.monitor.monitor import monitor

LOGGER = LoggerFactory().get_logger('UserResource')


class UserRegisterResource(Resource):

    @monitor
    def post(self):
        LOGGER.info('Registering a new user')
        request_json = request.get_json()
        return_value = UserService().register_new_user(request_json)
        return return_value
