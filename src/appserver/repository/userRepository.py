from appserver.logger import LoggerFactory
from appserver import app

LOGGER = LoggerFactory.get_logger(__name__)

user_collection = app.database.user


class UserRepository(object):
    @staticmethod
    def insert(user):
        LOGGER.info('Inserting new vale into user_table')
        user_id = user_collection.insert_one(user)
        return user_id

    @staticmethod
    def update_user_token(user, token):
        LOGGER.info('Updating token to existing user')
        user_id = user_collection.find_one({"username": user})["_id"]
        user_collection.update_one({'_id': user_id}, {"$set": token}, upsert=False)

    @staticmethod
    def username_exists(username):
        LOGGER.info("Trying to see if " + username + " exists in database")
        return user_collection.find_one({"username": username})
