from unittest.mock import *

from appserver.app import database
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


def mock_authenticate_user(request_json):
    shared_server_response = {
        'code': 200,
        'data': {
            'facebook_id': 'facebookId',
            'token': 'token',
            'expires_at': 'expires_at'
        }
    }

    return shared_server_response


def bad_request(*args, **kwargs):
    shared_server_response = Mock()
    shared_server_response.text = 'text'
    shared_server_response.status_code = 400

    return shared_server_response


def bad_request_json(*args, **kwargs):
    return {'code': 400}


def mock_get_file(file_id):
    file = Object()
    file.content = b'file'

    return file


def mock_get_file_stream(file_id):
    return 'file'


def mock_raise_exception(*args, **kwargs):
    raise Exception('Test')


class Object(object):
    pass


@patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
@patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
@patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
@patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file', mock_upload_file)
@patch('appserver.externalcommunication.FirebaseCloudMessaging.FirebaseCloudMessaging.send_notification', MagicMock())
class UserTests(BaseTestCase):

    def test_register_user(self):
        response_register_user = TestsCommons.create_default_user()

        self.assertEqual(response_register_user.status_code, 201)

        inserted_user = database.user.find_one({'facebookUserId': 'facebookUserId'})

        self.assertEqual(inserted_user['facebookUserId'], 'facebookUserId')
        self.assertEqual(inserted_user['facebookAuthToken'], 'facebookAuthToken')
        self.assertEqual(inserted_user['last_name'], 'last_name')
        self.assertEqual(inserted_user['first_name'], 'first_name')

    def test_register_user_bad_input(self):
        response_register_user = UserService.register_new_user({})

        self.assertEqual(response_register_user.status_code, 400)

    def test_register_user_no_json(self):
        response_register_user = UserService.register_new_user(None)

        self.assertEqual(response_register_user.status_code, 400)

    def test_register_user_unavailable_facebook_service(self):
        with patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', mock_raise_exception):
            response_register_user = TestsCommons.create_default_user()

            self.assertEqual(response_register_user.status_code, 503)

    def test_register_user_facebook_token_invalid(self):
        with patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid',
                   MagicMock(return_value=False)):
            response_register_user = TestsCommons.create_default_user()

            self.assertEqual(response_register_user.status_code, 400)

    def test_register_user_unavailable_shared_service(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_raise_exception):
            response_register_user = TestsCommons.create_default_user()

            self.assertEqual(response_register_user.status_code, 503)

    def test_register_user_invalid_for_shared_server(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', bad_request):
            response_register_user = TestsCommons.create_default_user()

            self.assertEqual(response_register_user.status_code, 400)

    def test_register_existing_user_doesnt_add_it_again(self):
        TestsCommons.create_default_user()
        response_register_user = UserService.register_new_user(
            {'facebookUserId': 'facebookUserId',
             'facebookAuthToken': 'facebookAuthToken'})

        self.assertEqual(response_register_user.status_code, 400)
        self.assertEqual(response_register_user.get_json()['message'], 'User already registered.')

    def test_create_user_profile(self):
        TestsCommons.create_default_user()
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

    def test_create_user_profile_no_json(self):
        TestsCommons.create_default_user()
        response_update_profile = UserService.modify_user_profile(None, {'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_update_profile.status_code, 400)

    def test_create_user_profile_no_header(self):
        TestsCommons.create_default_user()
        response_update_profile = UserService.modify_user_profile(None, None)

        self.assertEqual(response_update_profile.status_code, 400)

    @patch('appserver.externalcommunication.sharedServer.SharedServer.authenticate_user', mock_authenticate_user)
    def test_authenticate_user(self):
        response_authenticate = UserService.authenticate_user({'facebookUserId': 'facebookUserId',
                                                               'facebookAuthToken': 'facebookAuthToken',
                                                               'firebaseId': 'firebaseId'})

        self.assertEqual(response_authenticate.status_code, 200)

        response_json = response_authenticate.get_json()['data']

        self.assertEqual(response_json['token'], 'token')

    def test_authenticate_user_no_json(self):
        response_authenticate = UserService.authenticate_user(None)

        self.assertEqual(response_authenticate.status_code, 400)

    def test_authenticate_user_bad_request(self):
        response_authenticate = UserService.authenticate_user({})

        self.assertEqual(response_authenticate.status_code, 400)

    @patch('appserver.externalcommunication.sharedServer.SharedServer.authenticate_user', mock_authenticate_user)
    def test_authenticate_user_invalid_token(self):
        with patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid',
                   MagicMock(return_value=False)):
            response_authenticate = UserService.authenticate_user({'facebookUserId': 'facebookUserId',
                                                                   'facebookAuthToken': 'facebookAuthToken',
                                                                   'firebaseId': 'firebaseId'})

            self.assertEqual(response_authenticate.status_code, 400)

    @patch('appserver.externalcommunication.sharedServer.SharedServer.authenticate_user', mock_authenticate_user)
    def test_authenticate_user_unavailable_facebook_service(self):
        with patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', mock_raise_exception):
            response_authenticate = UserService.authenticate_user({'facebookUserId': 'facebookUserId',
                                                                   'facebookAuthToken': 'facebookAuthToken',
                                                                   'firebaseId': 'firebaseId'})

            self.assertEqual(response_authenticate.status_code, 503)

    @patch('appserver.externalcommunication.sharedServer.SharedServer.authenticate_user', mock_raise_exception)
    def test_authenticate_user_unavailable_shared_service(self):
        response_authenticate = UserService.authenticate_user({'facebookUserId': 'facebookUserId',
                                                               'facebookAuthToken': 'facebookAuthToken',
                                                               'firebaseId': 'firebaseId'})

        self.assertEqual(response_authenticate.status_code, 503)

    @patch('appserver.externalcommunication.sharedServer.SharedServer.authenticate_user', bad_request_json)
    def test_authenticate_user_invalid_response_shared_service(self):
        response_authenticate = UserService.authenticate_user({'facebookUserId': 'facebookUserId',
                                                               'facebookAuthToken': 'facebookAuthToken',
                                                               'firebaseId': 'firebaseId'})

        self.assertEqual(response_authenticate.status_code, 400)

    def test_get_user_profile(self):
        TestsCommons.create_default_user()
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
        TestsCommons.create_default_user()
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        response_send_friendship_request = UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_send_friendship_request.status_code, 200)

        inserted_friendship = database.friendship.find_one({'requester': 'facebookUserId'})

        self.assertEqual(inserted_friendship['requester'], 'facebookUserId')
        self.assertEqual(inserted_friendship['target'], 'target')
        self.assertEqual(inserted_friendship['message'], 'Add me to your friend list')

    def test_send_friendship_request_twice_fails(self):
        TestsCommons.create_default_user()
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.send_user_friendship_request({'mTargetUsername': 'target',
                                                  'mDescription': 'Add me to your friend list'},
                                                 {'facebookUserId': 'facebookUserId'})
        response_send_friendship_request = UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_send_friendship_request.status_code, 400)

    def test_send_friendship_request_no_firebase_available(self):
        with patch('appserver.externalcommunication.FirebaseCloudMessaging.FirebaseCloudMessaging.send_notification',
                   mock_raise_exception):
            TestsCommons.create_default_user()
            UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
            response_send_friendship_request = UserService.send_user_friendship_request(
                {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
                {'facebookUserId': 'facebookUserId'})

            self.assertEqual(response_send_friendship_request.status_code, 200)

            inserted_friendship = database.friendship.find_one({'requester': 'facebookUserId'})

            self.assertEqual(inserted_friendship['requester'], 'facebookUserId')
            self.assertEqual(inserted_friendship['target'], 'target')
            self.assertEqual(inserted_friendship['message'], 'Add me to your friend list')

    def test_send_friendship_request_no_header(self):
        TestsCommons.create_default_user()
        response_send_friendship_request = UserService.send_user_friendship_request(None, None)

        self.assertEqual(response_send_friendship_request.status_code, 400)

    def test_send_friendship_request_no_json(self):
        TestsCommons.create_default_user()
        response_send_friendship_request = UserService.send_user_friendship_request(None, {
            'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_send_friendship_request.status_code, 400)

    def test_send_friendship_request_non_existant_user(self):
        TestsCommons.create_default_user()
        response_send_friendship_request = UserService.send_user_friendship_request(
            {'mTargetUsername': 'nonExistantUser', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_send_friendship_request.status_code, 400)

    def test_get_friendship_requests(self):
        TestsCommons.create_default_user()
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'facebookUserId'})
        friendship_response = UserService.get_friendship_requests({'facebookUserId': 'target'})

        self.assertEqual(friendship_response.status_code, 200)

        friendship_list = friendship_response.get_json()['data']

        self.assertEqual(len(friendship_list), 1)
        friendship_request = friendship_list[0]
        self.assertEqual(friendship_request['requester'], 'facebookUserId')
        self.assertEqual(friendship_request['target'], 'target')
        self.assertEqual(friendship_request['message'], 'Add me to your friend list')
        self.assertTrue('mProfilePictureId' in friendship_request)
        self.assertTrue('mFirstName' in friendship_request)
        self.assertTrue('mLastName' in friendship_request)

    def test_get_friendship_requests_no_json(self):
        friendship_response = UserService.get_friendship_requests(None)

        self.assertEqual(friendship_response.status_code, 400)

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

        self.assertEqual(len(friendship_list), 0)

        friends_of_requester = database.user.find_one({'facebookUserId': 'requester'})['friendshipList']
        self.assertTrue('target' in friends_of_requester)

        friends_of_target = database.user.find_one({'facebookUserId': 'target'})['friendshipList']
        self.assertTrue('requester' in friends_of_target)

    def test_accept_friendship_request_without_firebase(self):
        with patch('appserver.externalcommunication.FirebaseCloudMessaging.FirebaseCloudMessaging.send_notification',
                   mock_raise_exception):
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

            self.assertEqual(len(friendship_list), 0)

            friends_of_requester = database.user.find_one({'facebookUserId': 'requester'})['friendshipList']
            self.assertTrue('target' in friends_of_requester)

            friends_of_target = database.user.find_one({'facebookUserId': 'target'})['friendshipList']
            self.assertTrue('requester' in friends_of_target)

    def test_send_friendship_request_with_an_existing_friendship(self):
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.register_new_user({'facebookUserId': 'requester', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'requester'})

        UserService.accept_friendship_request({'facebookUserId': 'target'}, 'requester')
        response_send_request = UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'requester'})

        self.assertEqual(response_send_request.status_code, 400)

    def test_accept_friendship_request_no_json(self):
        accept_response = UserService.accept_friendship_request(None, 'requester')

        self.assertEqual(accept_response.status_code, 400)

    def test_accept_friendship_request_without_request(self):
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.register_new_user({'facebookUserId': 'requester', 'facebookAuthToken': 'facebookAuthToken'})

        accept_response = UserService.accept_friendship_request({'facebookUserId': 'target'}, 'requester')

        self.assertEqual(accept_response.status_code, 400)

    def test_reject_friendship_request(self):
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.register_new_user({'facebookUserId': 'requester', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.send_user_friendship_request(
            {'mTargetUsername': 'target', 'mDescription': 'Add me to your friend list'},
            {'facebookUserId': 'requester'})

        reject_response = UserService.reject_friendship_request({'facebookUserId': 'target'}, 'requester')

        self.assertEqual(reject_response.status_code, 200)

        friendship_response = UserService.get_friendship_requests({'facebookUserId': 'target'})

        self.assertEqual(friendship_response.status_code, 200)

        friendship_list = friendship_response.get_json()['data']

        self.assertEqual(len(friendship_list), 0)

    def test_reject_friendship_request_no_json(self):
        reject_response = UserService.reject_friendship_request(None, 'requester')

        self.assertEqual(reject_response.status_code, 400)

    def test_reject_friendship_request_without_request(self):
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken'})
        UserService.register_new_user({'facebookUserId': 'requester', 'facebookAuthToken': 'facebookAuthToken'})

        reject_response = UserService.reject_friendship_request({'facebookUserId': 'target'}, 'requester')

        self.assertEqual(reject_response.status_code, 400)

    def test_get_friends(self):
        UserService.register_new_user({'facebookUserId': 'target', 'facebookAuthToken': 'facebookAuthToken',
                                       'firebase_id': '1234'})
        UserService.register_new_user({'facebookUserId': 'requester', 'facebookAuthToken': 'facebookAuthToken',
                                       'firebase_id': '5678'})
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
        self.assertEqual(friend['mFacebookUserId'], 'requester')

    def test_modify_profile_picture_stream(self):
        TestsCommons.create_default_user()
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = {'mFileType': 'jpg'}
        modify_profile_response = UserService.modify_user_profile_picture(request)

        self.assertEqual(modify_profile_response.status_code, 200)

        updated_user = database.user.find_one({'facebookUserId': 'facebookUserId'})
        self.assertEqual(updated_user['profile_picture_id'], 1)
        self.assertEqual(updated_user['file_type_profile_picture'], 'jpg')

    def test_modify_profile_picture_json(self):
        TestsCommons.create_default_user()
        file_json = {'file': 'data', 'mFileType': 'jpg'}
        modify_profile_response = UserService.modify_user_profile_picture_json(TestsCommons.default_header(), file_json)

        self.assertEqual(modify_profile_response.status_code, 200)

        updated_user = database.user.find_one({'facebookUserId': 'facebookUserId'})
        self.assertEqual(updated_user['profile_picture_id'], 1)
        self.assertEqual(updated_user['file_type_profile_picture'], 'jpg')

    def test_modify_profile_picture_invalid_format_json(self):
        TestsCommons.create_default_user()
        file_json = {'file': 'data', 'mFileType': 'txt'}
        modify_profile_response = UserService.modify_user_profile_picture_json(TestsCommons.default_header(), file_json)

        self.assertEqual(modify_profile_response.status_code, 400)

    def test_modify_profile_picture_stream_no_form(self):
        TestsCommons.create_default_user()
        request = Object()
        request.headers = {'facebookUserId': 'facebookUserId'}
        request.files = {'file': 'data'}
        request.form = None
        modify_profile_response = UserService.modify_user_profile_picture(request)

        self.assertEqual(modify_profile_response.status_code, 400)

    def test_modify_profile_picture_stream_shared_server_unavailable(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file', mock_raise_exception):
            TestsCommons.create_default_user()
            request = Object()
            request.headers = {'facebookUserId': 'facebookUserId'}
            request.files = {'file': 'data'}
            request.form = {'mFileType': 'jpg'}
            modify_profile_response = UserService.modify_user_profile_picture(request)

            self.assertEqual(modify_profile_response.status_code, 503)

    def test_modify_profile_picture_stream_shared_server_bad_request(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file', bad_request):
            TestsCommons.create_default_user()
            request = Object()
            request.headers = {'facebookUserId': 'facebookUserId'}
            request.files = {'file': 'data'}
            request.form = {'mFileType': 'jpg'}
            modify_profile_response = UserService.modify_user_profile_picture(request)

            self.assertEqual(modify_profile_response.status_code, 400)

    def test_modify_profile_picture_json_no_form(self):
        TestsCommons.create_default_user()
        modify_profile_response = UserService.modify_user_profile_picture_json(TestsCommons.default_header(), None)

        self.assertEqual(modify_profile_response.status_code, 400)

    def test_modify_profile_picture_json_shared_server_unavailable(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file_as_json',
                   mock_raise_exception):
            TestsCommons.create_default_user()
            file_json = {'file': 'data', 'mFileType': 'jpg'}
            modify_profile_response = UserService.modify_user_profile_picture_json(TestsCommons.default_header(),
                                                                                   file_json)

            self.assertEqual(modify_profile_response.status_code, 503)

    def test_modify_profile_picture_json_shared_server_bad_request(self):
        with patch('appserver.externalcommunication.sharedServer.SharedServer.upload_file', bad_request):
            TestsCommons.create_default_user()
            file_json = {'file': 'data', 'mFileType': 'jpg'}
            modify_profile_response = UserService.modify_user_profile_picture_json(TestsCommons.default_header(),
                                                                                   file_json)

            self.assertEqual(modify_profile_response.status_code, 400)

    def test_get_user_profile_after_adding_profile_picture(self):
        TestsCommons.create_default_user()
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

    def test_list_users_returns_all_but_oneself(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_user(facebook_user_id='otherUserOne')
        TestsCommons.create_default_user(facebook_user_id='otherUserTwo')

        user_list_response = UserService.get_user_list(TestsCommons.default_header())

        self.assertEqual(user_list_response.status_code, 200)

        user_list = TestsCommons.get_data_from_response(user_list_response)

        self.assertEqual(len(user_list), 2)
        self.assertTrue(user_list[0]['mFacebookUserId'] is not 'facebookUserId')
        self.assertTrue(user_list[1]['mFacebookUserId'] is not 'facebookUserId')

    def test_list_users_invalid_header(self):
        TestsCommons.create_default_user()
        TestsCommons.create_default_user(facebook_user_id='otherUserOne')

        user_list_response = UserService.get_user_list({})

        self.assertEqual(user_list_response.status_code, 400)
