import json
from datetime import datetime

from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.logger import LoggerFactory
from appserver.repository.storyRepository import StoryRepository
from appserver.repository.userRepository import UserRepository
from appserver.transformer.MobileTransformer import MobileTransformer
from appserver.validator.jsonValidator import JsonValidator

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
        story_data = MobileTransformer.mobile_story_to_database(request_form, request.headers['facebookUserId'], file_id, date)

        response = StoryRepository.create_story(story_data)
        LOGGER.info('This is what I got from the database ' + str(response))

        return ApplicationResponse.created(message='Created story successfully')

    @staticmethod
    def get_permanent_stories_for_requester(request_header):
        validation_response = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        facebook_user_id = request_header["facebookUserId"]
        friendship_list = UserRepository.get_friendship_list(facebook_user_id)["friendshipList"]
        LOGGER.info("Got friendshipList" + str(friendship_list))
        stories = StoryRepository.get_all_permanent_stories()

        filtered_stories = StoryService.__get_all_public_and_friends_private_stories(stories, friendship_list)
        filtered_stories_for_mobile = MobileTransformer.database_list_of_stories_to_mobile(filtered_stories)

        return ApplicationResponse.success(data=filtered_stories_for_mobile)

    @staticmethod
    def __get_all_public_and_friends_private_stories(stories, friendship_list):
        stories_list = []
        LOGGER.info('This is the amount of stories that I have ' + str(stories.count()))
        for story in stories:
            LOGGER.info('Story to review ' + str(story))
            if (not story['is_private']) or (story['is_private'] and story['facebook_user_id'] in friendship_list):
                LOGGER.info('Adding story to list ' + str(story))
                stories_list.append(story)
        return stories_list

    @staticmethod
    def get_permanent_stories_of_given_user(requester_facebook_user_id, target_facebook_user_id):
        friendship_list = UserRepository.get_friendship_list(requester_facebook_user_id)["friendshipList"]
        stories = StoryRepository.get_permanent_stories_from_user(target_facebook_user_id)
        return StoryService.__get_all_public_and_friends_private_stories(stories=stories, friendship_list=friendship_list)
