from flask import request, Blueprint

from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.service.StoryService import StoryService
from appserver.validator.authValidator import secure

LOGGER = LoggerFactory().get_logger(__name__)
storiesEndpoint = Blueprint('storiesEndpoint', __name__)


@storiesEndpoint.route("", methods=['POST'])
@monitor
@secure
def post():
    LOGGER.info('Creating new story')
    return_value = StoryService().post_new_story(request)

    return return_value


@storiesEndpoint.route("", methods=['GET'])
@monitor
@secure
def get():
    LOGGER.info('Getting all permanent stories')
    request_header = request.headers
    return_value = StoryService().get_all_stories_for_requester(request_header)

    return return_value
