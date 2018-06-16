from appserver.logger import LoggerFactory
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.datastructure.ApplicationResponse import ApplicationResponse
from bson import json_util


LOGGER = LoggerFactory().get_logger('FileService')


class FileService(object):

    @staticmethod
    def get_file(file_id):
        image_response = SharedServer.get_file(file_id)

        LOGGER.info('response from shared server is' + str(image_response))

        return ApplicationResponse.file(image_response)
