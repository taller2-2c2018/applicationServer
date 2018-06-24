import os
import requests
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger(__name__)
URL = 'https://fcm.googleapis.com/fcm/send'
FIREBASE_SERVER_KEY = os.environ.get('FIREBASE_SERVER_KEY')
if not FIREBASE_SERVER_KEY:
    LOGGER.warn('NO FIREBASE SERVER KEY PRESENT. PUSH NOTIFICATIONS WILL NOT WORK')
else:
    LOGGER.info('Firebase server key is present and loaded')


class FirebaseCloudMessaging(object):

    @staticmethod
    def send_notification(title, body, list_of_firebase_ids):
        try:
            json = {
                "registration_ids": list_of_firebase_ids,
                "notification": {
                    "title": title,
                    "body": body}
            }

            response = requests.post(URL, json=json, headers={'Authorization': FIREBASE_SERVER_KEY})
            LOGGER.info('Sent message successfully. Response: ' + response.json())
        except Exception as e:
            LOGGER.error('There was a problem while sending notification. Reason: ' + str(e))
