import time
from functools import wraps
from redis import Redis
from flask import Blueprint

monitor_controller = Blueprint('monitor', __name__)

# Redis config
redis = Redis(host='redis', port=6379)


def monitor(method):
    @wraps(method)
    def decorated_function(*args, **kwargs):
        redis.incr('hits')
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()
        redis.set('timeElapsed', str(int((te - ts) * 1000)) +  'ms')
        return result

    return decorated_function

@monitor_controller.route('/monitor/')
def monitor_route():
    return redis.get('timeElapsed')