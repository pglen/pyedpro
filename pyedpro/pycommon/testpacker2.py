#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

import pypacker


# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    xorg = ["val1", "val2"]
    yorg = ("str1", "2", "3")
    zorg = { "key1" : "111", 'key2' : 222, "arr": xorg }

    pb = pypacker.packbin();
    pb.verbose = 5

    #print("doc", pypacker.__doc__)
    #print("dict", dir(pypacker))

    #sorg_var = [xorg , xorg]
    #sorg_var = [ zorg, yorg ]
    sorg_var = [ 334, "subx", 'x', xorg, yorg]
    #sorg_var  = [ 334, "subx", 'x', xorg, zorg]
    #sorg_var = "hello string"

    if pb.verbose > 2:
        print ("sorg_var: ",  sorg_var)

    eee_var = pb.encode_data("", *sorg_var)
    if pb.verbose > 2:
        print ("eee_var type", type(eee_var).__name__, ":\n", eee_var)

    fff_var = pb.decode_data(eee_var)

    if pb.verbose > 1:
        print ("fff_var:\n", fff_var)

    if  sorg_var != fff_var:
        print("Error on compare")
    else:
        print("Compare OK")

    #sys.exit(0)

