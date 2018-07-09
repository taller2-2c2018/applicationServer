import unittest
from unittest.mock import *

from appserver.service.FileService import FileService
from tests.app.TestsCommons import TestsCommons


def mock_get_file_stream(file_id):
    return 'file'


def mock_raise_exception(*args, **kwargs):
    raise Exception('Test')


class FileTests(unittest.TestCase):

    @patch('appserver.externalcommunication.sharedServer.SharedServer.get_file', mock_get_file_stream)
    def test_get_file(self):
        response_file = FileService.get_file(1)

        self.assertEqual(response_file.status_code, 200)
        self.assertTrue(response_file.data is not None)

    @patch('appserver.externalcommunication.sharedServer.SharedServer.get_file', mock_raise_exception)
    def test_get_file_unavailable_service(self):
        response_file = FileService.get_file(1)

        self.assertEqual(response_file.status_code, 503)

    @patch('appserver.externalcommunication.sharedServer.SharedServer.get_file', TestsCommons.mock_get_file)
    def test_get_file_json(self):
        response_file = FileService.get_file_json(1)

        self.assertEqual(response_file.status_code, 200)

        response_json = TestsCommons.get_data_from_response(response_file)
        self.assertEqual(response_json['mFile'], 'file')

    @patch('appserver.externalcommunication.sharedServer.SharedServer.get_file', mock_raise_exception)
    def test_get_file_json_unavailable_service(self):
        response_file = FileService.get_file_json(1)

        self.assertEqual(response_file.status_code, 503)
