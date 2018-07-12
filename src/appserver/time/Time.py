from datetime import datetime, timedelta, date, time

import pytz


class Time(object):

    @staticmethod
    def now():
        return datetime.now(pytz.timezone(zone='America/Argentina/Buenos_Aires'))

    @staticmethod
    def convert_time_argentina_time(date_time):
        return date_time.astimezone(pytz.timezone("America/Argentina/Buenos_Aires"))

    @staticmethod
    def timedelta(hours):
        return timedelta(hours=hours)

    @staticmethod
    def start_of_today():
        return datetime.combine(date.today(), time())

    @staticmethod
    def hours_passed(date_to_compare):
        time_difference = Time.now() - date_to_compare
        return time_difference / timedelta(hours=1)
