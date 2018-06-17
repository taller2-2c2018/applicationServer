from appserver.logger import LoggerFactory
from appserver import app

LOGGER = LoggerFactory.get_logger(__name__)

story_collection = app.database.story


class StoryRepository(object):
    @staticmethod
    def create_story(request_json):
        LOGGER.info('Creating a new story')
        story_id = story_collection.insert_one(request_json)
        return story_id

    @staticmethod
    def get_stories_from_user(friend_username):
        LOGGER.info('Getting all stories from ' + friend_username)
        return story_collection.find({"facebook_user_id": friend_username}, {"_id": 0})

    @staticmethod
    def get_all_permanent_stories():
        LOGGER.info('Getting all permanent stories')
        return story_collection.find({'is_flash': 'False'})

    @staticmethod
    def get_permanent_stories_from_user(target_facebook_user_id):
        LOGGER.info('Getting permanent stories from user with facebookId: ' + str(target_facebook_user_id))
        return story_collection.find({'is_flash': 'False', 'facebook_user_id': target_facebook_user_id},  {"_id": 0})
