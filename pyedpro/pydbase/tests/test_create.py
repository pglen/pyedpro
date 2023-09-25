#!/usr/bin/env python3

import pytest, os, sys

fff = __file__[:]
from mytest import *
import twincore, pypacker


core = None

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global core
    core = create_db()
    assert core != None

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

def test_create(tmp_path):
    global core
    try:
        # Fresh start
        #os.remove("data/tests.pydb")
        #os.remove("data/tests.pidx")
        pass
    except:
        pass

def test_write():
    print("write", core)
    ret = core.save_data("1111", "2222")
    assert ret != 0
    ret = core.save_data("11111", "22222")
    assert ret != 0
    ret = core.save_data("111", "222")
    assert ret != 0

def test_get():
    ret = core.get_rec(2)
    assert ret != 0
    assert ret == [b'111', b'222']

def test_read():
    ret = core.retrieve("111")
    assert ret == [[b'111', b'222']]

    ret = core.retrieve("1111")
    assert ret == [[b'1111', b'2222']]

def test_create_file(tmp_path):
    #print("tmp_path", tmp_path)
    #assert core == 0
    pass

# EOF
