from flask import request
from flask_restful import Resource
from appserver.logger import LoggerFactory
from appserver.service.UserService import UserService
from appserver.monitor.monitor import monitor


LOGGER = LoggerFactory().get_logger('UserFriendshipAcceptResource')


class UserFriendshipAcceptResource(Resource):

    @monitor
    def post(self, username):
        LOGGER.info('Sending new friendship request')
        request_header = request.headers
        return_value = UserService().accept_friendship_request(request_header, username)
        return return_value
