from flask import Blueprint

from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.service.FileService import FileService
from appserver.validator.authValidator import secure

LOGGER = LoggerFactory().get_logger('fileController')
filesEndpoint = Blueprint('filesEndpoint', __name__)


@filesEndpoint.route("/<file_id>", methods=['GET'])
@monitor
@secure
def get(file_id):
    LOGGER.info('Getting file with id: ' + str(file_id))
    return FileService().get_file(file_id)
