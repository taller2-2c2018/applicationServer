import time
import datetime
import pytz
from bson.codec_options import CodecOptions
from functools import wraps
from flask import Blueprint, request, jsonify
from appserver import app
import sys

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
            "method": request.method,
            "date_time": datetime.datetime.utcnow(),
            "day": time.strftime('%Y-%m-%d'),
            "hour": time.strftime('%H'),
            "time_elapsed_ms": int((te - ts) * 1000)
        }
        monitor_collection.insert_one(request_data)
        return result

    return decorated_function


@monitor_controller.route('/monitor/')
@monitor
def monitor_route():
    pipeline = [
        {"$group":
            {
                "_id": {"route": "$route", "method": "$method", "day": "$day", "hour": "$hour"},
                "totalRequests": {"$sum": 1},
                "averageTimeElapsed": {"$avg": "$time_elapsed_ms"}
            }
        }
    ]

    aware_colection = monitor_collection.with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=pytz.timezone('America/Argentina/Buenos_Aires')))
    cursor = aware_colection.aggregate(pipeline)
    data =  {}
    for row in cursor:
        print(row, file = sys.stderr)
        request_string = row["_id"]["method"] + row["_id"]["route"]
        if not request_string in data:
            data[request_string] = []

        data[request_string].append({
            "day": row["_id"]["day"],
            "hour": row["_id"]["hour"],
            "avg_time_elapsed": row["averageTimeElapsed"],
            "totalRequests": row["totalRequests"]
        })
    return jsonify(data)
