import unittest
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
