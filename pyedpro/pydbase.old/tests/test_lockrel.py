#!/usr/bin/env python3

import pytest, os, sys
from mytest import *
import twincore, pypacker

# Test for pydbase

core = None

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global core

    core = 0
    ttt = "test_ro"
    fff = "test_ro/test_file.pydb"
    xxx = "test_ro/test_file.pidx"
    lll = "test_ro/test_file.lock"

    if not os.path.isdir(ttt):
        os.mkdir(ttt)
    try:
        fp = open(fff, "w+")
        fp.close()
        os.chmod(fff, 0o444)
        core = twincore.TwinCore(fff)
        #print(core)
        #assert 0
    except:
        print(sys.exc_info())

    # testing for lock
    assert core == 0

    if os.path.isfile(lll):
        print("Unexpected lock file")
        assert 0

    try:
        os.remove(fff)
        os.remove(xxx)
        os.remove(lll)
    except:
        pass

    os.rmdir(ttt)

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """

def setup_function(function):
    #assert 0
    pass

def teardown_function(function):
    #assert tmp_path == ""
    #assert 0, "test here, function %s" % function.__name__
    pass

# ------------------------------------------------------------------------
# Start

def test_data():
    pass
    #ret = core.get_rec(2)
    #assert ret != 0
    #assert ret == [b'111', b'222']

def test_lock():

    pass

    #core.core_verbose = 2
    #print (ret[0], ret[1])
    #assert 0
    #assert ret[0] == ret[1]

# EOF
