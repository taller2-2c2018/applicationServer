import unittest
import json
from unittest.mock import *

from appserver.app import database
from appserver.service.UserService import UserService
from tests.app.testCommons import BaseTestCase


def mock_user_identification(request_json):
    request_json['last_name'] = 'last_name'
    request_json['first_name'] = 'first_name'


def mock_register_user(request_json):
    shared_server_response = Mock()
    shared_server_response.text = 'text'
    shared_server_response.status_code = 200

    return shared_server_response


class Tests(BaseTestCase):

    @patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
    @patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
    @patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
    def test_register_user(self):
        response_register_user = UserService.register_new_user(
            {'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})

        self.assertEqual(response_register_user.status_code, 201)

        inserted_user = database.user.find_one({'facebookUserId': 'facebookUserId'})

        self.assertEqual(inserted_user['facebookUserId'], 'facebookUserId')
        self.assertEqual(inserted_user['facebookAuthToken'], 'facebookAuthToken')
        self.assertEqual(inserted_user['last_name'], 'last_name')
        self.assertEqual(inserted_user['first_name'], 'first_name')

    @patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
    @patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
    @patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
    def test_register_existing_user_doesnt_add_it_again(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        response_register_user = UserService.register_new_user(
            {'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})

        self.assertEqual(response_register_user.status_code, 400)
        self.assertEqual(response_register_user.get_json()['message'], 'User already registered.')

    @patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
    @patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
    @patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
    def test_create_user_profile(self):
        UserService.register_new_user({'facebookUserId': 'facebookUserId', 'facebookAuthToken': 'facebookAuthToken'})
        response_update_profile = UserService.create_user_profile(
            {'mFirstName': 'name', 'mLastName': 'surname', 'mBirthDate': '01/01/1990', 'mEmail': 'mail@email.com', 'mSex': 'male'},
            {'facebookUserId': 'facebookUserId'})

        self.assertEqual(response_update_profile.status_code, 201)

        inserted_profile = database.user.find_one({'facebookUserId': 'facebookUserId'})

        self.assertEqual(inserted_profile['first_name'], 'name')
        self.assertEqual(inserted_profile['last_name'], 'surname')
        self.assertEqual(inserted_profile['birth_date'], '01/01/1990')
        self.assertEqual(inserted_profile['mail'], 'mail@email.com')
        self.assertEqual(inserted_profile['sex'], 'male')


    @patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
    @patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
    @patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
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

    @patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
    @patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
    @patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
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

    @patch('appserver.externalcommunication.facebook.Facebook.user_token_is_valid', MagicMock(return_value=True))
    @patch('appserver.externalcommunication.facebook.Facebook.get_user_identification', mock_user_identification)
    @patch('appserver.externalcommunication.sharedServer.SharedServer.register_user', mock_register_user)
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
        self.assertEqual(friends_of_requester[0], 'target')

        friends_of_target = database.user.find_one({'facebookUserId': 'target'})['friendshipList']
        self.assertEqual(friends_of_target[0], 'requester')


    # def test_authenticate_user(self):
    #     response = UserService.authenticate_user(
    #         {"username": "username", "password": "password", "facebookAuthToken": "facebookAuthToken"})
    #
    #     self.assertEqual("Functionality authenticate user not finished", response)
    #
    # def test_friendship_request_sent(self):
    #     UserService.register_new_user(
    #         {"username": "requesterUser", "password": "password", "facebookAuthToken": "facebookAuthToken"})
    #     UserService.register_new_user(
    #         {"username": "targetUser", "password": "password", "facebookAuthToken": "facebookAuthToken"})
    #     UserService.send_user_friendship_request({"requesterUser": "requesterUser", "targetUser": "targetUser"})
    #     inserted_friendship = database.friendship.find_one({"requesterUser": "requesterUser"})
    #
    #     self.assertEqual(inserted_friendship["requesterUser"], "requesterUser")
    #     self.assertEqual(inserted_friendship["targetUser"], "targetUser")
    #
    # def test_friendship_request_accepted(self):
    #     UserService.register_new_user(
    #         {"username": "requesterUser", "password": "password", "facebookAuthToken": "facebookAuthToken"})
    #     UserService.register_new_user(
    #         {"username": "targetUser", "password": "password", "facebookAuthToken": "facebookAuthToken"})
    #     UserService.send_user_friendship_request({"requesterUser": "requesterUser", "targetUser": "targetUser"})
    #     UserService.accept_friendship_request(
    #         {"userAccepting": "targetUser", "friendshipWith": "requesterUser"})
    #     friendship_request_after_accepting = database.friendship.find_one({"requesterUser": "requesterUser", "targetUser": "targetUser"})
    #     requester_user = database.user.find_one({"username": "requesterUser"})
    #     accepting_user = database.user.find_one({"username": "targetUser"})
    #
    #     self.assertIsNone(friendship_request_after_accepting)
    #     self.assertTrue("targetUser" in requester_user["friends"])
    #     self.assertTrue("requesterUser" in accepting_user["friends"])


if __name__ == '__main__':
    unittest.main()
