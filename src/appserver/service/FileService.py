from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger(__name__)


class FileService(object):

    @staticmethod
    def get_file(file_id):
        try:
            file_response = SharedServer.get_file(file_id)
            LOGGER.info('response from shared server is' + str(file_response))
        except Exception as e:
            LOGGER.error('There was error while getting file from shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not get file from Shared Server')

        return ApplicationResponse.file(file_response)

    @staticmethod
    def get_file_json(file_id):
        try:
            LOGGER.info('Getting file from shared server')
            file_response = SharedServer.get_file(file_id)
            LOGGER.info('response from shared server is' + str(file_response))

            decoded_content = file_response.content.decode('utf-8', 'ignore')

            data = {'mFile': decoded_content}
        except Exception as e:
            LOGGER.error('There was error while getting file from shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not get file from Shared Server')

        return ApplicationResponse.success(data=data)
