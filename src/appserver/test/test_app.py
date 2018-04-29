from appserver.app import app
import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the status code of the response

        self.assertEqual(result.status_code, 200)


if __name__ == '__main__':
    unittest.main()
