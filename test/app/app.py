import unittest
from appserver.service.UserService import UserService


class Tests(unittest.TestCase):
    def test_example(self):
        response = UserService.authenticate_user({"username": "data", "password": "password", "facebookAuthToken": "asd"})
        self.assertEqual("Functionality authenticate user not finished", response)


if __name__ == '__main__':
    unittest.main()
