import requests

from appserver import app
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger(__name__)
ANDROID_APP_TOKEN = app.android_app_token

# Facebook host root
HOST = 'https://graph.facebook.com/v3.0'

# Routes
DEBUG_ACCESS_TOKEN_PATH = '/debug_token'


class Facebook(object):

    @staticmethod
    def user_token_is_valid(request_json):
        LOGGER.info('Validating user against facebook')
        payload = {
            'input_token': request_json['facebookAuthToken'],
            'access_token': ANDROID_APP_TOKEN
        }
        response = requests.get(HOST + DEBUG_ACCESS_TOKEN_PATH, params=payload)
        response_json = response.json()

        return Facebook.is_successful(response) and \
            response_json['data']['is_valid'] and \
            response_json['data']['user_id'] == request_json['facebookUserId']

    @staticmethod
    def get_user_identification(request_json):
        LOGGER.info('Getting user first and last name')
        payload = {
            'fields': 'name',
            'access_token': request_json['facebookAuthToken'],
        }
        response = requests.get(HOST + '/' + request_json['facebookUserId'], params=payload)
        response.raise_for_status()

        response_json = response.json()
        full_name = response_json['name']
        names_list = full_name.split()
        request_json['last_name'] = names_list[-1]
        first_names_list = names_list[0: len(names_list) - 1]
        request_json['first_name'] = ' '.join(first_names_list)

    @staticmethod
    def is_successful(response):
        return response.status_code == requests.codes.ok
