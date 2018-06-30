import datetime
import json
import unittest
from unittest.mock import *

import pytz
from bson import ObjectId

from appserver.app import database
from appserver.service.StoryService import StoryService
from appserver.service.UserService import UserService
from tests.app.testCommons import BaseTestCase
from appserver.rules.RelevanceEngine import RelevanceEngine
from appserver.rules.StoryRelevance import StoryRelevance


def mock_user_identification(request_json):
    request_json['last_name'] = 'last_name'
    request_json['first_name'] = 'first_name'


def mock_register_user(request_json):
    shared_server_response = Mock()
    shared_server_response.text = 'text'
    shared_server_response.status_code = 200

    return shared_server_response


def mock_upload_file(file):
    shared_server_response = Mock()
    shared_server_response.text = '{"data": {"id": 1}}'
    shared_server_response.status_code = 200

    return shared_server_response


def mock_time_now():
    buenos_aires = pytz.timezone(zone='America/Argentina/Buenos_Aires')
    return datetime.datetime(year=2018, month=12, day=25, hour=17, minute=5, second=55, tzinfo=buenos_aires)


def mock_time_timedelta(hours):
    return -datetime.timedelta(hours=1)


class Object(object):
    pass


@patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
@patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
@patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
@patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file', mock_upload_file)
@patch('appserver.externalcommunication.GoogleMapsApi.GoogleMapsApi.get_location',
       MagicMock(return_value='San Telmo, Buenos Aires'))
@patch('appserver.externalcommunication.FirebaseCloudMessaging.FirebaseCloudMessaging.send_notification', MagicMock())
class Tests(BaseTestCase):

    def test_register_user(self):
        response_register_user = Tests.__create_default_user()

        self.assertEqual(response_register_user.status_code, 201)

        inserted_user = database.user.find_one({'facebookUserId': 'facebookUserId'})

        self.assertEqual(inserted_user['facebookUserId'], 'facebookUserId')
        self.assertEqual(inserted_user['facebookAuthToken'], 'facebookAuthToken')
        self.assertEqual(inserted_user['last_name'], 'last_name')
        self.assertEqual(inserted_user['first_name'], 'first_name')

    def test_register_existing_user_doesnt_add_it_again(self):
        Tests.__create_default_user()
        response_register_user = UserService.register_new_user(
            {'facebookUserId': 'facebookUserId',
             'facebookAuthToken': 'facebookAuthToken'})

        self.assertEqual(response_register_user.status_code, 400)
        self.assertEqual(response_register_user.get_json()['message'], 'User already registered.')

    def test_create_user_profile(self):
        Tests.__create_default_user()
        response_update_profile = UserService.modify_user_profile(
            {'mFirstName': 'name', 'mLastName': 'surname', 'mBirthDate': '01/01/1990', 'mEmail': 'mail@email.com',
             'mSex': 'male'},
            {'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_update_profile.status_code, 201)

        inserted_profile = database.user.find_one({'facebookUserId': 'facebookUserId'})

        self.assertEqual(inserted_profile['first_name'], 'name')
        self.assertEqual(inserted_profile['last_name'], 'surname')
        self.assertEqual(inserted_profile['birth_date'], '01/01/1990')
        self.assertEqual(inserted_profile['mail'], 'mail@email.com')
        self.assertEqual(inserted_profile['sex'], 'male')

    def test_get_user_profile(self):
        Tests.__create_default_user()
        UserService.modify_user_profile(
            {'mFirstName': 'name', 'mLastName': 'surname', 'mBirthDate': '01/01/1990', 'mEmail': 'mail@email.com',
             'mSex': 'male'},
            {'facebookUserId': 'facebookUserId'})
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        response_user_profile = UserService.get_user_profile(request, 'facebookUserId')

        self.assertEqual(response_user_profile.status_code, 200)

        response_json = response_user_profile.get_json()['data']

        self.assertEqual(response_json['mFirstName'], 'name')
        self.assertEqual(response_json['mLastName'], 'surname')
        self.assertEqual(response_json['mBirthDate'], '01/01/1990')
        self.assertEqual(response_json['mEmail'], 'mail@email.com')
        self.assertEqual(response_json['mSex'], 'male')

    def test_send_friendship_request(self):
        Tests.__create_default_user()
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        response_send_friendship_request = UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_send_friendship_request.status_code, 200)

        inserted_friendship = database.friendship.find_one({'requester': 'facebookUserId'})

        self.assertEqual(inserted_friendship['requester'], 'facebookUserId')
        self.assertEqual(inserted_friendship['target'], 'target')
        self.assertEqual(inserted_friendship['message'], 'Add me to your friend list')

    def test_get_friendship_requests(self):
        Tests.__create_default_user()
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'facebookUserId'})
        friendship_response = UserService.get_friendship_requests({'facebookUserId': 'target'})

        self.assertEqual(friendship_response.status_code, 200)

        friendship_list = friendship_response.get_json()['data']
        friendship_list = json.loads(friendship_list)

        self.assertEqual(len(friendship_list), 1)
        self.assertEqual(friendship_list[0]['requester'], 'facebookUserId')
        self.assertEqual(friendship_list[0]['target'], 'target')
        self.assertEqual(friendship_list[0]['message'], 'Add me to your friend list')

    def test_accept_friendship_request(self):
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.register_new_user({'facebookUserId': 'requester', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'requester'})

        accept_response = UserService.accept_friendship_request({'facebookUserId': 'target'}, 'requester')

        self.assertEqual(accept_response.status_code, 200)

        friendship_response = UserService.get_friendship_requests({'facebookUserId': 'target'})

        self.assertEqual(friendship_response.status_code, 200)

        friendship_list = friendship_response.get_json()['data']
        friendship_list = json.loads(friendship_list)

        self.assertEqual(len(friendship_list), 0)

        friends_of_requester = database.user.find_one({'facebookUserId': 'requester'})['friendshipList']
        self.assertTrue('target' in friends_of_requester)

        friends_of_target = database.user.find_one({'facebookUserId': 'target'})['friendshipList']
        self.assertTrue('requester' in friends_of_target)

    def test_get_friends(self):
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken',
                                       'birth_date': '10/02/1992', 'firebase_id': '1234'})
        UserService.register_new_user({'facebookUserId': 'requester', 'facebookAuthToken': 'facebookAuthToken',
                                       'birth_date': '11/02/1992', 'firebase_id': '5678'})
        UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'requester'})

        accept_response = UserService.accept_friendship_request({'facebookUserId': 'target'}, 'requester')

        self.assertEqual(accept_response.status_code, 200)

        friends_response = UserService.get_user_friends({'facebookUserId': 'target'})

        self.assertEqual(friends_response.status_code, 200)

        friends_list = friends_response.get_json()['data']

        self.assertEqual(len(friends_list), 1)
        friend = friends_list[0]
        self.assertEqual(friend['mFirebaseId'], '5678')
        self.assertEqual(friend['mBirthDate'], '11/02/1992')
        self.assertEqual(friend['mFacebookUserId'], 'requester')

    def test_modify_profile_picture(self):
        Tests.__create_default_user()
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mFileType': 'jpg'}
        modify_profile_response = UserService.modify_user_profile_picture(request)

        self.assertEqual(modify_profile_response.status_code, 200)

        updated_user = database.user.find_one({'facebookUserId': 'facebookUserId'})
        self.assertEqual(updated_user['profile_picture_id'], 1)
        self.assertEqual(updated_user['file_type_profile_picture'], 'jpg')

    def test_get_user_profile_after_adding_profile_picture(self):
        Tests.__create_default_user()
        UserService.modify_user_profile(
            {'mFirstName': 'name', 'mLastName': 'surname', 'mBirthDate': '01/01/1990', 'mEmail': 'mail@email.com',
             'mSex': 'male'},
            {'facebookUserId': 'facebookUserId'})
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mFileType': 'jpg'}
        UserService.modify_user_profile_picture(request)
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        response_user_profile = UserService.get_user_profile(request, 'facebookUserId')

        self.assertEqual(response_user_profile.status_code, 200)

        response_json = response_user_profile.get_json()['data']

        self.assertEqual(response_json['mFirstName'], 'name')
        self.assertEqual(response_json['mLastName'], 'surname')
        self.assertEqual(response_json['mBirthDate'], '01/01/1990')
        self.assertEqual(response_json['mEmail'], 'mail@email.com')
        self.assertEqual(response_json['mSex'], 'male')
        self.assertEqual(response_json['mProfilePictureId'], 1)
        self.assertEqual(response_json['mFileTypeProfilePicture'], 'jpg')

    def test_post_new_story(self):
        Tests.__create_default_user()

        response_post_new_story = Tests.__create_default_story()
        self.assertEqual(response_post_new_story.status_code, 201)

        story = database.story.find_one({'facebook_user_id': 'facebookUserId'})

        self.assertEqual(story['title'], 'title')
        self.assertEqual(story['description'], 'description')
        self.assertEqual(story['facebook_user_id'], 'facebookUserId')
        self.assertEqual(story['is_flash'], False)
        self.assertEqual(story['is_private'], False)
        self.assertEqual(story['latitude'], 40.714224)
        self.assertEqual(story['longitude'], -73.961452)
        self.assertEqual(story['file_id'], 1)
        self.assertEqual(story['file_type'], 'jpg')
        self.assertEqual(story['location'], 'San Telmo, Buenos Aires')
        self.assertEqual(story['total_friends'], 0)
        self.assertEqual(story['stories_posted_today'], 0)

    def test_get_all_stories_for_requester_gets_permanent_story(self):
        Tests.__create_default_user()
        Tests.__create_default_story()

        response_stories = StoryService.get_all_stories_for_requester(Tests.__default_header())
        self.assertEqual(response_stories.status_code, 200)

        stories_list = response_stories.get_json()['data']
        self.assertEqual(len(stories_list), 1)

        story = stories_list[0]
        self.assertTrue(story['mStoryId'] is not None)
        self.assertEqual(story['mTitle'], 'title')
        self.assertEqual(story['mDescription'], 'description')
        self.assertEqual(story['mFacebookUserId'], 'facebookUserId')
        self.assertEqual(story['mLatitude'], 40.714224)
        self.assertEqual(story['mLongitude'], -73.961452)
        self.assertEqual(story['mFileId'], 1)
        self.assertEqual(story['mFileType'], 'jpg')
        self.assertEqual(story['mFlash'], False)
        self.assertEqual(story['mLocation'], 'San Telmo, Buenos Aires')
        self.assertTrue(story['mRelevance'] is not None)

    def test_get_all_stories_for_requester_gets_flash_story(self):
        Tests.__create_default_user()
        Tests.__create_default_story(is_flash=True)

        response_stories = StoryService.get_all_stories_for_requester(Tests.__default_header())
        self.assertEqual(response_stories.status_code, 200)

        stories_list = response_stories.get_json()['data']
        self.assertEqual(len(stories_list), 1)

        story = stories_list[0]
        self.assertTrue(story['mStoryId'] is not None)
        self.assertEqual(story['mTitle'], 'title')
        self.assertEqual(story['mDescription'], 'description')
        self.assertEqual(story['mFacebookUserId'], 'facebookUserId')
        self.assertEqual(story['mLatitude'], 40.714224)
        self.assertEqual(story['mLongitude'], -73.961452)
        self.assertEqual(story['mFileId'], 1)
        self.assertEqual(story['mFileType'], 'jpg')
        self.assertEqual(story['mFlash'], True)
        self.assertEqual(story['mLocation'], 'San Telmo, Buenos Aires')
        self.assertTrue(story['mRelevance'] is not None)

    @patch('appserver.time.Time.Time.now', mock_time_now)
    def test_get_all_stories_for_requester_gets_stories_ordered_by_relevance(self):
        Tests.__create_default_user()
        Tests.__create_default_story()
        Tests.__create_default_story(title='secondTitle', description='secondDescription')

        response_stories = StoryService.get_all_stories_for_requester(Tests.__default_header())
        self.assertEqual(response_stories.status_code, 200)

        stories_list = response_stories.get_json()['data']
        self.assertEqual(len(stories_list), 2)

        first_story = stories_list[0]
        self.assertTrue(first_story['mStoryId'] is not None)
        self.assertEqual(first_story['mTitle'], 'title')
        self.assertEqual(first_story['mDescription'], 'description')
        self.assertEqual(first_story['mFacebookUserId'], 'facebookUserId')
        self.assertEqual(first_story['mLatitude'], 40.714224)
        self.assertEqual(first_story['mLongitude'], -73.961452)
        self.assertEqual(first_story['mFileId'], 1)
        self.assertEqual(first_story['mFileType'], 'jpg')
        self.assertEqual(first_story['mFlash'], False)
        self.assertEqual(first_story['mLocation'], 'San Telmo, Buenos Aires')
        self.assertTrue(first_story['mRelevance'] is not None)

        second_story = stories_list[1]
        self.assertTrue(second_story['mStoryId'] is not None)
        self.assertEqual(second_story['mTitle'], 'secondTitle')
        self.assertEqual(second_story['mDescription'], 'secondDescription')
        self.assertEqual(second_story['mFacebookUserId'], 'facebookUserId')
        self.assertEqual(second_story['mLatitude'], 40.714224)
        self.assertEqual(second_story['mLongitude'], -73.961452)
        self.assertEqual(second_story['mFileId'], 1)
        self.assertEqual(second_story['mFileType'], 'jpg')
        self.assertEqual(second_story['mFlash'], False)
        self.assertEqual(second_story['mLocation'], 'San Telmo, Buenos Aires')
        self.assertTrue(second_story['mRelevance'] is not None)

        self.assertTrue(second_story['mRelevance'] < first_story['mRelevance'])

    @patch('appserver.time.Time.Time.now', mock_time_now)
    @patch('appserver.time.Time.Time.timedelta', mock_time_timedelta)
    def test_get_all_stories_for_requester_doesnt_get_caducated_flash_story(self):
        Tests.__create_default_user()
        Tests.__create_default_story(is_flash=True)

        response_stories = StoryService.get_all_stories_for_requester(Tests.__default_header())
        self.assertEqual(response_stories.status_code, 200)

        stories_list = response_stories.get_json()['data']
        self.assertEqual(len(stories_list), 0)

    def test_post_new_comment_in_story(self):
        Tests.__create_default_user()
        Tests.__create_default_story()

        response_stories = StoryService.get_all_stories_for_requester(Tests.__default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        comment_json = {'mComment': 'comment'}
        response_comment = StoryService.post_comment(Tests.__default_header(), comment_json, story_id)

        self.assertEqual(response_comment.status_code, 201)

        modified_story = database.story.find_one({'_id': ObjectId(story_id)})
        list_of_comments = modified_story['comments']
        self.assertEqual(len(list_of_comments), 1)

        comment = list_of_comments[0]

        self.assertEqual(comment['text'], 'comment')
        self.assertEqual(comment['facebook_user_id'], 'facebookUserId')
        self.assertTrue(comment['date'] is not None)

    def test_post_new_reaction_in_story(self):
        Tests.__create_default_user()
        Tests.__create_default_story()
        response_stories = StoryService.get_all_stories_for_requester(Tests.__default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        header = {'facebookUserId': 'facebookUserId'}
        reaction_json = {'mReaction': 'me gusta'}
        response_comment = StoryService.post_reaction(header, reaction_json, story_id)

        self.assertEqual(response_comment.status_code, 201)

        modified_story = database.story.find_one({'_id': ObjectId(story_id)})
        list_of_reactions = modified_story['reactions']
        self.assertEqual(len(list_of_reactions), 1)

        reaction = list_of_reactions[0]

        self.assertEqual(reaction['reaction'], 'me gusta')
        self.assertEqual(reaction['facebook_user_id'], 'facebookUserId')
        self.assertTrue(reaction['date'] is not None)

    def test_relevance_engine_low_rules(self):
        story_relevance = StoryRelevance(1, 0, 1, 1, 1)
        RelevanceEngine.run_rule(story_relevance)

        expected_points = 1 * 1 + 5 + 1 * 2 + 1 * 0.5 - 1.5

        self.assertEqual(story_relevance.get_relevance_points(), expected_points)

    def test_relevance_engine_medium_rules(self):
        story_relevance = StoryRelevance(10, 0, 10, 10, 1)
        RelevanceEngine.run_rule(story_relevance)

        expected_points = 10 * 0.4 + 5 + 10 * 0.8 + 10 * 0.2 - 1.5

        self.assertEqual(story_relevance.get_relevance_points(), expected_points)

    def test_relevance_engine_high_rules(self):
        story_relevance = StoryRelevance(100, 0, 100, 100, 1)
        RelevanceEngine.run_rule(story_relevance)

        expected_points = 100 * 0.12 + 5 + 100 * 0.24 + 100 * 0.06 - 1.5

        self.assertEqual(story_relevance.get_relevance_points(), expected_points)

    def test_relevance_engine_multiple_stories_rule(self):
        story_relevance = StoryRelevance(0, 10, 0, 0, 0)
        RelevanceEngine.run_rule(story_relevance)

        expected_points = -3 * 10

        self.assertEqual(story_relevance.get_relevance_points(), expected_points)

    @staticmethod
    def __create_default_user():
        return UserService.register_new_user({'facebookUserId': 'facebookUserId',
                                              'facebookAuthToken': 'facebookAuthToken'})

    @staticmethod
    def __create_default_story(is_flash=False, title='title', description='description'):
        headers = Tests.__default_header()
        story_json = {'file': 'data', 'mTitle': title, 'mDescription': description, 'mFileType': 'jpg',
                      'mFlash': is_flash, 'mPrivate': False, 'mLatitude': 40.714224, 'mLongitude': -73.961452}

        return StoryService.post_new_story(headers=headers, story_json=story_json)

    @staticmethod
    def __default_header():
        return {'facebookUserId': 'facebookUserId'}


if __name__ == '__main__':
    unittest.main()
