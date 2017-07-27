import os
import pickle
import unicodedata

try:
    from __builtin__ import unicode
except ImportError:
    unicode = lambda x, *args: x

DEBUG = os.environ.get('DEBUG')
CACHE_DIR = os.environ.get('CACHE_DIR', '/var/tmp/scrapper-helpers/')


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        )
    for code in htmlCodes:
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


def caching(func):
    if DEBUG:
        def decorated(*args):
            key = '{0}_{1}'.format(func.__name__, str(args[0]).replace('/', '').replace(':', ''))
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
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        with open(os.path.join(CACHE_DIR, key), "wb") as file:
            pickle.dump(response, file)

    @classmethod
    def get(cls, key):
        try:
            with open(os.path.join(CACHE_DIR, key), "rb") as file:
                return pickle.load(file)
        except FileNotFoundError as e:
            return None
