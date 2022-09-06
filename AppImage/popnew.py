#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

from mainwin import  *
from pgutil import  *

import popsql

dbfile = os.path.expanduser("~/history.sql")

# ------------------------------------------------------------------------
# Globals

version = "0.00"

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -v        - Verbose")
    print( "            -V        - Version")
    print( "            -a        - Show dAta")
    print( "            -c        - Clear data")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

# ------------------------------------------------------------------------
def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     9999,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["a",   "data",     0,      None],      \
    ["c",   "clear",    0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = Config(optarr)

if __name__ == '__main__':

    global mw
    args = conf.comline(sys.argv[1:])

    #print("conf.data", conf.data)
    if conf.data:
        ddd = popsql.popsql(dbfile).getall()
        print("data", ddd)
        sys.exit(0)

    if conf.clear:
        ddd = popsql.popsql(dbfile).rmall()
        print("Cleared data");
        sys.exit(0)

    mw = MainWin()
    Gtk.main()
    sys.exit(0)

# EOF