#!/usr/bin/env python3

import pytest, os, sys, random
from mytest import *
import twincore, pypacker

core = None

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global core
    core = create_db()
    assert core != 0

    ret = core.save_data("1111", "2222")
    assert ret != 0
    ret = core.save_data("11111", "22222")
    assert ret != 0
    ret = core.save_data("11111", "22222")
    assert ret != 0
    ret = core.save_data("111", "222")
    assert ret != 0

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    uncreate_db()

def setup_function(function):
    #assert 0
    pass

def teardown_function(function):
    #assert tmp_path == ""
    #assert 0, "test here, function %s" % function.__name__
    pass

# ------------------------------------------------------------------------
# Start

def test_get():
    ret = core.get_rec(3)
    assert ret == [b'111', b'222']

def test_search():

    strx = "1111"
    ret = core.find_key(strx)
    assert ret == [32]
    arr = core.get_rec_offs(ret[0])
    assert arr == [b"1111", b"2222"]

def test_search2():

    strx = "11111"
    ret = core.find_key(strx)
    assert ret == [98, 64]
    arr = core.get_rec_offs(ret[0])
    assert arr == [b"11111", b"22222"]
    arr = core.get_rec_offs(ret[1])
    assert arr == [b"11111", b"22222"]

# EOF
