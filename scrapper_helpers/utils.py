#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pickle
import random
import hashlib
import subprocess
import unicodedata

try:
    from __builtin__ import unicode
except ImportError:
    unicode = lambda x, *args: x

DEBUG = os.environ.get('DEBUG')
CACHE_DIR = os.environ.get('CACHE_DIR', '/var/tmp/scrapper-helpers/')
MAX_FILENAME_LENGTH = os.environ.get(
    'MAX_FILENAME_LENGTH',
)
if not MAX_FILENAME_LENGTH:
    MAX_FILENAME_LENGTH = subprocess.check_output("getconf NAME_MAX /", shell=True).strip()
MAX_FILENAME_LENGTH = int(MAX_FILENAME_LENGTH)

USER_AGENTS = [
    'Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
    '42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/'
    '9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
]


def key_md5(*args):
    """This method creates an MD5 from the input parameters, used for caching filename"""
    return hashlib.md5("".join(str(args)).encode("utf-8")).hexdigest()


def key_sha1(*args):
    """This method creates an SHA-1 from the input parameters, used for caching filename"""
    return hashlib.sha1("".join(str(args)).encode("utf-8")).hexdigest()


def default_key_func(*args):
    """This method creates the default string representation of the input parameters, used for caching filename"""
    return '{0}'.format(str(args[0]).replace('/', '').replace(':', ''))[:MAX_FILENAME_LENGTH]


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    html_codes = (
        ("'", '&#39;'),
        ('"', '&quot;'),
        ('>', '&gt;'),
        ('<', '&lt;'),
        ('&', '&amp;')
    )
    for code in html_codes:
        s = s.replace(code[1], code[0])
    return s


def replace_all(text, dic):
    """
    This method returns the input string, but replaces its characters according to the input dictionary.
    :param text: input string
    :param dic: dictionary containing the changes. key is the character that's supposed to be changed and value is
            the desired value
    :rtype: string
    :return: String with the according characters replaced
    """
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def normalize_text(text, lower=True, replace_spaces='_'):
    """
    This method returns the input string, but normalizes is it for use in the url.
    :param text: input string
    :rtype: string
    :return: Normalized string. lowercase, no diacritics, '-' instead of ' '
    """
    try:
        unicoded = unicode(text, 'utf8')
    except TypeError:
        unicoded = text
    if lower:
        unicoded = unicoded.lower()
    normalized = unicodedata.normalize('NFKD', unicoded)
    encoded_ascii = normalized.encode('ascii', 'ignore')
    decoded_utf8 = encoded_ascii.decode("utf-8")
    if replace_spaces:
        decoded_utf8 = decoded_utf8.replace(" ", replace_spaces)
    return decoded_utf8


def _float(number, default=None):
    """Returns a float created from the given string or default if the cast is not possible."""
    return get_number_from_string(number, float, default)


def _int(number, default=None):
    """Returns an int created from the given string or default if the cast is not possible."""
    return get_number_from_string(number, int, default)


def get_number_from_string(s, number_type, default):
    """Returns a numeric value of number_type created from the given string or default if the cast is not possible."""
    try:
        return number_type(s.replace(",", "."))
    except ValueError:
        return default


def get_random_user_agent():
    """ Randoms user agent to prevent "python" user agent
    :return: Random user agent from USER_AGENTS
    :rtype: str
    """
    return random.choice(USER_AGENTS)


def flatten(container):
    """ Flattens a list
    :param container: list with nested lists
    :type container: list
    :return: list with elements that were nested in container
    :rtype: list
    """
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i


def caching(key_func=default_key_func):
    """A decorator that creates local dumps of the decorated function's return values for given parameters.
    It can take a key_func argument that determines the name of the output file."""

    def caching_func(func):
        if DEBUG:
            def decorated(*args, **kwargs):
                key = key_func(args, kwargs)
                if Cache.get(key):
                    return Cache.get(key)
                response = func(*args, **kwargs)
                Cache.set(key, response)
                return response

            return decorated
        else:
            return func

    return caching_func


class Cache:
    @classmethod
    def set(cls, key, response):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        with open(os.path.join(CACHE_DIR, key), "wb") as file:
            pickle.dump(response, file)

    @classmethod
    def get(cls, key):
        try:
            with open(os.path.join(CACHE_DIR, key), "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None
