from flask import request, Blueprint

from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.service.StoryService import StoryService
from appserver.validator.authValidator import secure
from appserver.controller.ControllerAuditory import controller_auditory

LOGGER = LoggerFactory().get_logger(__name__)
storiesEndpoint = Blueprint('storiesEndpoint', __name__)


@storiesEndpoint.route("", methods=['POST'])
@monitor
@secure
@controller_auditory
def post_story():
    LOGGER.info('Creating new story')
    return_value = StoryService.post_new_story(request)

    return return_value


@storiesEndpoint.route("", methods=['GET'])
@monitor
@secure
@controller_auditory
def get_stories():
    LOGGER.info('Getting all permanent stories')
    request_header = request.headers
    return_value = StoryService.get_all_stories_for_requester(request_header)

    return return_value


@storiesEndpoint.route("/<story_id>/comment", methods=['POST'])
@monitor
@secure
@controller_auditory
def post_comment(story_id):
    LOGGER.info('Commenting story')
    header = request.headers
    json = request.get_json()
    return_value = StoryService.post_comment(header, json, story_id)

    return return_value


@storiesEndpoint.route("/<story_id>/reaction", methods=['POST'])
@monitor
@secure
@controller_auditory
def post_reaction(story_id):
    LOGGER.info('Reacting to story')
    header = request.headers
    json = request.get_json()
    return_value = StoryService.post_reaction(header, json, story_id)

    return return_value
