import time
from functools import wraps
from flask import Blueprint, request, jsonify
from appserver import app

monitor_controller = Blueprint('monitor', __name__)

monitor_collection = app.database.monitor


def monitor(method):
    @wraps(method)
    def decorated_function(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()

        request_data = {
            "route": request.path,
            "date_time": time.strftime("%d/%m/%Y %H:%M:%S"),
            "day_hour": time.strftime('%Y%m%d_%H'),
            "time_elapsed": int((te - ts) * 1000)
        }
        monitor_collection.insert_one(request_data)
        return result

    return decorated_function


@monitor_controller.route('/monitor/')
def monitor_route():
    cursor = monitor_collection.find()
    data = []
    for row in cursor:
        data.append({
            "route": row["route"],
            "date_time": row["date_time"],
            "day_hour": row["day_hour"],
            "time_elapsed": row["time_elapsed"]
        })
    return jsonify(data)
