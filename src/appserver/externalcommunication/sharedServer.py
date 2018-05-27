import requests
import json
from appserver import app
from appserver.logger import LoggerFactory

USER = 'nledesma@taller.com.ar'
PASSWORD = 'nledesma'
HOST = 'https://apinodebackend.herokuapp.com/v0/api/'
TOKEN_PATH = 'token'
USER_REGISTER_PATH = 'users/register'

LOGGER = LoggerFactory().get_logger('SharedServerClient')

class SharedServer(object):


    @staticmethod
    def authenticate_user(request_json):
        # TODO finish this and make it connect with the real shared server
        return "Functionality authenticate user not finished"

    @staticmethod
    def registerUser(request_json):
        data = {
            "id": None,
            "_rev": None,
            "password": request_json['password'],
            "username": request_json['username'],
            "facebookAuthToken": request_json['facebookAuthToken']
        }
        shared_server_response = requests.post(HOST + USER_REGISTER_PATH, json=data, headers={'Authorization': SharedServer.get_token()})

        if shared_server_response.status_code == 200:
            return shared_server_response.json() # json.loads(shared_server_response.text)

    @staticmethod
    def get_token():
        token = app.memory_database.get('token')

        if token is None:
            data = {
                'username': USER,
                'password': PASSWORD
            }
            response = requests.post(HOST + TOKEN_PATH, json=data)
            app.memory_database.set('app_token', response.json()['token']['token'])
            token = response.json()['token']['token']
        return token
