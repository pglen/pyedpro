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
    ret = core.save_data("11111", "333333")
    assert ret != 0
    ret = core.save_data("3333", "4444")
    assert ret != 0
    ret = core.save_data("111", "222")
    assert ret != 0
    ret = core.save_data("1111", "3333")
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
    ret = core.get_rec(4)
    assert ret == [b'111', b'222']

def test_list():

    ret = core.del_rec_bykey("3333")
    #print("delrec", ret)
    assert ret == 1

    ret = core.listall()
    #print("listall", ret)
    assert ret == [5, 4, 2]

    sss = []
    for aa in ret:
        ret = core.get_rec(aa)
        sss.append(ret)
    #print(sss)
    assert sss == [[b'1111', b'3333'], [b'111', b'222'], [b'11111', b'333333']]

# EOF
