from appserver.validator.jsonValidator import JsonValidator
from appserver.repository.userRepository import UserRepository
from appserver.logger import LoggerFactory
from datetime import datetime
from appserver.repository.storyRepository import StoryRepository
from appserver.datastructure.ApplicationResponse import ApplicationResponse
from bson.json_util import dumps


LOGGER = LoggerFactory().get_logger('UserService')


class StoryService(object):
    @staticmethod
    def post_new_story(request_json, request_header):
        validation_response = JsonValidator.validate_header_has_username(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request_message(validation_response.message)
        validation_response = JsonValidator.validate_story_datafields(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request_message(validation_response.message)
        username = request_header["mUsername"]
        request_json["mUsername"] = username
        request_json["mDate"] = str(datetime.now())
        request_json["mPictureUser"] = UserRepository.get_profile(username)["mPicture"]
        StoryRepository().create_story(request_json)

        return ApplicationResponse.created_message("Created story successfully")

    @staticmethod
    def get_friends_stories(request_header):
        validation_response = JsonValidator.validate_header_has_username(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request_message(validation_response.message)
        username = request_header["mUsername"]
        friendship_list = UserRepository.get_friendship_list(username)["friendshipList"]
        LOGGER.info("Got friendshipList" + str(friendship_list))
        stories_list = []
        for friend_username in friendship_list:
            stories = StoryRepository.get_stories_from_user(friend_username)
            for story in stories:
                stories_list.append(story)

        return ApplicationResponse.success(dumps(stories_list))
