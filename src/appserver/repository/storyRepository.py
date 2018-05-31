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
        return story_collection.find({"mUsername": friend_username}, {"_id": 0})
