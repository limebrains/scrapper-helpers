import os
import pickle

DEBUG = os.environ.get('DEBUG')


def caching(func):
    if DEBUG:
        def decorated(*args):
            key = '{0}_{1}'.format(func.__name__, args[0].replace('/', '').replace(':', ''))
            if Cache.get(key):
                return Cache.get(key)
            response = func(*args)
            Cache.set(key, response)
            return response

        return decorated
    else:
        return func


class Cache:
    @classmethod
    def set(cls, key, response):
        if not os.path.exists("cache"):
            os.makedirs("cache")
        with open(os.path.join(os.path.dirname(__file__), "cache", key), "wb") as file:
            pickle.dump(response, file)

    @classmethod
    def get(cls, key):
        try:
            with open(os.path.join(os.path.dirname(__file__), "cache", key), "rb") as file:
                return pickle.load(file)
        except FileNotFoundError as e:
            return None
