import os
from bson import ObjectId

from appserver import app
from appserver.logger import LoggerFactory
from appserver.time.Time import Time

LOGGER = LoggerFactory.get_logger(__name__)

story_collection = app.database.story
flash_story_valid_hours = os.environ.get('FLASH_STORY_VALID_HOURS', 4)


class StoryRepository(object):
    @staticmethod
    def create_story(request_json):
        LOGGER.info('Creating a new story')
        story_id = story_collection.insert_one(request_json)
        return story_id

    @staticmethod
    def get_all_permanent_stories():
        LOGGER.info('Getting all permanent stories')
        return story_collection.find({'is_flash': False})

    @staticmethod
    def get_permanent_stories_from_user(target_facebook_user_id):
        LOGGER.info('Getting permanent stories from user with facebookId: ' + str(target_facebook_user_id))
        return story_collection.find({'is_flash': False, 'facebook_user_id': target_facebook_user_id})

    @staticmethod
    def get_all_valid_flash_stories():
        LOGGER.info('Getting all flash stories')
        valid_time_for_stories = Time.now() - Time.timedelta(hours=flash_story_valid_hours)
        return story_collection.find({'is_flash': True, 'publication_date': {'$gte': valid_time_for_stories}})

    @staticmethod
    def get_story_by_id(story_id):
        try:
            LOGGER.info('Getting story with id: ' + story_id)
            return story_collection.find_one({'_id': ObjectId(story_id)})
        except:
            LOGGER.error('No story found with given id')
            return None

    @staticmethod
    def update_story_by_id(story_id, story):
        LOGGER.info('Updating story')
        return story_collection.update_one({'_id': ObjectId(story_id)}, {'$set': story}, upsert=False)

    @staticmethod
    def get_total_stories_posted_today_by_user(facebook_id):
        LOGGER.info('Getting total stories posted today by user ' + str(facebook_id))
        start_of_day = Time.start_of_today()

        return story_collection.find(
            {'facebook_user_id': facebook_id, 'publication_date': {'$gte': start_of_day}}).count()

    @staticmethod
    def delete_story_by_id(story_id):
        story_collection.remove({'_id': story_id})
