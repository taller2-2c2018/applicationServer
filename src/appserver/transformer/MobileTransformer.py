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
        story_data = {
            'title': MobileTransformer.__optional_value(request_form, 'mTitle'),
            'description': MobileTransformer.__optional_value(request_form, 'mDescription'),
            'facebook_user_id': facebook_user_id,
            'is_flash': request_form['mFlash'],
            'is_private': request_form['mPrivate'],
            'latitude': request_form['mLatitude'],
            'longitude': request_form['mLongitude'],
            'publication_date': date,
            'file_id': file_id,
            'file_type': request_form['mFileType'],
            'location': location,
            'comments': []
        }

        return story_data

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
    def mobile_comment_to_database(comment, date):
        return {'text': comment, 'date': date}
