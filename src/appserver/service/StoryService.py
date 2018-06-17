from appserver.validator.jsonValidator import JsonValidator
from appserver.repository.userRepository import UserRepository
from appserver.logger import LoggerFactory
from appserver.repository.storyRepository import StoryRepository
from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.externalcommunication.sharedServer import SharedServer
from bson.json_util import dumps
from datetime import datetime
import json

LOGGER = LoggerFactory().get_logger(__name__)


class StoryService(object):
    @staticmethod
    def post_new_story(request):
        validation_response = JsonValidator.validate_story_request(request)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        file = request.files
        upload_file_response = SharedServer.upload_file(file)

        LOGGER.info("Response from shared server: " + str(upload_file_response))
        shared_server_response_validation = JsonValidator.validate_shared_server_register_user(upload_file_response)
        if shared_server_response_validation.hasErrors:
            return ApplicationResponse.bad_request(message=shared_server_response_validation.message)

        file_id = json.loads(upload_file_response.text)['data']['id']

        request_form = request.form
        date = datetime.now()
        LOGGER.info('Date is ' + str(date))
        story_data = {
            'title': request_form['mTitle'],
            'description': request_form['mDescription'],
            'facebook_user_id': request.headers['facebookUserId'],
            'is_flash': request_form['mFlash'],
            'is_private': request_form['mPrivate'],
            'latitude': request_form['mLatitude'],
            'longitude': request_form['mLongitude'],
            'publication_date': date,
            'file_id': file_id,
            'file_type': request_form['mFileType']
        }
        response = StoryRepository.create_story(story_data)
        LOGGER.info('This is what I got from the database ' + str(response))

        return ApplicationResponse.created(message='Created story successfully')

    @staticmethod
    def get_friends_stories(request_header):
        validation_response = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)
        username = request_header["mUsername"]
        friendship_list = UserRepository.get_friendship_list(username)["friendshipList"]
        LOGGER.info("Got friendshipList" + str(friendship_list))
        stories_list = []
        for friend_username in friendship_list:
            stories = StoryRepository.get_stories_from_user(friend_username)
            for story in stories:
                stories_list.append(story)

        return ApplicationResponse.success(data=dumps(stories_list))
