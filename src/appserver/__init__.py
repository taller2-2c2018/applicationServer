from flask import Flask
from flask_cors import CORS

from appserver.config import Configuration
from appserver.logger import LoggerFactory

LOGGER = LoggerFactory().get_logger('ConfigurationSetup')


app = Flask(__name__)
CORS(app)


Configuration().set_up_environment()

mongodb = Configuration().set_up_mongodb(app)

redisConnection = Configuration().set_up_redis()

shared_server_host = Configuration.get_shared_server_host_url()
LOGGER.info("Shared server host: " + shared_server_host)
server_user = Configuration.get_server_user()
LOGGER.info("Server user: " + server_user)
server_password = Configuration.get_server_password()
LOGGER.info("Server password: " + server_password)
android_app_token = Configuration.get_android_app_token()
LOGGER.info("Android app token: " + android_app_token)


with app.app_context():
    app.database = mongodb.db
    app.memory_database = redisConnection
    app.shared_server_host = shared_server_host
    app.server_user = server_user
    app.server_password = server_password
    app.android_app_token = android_app_token
