import json

from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.externalcommunication.GoogleMapsApi import GoogleMapsApi
from appserver.externalcommunication.FirebaseCloudMessaging import FirebaseCloudMessaging
from appserver.logger import LoggerFactory
from appserver.repository.storyRepository import StoryRepository
from appserver.repository.userRepository import UserRepository
from appserver.transformer.MobileTransformer import MobileTransformer
from appserver.validator.jsonValidator import JsonValidator
from appserver.time.Time import Time

LOGGER = LoggerFactory().get_logger(__name__)


class StoryService(object):
    @staticmethod
    def post_new_story(request):
        validation_response = JsonValidator.validate_story_request(request)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        try:
            file = request.files
            upload_file_response = SharedServer.upload_file(file)
            LOGGER.info("Response from shared server: " + str(upload_file_response))
        except Exception as e:
            LOGGER.error('There was error while getting file from shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not upload file to Shared Server')

        shared_server_response_validation = JsonValidator.validate_shared_server_register_user(upload_file_response)
        if shared_server_response_validation.hasErrors:
            return ApplicationResponse.bad_request(message=shared_server_response_validation.message)

        file_id = json.loads(upload_file_response.text)['data']['id']

        request_form = request.form
        facebook_id_poster = request.headers['facebookUserId']
        date = Time.now()
        LOGGER.info('Date is ' + str(date))
        location = GoogleMapsApi.get_location(request_form['mLatitude'], request_form['mLongitude'])
        user = UserRepository.get_profile(facebook_id_poster)
        total_friends = len(user['friendshipList']) - 1
        stories_posted_today = StoryRepository.get_total_stories_posted_today_by_user(facebook_id_poster)
        story_data = MobileTransformer.mobile_story_to_database(request_form, facebook_id_poster, file_id, date,
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

        facebook_user_id = request_header["facebookUserId"]
        friendship_list = UserRepository.get_friendship_list(facebook_user_id)
        LOGGER.info("Got friendshipList" + str(friendship_list))
        LOGGER.info('Fetching permantent and flash stories')
        permanent_stories = StoryRepository.get_all_permanent_stories()
        flash_stories = StoryRepository.get_all_valid_flash_stories()

        filtered_stories = StoryService.__get_all_public_and_friends_private_stories(permanent_stories, friendship_list)
        filtered_stories.extend(list(flash_stories))
        filtered_stories = StoryService.__calculate_relevance_of_story(filtered_stories)
        filtered_stories_for_mobile = MobileTransformer.database_list_of_stories_to_mobile(filtered_stories)

        return ApplicationResponse.success(data=filtered_stories_for_mobile)

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
            # TODO cuenta mágica
            # TODO story['mRelevance'] = cuenta mágica
            story['relevance'] = 0.0
            rated_stories.append(story)

        return rated_stories

    @staticmethod
    def get_permanent_stories_of_given_user(requester_facebook_user_id, target_facebook_user_id):
        friendship_list = UserRepository.get_friendship_list(requester_facebook_user_id)
        stories = StoryRepository.get_permanent_stories_from_user(target_facebook_user_id)
        return StoryService.__get_all_public_and_friends_private_stories(stories=stories, friendship_list=friendship_list)

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
        LOGGER.info('Added comment to story')
        StoryService.__send_new_comment_notification(facebook_user_id, comment)

        return ApplicationResponse.created('Comment created successfully')

    @staticmethod
    def __send_new_comment_notification(facebook_user_id, comment):
        LOGGER.info('Sending comment notification')
        user = UserRepository.get_profile(facebook_user_id)
        user_name = user['first_name'] + ' ' + user['last_name']
        title = user_name + ' ha realizado un comentario en tu historia'
        body = {'mMessage': user_name + ": " + comment}

        StoryService.__send_notification_to_friends(facebook_user_id, title, body)

    @staticmethod
    def post_reaction(header, json_reaction, story_id):
        validation_response = JsonValidator.validate_reaction_request(header, json_reaction)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        story = StoryRepository.get_story_by_id(story_id)

        if story is None:
            return ApplicationResponse.bad_request(message='No such story was found')

        reaction = json_reaction['mReaction']
        facebook_user_id = header['facebookUserId']
        date = Time.now()
        comment_database = MobileTransformer.mobile_reaction_to_database(reaction, facebook_user_id, date)
        story['reactions'].append(comment_database)

        StoryRepository.update_story_by_id(story_id, story)
        LOGGER.info('Added reaction to story')
        StoryService.__send_new_reaction_notification(facebook_user_id, reaction)

        return ApplicationResponse.created('Reaction created successfully')

    @staticmethod
    def __send_new_reaction_notification(facebook_user_id, reaction):
        LOGGER.info('Sending reaction notification')
        user = UserRepository.get_profile(facebook_user_id)
        user_name = user['first_name'] + ' ' + user['last_name']
        title = user_name + ' ha reaccionado a tu historia'
        body = {'mMessage': user_name + ": ha reaccionado con un " + reaction}

        StoryService.__send_notification_to_friends(facebook_user_id, title, body)
