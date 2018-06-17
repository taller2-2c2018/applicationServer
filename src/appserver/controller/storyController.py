from flask import request, Blueprint

from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.service.StoryService import StoryService
from appserver.validator.authValidator import secure

LOGGER = LoggerFactory().get_logger('StoryController')
storiesEndpoint = Blueprint('storiesEndpoint', __name__)


@storiesEndpoint.route("", methods=['POST'])
@monitor
@secure
def post():
    LOGGER.info('Creating new story')
    request_json = request.get_json()
    request_header = request.headers
    return_value = StoryService().post_new_story(request_json, request_header)

    return return_value


@storiesEndpoint.route("", methods=['GET'])
@monitor
@secure
def get():
    LOGGER.info('Getting all stories')
    request_header = request.headers
    return_value = StoryService().get_friends_stories(request_header)

    return return_value
