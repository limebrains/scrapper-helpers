import os
import pickle

DEBUG = os.environ.get('DEBUG')
CACHE_DIR = os.environ.get('CACHE_DIR', '/var/tmp/scrapper-helpers/')


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
        print(key, response, CACHE_DIR)
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        print(os.path.join(CACHE_DIR, key))
        with open(os.path.join(CACHE_DIR, key), "wb") as file:
            pickle.dump(response, file)

    @classmethod
    def get(cls, key):
        print(key, CACHE_DIR)
        try:
            with open(os.path.join(CACHE_DIR, key), "rb") as file:
                return pickle.load(file)
        except FileNotFoundError as e:
            return None
