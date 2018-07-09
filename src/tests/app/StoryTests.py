import datetime
from unittest.mock import *

import pytz
from bson import ObjectId

from appserver.app import database
from appserver.service.StoryService import StoryService
from appserver.service.UserService import UserService
from tests.app.BaseTestCase import BaseTestCase
from tests.app.TestsCommons import TestsCommons


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


def mock_raise_exception(*args, **kwargs):
    raise Exception('Test')


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
@patch('appserver.externalcommunication.sharedServer.SharedServer.get_file', TestsCommons.mock_get_file)
@patch('appserver.externalcommunication.GoogleMapsApi.GoogleMapsApi.get_location',
       MagicMock(return_value='San Telmo, Buenos Aires'))
@patch('appserver.externalcommunication.FirebaseCloudMessaging.FirebaseCloudMessaging.send_notification', MagicMock())
class StoryTests(BaseTestCase):

    def test_post_new_story(self):
        TestsCommons.create_default_user()
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'facebookUserId'})

        UserService.accept_friendship_request({'facebookUserId': 'target'}, 'facebookUserId')

        response_post_new_story = TestsCommons.create_default_story()
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
        self.assertEqual(story['total_friends'], 1)
        self.assertEqual(story['stories_posted_today'], 0)

    def test_post_new_story_shared_server_gives_wrong_response(self):
        TestsCommons.create_default_user()

        with patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file_as_json', TestsCommons.mock_bad_request_response):
            response_post_new_story = TestsCommons.create_default_story()
            self.assertEqual(response_post_new_story.status_code, 400)

    def test_post_new_story_no_header_gives_bad_request(self):
        TestsCommons.create_default_user()

        response_post_new_story = StoryService.post_new_story(headers={}, story_json=None)
        self.assertEqual(response_post_new_story.status_code, 400)

    def test_post_new_story_no_json(self):
        TestsCommons.create_default_user()

        response_post_new_story = StoryService.post_new_story(headers=TestsCommons.default_header(), story_json=None)
        self.assertEqual(response_post_new_story.status_code, 400)

    def test_post_new_story_shared_server_unavailable(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file_as_json', mock_raise_exception):
            TestsCommons.create_default_user()

            response_post_new_story = TestsCommons.create_default_story()
            self.assertEqual(response_post_new_story.status_code, 503)

    def test_post_new_story_multipart(self):
        TestsCommons.create_default_user()
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mFileType': 'jpg', 'mFlash': False, 'mPrivate': False, 'mLatitude': 40.714224,
                        'mLongitude': -73.961452}

        response_post_new_story = StoryService.post_new_story_multipart(request=request)
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
        self.assertEqual(story['total_friends'], 0)
        self.assertEqual(story['stories_posted_today'], 0)

    def test_post_new_story_multipart_no_form(self):
        TestsCommons.create_default_user()

        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = None

        response_post_new_story = StoryService.post_new_story_multipart(request=request)

        self.assertEqual(response_post_new_story.status_code, 400)

    def test_post_new_story_multipart_shared_server_exception(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file', mock_raise_exception):
            TestsCommons.create_default_user()

            request = Object()
            request.headers = {'facebookUserId': 'facebookUserId'}
            request.files = {'file': 'data'}
            request.form = {'mFileType': 'jpg', 'mFlash': False, 'mPrivate': False, 'mLatitude': 40.714224,
                            'mLongitude': -73.961452}

            response_post_new_story = StoryService.post_new_story_multipart(request=request)

            self.assertEqual(response_post_new_story.status_code, 503)

    def test_post_new_story_with_wrong_flash_type(self):
        TestsCommons.create_default_user()

        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mFileType': 'jpg', 'mFlash': 'wrong', 'mPrivate': False, 'mLatitude': 40.714224,
                        'mLongitude': -73.961452}

        response_post_new_story = StoryService.post_new_story_multipart(request=request)

        self.assertEqual(response_post_new_story.status_code, 400)

    def test_post_new_story_multipart_shared_server_bad_request(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file', TestsCommons.mock_bad_request_response):
            TestsCommons.create_default_user()

            request = Object()
            request.headers = {'facebookUserId': 'facebookUserId'}
            request.files = {'file': 'data'}
            request.form = {'mFileType': 'jpg', 'mFlash': False, 'mPrivate': False, 'mLatitude': 40.714224,
                            'mLongitude': -73.961452}

            response_post_new_story = StoryService.post_new_story_multipart(request=request)

            self.assertEqual(response_post_new_story.status_code, 400)

    def test_get_all_stories_for_requester_gets_permanent_story(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story(is_flash='False')

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
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
        self.assertTrue('mProfilePictureId' in story)
        self.assertTrue('mFirstName' in story)
        self.assertTrue('mLastName' in story)

    def test_get_all_stories_for_requester_with_no_facebook_user_id_in_header_gives_bad_request(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story(is_flash='False')
        response_stories = StoryService.get_all_stories_for_requester({})

        self.assertEqual(response_stories.status_code, 400)

    def test_get_all_stories_for_requester_gets_with_file_not_found(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story(is_flash='False')

        with patch('appserver.externalcommunication.sharedServer.SharedServer.get_file', TestsCommons.mock_get_file_not_found):
            response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
            self.assertEqual(response_stories.status_code, 200)

            stories_list = response_stories.get_json()['data']
            self.assertEqual(len(stories_list), 0)

    def test_get_all_stories_for_requester_gets_flash_story(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story(is_flash=True)

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
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
        self.assertTrue('mProfilePictureId' in story)
        self.assertTrue('mFirstName' in story)
        self.assertTrue('mLastName' in story)

    @patch('appserver.time.Time.Time.now', mock_time_now)
    def test_get_all_stories_for_requester_gets_stories_ordered_by_relevance(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()
        TestsCommons.create_default_story(title='secondTitle', description='secondDescription')

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
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
        self.assertTrue('mProfilePictureId' in first_story)
        self.assertTrue('mFirstName' in first_story)
        self.assertTrue('mLastName' in first_story)

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
        self.assertTrue('mProfilePictureId' in second_story)
        self.assertTrue('mFirstName' in second_story)
        self.assertTrue('mLastName' in second_story)

        self.assertTrue(second_story['mRelevance'] < first_story['mRelevance'])

    @patch('appserver.time.Time.Time.now', mock_time_now)
    @patch('appserver.time.Time.Time.timedelta', mock_time_timedelta)
    def test_get_all_stories_for_requester_doesnt_get_caducated_flash_story(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story(is_flash=True)

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        self.assertEqual(response_stories.status_code, 200)

        stories_list = response_stories.get_json()['data']
        self.assertEqual(len(stories_list), 0)

    def test_post_new_comment_in_story(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        comment_json = {'mComment': 'comment'}
        response_comment = StoryService.post_comment(TestsCommons.default_header(), comment_json, story_id)

        self.assertEqual(response_comment.status_code, 201)

        modified_story = database.story.find_one({'_id': ObjectId(story_id)})
        list_of_comments = modified_story['comments']
        self.assertEqual(len(list_of_comments), 1)

        comment = list_of_comments[0]

        self.assertEqual(comment['text'], 'comment')
        self.assertEqual(comment['facebook_user_id'], 'facebookUserId')
        self.assertTrue(comment['date'] is not None)

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        response_json = TestsCommons.get_data_from_response(response_stories)[0]

        self.assertTrue(len(response_json['mComments']) == 1)
        comment_data = response_json['mComments'][0]
        self.assertEqual(comment_data['mComment'], 'comment')
        self.assertEqual(comment_data['mFacebookUserId'], 'facebookUserId')
        self.assertEqual(comment_data['mFirstName'], 'first_name')
        self.assertEqual(comment_data['mLastName'], 'last_name')

    def test_post_new_comment_in_story_with_deleted_story_is_bad_request(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']
        with patch('appserver.externalcommunication.sharedServer.SharedServer.get_file', TestsCommons.mock_get_file_not_found):
            StoryService.get_all_stories_for_requester(TestsCommons.default_header())

        comment_json = {'mComment': 'comment'}
        response_comment = StoryService.post_comment(TestsCommons.default_header(), comment_json, story_id)

        self.assertEqual(response_comment.status_code, 400)

    def test_post_new_comment_in_story_with_no_facebook_user_id_in_header_gives_bad_request(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        comment_json = {'mComment': 'comment'}
        response_comment = StoryService.post_comment({}, comment_json, story_id)

        self.assertEqual(response_comment.status_code, 400)

    def test_post_new_comment_in_story_with_no_json_gives_bad_request(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        response_comment = StoryService.post_comment(TestsCommons.default_header(), {}, story_id)

        self.assertEqual(response_comment.status_code, 400)

    def test_post_new_reaction_in_story(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()
        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
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

        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        response_json = TestsCommons.get_data_from_response(response_stories)[0]

        self.assertTrue(len(response_json['mReactions']) == 1)
        self.assertEqual(response_json['mReactions'][0]['mReaction'], 'me gusta')
        self.assertEqual(response_json['mReactions'][0]['mFacebookUserId'], 'facebookUserId')

    def test_post_new_invalid_reaction_in_story(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()
        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        header = {'facebookUserId': 'facebookUserId'}
        reaction_json = {'mReaction': 'invalid reaction'}
        response_comment = StoryService.post_reaction(header, reaction_json, story_id)

        self.assertEqual(response_comment.status_code, 400)

    def test_post_new_reaction_in_inexistent_story(self):
        TestsCommons.create_default_user()

        header = {'facebookUserId': 'facebookUserId'}
        reaction_json = {'mReaction': 'me gusta'}
        response_comment = StoryService.post_reaction(header, reaction_json, 666)

        self.assertEqual(response_comment.status_code, 400)

    def test_post_different_reaction_in_story_changes_reaction(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()
        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        header = {'facebookUserId': 'facebookUserId'}
        reaction_json = {'mReaction': 'me divierte'}
        StoryService.post_reaction(header, reaction_json, story_id)
        reaction_json['mReaction'] = 'me gusta'
        response_comment = StoryService.post_reaction(header, reaction_json, story_id)

        self.assertEqual(response_comment.status_code, 201)

        modified_story = database.story.find_one({'_id': ObjectId(story_id)})
        list_of_reactions = modified_story['reactions']
        self.assertEqual(len(list_of_reactions), 1)

        reaction = list_of_reactions[0]

        self.assertEqual(reaction['reaction'], 'me gusta')
        self.assertEqual(reaction['facebook_user_id'], 'facebookUserId')
        self.assertTrue(reaction['date'] is not None)

    def test_post_same_reaction_in_story_removes_it(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_story()
        response_stories = StoryService.get_all_stories_for_requester(TestsCommons.default_header())
        story_id = response_stories.get_json()['data'][0]['mStoryId']

        header = {'facebookUserId': 'facebookUserId'}
        reaction_json = {'mReaction': 'me gusta'}
        StoryService.post_reaction(header, reaction_json, story_id)
        response_comment = StoryService.post_reaction(header, reaction_json, story_id)

        self.assertEqual(response_comment.status_code, 200)

        modified_story = database.story.find_one({'_id': ObjectId(story_id)})
        list_of_reactions = modified_story['reactions']
        self.assertEqual(len(list_of_reactions), 0)
