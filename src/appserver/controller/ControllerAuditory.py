from functools import wraps

from appserver.datastructure.ApplicationResponse import ApplicationResponse
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger(__name__)


def controller_auditory(method):
    @wraps(method)
    def audit_controller(*args, **kwargs):
        try:
            LOGGER.info('Auditing controller')
            return method(*args, **kwargs)
        except Exception as e:
            error_message = 'Endpoint failed. Reason: ' + str(e)
            LOGGER.error(error_message)
            return ApplicationResponse.internal_server_error(message=error_message)

    return audit_controller
