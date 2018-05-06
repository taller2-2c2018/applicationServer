from appserver.logger import LoggerFactory
from appserver import app

LOGGER = LoggerFactory.get_logger(__name__)

user_collection = app.database.user


class UserRepository(object):
    def insert(self, user):
        LOGGER.info('Inserting new vale into user_table')
        user_id = user_collection.insert(user)
        return user_id
