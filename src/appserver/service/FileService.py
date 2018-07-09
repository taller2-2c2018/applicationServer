from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.logger import LoggerFactory
from appserver.repository.storyRepository import StoryRepository
from appserver.validator.jsonValidator import JsonValidator

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

    @staticmethod
    def add_file_to_dictionaries(dictionaries, key_dictionaries):
        filtered_stories = []
        for story in dictionaries:
            try:
                story_with_file = FileService.add_file_to_dictionary(story, key_dictionaries)
                filtered_stories.append(story_with_file)
            except:
                pass

        return filtered_stories

    @staticmethod
    def add_file_to_dictionary(dictionary, key_dictionary):
        file_response = SharedServer.get_file(dictionary[key_dictionary])
        shared_server_response_validation = JsonValidator.validate_file_response(file_response)

        if shared_server_response_validation.hasErrors:
            if shared_server_response_validation.message == 404:
                StoryRepository.delete_story_by_id(dictionary['__id'])
            raise Exception
        else:
            decoded_content = file_response.content.decode('utf-8', 'ignore')
            dictionary.update({'file': decoded_content})
            return dictionary

    @staticmethod
    def add_file_to_dictionaries_optional(user_list, key_dictionaries):
        user_with_image_list = []
        for user in user_list:
            user = FileService.add_file_to_dictionary_optional(user, key_dictionaries)
            user_with_image_list.append(user)

        return user_with_image_list

    @staticmethod
    def add_file_to_dictionary_optional(dictionary, key_dictionary):
        file_response = SharedServer.get_file(dictionary[key_dictionary])
        shared_server_response_validation = JsonValidator.validate_file_response(file_response)

        if not shared_server_response_validation.hasErrors:
            decoded_content = file_response.content.decode('utf-8', 'ignore')
            dictionary.update({'file': decoded_content})

        return dictionary
