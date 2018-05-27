from flask import Response
from flask.ext import status

SUCCESS = 200
NOT_FOUND

class applicationResponse:
    @staticmethod
    def getSuccess(data):
        return Response(data, status.HTTP)