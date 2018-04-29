from appserver.logger import LoggerFactory
from appserver import app

LOGGER = LoggerFactory.get_logger(__name__)


class Database(object):
    def get_user_table(self):
        return app.Configuration().get_database().user_table


class UserRepository(object):
    def insert(self, user):
        LOGGER.info('Inserting new vale into user_table')
        user_id = Database().get_user_table().insert(user)
        return user_id
