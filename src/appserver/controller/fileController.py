from flask import request, Blueprint

from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.service.FileService import FileService

LOGGER = LoggerFactory().get_logger('fileController')
filesEndpoint = Blueprint('filesEndpoint', __name__)


@filesEndpoint.route("/<file_id>", methods=['GET'])
@monitor
def get(file_id):
    LOGGER.info('Getting file with id: ' + str(file_id))
    return FileService().get_file(file_id)