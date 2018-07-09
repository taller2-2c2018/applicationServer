import requests

from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger(__name__)
URL = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='


class GoogleMapsApi(object):

    @staticmethod
    def get_location(latitude, longitude):
        try:
            LOGGER.info('Getting location info from GoogleMaps API')
            complete_url = URL + str(latitude) + ',' + str(longitude)
            response = requests.get(complete_url)
            location = response.json()['results'][2]['formatted_address']

            return location
        except Exception as e:
            LOGGER.warn('There was an error while getting location from google maps. Reason: ' + str(e))
            return 'Unknown'
