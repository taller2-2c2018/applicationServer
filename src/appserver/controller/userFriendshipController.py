from flask import request
from flask_restful import Resource
from appserver.logger import LoggerFactory
from appserver.service.UserService import UserService
from appserver.monitor.monitor import monitor


LOGGER = LoggerFactory().get_logger('UserFriendshipResource')


class UserFriendshipResource(Resource):

    @monitor
    def post(self):
        LOGGER.info('Sending new friendship request')
        request_json = request.get_json()
        return_value = UserService().send_user_friendship_request(request_json)
        return return_value
