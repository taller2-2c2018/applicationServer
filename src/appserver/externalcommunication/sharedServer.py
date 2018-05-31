import requests
from appserver import app
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger('SharedServerClient')
TOKEN_PATH = '/token'
USER_PATH = '/users'

HOST = app.shared_server_host
SERVER_USER = app.server_user
SEVER_PASSWORD = app.server_password


class SharedServer(object):

    @staticmethod
    def authenticate_user(request_json):
        # TODO finish this and make it connect with the real shared server
        LOGGER.info("Validating user, hardcoded data response")
        return {"metadata": {"version": "string"}, "token": {"expiresAt": 0, "token": "defaultUserToken"}}

    @staticmethod
    def register_user(request_json):
        LOGGER.info("Sending request to shared server: " + HOST + USER_PATH)
        data = {
            "id": None,
            "_rev": None,
            "password": request_json['password'],
            "username": request_json['username'],
            "facebookAuthToken": request_json['facebookAuthToken']
        }
        return SharedServer.request_shared_server(json=data, path=HOST + USER_PATH)

    @staticmethod
    def get_token():
        LOGGER.info("Retrieving token from memory")
        token = app.memory_database.get('token')

        if token is None:
            LOGGER.info("Token not found in memory, requesting to shared server")
            data = {
                'username': SERVER_USER,
                'password': SEVER_PASSWORD
            }
            response = requests.post(HOST + TOKEN_PATH, json=data)
            LOGGER.info("Got token from shared server: " + response.text)
            app.memory_database.set('app_token', response.json()['token']['token'])
            token = response.json()['token']['token']
        return token

    @staticmethod
    def request_shared_server(json, path):
        return requests.post(path, json=json, headers={'Authorization': SharedServer.get_token()})
