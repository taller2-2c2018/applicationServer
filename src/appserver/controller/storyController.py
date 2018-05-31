from flask import request, Blueprint
from flask_restful import Resource
from appserver.logger import LoggerFactory
from appserver.service.StoryService import StoryService
from appserver.monitor.monitor import monitor


LOGGER = LoggerFactory().get_logger('StoryResource')
storiesEndpoint = Blueprint('storiesEndpoint', __name__)


@storiesEndpoint.route("", methods=['POST'])
@monitor
def post():
    LOGGER.info('Creating new story')
    request_json = request.get_json()
    request_header = request.headers
    return_value = StoryService().post_new_story(request_json, request_header)

    return return_value


@storiesEndpoint.route("", methods=['GET'])
@monitor
def get():
    LOGGER.info('Getting all stories')
    request_header = request.headers
    return_value = StoryService().get_friends_stories(request_header)

    return return_value
