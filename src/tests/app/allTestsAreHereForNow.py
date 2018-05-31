import unittest
from appserver.service.UserService import UserService
from tests.app.testCommons import BaseTestCase
from appserver.app import database


class Tests(BaseTestCase):
    def test_dummy(self):
        self.assertEqual(1, 1)

    # def test_register_user(self):
    #     UserService.register_new_user(
    #         {"username": "username", "password": "password", "facebookAuthToken": "facebookAuthToken"})
    #     inserted_user = database.user.find_one({"username": "username"})
    #
    #     self.assertEqual(inserted_user["username"], "username")
    #     self.assertEqual(inserted_user["password"], "password")
    #     self.assertEqual(inserted_user["facebookAuthToken"], "facebookAuthToken")
    #
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
