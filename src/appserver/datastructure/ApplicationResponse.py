from flask import Response
import json

SUCCESS = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404


class ApplicationResponse:
    @staticmethod
    def success(message='', data=None):
        return ApplicationResponse.__json_response(SUCCESS, message, data)

    @staticmethod
    def created(message='', data=None):
        return ApplicationResponse.__json_response(CREATED, message, data)

    @staticmethod
    def bad_request(message=''):
        return ApplicationResponse.__json_response(BAD_REQUEST, message, None)

    @staticmethod
    def file(file):
        return Response(file, mimetype='application/octet-stream')

    @staticmethod
    def __create_json(status, message="", data=None):
        response = {'status': status, 'message': message, 'data': data}
        return json.dumps(response)

    @staticmethod
    def __json_response(status, message, data):
        message_json = ApplicationResponse.__create_json(status, message, data)
        return Response(message_json, status=status, mimetype='application/json')
