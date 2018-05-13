from appserver.logger import LoggerFactory
from appserver import app

LOGGER = LoggerFactory.get_logger(__name__)

friendship_collection = app.database.friendship


class FriendshipRepository(object):
    @staticmethod
    def insert(friendship):
        LOGGER.info('Inserting new vale into user_table')
        friendship_id = friendship_collection.insert(friendship)
        return friendship_id
