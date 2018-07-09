import json

from operator import itemgetter

from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.externalcommunication.FirebaseCloudMessaging import FirebaseCloudMessaging
from appserver.externalcommunication.GoogleMapsApi import GoogleMapsApi
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.logger import LoggerFactory
from appserver.repository.storyRepository import StoryRepository
from appserver.repository.userRepository import UserRepository
from appserver.rules.RelevanceEngine import RelevanceEngine
from appserver.rules.StoryRelevance import StoryRelevance
from appserver.service.FileService import FileService
from appserver.time.Time import Time
from appserver.transformer.MobileTransformer import MobileTransformer
from appserver.validator.jsonValidator import JsonValidator

LOGGER = LoggerFactory().get_logger(__name__)


class StoryService(object):
    @staticmethod
    def post_new_story(headers, story_json):
        validation_response = JsonValidator.validate_story_request(headers, story_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        try:
            file_content = story_json['file']
            upload_file_response = SharedServer.upload_file_as_json(file_content)
            LOGGER.info('Response from shared server: ' + str(upload_file_response))
        except Exception as e:
            LOGGER.error('There was error while getting file from shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not upload file to Shared Server')

        shared_server_response_validation = JsonValidator.validate_shared_server_response(upload_file_response)
        if shared_server_response_validation.hasErrors:
            return ApplicationResponse.bad_request(message=shared_server_response_validation.message)

        file_id = json.loads(upload_file_response.text)['data']['id']

        facebook_id_poster = headers['facebookUserId']
        date = Time.now()
        LOGGER.info('Date is ' + str(date))
        location = GoogleMapsApi.get_location(story_json['mLatitude'], story_json['mLongitude'])
        user = UserRepository.get_profile(facebook_id_poster)
        total_friends = len(user['friendshipList']) - 1
        stories_posted_today = StoryRepository.get_total_stories_posted_today_by_user(facebook_id_poster)
        story_data = MobileTransformer.mobile_story_to_database(story_json, facebook_id_poster, file_id, date,
                                                                location, total_friends, stories_posted_today)

        response = StoryRepository.create_story(story_data)
        LOGGER.info('This is what I got from the database ' + str(response))
        StoryService.__send_new_story_notification(user)

        return ApplicationResponse.created(message='Created story successfully')

    @staticmethod
    def post_new_story_multipart(request):
        validation_response = JsonValidator.validate_story_request_multipart(request)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        try:
            file = request.files
            upload_file_response = SharedServer.upload_file(file)
        except Exception as e:
            LOGGER.error('There was error while getting file from shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not upload file to Shared Server')

        shared_server_response_validation = JsonValidator.validate_shared_server_response(upload_file_response)
        if shared_server_response_validation.hasErrors:
            return ApplicationResponse.bad_request(message=shared_server_response_validation.message)

        file_id = json.loads(upload_file_response.text)['data']['id']

        facebook_id_poster = request.headers['facebookUserId']
        date = Time.now()
        LOGGER.info('Date is ' + str(date))
        location = GoogleMapsApi.get_location(request.form['mLatitude'], request.form['mLongitude'])
        user = UserRepository.get_profile(facebook_id_poster)
        total_friends = len(user['friendshipList']) - 1
        stories_posted_today = StoryRepository.get_total_stories_posted_today_by_user(facebook_id_poster)
        story_data = MobileTransformer.mobile_story_to_database(request.form, facebook_id_poster, file_id, date,
                                                                location, total_friends, stories_posted_today)

        response = StoryRepository.create_story(story_data)
        LOGGER.info('This is what I got from the database ' + str(response))
        StoryService.__send_new_story_notification(user)

        return ApplicationResponse.created(message='Created story successfully')

    @staticmethod
    def __send_new_story_notification(user):
        LOGGER.info('Sending push notification of new story')
        facebook_id_poster = user['facebookUserId']
        user_name = user['first_name'] + ' ' + user['last_name']
        title = user_name + ' ha subido una nueva historia'
        body = {'mMessage': 'Mira la nueva historia de ' + user_name}

        StoryService.__send_notification_to_friends(facebook_id_poster, title, body)

    @staticmethod
    def __send_notification_to_friends(facebook_id_poster, title, body):
        list_of_friends = UserRepository.get_friendship_list(facebook_id_poster)
        if facebook_id_poster in list_of_friends:
            list_of_friends.remove(facebook_id_poster)

        LOGGER.info('Friends to send message to: ' + str(len(list_of_friends)))
        if len(list_of_friends) > 0:
            list_of_firebase_ids = UserRepository.get_firebase_id_list(list_of_friends)
            FirebaseCloudMessaging.send_notification(title=title, body=body, list_of_firebase_ids=list_of_firebase_ids)

    @staticmethod
    def get_all_stories_for_requester(request_header):
        validation_response = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        facebook_user_id = request_header['facebookUserId']
        friendship_list = UserRepository.get_friendship_list(facebook_user_id)
        LOGGER.info('Got friendshipList' + str(friendship_list))
        LOGGER.info('Fetching permantent and flash stories')
        permanent_stories = StoryRepository.get_all_permanent_stories()
        flash_stories = StoryRepository.get_all_valid_flash_stories()

        filtered_stories = StoryService.__get_all_public_and_friends_private_stories(permanent_stories, friendship_list)
        filtered_stories.extend(list(flash_stories))
        filtered_stories = FileService.add_file_to_dictionaries(filtered_stories, 'file_id')
        filtered_stories = StoryService.__add_profile_data_to_stories(filtered_stories)
        filtered_stories = StoryService.__calculate_relevance_of_story(filtered_stories)
        filtered_stories = sorted(filtered_stories, key=itemgetter('relevance'), reverse=True)
        filtered_stories_for_mobile = MobileTransformer.database_list_of_stories_with_relevance_to_mobile(filtered_stories)

        return ApplicationResponse.success(data=filtered_stories_for_mobile)

    @staticmethod
    def get_permanent_stories_of_given_user(requester_facebook_user_id, target_facebook_user_id):
        friendship_list = UserRepository.get_friendship_list(requester_facebook_user_id)
        stories = StoryRepository.get_permanent_stories_from_user(target_facebook_user_id)
        filtered_stories = StoryService.__get_all_public_and_friends_private_stories(stories=stories, friendship_list=friendship_list)
        filtered_stories = FileService.add_file_to_dictionaries(filtered_stories, 'file_id')
        filtered_stories = StoryService.__add_profile_data_to_stories(filtered_stories)
        filtered_stories = StoryService.__calculate_relevance_of_story(filtered_stories)
        filtered_stories = sorted(filtered_stories, key=itemgetter('relevance'), reverse=True)
        filtered_stories_for_mobile = MobileTransformer.database_list_of_stories_with_relevance_to_mobile(
            filtered_stories)

        return filtered_stories_for_mobile

    @staticmethod
    def __get_all_public_and_friends_private_stories(stories, friendship_list):
        stories_list = []
        LOGGER.info('Fetched ' + str(stories.count()) + ' stories')
        for story in stories:
            LOGGER.info('Story to review ' + str(story))
            if (not story['is_private']) or (story['is_private'] and story['facebook_user_id'] in friendship_list):
                LOGGER.info('Adding story to list ' + str(story))

                stories_list.append(story)
        return stories_list

    @staticmethod
    def __calculate_relevance_of_story(stories):
        rated_stories = []
        LOGGER.info('Calculating relevance of stories')
        for story in stories:
            total_friends = story['total_friends']
            total_publications = story['stories_posted_today']
            total_comments = len(story['comments'])
            total_reactions = len(story['reactions'])
            total_hours_passed = Time.hours_passed(story['publication_date'])

            story_relevance = StoryRelevance(total_friends, total_publications, total_comments, total_reactions,
                                             total_hours_passed)
            RelevanceEngine.run_rule(story_relevance)
            story['relevance'] = story_relevance.get_relevance_points()

            rated_stories.append(story)

        return rated_stories

    @staticmethod
    def post_comment(header, json_comment, story_id):
        validation_response = JsonValidator.validate_comment_request(header, json_comment)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        story = StoryRepository.get_story_by_id(story_id)
        if story is None:
            return ApplicationResponse.bad_request(message='No such story was found')

        comment = json_comment['mComment']
        facebook_user_id = header['facebookUserId']
        date = Time.now()
        comment_database = MobileTransformer.mobile_comment_to_database(comment, facebook_user_id, date)
        story['comments'].append(comment_database)

        StoryRepository.update_story_by_id(story_id, story)
        story = StoryRepository.get_story_by_id(story_id)
        LOGGER.info('Added comment to story')

        story = FileService.add_file_to_dictionary(story, 'file_id')
        story = StoryService.__add_profile_data_to_story(story)
        story_for_mobile = MobileTransformer.database_story_to_mobile(story)
        StoryService.__send_new_comment_notification(facebook_user_id, body=story_for_mobile)

        return ApplicationResponse.created('Comment created successfully')

    @staticmethod
    def __send_new_comment_notification(facebook_user_id, body):
        LOGGER.info('Sending comment notification')
        user = UserRepository.get_profile(facebook_user_id)
        user_name = user['first_name'] + ' ' + user['last_name']
        title = user_name + ' ha realizado un comentario en tu historia'

        StoryService.__send_notification_to_friends(facebook_user_id, title, body)

    @staticmethod
    def post_reaction(header, json_reaction, story_id):
        validation_response = JsonValidator.validate_reaction_request(header, json_reaction)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        story = StoryRepository.get_story_by_id(story_id)

        if story is None:
            return ApplicationResponse.bad_request(message='No such story was found')

        poster_facebook_id = header['facebookUserId']
        reaction = json_reaction['mReaction']
        facebook_user_id = header['facebookUserId']
        date = Time.now()
        user_reactions_to_story = StoryService.__search_in_dictionary_with_key_value('facebook_user_id', poster_facebook_id, story['reactions'])
        if len(user_reactions_to_story) > 0:
            story['reactions'] = StoryService.__remove_dictionary_entry_from_list('facebook_user_id',
                                                                                  poster_facebook_id,
                                                                                  story['reactions'])
            old_reaction = user_reactions_to_story[0]['reaction']
            if old_reaction == reaction:
                StoryRepository.update_story_by_id(story_id, story)
                LOGGER.info('Removed reaction successfully')

                return ApplicationResponse.success('Reaction removed successfully')

        comment_database = MobileTransformer.mobile_reaction_to_database(reaction, facebook_user_id, date)
        story['reactions'].append(comment_database)

        StoryRepository.update_story_by_id(story_id, story)
        story = StoryRepository.get_story_by_id(story_id)
        LOGGER.info('Added reaction to story')
        story = FileService.add_file_to_dictionary(story, 'file_id')
        story = StoryService.__add_profile_data_to_story(story)
        story_for_mobile = MobileTransformer.database_story_to_mobile(story)
        StoryService.__send_new_reaction_notification(facebook_user_id, reaction, body=story_for_mobile)

        return ApplicationResponse.created('Reaction created successfully')

    @staticmethod
    def __send_new_reaction_notification(facebook_user_id, reaction, body):
        LOGGER.info('Sending reaction notification')
        user = UserRepository.get_profile(facebook_user_id)
        user_name = user['first_name'] + ' ' + user['last_name']
        title = user_name + ' ha reaccionado con un ' + reaction + ' a tu historia'

        StoryService.__send_notification_to_friends(facebook_user_id, title, body)

    @staticmethod
    def __add_profile_data_to_stories(filtered_stories):
        stories_with_profile_picture = []
        all_users = UserRepository.get_all()

        for story in filtered_stories:
            story = StoryService.__add_profile_data_to_story(story, all_users)

            stories_with_profile_picture.append(story)

        return stories_with_profile_picture

    @staticmethod
    def __add_profile_data_to_story(story, all_users=None):
        if all_users is None:
            all_users = UserRepository.get_all()

        for comment in story['comments']:
            commentor_facebook_user_id = comment['facebook_user_id']
            commentor_user = StoryService.__search_in_dictionary_with_key_value('facebookUserId', commentor_facebook_user_id, all_users)[0]
            comment.update({'first_name': commentor_user['first_name'], 'last_name': commentor_user['last_name']})

        user = StoryService.__search_in_dictionary_with_key_value('facebookUserId', story['facebook_user_id'], all_users)[0]

        profile_picture_id = user['profile_picture_id']
        first_name = user['first_name']
        last_name = user['last_name']
        story.update({'profile_picture_id': profile_picture_id, 'first_name': first_name, 'last_name': last_name,
                      'comments': story['comments']})

        return story

    @staticmethod
    def __search_in_dictionary_with_key_value(key, value, list_of_dictionaries):
        return [element for element in list_of_dictionaries if element[key] == value]

    @staticmethod
    def __remove_dictionary_entry_from_list(key, value, list_of_dictionaries):
        list_of_dictionaries[:] = [element for element in list_of_dictionaries if element.get(key) != value]

        return list_of_dictionaries
