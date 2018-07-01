from appserver.logger import LoggerFactory
from appserver import app

LOGGER = LoggerFactory.get_logger(__name__)

user_collection = app.database.user


class UserRepository(object):
    @staticmethod
    def insert(user):
        LOGGER.info('Inserting new value into user_table')
        user_id = user_collection.insert_one(user)
        return user_id

    @staticmethod
    def update_user_token(facebook_id, token, expires_at):
        LOGGER.info('Updating token to existing user')
        user_collection.update_one({'facebookUserId': facebook_id}, {
            '$set': {
                'token': token,
                'expires_at': expires_at
            }
        }, upsert=False)

    @staticmethod
    def update_firebase_id(facebook_id, firebase_id):
        LOGGER.info('Updating firebase_id to existing user')
        user_collection.update_one({'facebookUserId': facebook_id}, {
            '$set': {
                'firebase_id': firebase_id
            }
        }, upsert=False)

    @staticmethod
    def username_exists(facebook_user_id):
        LOGGER.info('Trying to see if ' + facebook_user_id + ' exists in database')
        return user_collection.find_one({'facebookUserId': facebook_user_id}) is not None

    @staticmethod
    def add_friendship(user_that_accepts_friendship, target_user):
        UserRepository.add_friend_to_list(user_that_accepts_friendship, target_user)
        UserRepository.add_friend_to_list(target_user, user_that_accepts_friendship)

    @staticmethod
    def add_friend_to_list(user, friend_to_add):
        user_entity = user_collection.find_one({'facebookUserId': user})
        if 'friendshipList' not in user_entity:
            friendship_list = [friend_to_add]
        else:
            friendship_list = user_entity['friendshipList']
            friendship_list.append(friend_to_add)
        user_collection.update_one({'facebookUserId': user}, {'$set': {'friendshipList': friendship_list}},
                                   upsert=False)

    @staticmethod
    def modify_profile(facebook_user_id, profile):
        LOGGER.info('Creating profile por user: ' + facebook_user_id)
        user_collection.update_one({'facebookUserId': facebook_user_id}, {'$set': profile}, upsert=False)

    @staticmethod
    def get_profile(facebook_user_id):
        return user_collection.find_one({'facebookUserId': facebook_user_id}, {'_id': 0})

    @staticmethod
    def get_friendship_list(facebook_user_id):
        return user_collection.find_one({'facebookUserId': facebook_user_id}, {'friendshipList': 1})['friendshipList']

    @staticmethod
    def get_firebase_id_list(list_of_friends):
        return list(
            user_collection.find({'facebookUserId': {'$in': list_of_friends}}, {'firebase_id': 1})['firebase_id'])

    @staticmethod
    def get_friends_information_list(list_of_friend_facebook_ids):
        return list(user_collection.find({'facebookUserId': {'$in': list_of_friend_facebook_ids}},
                                         {'facebookUserId': 1, 'last_name': 1, 'first_name': 1, 'mail': 1,
                                          'firebase_id': 1, 'birth_date': 1, '_id': 0}))

    @staticmethod
    def get_all_but(user_facebook_id):
        return list(user_collection.find({'facebookUserId': {'$not': {'$eq': user_facebook_id}}}))
