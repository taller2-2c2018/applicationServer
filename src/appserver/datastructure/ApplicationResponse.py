from flask import Response
import json

SUCCESS = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404


class ApplicationResponse:
    @staticmethod
    def success(data):
        return Response(data, status=SUCCESS, mimetype='application/json')

    @staticmethod
    def success_message(message):
        message_json = ApplicationResponse.__message_json(CREATED, message)
        return Response(message_json, status=SUCCESS, mimetype='application/json')

    @staticmethod
    def created(data):
        return Response(data, status=CREATED, mimetype='application/json')

    @staticmethod
    def created_message(message):
        message_json = ApplicationResponse.__message_json(CREATED, message)
        return Response(message_json, status=CREATED, mimetype='application/json')

    @staticmethod
    def bad_request_message(error_message):
        message_json = ApplicationResponse.__message_json(BAD_REQUEST, error_message)
        return Response(message_json, status=BAD_REQUEST, mimetype='application/json')

    @staticmethod
    def __message_json(status, message):
        response = {'status': status, 'message': message}
        return json.dumps(response)
