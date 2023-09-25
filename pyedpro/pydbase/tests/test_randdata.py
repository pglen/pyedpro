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

    # Create a database of 5000 random records
    for aa in range(5000):
        key = randstr(random.randint(6, 12))
        val = randstr(random.randint(24, 96))
        ret = core.save_data(str(key), str(val))
        assert ret != 0

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    uncreate_db()

def test_randdata(capsys):

    #core.reindex()
    #core.dump_data(twincore.INT_MAX)
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

    nnn = []
    try:
        for aa in range(dbsize2):
            vvv = core.get_rec(aa)
            nnn.append(vvv)
    except:
        pass

    try:
        # No dangling data
        #os.remove("data/test_randdata.pydb")
        #os.remove("data/test_randdata.pidx")
        pass
    except:
        #print(sys.exc_info())
        pass

    assert dbsize == dbsize2
    assert nnn == ddd

# EOF
