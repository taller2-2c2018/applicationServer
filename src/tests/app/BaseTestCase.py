import unittest

from appserver.app import app, database


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
        try:
            database.story.drop()
        except Exception:
            pass
        database.create_collection('story')

    def tearDown(self):
        database.drop_collection('friendship')
        database.drop_collection('user')
        database.drop_collection('story')
        app.memory_database.flushall()
        app.memory_database.flushdb()
