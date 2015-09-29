# -*- coding: utf-8 -*-
from server import build_cache_key


def test_build_cache_key():
    assert build_cache_key('GET', '/path/', 'k=v', {}) == 'GET|/path/|k=v'
    assert build_cache_key('GET', '/', 'k1=v1', {'k2': 'v2'}) == 'GET|/|k1=v1'
    assert build_cache_key('POST', '/path/', '', {'k': 'v'}) ==\
        'POST|/path/|k=v'
    assert build_cache_key('POST', '/path/', 'k1=v1', {'k2': 'v2'}) ==\
        'POST|/path/|k2=v2'
    assert build_cache_key('POST', '/path/', '', {'key': 'кирилица'}) ==\
        'POST|/path/|key=кирилица'
