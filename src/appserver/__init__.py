from flask import Flask
from appserver.config import Configuration

app = Flask(__name__)

Configuration().set_up_environment()

mongodb = Configuration().set_up_mongodb(app)

redisConnection = Configuration().set_up_redis()

shared_server_host = Configuration.get_shared_server_host_url()
server_user = Configuration.get_server_user()
server_password = Configuration.get_server_password()

with app.app_context():
    app.database = mongodb.db
    app.memory_database = redisConnection
    app.shared_server_host = shared_server_host
    app.server_user = server_user
    app.server_password = server_password
