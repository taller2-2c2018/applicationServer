import datetime


class Time(object):

    @staticmethod
    def now():
        return datetime.datetime.utcnow()

    @staticmethod
    def timedelta(hours):
        return datetime.timedelta(hours=hours)
