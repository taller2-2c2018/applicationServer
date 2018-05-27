import requests
from appserver import app
from appserver.logger import LoggerFactory

USER = 'nledesma@taller.com.ar'
PASSWORD = 'nledesma'
HOST = 'https://apinodebackend.herokuapp.com/v0/api'
TOKEN_PATH = '/token'
USER_REGISTER_PATH = '/users'

LOGGER = LoggerFactory().get_logger('SharedServerClient')


class SharedServer(object):

    @staticmethod
    def authenticate_user(request_json):
        # TODO finish this and make it connect with the real shared server
        return "Functionality authenticate user not finished"

    @staticmethod
    def register_user(request_json):
        LOGGER.info("Sending request to shared server")
        data = {
            "id": None,
            "_rev": None,
            "password": request_json['password'],
            "username": request_json['username'],
            "facebookAuthToken": request_json['facebookAuthToken']
        }
        return requests.post(HOST + USER_REGISTER_PATH, json=data, headers={'Authorization': SharedServer.get_token()})

    @staticmethod
    def get_token():
        LOGGER.info("Retrieving token from memory")
        token = app.memory_database.get('token')

        if token is None:
            LOGGER.info("Token not found in memory, requesting to shared server")
            data = {
                'username': USER,
                'password': PASSWORD
            }
            response = requests.post(HOST + TOKEN_PATH, json=data)
            LOGGER.info("Got token from shared server: " + response.text)
            app.memory_database.set('app_token', response.json()['token']['token'])
            token = response.json()['token']['token']
        return token
