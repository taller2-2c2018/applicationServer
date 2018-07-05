class MobileTransformer(object):

    @staticmethod
    def database_list_of_stories_with_relevance_to_mobile(stories):
        list_of_stories = []
        for story in stories:
            story_for_mobile = MobileTransformer.database_story_to_mobile(story)
            story_for_mobile['mRelevance'] = story['relevance']
            list_of_stories.append(story_for_mobile)

        return list_of_stories

    @staticmethod
    def database_story_to_mobile(story):
        return {
                'mStoryId': story['_id'],
                'mTitle': MobileTransformer.__optional_value(story, 'title'),
                'mDescription': MobileTransformer.__optional_value(story, 'description'),
                'mFacebookUserId': story['facebook_user_id'],
                'mLatitude': story['latitude'],
                'mLongitude': story['longitude'],
                'mFileId': story['file_id'],
                'mFileType': story['file_type'],
                'mFlash': story['is_flash'],
                'mLocation': story['location'],
                'mComments': MobileTransformer.__database_comments_to_mobile(story['comments']),
                'mReactions': MobileTransformer.__database_reactions_to_mobile(story['reactions']),
                'mProfilePictureId': story['profile_picture_id'],
                'mFirstName': story['first_name'],
                'mLastName': story['last_name']
            }

    @staticmethod
    def mobile_story_to_database(request_form, facebook_user_id, file_id, date, location, total_friends, stories_posted_today):
        flash = MobileTransformer.__string_to_boolean_value(dictionary=request_form, attribute='mFlash')
        private = MobileTransformer.__string_to_boolean_value(dictionary=request_form, attribute='mPrivate')

        story_data = {
            'title': MobileTransformer.__optional_value(request_form, 'mTitle'),
            'description': MobileTransformer.__optional_value(request_form, 'mDescription'),
            'facebook_user_id': facebook_user_id,
            'is_flash': flash,
            'is_private': private,
            'latitude': request_form['mLatitude'],
            'longitude': request_form['mLongitude'],
            'publication_date': date,
            'file_id': file_id,
            'file_type': request_form['mFileType'],
            'location': location,
            'comments': [],
            'reactions': [],
            'total_friends': total_friends,
            'stories_posted_today': stories_posted_today
        }

        return story_data

    @staticmethod
    def __string_to_boolean_value(dictionary, attribute):
        if not isinstance(dictionary[attribute], bool):
            return 'true' == dictionary[attribute].lower()
        else:
            return dictionary[attribute]

    @staticmethod
    def __optional_value(dictionary, key, optional_value=''):
        return dictionary[key] if key in dictionary else optional_value

    @staticmethod
    def database_profile_to_mobile(database_profile, stories):
        profile_data = {
            'mFirstName': database_profile['first_name'],
            'mLastName': database_profile['last_name'],
            'mBirthDate': database_profile['birth_date'],
            'mEmail': database_profile['mail'],
            'mSex': database_profile['sex'],
            'mProfilePictureId': MobileTransformer.__optional_value(database_profile, 'profile_picture_id', None),
            'mFileTypeProfilePicture': MobileTransformer.__optional_value(database_profile, 'file_type_profile_picture', None),
            'mFriendshipList': database_profile['friendshipList'],
            'mStories': stories
        }

        return profile_data

    @staticmethod
    def mobile_profile_to_database(request_json):
        return {'first_name': request_json['mFirstName'], 'last_name': request_json['mLastName'],
                'birth_date': request_json['mBirthDate'], 'mail': request_json['mEmail'], 'sex': request_json['mSex']}

    @staticmethod
    def mobile_comment_to_database(comment, facebook_user_id, date):
        return {'text': comment, 'facebook_user_id': facebook_user_id, 'date': date}

    @staticmethod
    def mobile_reaction_to_database(reaction, facebook_user_id, date):
        return {'reaction': reaction, 'facebook_user_id': facebook_user_id, 'date': date}

    @staticmethod
    def database_list_of_friends_to_mobile(friends_list):
        mobile_friend_list = []
        for friend in friends_list:
            mobile_friend = {
                'mFirebaseId': friend['firebase_id'],
                'mBirthDate': friend['birth_date'],
                'mFacebookUserId': friend['facebookUserId']
            }
            mobile_friend_list.append(mobile_friend)

        return mobile_friend_list

    @staticmethod
    def database_list_of_users_to_mobile(user_list):
        mobile_users = []

        for user in user_list:
            mobile_user = {
                'mFacebookUserId': user['facebookUserId'],
                'mFirebaseId': MobileTransformer.__optional_value(user, 'firebase_id', None),
                'mFirstName': MobileTransformer.__optional_value(user, 'first_name', None),
                'mLastName': MobileTransformer.__optional_value(user, 'last_name', None),
                'mProfilePictureId': MobileTransformer.__optional_value(user, 'profile_picture_id', None)
            }

            mobile_users.append(mobile_user)

        return mobile_users

    @staticmethod
    def __database_comments_to_mobile(comments_list):
        mobile_comment_list = []

        for comment in comments_list:
            mobile_comment = {
                'mComment': comment['text'],
                'mFacebookUserId': comment['facebook_user_id'],
                'mDate': comment['date']
            }

            mobile_comment_list.append(mobile_comment)

        return mobile_comment_list

    @staticmethod
    def __database_reactions_to_mobile(reactions_list):
        mobile_reaction_list = []

        for reaction in reactions_list:
            mobile_reaction = {
                'mReaction': reaction['reaction'],
                'mFacebookUserId': reaction['facebook_user_id'],
                'mDate': reaction['date']
            }

            mobile_reaction_list.append(mobile_reaction)

        return mobile_reaction_list

    @staticmethod
    def mobile_register_to_database(request_json):
        return {
            'facebookUserId': request_json['facebookUserId'],
            'facebookAuthToken': request_json['facebookAuthToken'],
            'friendshipList': [request_json['facebookUserId']],
            'profile_picture_id': '',
            'birth_date': '',
            'mail': '',
            'sex': '',
            'firebase_id': MobileTransformer.__optional_value(request_json, 'firebase_id', ''),
            'first_name': request_json['first_name'],
            'last_name': request_json['last_name']
        }
