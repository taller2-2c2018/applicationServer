from appserver import app
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory.get_logger(__name__)

friendship_collection = app.database.friendship


class FriendshipRepository(object):
    @staticmethod
    def insert(friendship):
        LOGGER.info('Inserting new vale into user_table')
        friendship_id = friendship_collection.insert_one(friendship)
        return friendship_id

    @staticmethod
    def get_friendship_requests_of_username(username):
        LOGGER.info('Getting all friendship requests of ' + username)
        return list(friendship_collection.find({'target': username}))

    @staticmethod
    def friendship_request_exists(target_facebook_id, requester_facebook_id):
        LOGGER.info('Seeing if friendship exists')
        return friendship_collection.find(
            {'requester': requester_facebook_id, 'target': target_facebook_id}).count() > 0

    @staticmethod
    def remove_friendship(user_that_accepts_friendship, target_user):
        LOGGER.info('Removing friendship request from database')
        friendship_collection.remove({'requester': target_user, 'target': user_that_accepts_friendship})
