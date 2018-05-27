from flask import Flask
from appserver.config import Configuration

app = Flask(__name__)
mongodb = Configuration().set_up_mongodb(app)
redisConnection = Configuration().set_up_redis()
with app.app_context():
    app.database = mongodb.db
    app.memory_database = redisConnection

