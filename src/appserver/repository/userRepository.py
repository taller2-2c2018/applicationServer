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
    def update_user_token(facebook_id, token, expires_at):
        LOGGER.info('Updating token to existing user')
        user_id = user_collection.find_one({"facebookUserId": facebook_id})["_id"]
        user_collection.update_one({'_id': user_id}, {
            "$set": {
                       "token": token,
                       "expires_at": expires_at
            }
        }, upsert=False)

    @staticmethod
    def username_exists(facebook_user_id):
        LOGGER.info("Trying to see if " + facebook_user_id + " exists in database")
        return user_collection.find_one({'facebookUserId': facebook_user_id}) is not None

    @staticmethod
    def add_friendship(user_that_accepts_friendship, target_user):
        UserRepository.add_friend_to_list(user_that_accepts_friendship, target_user)
        UserRepository.add_friend_to_list(target_user, user_that_accepts_friendship)

    @staticmethod
    def add_friend_to_list(user, friend_to_add):
        user_entity = user_collection.find_one({'facebookUserId': user})
        if "friendshipList" not in user_entity:
            friendship_list = [friend_to_add]
        else:
            friendship_list = user_entity["friendshipList"]
            friendship_list.append(friend_to_add)
        user_collection.update_one({'facebookUserId': user}, {"$set": {"friendshipList": friendship_list}}, upsert=False)

    @staticmethod
    def create_profile(username, profile):
        LOGGER.info("Creating profile por user: " + username)
        user_collection.update_one({"username": username}, {"$set": profile}, upsert=False)

    @staticmethod
    def get_profile(username):
        return user_collection.find_one({"username": username}, {"_id": 0, "mFirstName": 1, "mLastname": 1, "mBirthDate": 1,
                                                                 "mFacebookUrl": 1, "mPicture": 1, "mSex": 1})

    @staticmethod
    def get_friendship_list(username):
        return user_collection.find_one({"username": username}, {"_id": 0, "friendshipList": 1})
