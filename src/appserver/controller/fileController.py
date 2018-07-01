from flask import Blueprint

from appserver.logger import LoggerFactory
from appserver.monitor.monitor import monitor
from appserver.service.FileService import FileService
from appserver.validator.authValidator import secure
from appserver.controller.ControllerAuditory import controller_auditory

LOGGER = LoggerFactory().get_logger('fileController')
filesEndpoint = Blueprint('filesEndpoint', __name__)


@filesEndpoint.route('/stream/<file_id>', methods=['GET'])
@monitor
@secure
@controller_auditory
def get_file(file_id):
    LOGGER.info('Getting file with id: ' + str(file_id))
    return FileService().get_file(file_id)


@filesEndpoint.route('/<file_id>', methods=['GET'])
@monitor
@secure
@controller_auditory
def get_file_as_json(file_id):
    LOGGER.info('Getting file with id: ' + str(file_id))
    return FileService().get_file_json(file_id)
