import json

from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.externalcommunication.FirebaseCloudMessaging import FirebaseCloudMessaging
from appserver.externalcommunication.facebook import Facebook
from appserver.externalcommunication.sharedServer import SharedServer
from appserver.logger import LoggerFactory
from appserver.repository.friendshipRepository import FriendshipRepository
from appserver.repository.userRepository import UserRepository
from appserver.service.FileService import FileService
from appserver.service.StoryService import StoryService
from appserver.transformer.MobileTransformer import MobileTransformer
from appserver.validator.databaseValidator import DatabaseValidator
from appserver.validator.jsonValidator import JsonValidator

LOGGER = LoggerFactory().get_logger('UserService')


class UserService(object):
    @staticmethod
    def register_new_user(request_json):
        validation_response = JsonValidator.validate_user_register(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)
        LOGGER.info('Register user Json is valid')

        try:
            facebook_token_is_valid = Facebook.user_token_is_valid(request_json)
            if not facebook_token_is_valid:
                return ApplicationResponse.bad_request(message='Invalid Facebook credentials')
            LOGGER.info('Facebook user token is valid')

            Facebook.get_user_identification(request_json)
        except Exception as e:
            LOGGER.error('There was error while getting validating user with Facebook. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not get validated from Facebook')

        validation_existing_user = DatabaseValidator.validate_is_existing_user(request_json)
        if validation_existing_user.hasErrors:
            return ApplicationResponse.bad_request(message=validation_existing_user.message)

        try:
            shared_server_response = SharedServer.register_user(request_json)
            LOGGER.info('Response from shared server: ' + str(shared_server_response))
            shared_server_response_validation = JsonValidator.validate_shared_server_response(
                shared_server_response)
            if shared_server_response_validation.hasErrors:
                return ApplicationResponse.bad_request(message=shared_server_response_validation.message)
        except Exception as e:
            LOGGER.error('There was error while getting registering user into shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not register user to Shared Server')

        user_registration = MobileTransformer.mobile_register_to_database(request_json)

        UserRepository.insert(user_registration)

        return ApplicationResponse.created(message='Created user successfully')

    @staticmethod
    def authenticate_user(request_json):
        validation_response = JsonValidator.validate_user_authenticate(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        try:
            facebook_token_is_valid = Facebook.user_token_is_valid(request_json)
            if not facebook_token_is_valid:
                return ApplicationResponse.bad_request(message='Invalid Facebook credentials')
            LOGGER.info('Facebook user token is valid')
        except Exception as e:
            LOGGER.error('There was error while authenticating user with Facebook. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not get authenticated by Facebook')

        try:
            response = SharedServer.authenticate_user(request_json)
            LOGGER.info('Response gotten from server: ' + str(response))
            shared_server_response_validation = JsonValidator.validate_shared_server_authorization(response)
            if shared_server_response_validation.hasErrors:
                return ApplicationResponse.bad_request(message=shared_server_response_validation.message)
        except Exception as e:
            LOGGER.error('There was error while getting authenticating user by shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not authenticate user by Shared Server')

        data = response['data']
        facebook_id = data['facebook_id']
        token = data['token']
        expires_at = data['expires_at']
        UserRepository.update_user_token(facebook_id, token, expires_at)
        firebase_id = request_json['firebaseId']
        UserRepository.update_firebase_id(facebook_id, firebase_id)
        response = {'message': 'Logged in successfully.', 'token': token}

        return ApplicationResponse.success(data=response)

    @staticmethod
    def send_user_friendship_request(request_json, request_header):
        validation_header = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_header.hasErrors:
            return ApplicationResponse.bad_request(message=validation_header.message)

        validation_response = JsonValidator.validate_user_friendship_post(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        target = request_json['mTargetUsername']
        if UserRepository.username_exists(target):
            requester = request_header['facebookUserId']
            message = request_json['mDescription']
            if UserService.__can_send_request(requester=requester, target=target):
                friendship_to_insert = {'requester': requester, 'target': target, 'message': message}
                FriendshipRepository.insert(friendship_to_insert)
                UserService.__send_notification_of_friendship_request(facebook_id_requester=requester,
                                                                      facebook_id_target=target,
                                                                      requester_message=message)

                return ApplicationResponse.success(message='Friendship request sent successfully')
            else:
                return ApplicationResponse.bad_request(message='Friendship request was already sent')

        return ApplicationResponse.bad_request(message='Target username doesn\'t exist')

    @staticmethod
    def __send_notification_of_friendship_request(facebook_id_requester, facebook_id_target, requester_message):
        requester = UserRepository.get_profile(facebook_id_requester)
        requester_name = requester['first_name'] + ' ' + requester['last_name']
        target = UserRepository.get_profile(facebook_id_target)
        title = requester_name + ' quiere ser tu amigo'
        body = {'mMessage': requester_message}

        try:
            FirebaseCloudMessaging.send_notification(title=title, body=body, list_of_firebase_ids=target['firebase_id'])
        except:
            LOGGER.warn('No firebase Id found for user, not sending push notification')

    @staticmethod
    def get_friendship_requests(request_header):
        validation_response = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        username = request_header['facebookUserId']
        friendship_list = FriendshipRepository.get_friendship_requests_of_username(username)
        friendship_list = UserService.__add_profile_data_to_list_of_users(friendship_list)

        return ApplicationResponse.success(data=friendship_list)

    @staticmethod
    def __add_profile_data_to_list_of_users(friendship_list):
        all_users = UserRepository.get_all()

        for friendship in friendship_list:
            user = UserService.__search_dictionaries('facebookUserId', friendship['requester'], all_users)[0]

            profile_picture_id = user['profile_picture_id']
            first_name = user['first_name']
            last_name = user['last_name']
            friendship.update(
                {'mProfilePictureId': profile_picture_id, 'mFirstName': first_name, 'mLastName': last_name})

        return friendship_list

    @staticmethod
    def __search_dictionaries(key, value, list_of_dictionaries):
        return [element for element in list_of_dictionaries if element[key] == value]

    @staticmethod
    def get_user_friends(request_header):
        requester_facebook_id = request_header['facebookUserId']
        list_of_friends = UserRepository.get_friendship_list(requester_facebook_id)
        if requester_facebook_id in list_of_friends:
            list_of_friends.remove(requester_facebook_id)

        friends_list = UserRepository.get_friends_information_list(list_of_friends)
        mobile_friend_list = MobileTransformer.database_list_of_friends_to_mobile(friends_list)

        return ApplicationResponse.success(data=mobile_friend_list)

    @staticmethod
    def accept_friendship_request(request_header, who_i_am_accepting):
        validation_response = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        user_that_accepts_friendship = request_header['facebookUserId']
        if UserService.__can_accept_request(requester=who_i_am_accepting, target=user_that_accepts_friendship):
            FriendshipRepository.remove_friendship(user_that_accepts_friendship, who_i_am_accepting)
            UserRepository.add_friendship(user_that_accepts_friendship, who_i_am_accepting)
            UserService.__send_notification_of_friendship_accepted(facebook_id_acceptor=user_that_accepts_friendship,
                                                                   facebook_id_target=who_i_am_accepting)

            return ApplicationResponse.success(message='Friendship was accepted successfully')

        return ApplicationResponse.bad_request(message='Friendship request couldn\'t be found')

    @staticmethod
    def reject_friendship_request(request_header, target_user):
        validation_response = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        user_that_rejects_friendship = request_header['facebookUserId']
        if FriendshipRepository.friendship_request_exists(user_that_rejects_friendship, target_user):
            FriendshipRepository.remove_friendship(user_that_rejects_friendship, target_user)

            return ApplicationResponse.success(message='Friendship was rejected successfully')

        return ApplicationResponse.bad_request(message='Friendship request couldn\'t be found')

    @staticmethod
    def __send_notification_of_friendship_accepted(facebook_id_acceptor, facebook_id_target):
        acceptor = UserRepository.get_profile(facebook_id_acceptor)
        acceptor_name = acceptor['first_name'] + ' ' + acceptor['last_name']
        target = UserRepository.get_profile(facebook_id_target)
        title = acceptor_name + ' ha aceptado tu solicitud de amistad'
        body = {'mMessage': 'Tú y ' + acceptor_name + ' ahora son amigos'}

        try:
            FirebaseCloudMessaging.send_notification(title=title, body=body, list_of_firebase_ids=target['firebase_id'])
        except:
            LOGGER.warn('No firebase Id found for user, not sending push notification')

    @staticmethod
    def modify_user_profile(request_json, request_header):
        validation_response = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        validation_response = JsonValidator.validate_profile_datafields(request_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        facebook_user_id = request_header['facebookUserId']
        profile_to_create = MobileTransformer.mobile_profile_to_database(request_json)
        UserRepository.modify_profile(facebook_user_id, profile_to_create)

        return ApplicationResponse.created(message='Created profile successfully')

    @staticmethod
    def get_user_profile(request, facebook_user_id):
        requester_facebook_user_id = request.headers['facebookUserId']
        stories = StoryService.get_permanent_stories_of_given_user(requester_facebook_user_id, facebook_user_id)

        profile = UserRepository.get_profile(facebook_user_id)
        profile = FileService.add_file_to_dictionary_default_value(profile, profile['profile_picture_id'])
        profile_data = MobileTransformer.database_profile_to_mobile(profile, stories)

        return ApplicationResponse.success(data=profile_data)

    @staticmethod
    def modify_user_profile_picture(request):
        request_validation = JsonValidator.validate_profile_picture(request)
        if request_validation.hasErrors:
            return ApplicationResponse.bad_request(message=request_validation.message)

        try:
            file = request.files
            LOGGER.info('FILE ' + str(request.files))
            LOGGER.info('Sending file to shared server ' + str(file))
            upload_file_response = SharedServer.upload_file(file)
            LOGGER.info('Response from shared server: ' + str(upload_file_response))
            shared_server_response_validation = JsonValidator.validate_shared_server_response(upload_file_response)

            if shared_server_response_validation.hasErrors:
                return ApplicationResponse.bad_request(message=shared_server_response_validation.message)
        except Exception as e:
            LOGGER.error('There was error while uploading file to shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not upload file to Shared Server')

        response_json = json.loads(upload_file_response.text)
        file_type = request.form['mFileType']
        profile_update = {'profile_picture_id': response_json['data']['id'],
                          'file_type_profile_picture': file_type}
        UserRepository.modify_profile(request.headers['facebookUserId'], profile_update)

        return ApplicationResponse.success(message='Profile picture updated')

    @staticmethod
    def modify_user_profile_picture_json(headers, file_json):
        validation_response = JsonValidator.validate_modify_profile_picture_json(headers, file_json)
        if validation_response.hasErrors:
            return ApplicationResponse.bad_request(message=validation_response.message)

        try:
            file_content = file_json['file']
            upload_file_response = SharedServer.upload_file_as_json(file_content)
            LOGGER.info('Response from shared server: ' + str(upload_file_response))
        except Exception as e:
            LOGGER.error('There was error while getting file from shared server. Reason:' + str(e))
            return ApplicationResponse.service_unavailable(message='Could not upload file to Shared Server')

        shared_server_response_validation = JsonValidator.validate_shared_server_response(upload_file_response)
        if shared_server_response_validation.hasErrors:
            return ApplicationResponse.bad_request(message=shared_server_response_validation.message)

        response_json = json.loads(upload_file_response.text)
        file_type = file_json['mFileType']
        profile_update = {'profile_picture_id': response_json['data']['id'],
                          'file_type_profile_picture': file_type}
        UserRepository.modify_profile(headers['facebookUserId'], profile_update)

        return ApplicationResponse.success(message='Profile picture updated')

    @staticmethod
    def get_user_list(request_header):
        validation_header = JsonValidator.validate_header_has_facebook_user_id(request_header)
        if validation_header.hasErrors:
            return ApplicationResponse.bad_request(message=validation_header.message)

        user_facebook_id = request_header['facebookUserId']
        user_list = UserRepository.get_all_but(user_facebook_id)
        user_list = FileService.add_file_to_dictionaries_optional(user_list, 'profile_picture_id')
        user_list = MobileTransformer.database_list_of_users_to_mobile(user_list)

        return ApplicationResponse.success(data=user_list)

    @staticmethod
    def __can_send_request(requester, target):
        return not UserRepository.friendship_exists(target_facebook_id=target, requester_facebook_id=requester) and not \
            FriendshipRepository.friendship_request_exists(target_facebook_id=target, requester_facebook_id=requester)

    @staticmethod
    def __can_accept_request(requester, target):
        return not UserRepository.friendship_exists(target_facebook_id=target, requester_facebook_id=requester) and \
               FriendshipRepository.friendship_request_exists(target_facebook_id=target,
                                                              requester_facebook_id=requester)
