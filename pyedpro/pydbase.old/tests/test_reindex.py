#!/usr/bin/env python3

import pytest, os, sys, random
from mytest import *
import twincore, pypacker

# --------------------------------------------------------------
# Test for pydbase integrity test

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

    core = create_db(fname)
    assert core != 0

    kkk = 100; vvv = 1000; xxx = 10
    # Create a database of xxx records
    for aa in range(xxx):
        ret = core.save_data(str(kkk), str(vvv))
        assert ret != 0
        kkk += 1; vvv += 1

    #assert 0

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


def test_reindex(capsys):

    #core.reindex()
    #core.dump_data()
    dbsize = core.getdbsize()
    #print("dbsize", dbsize)
    #assert 0

    ddd = []
    for aa in range(dbsize):
        vvv = core.get_rec(aa)
        ddd.append(vvv)

    #twincore.core_verbose = 2
    core.reindex()
    dbsize2 = core.getdbsize()
    #twincore.core_verbose = 0

    assert dbsize == dbsize2

    nnn = []
    try:
        for aa in range(dbsize2):
            vvv = core.get_rec(aa)
            nnn.append(vvv)
    except:
        pass

    try:
        # No dangling data
        #os.remove("data/test_reindex.pydb")
        #os.remove("data/test_reindex.pidx")
        pass
    except:
        #print(sys.exc_info())
        pass

    assert dbsize == dbsize2
    assert nnn == ddd

# EOF
