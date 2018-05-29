from flask import Response

SUCCESS = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404


class ApplicationResponse:
    @staticmethod
    def get_success(data):
        return Response(data, SUCCESS)

    @staticmethod
    def get_bad_request(data):
        return Response(data, BAD_REQUEST)

    @staticmethod
    def get_created(data):
        return Response(data, CREATED)
