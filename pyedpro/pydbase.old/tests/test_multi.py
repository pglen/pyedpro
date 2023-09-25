#!/usr/bin/env python3

import pytest, os, sys, threading
from mytest import *
import twincore, pypacker

core = None
fname = createname(__file__)
iname = createidxname(__file__)

def oneproc():

    #print("started thread")
    # Create a database of 500 random records
    for aa in range(5):
        #key = randbin(random.randint(6, 12))
        #val = randbin(random.randint(24, 96))
        key = randstr(random.randint(6, 12))
        val = randstr(random.randint(24, 96))
        ret = core.save_data(str(key), str(val))
        assert ret != 0

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


def teardown_module(module):

    try:
        # No dangling data
        os.remove(fname)
        os.remove(iname)
        pass
    except:
        #print(sys.exc_info())
        pass

def test_adders(capsys):

    # Start a handful of threads

    ttt = []
    for aa in range(300):
        tt = threading.Thread(target = oneproc)
        ttt.append(tt)
        tt.run()

    while 1:
        aa = False
        for tt in ttt:
            if tt.is_alive():
                aa = True
        if not aa:
            break

def test_integrity(capsys):
    ddd = core.integrity_check()
    assert len(ddd) == 2

    #print (ddd)
    #assert 0

    assert ddd[0] == ddd[1]


# EOF
