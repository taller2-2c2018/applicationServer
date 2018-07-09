from flask import request, Blueprint

from appserver.controller.ControllerAuditory import controller_auditory
from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.service.StoryService import StoryService
from appserver.validator.authValidator import secure

LOGGER = LoggerFactory().get_logger(__name__)
storiesEndpoint = Blueprint('storiesEndpoint', __name__)


@storiesEndpoint.route('', methods=['POST'])
@monitor
@secure
@controller_auditory
def post_story():
    LOGGER.info('Creating new story')
    headers = request.headers
    story_json = request.get_json()
    return_value = StoryService.post_new_story(headers=headers, story_json=story_json)

    return return_value


@storiesEndpoint.route('/multipart', methods=['POST'])
@monitor
@secure
@controller_auditory
def post_story_multipart():
    LOGGER.info('Creating new story using multipart')
    return_value = StoryService().post_new_story_multipart(request)

    return return_value


@storiesEndpoint.route('', methods=['GET'])
@monitor
@secure
@controller_auditory
def get_stories():
    LOGGER.info('Getting all permanent stories')
    request_header = request.headers
    return_value = StoryService.get_all_stories_for_requester(request_header)

    return return_value


@storiesEndpoint.route('/<story_id>/comment', methods=['POST'])
@monitor
@secure
@controller_auditory
def post_comment(story_id):
    LOGGER.info('Commenting story')
    header = request.headers
    json = request.get_json()
    return_value = StoryService.post_comment(header, json, story_id)

    return return_value


@storiesEndpoint.route('/<story_id>/reaction', methods=['POST'])
@monitor
@secure
@controller_auditory
def post_reaction(story_id):
    LOGGER.info('Reacting to story')
    header = request.headers
    json = request.get_json()
    return_value = StoryService.post_reaction(header, json, story_id)

    return return_value
