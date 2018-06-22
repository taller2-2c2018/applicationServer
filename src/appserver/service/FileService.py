from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger('FileService')


class FileService(object):

    @staticmethod
    def get_file(file_id):
        try:
            image_response = SharedServer.get_file(file_id)
            LOGGER.info('response from shared server is' + str(image_response))
        except Exception as e:
            LOGGER.error('There was error while getting file from shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not get file from Shared Server')

        return ApplicationResponse.file(image_response)
