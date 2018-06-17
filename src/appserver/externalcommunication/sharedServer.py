import requests
from appserver import app
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger('SharedServerClient')
TOKEN_PATH = '/token'
USER_PATH = '/users'
AUTH_PATH = '/authorization'
FILES_PATH = '/files'

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
        response = SharedServer.post_json_shared_server(json=data, path=HOST + AUTH_PATH)
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
        return SharedServer.post_json_shared_server(json=data, path=HOST + USER_PATH)

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
    def post_json_shared_server(json, path):
        return requests.post(path, json=json, headers={'Authorization': SharedServer.get_token()})

    @staticmethod
    def upload_file(file):
        LOGGER.info("Sending file to shared server: " + HOST + FILES_PATH)

        return SharedServer.post_file_shared_server(file=file, path=HOST + FILES_PATH)

    @staticmethod
    def get_file(file_id):
        LOGGER.info("Sending file to shared server: " + HOST + FILES_PATH + str(file_id))
        url_of_image = HOST + FILES_PATH + '/' + str(file_id)

        return requests.get(url_of_image, headers={'Authorization': SharedServer.get_token()})

    @staticmethod
    def post_file_shared_server(file, path):
        data_for_shared_server = {
            'id': '',
            '_rev': '',
            'created_at': '',
            'updated_at': '',
            'filename': '',
            'resource': '',
            'size': ''
        }
        return requests.post(path, files=file, data=data_for_shared_server, headers={'Authorization': SharedServer.get_token()})
