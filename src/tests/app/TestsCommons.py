from appserver.service.StoryService import StoryService
from appserver.service.UserService import UserService


class TestsCommons(object):
    @staticmethod
    def create_default_user(facebook_user_id='facebookUserId'):
        return UserService.register_new_user({'facebookUserId': facebook_user_id,
                                              'facebookAuthToken': 'facebookAuthToken'})

    @staticmethod
    def create_default_story(is_flash=False, title='title', description='description'):
        headers = TestsCommons.default_header()
        story_json = {'file': 'data', 'mTitle': title, 'mDescription': description, 'mFileType': 'jpg',
                      'mFlash': is_flash, 'mPrivate': False, 'mLatitude': 40.714224, 'mLongitude': -73.961452}

        return StoryService.post_new_story(headers=headers, story_json=story_json)

    @staticmethod
    def default_header():
        return {'facebookUserId': 'facebookUserId'}

    @staticmethod
    def get_data_from_response(response):
        return response.get_json()['data']
