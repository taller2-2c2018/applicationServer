import unittest

from appserver.app import app, database


# TODO now you need a local instance running 'sudo mongod' for this to run
# TODO and also set this environment variable in the test run 'MONGO_URL', 'mongodb://localhost:27017/'
class BaseTestCase(unittest.TestCase):
    @staticmethod
    def create_app():
        return app

    def setUp(self):
        try:
            database.friendship.drop()
        except Exception:
            pass
        database.create_collection('friendship')
        try:
            database.user.drop()
        except Exception:
            pass
        database.create_collection('user')

    def tearDown(self):
        database.drop_collection('friendship')
        database.drop_collection('user')
