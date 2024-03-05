#!/usr/bin/env python3

import pytest, os, sys
from mytest import *
import twincore, pypacker

fname = createname(__file__)
iname = createidxname(__file__)

core = None

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global core

    try:
        # Fresh start
        os.remove(fname)
        os.remove(iname)
    except:
        #print(sys.exc_info())
        pass

    core = create_db(fname)
    assert core != None

    ret = core.save_data("1111", "2222")
    assert ret != 0
    ret = core.save_data("11111", "22222")
    assert ret != 0
    ret = core.save_data("111", "222")
    assert ret != 0


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    try:
        # Fresh start
        os.remove(fname)
        os.remove(iname)
    except:
        #print(sys.exc_info())
        pass

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
    ret = core.get_rec(2)
    assert ret == [b'111', b'222']

    ret = core.get_rec(1)
    assert ret == [b'11111', b'22222']

    ret = False

    # Invalid index, passed end of file
    try:
        ret = core.get_rec(3)
        # Exception thrown, ret not set
    except:
        #print(ret)
        #assert 0
        pass

    assert ret == False

# EOF
