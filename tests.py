#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import pytest

import scrapper_helpers.utils as utils

if sys.version_info < (3, 3):
    from mock import mock
else:
    from unittest import mock


@pytest.mark.parametrize(
    'text,dic,expected_value', [
        ('ala', {'a': 'b'}, 'blb'),
        (u'Gdańsk', {u'ń': u'n'}, u'Gdansk')
    ])
def test_replace_all(text, dic, expected_value):
    assert utils.replace_all(text, dic) == expected_value


@pytest.mark.parametrize("list1", [[[2], [[3], [1]], [4, [0]]]])
def test_flatten(list1):
    result = utils.flatten(list1)
    for element in result:
        assert not isinstance(element, list)


@pytest.mark.parametrize(
    'text,expected_value', [
        ('ala MA KoTa', 'ala_ma_kota'),
        ('Gdańsk', 'gdansk')
    ])
def test_normalize_text(text, expected_value):
    assert utils.normalize_text(text) == expected_value


def test_key_md5():
    with mock.patch("scrapper_helpers.utils.hashlib.md5") as md5:
        utils.key_md5("test")
        assert md5.called


def test_key_sha1():
    with mock.patch("scrapper_helpers.utils.hashlib.sha1") as sha1:
        utils.key_sha1("test")
        assert sha1.called


@pytest.mark.parametrize(
    'text,expected_value', [
        ('ala MA KoTa', 'ala MA KoTa'),
        ('ala:MA/KoTa', 'alaMAKoTa')
    ])
def test_default_key_func(text, expected_value):
    assert utils.default_key_func(text) == expected_value


@pytest.mark.parametrize(
    'text,expected_value', [
        ('Mac&gt;Windows', 'Mac>Windows'),
        ('ala ma kota', 'ala ma kota')
    ])
def test_html_decode(text, expected_value):
    assert utils.html_decode(text) == expected_value


@pytest.mark.parametrize(
    'debug_value', [1, 0])
def test_caching(debug_value):
    with mock.patch("scrapper_helpers.utils.Cache.set") as set, \
            mock.patch("scrapper_helpers.utils.Cache.get") as get:
        utils.DEBUG = debug_value
        utils.caching()(list)("test")
        assert (set.called or get.called) or (not set.called and not get.called)


@pytest.mark.skipif(sys.version_info < (3, 5), reason="requires Python35")
def test_set():
    with mock.patch("scrapper_helpers.utils.pickle.dump") as dump, \
            mock.patch("scrapper_helpers.utils.open") as opn:
        utils.Cache.set("test", "test")
        assert dump.called and opn.called


@pytest.mark.skipif(sys.version_info < (3, 5), reason="requires Python35")
def test_get():
    with mock.patch("scrapper_helpers.utils.pickle.load") as load, \
            mock.patch("scrapper_helpers.utils.open") as opn:
        utils.Cache.get("test")
        assert load.called and opn.called
