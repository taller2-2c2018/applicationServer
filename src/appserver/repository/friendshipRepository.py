from appserver.logger import LoggerFactory
from appserver import app
from bson import json_util

LOGGER = LoggerFactory.get_logger(__name__)

friendship_collection = app.database.friendship


class FriendshipRepository(object):
    @staticmethod
    def insert(friendship):
        LOGGER.info('Inserting new vale into user_table')
        friendship_id = friendship_collection.insert(friendship)
        return friendship_id

    @staticmethod
    def get_friendship_requests_of_username(username):
        LOGGER.info('Getting all friendship requests of ' + username)
        friendship_list = friendship_collection.find({'target': username})

        return json_util.dumps(friendship_list)

    @staticmethod
    def friendship_exists(user_that_accepts_friendship, target_user):
        LOGGER.info('Seeing if friendship exists')
        return friendship_collection.find(
            {"requester": target_user, "target": user_that_accepts_friendship}).count() > 0

    @staticmethod
    def accept_friendship(user_that_accepts_friendship, target_user):
        LOGGER.info('Removing friendship request from database')
        friendship_collection.remove({'requester': target_user, "target": user_that_accepts_friendship})

