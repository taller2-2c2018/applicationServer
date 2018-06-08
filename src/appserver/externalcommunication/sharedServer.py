import requests
from appserver import app
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger('SharedServerClient')
TOKEN_PATH = '/token'
USER_PATH = '/users'
AUTH_PATH = '/authorization'

HOST = app.shared_server_host
SERVER_USER = app.server_user
SEVER_PASSWORD = app.server_password


class SharedServer(object):

    @staticmethod
    def authenticate_user(request_json):
        LOGGER.info("Authenticating user against sharedServer")
        data = {
            "facebook_id": request_json['facebookUserId'],
        }
        response = SharedServer.request_shared_server(json=data, path=HOST + AUTH_PATH)
        return response.json()

    @staticmethod
    def register_user(request_json):
        LOGGER.info("Sending request to shared server: " + HOST + USER_PATH)
        data = {
            "id": None,
            "_rev": None,
            "nombre": request_json["first_name"],
            "apellido": request_json['last_name'],
            "facebook_id": request_json['facebookUserId'],
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
