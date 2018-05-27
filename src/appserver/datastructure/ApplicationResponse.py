from flask import Response

SUCCESS = 200
CREATED = 201
NOT_FOUND = 404


class ApplicationResponse:
    @staticmethod
    def get_success(data):
        return Response(data, SUCCESS)

    @staticmethod
    def get_created(data):
        return Response(data, CREATED)
