#!/usr/bin/env python3

import pytest, os, sys
from mytest import *
import twincore, pypacker

# Test for pydbase

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

def test_integrity():

    core.core_verbose = 2
    ret = core.integrity_check()
    #print (ret[0], ret[1])
    #assert 0
    assert ret[0] == ret[1]

# EOF
