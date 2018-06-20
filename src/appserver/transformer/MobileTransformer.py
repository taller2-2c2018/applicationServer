class MobileTransformer(object):

    @staticmethod
    def database_list_of_stories_to_mobile(stories):
        list_of_stories = []
        for story in stories:
            story_for_mobile = {
                'mTitle': MobileTransformer.__optional_value(story, 'title'),
                'mDescription': MobileTransformer.__optional_value(story, 'description'),
                'mFacebookUserId': story['facebook_user_id'],
                'mLatitude': story['latitude'],
                'mLongitude': story['longitude'],
                'mFileId': story['file_id'],
                'mFileType': story['file_type']
            }
            list_of_stories.append(story_for_mobile)

        return list_of_stories

    @staticmethod
    def mobile_story_to_database(request_form, facebook_user_id, file_id, date):

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
            'file_type': request_form['mFileType']
        }

        return story_data


    @staticmethod
    def __optional_value(dictionary, key, optional_value=''):
        return dictionary[key] if key in dictionary else optional_value
