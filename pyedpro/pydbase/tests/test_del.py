#!/usr/bin/env python3

import pytest, os, sys
from mytest import *
import twincore, pypacker

# Test for pydbase

core = None
fname = createname(__file__)
iname = createidxname(__file__)

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

    core = twincore.TwinCore(fname)
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
    try:
        # Fresh start
        os.remove(fname)
        os.remove(iname)
    except:
        #print(sys.exc_info())
        pass

def test_del(capsys):

    core.del_rec_bykey(b"11111")
    core.del_rec_bykey("1111")

    core.dump_data()
    captured = capsys.readouterr()

    out =   "0     pos    98 Data: b'111' Data2: b'222'\n"

    assert captured.out == out

# EOF
