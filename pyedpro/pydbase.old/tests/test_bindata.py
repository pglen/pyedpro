#!/usr/bin/env python3

import pytest, os, sys
from mytest import *
import twincore, pypacker

core = None
fname = createname(__file__)
iname = createidxname(__file__)

# ------------------------------------------------------------------------

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

    # Create a database of 500 random records
    for aa in range(5000):
        key = randbin(random.randint(6, 12))
        val = randbin(random.randint(24, 96))
        ret = core.save_data(str(key), str(val))
        assert ret != 0


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """

    try:
        # No dangling data
        os.remove(fname)
        os.remove(iname)
        pass
    except:
        print(sys.exc_info())
        #assert 0
        pass

    #assert 0


def test_bindata(capsys):

    dbsize = core.getdbsize()

    ddd = []
    for aa in range(dbsize):
        vvv = core.get_rec(aa)
        ddd.append(vvv)

    #core.core_verbose = 2
    core.reindex()
    dbsize2 = core.getdbsize()
    #core.core_verbose = 0
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
        #os.remove(fname)
        #os.remove(iname)
        pass
    except:
        print(sys.exc_info())
        #assert 0
        pass

    assert nnn == ddd

# EOF
