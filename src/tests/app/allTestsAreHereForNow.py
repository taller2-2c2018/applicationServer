import json
import unittest
import datetime
from unittest.mock import *

from appserver.app import database
from appserver.service.UserService import UserService
from appserver.service.StoryService import StoryService
from tests.app.testCommons import BaseTestCase
from bson import ObjectId


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
    return datetime.datetime(year=2018, month=12, day=25, hour=17, minute=5, second=55)


def mock_time_timedelta(hours):
    return -datetime.timedelta(hours=1)


class Object(object):
    pass


@patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
@patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
@patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
@patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file', mock_upload_file)
@patch('appserver.externalcommunication.GoogleMapsApi.GoogleMapsApi.get_location', MagicMock(return_value='San Telmo, Buenos Aires'))
class Tests(BaseTestCase):

    def test_register_user(self):
        response_register_user = UserService.register_new_user(
            {'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})

        self.assertEqual(response_register_user.status_code, 201)

        inserted_user = database.user.find_one({'facebookUserId': 'facebookUserId'})

        self.assertEqual(inserted_user['facebookUserId'], 'facebookUserId')
        self.assertEqual(inserted_user['facebookAuthToken'], 'facebookAuthToken')
        self.assertEqual(inserted_user['last_name'], 'last_name')
        self.assertEqual(inserted_user['first_name'], 'first_name')

    def test_register_existing_user_doesnt_add_it_again(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        response_register_user = UserService.register_new_user(
            {'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})

        self.assertEqual(response_register_user.status_code, 400)
        self.assertEqual(response_register_user.get_json()['message'], 'User already registered.')

    def test_create_user_profile(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        response_update_profile = UserService.modify_user_profile(
            {'mFirstName': 'name', 'mLastName': 'surname', 'mBirthDate': '01/01/1990', 'mEmail': 'mail@email.com', 'mSex': 'male'},
            {'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_update_profile.status_code, 201)

        inserted_profile = database.user.find_one({'facebookUserId': 'facebookUserId'})

        self.assertEqual(inserted_profile['first_name'], 'name')
        self.assertEqual(inserted_profile['last_name'], 'surname')
        self.assertEqual(inserted_profile['birth_date'], '01/01/1990')
        self.assertEqual(inserted_profile['mail'], 'mail@email.com')
        self.assertEqual(inserted_profile['sex'], 'male')

    def test_get_user_profile(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.modify_user_profile(
            {'mFirstName': 'name', 'mLastName': 'surname', 'mBirthDate': '01/01/1990', 'mEmail': 'mail@email.com', 'mSex': 'male'},
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

    def test_modify_profile_picture(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
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
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
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
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mFileType': 'jpg', 'mFlash': False, 'mPrivate': False, 'mLatitude': 40.714224,
                        'mLongitude': -73.961452}

        response_post_new_story = StoryService.post_new_story(request=request)
        self.assertEqual(response_post_new_story.status_code, 201)

        story = database.story.find_one({'facebook_user_id': 'facebookUserId'})

        self.assertEqual(story['title'], '')
        self.assertEqual(story['description'], '')
        self.assertEqual(story['facebook_user_id'], 'facebookUserId')
        self.assertEqual(story['is_flash'], False)
        self.assertEqual(story['is_private'], False)
        self.assertEqual(story['latitude'], 40.714224)
        self.assertEqual(story['longitude'], -73.961452)
        self.assertEqual(story['file_id'], 1)
        self.assertEqual(story['file_type'], 'jpg')
        self.assertEqual(story['location'], 'San Telmo, Buenos Aires')

    def test_get_all_stories_for_requester_gets_permanent_story(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mDescription': 'description', 'mFileType': 'jpg', 'mFlash': False,
                        'mPrivate': False, 'mLatitude': 40.714224, 'mLongitude': -73.961452}

        StoryService.post_new_story(request=request)

        response_stories = StoryService.get_all_stories_for_requester(request.headers)
        self.assertEqual(response_stories.status_code, 200)

        stories_list = response_stories.get_json()['data']
        self.assertEqual(len(stories_list), 1)

        story = stories_list[0]
        self.assertTrue(story['mStoryId'] is not None)
        self.assertEqual(story['mTitle'], '')
        self.assertEqual(story['mDescription'], 'description')
        self.assertEqual(story['mFacebookUserId'], 'facebookUserId')
        self.assertEqual(story['mLatitude'], 40.714224)
        self.assertEqual(story['mLongitude'], -73.961452)
        self.assertEqual(story['mFileId'], 1)
        self.assertEqual(story['mFileType'], 'jpg')
        self.assertEqual(story['mFlash'], False)
        self.assertEqual(story['mLocation'], 'San Telmo, Buenos Aires')

    def test_get_all_stories_for_requester_gets_flash_story(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mDescription': 'description', 'mFileType': 'jpg', 'mFlash': True,
                        'mPrivate': False, 'mLatitude': 40.714224, 'mLongitude': -73.961452}

        StoryService.post_new_story(request=request)

        response_stories = StoryService.get_all_stories_for_requester(request.headers)
        self.assertEqual(response_stories.status_code, 200)

        stories_list = response_stories.get_json()['data']
        self.assertEqual(len(stories_list), 1)

        story = stories_list[0]
        self.assertTrue(story['mStoryId'] is not None)
        self.assertEqual(story['mTitle'], '')
        self.assertEqual(story['mDescription'], 'description')
        self.assertEqual(story['mFacebookUserId'], 'facebookUserId')
        self.assertEqual(story['mLatitude'], 40.714224)
        self.assertEqual(story['mLongitude'], -73.961452)
        self.assertEqual(story['mFileId'], 1)
        self.assertEqual(story['mFileType'], 'jpg')
        self.assertEqual(story['mFlash'], True)
        self.assertEqual(story['mLocation'], 'San Telmo, Buenos Aires')

    @patch('appserver.time.Time.Time.now', mock_time_now)
    @patch('appserver.time.Time.Time.timedelta', mock_time_timedelta)
    def test_get_all_stories_for_requester_doesnt_get_caducated_flash_story(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mDescription': 'description', 'mFileType': 'jpg', 'mFlash': True,
                        'mPrivate': False, 'mLatitude': 40.714224, 'mLongitude': -73.961452}

        StoryService.post_new_story(request=request)

        response_stories = StoryService.get_all_stories_for_requester(request.headers)
        self.assertEqual(response_stories.status_code, 200)

        stories_list = response_stories.get_json()['data']
        self.assertEqual(len(stories_list), 0)

    def test_post_new_comment_in_story(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mDescription': 'description', 'mFileType': 'jpg', 'mFlash': False,
                        'mPrivate': False, 'mLatitude': 40.714224, 'mLongitude': -73.961452}

        StoryService.post_new_story(request=request)
        response_stories = StoryService.get_all_stories_for_requester(request.headers)
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        header = {'facebookUserId': 'facebookUserId'}
        comment_json = {'mComment': 'comment'}
        response_comment = StoryService.post_comment(header, comment_json, story_id)

        self.assertEqual(response_comment.status_code, 201)

        modified_story = database.story.find_one({'_id': ObjectId(story_id)})
        list_of_comments = modified_story['comments']
        self.assertEqual(len(list_of_comments), 1)

        comment = list_of_comments[0]

        self.assertEqual(comment['text'], 'comment')
        self.assertEqual(comment['facebook_user_id'], 'facebookUserId')
        self.assertTrue(comment['date'] is not None)


if __name__ == '__main__':
    unittest.main()
