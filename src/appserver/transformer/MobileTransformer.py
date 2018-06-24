class MobileTransformer(object):

    @staticmethod
    def database_list_of_stories_to_mobile(stories):
        list_of_stories = []
        for story in stories:
            story_for_mobile = {
                'mStoryId': story['_id'],
                'mTitle': MobileTransformer.__optional_value(story, 'title'),
                'mDescription': MobileTransformer.__optional_value(story, 'description'),
                'mFacebookUserId': story['facebook_user_id'],
                'mLatitude': story['latitude'],
                'mLongitude': story['longitude'],
                'mFileId': story['file_id'],
                'mFileType': story['file_type'],
                'mFlash': story['is_flash'],
                'mLocation': story['location']
            }
            list_of_stories.append(story_for_mobile)

        return list_of_stories

    @staticmethod
    def mobile_story_to_database(request_form, facebook_user_id, file_id, date, location):
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
            'reactions': []
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
