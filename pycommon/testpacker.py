#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

import  pypacker

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
            "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ=="

    pb = pypacker.packbin();
    pb.verbose = 3

    #bindat = Random.new().read(64)
    #print("bindat64:\n", base64.b64encode(bindat))

    bindat = base64.b64decode(rrr)

    org = [ 33, "sub", 'd', "longer str here with \' and \" all crap",  33, 33333333.2,
                {"test": 1111, "test2": 1112, }, bindat ]

    if pb.verbose > 2:
        print ("org:\n", org)

    eeenc = pb.encode_data("", *org)
    if pb.verbose > 2:
        print("eeenc:\n", "{" + eeenc + "}")

    dddec = pb.decode_data(eeenc)
    if pb.verbose > 2:
        print("dddec:\n",  "{" + str(dddec) + "}")

    if org == dddec:
        #print("Data matches OK.")
        pass
    else:
        print("MISMATCH:")

    #sys.exit(0)

    #print ("Should print 3 successes")
    #iscsifb
    #eee = pb.encode_data("iscsfb", *org)

    eee = pb.encode_data("", *org)
    if pb.verbose > 2:
        print ("eee:\n", eee)

    ddd = pb.decode_data(eee)
    if pb.verbose > 2:
        print ("ddd:\n", ddd)

    if not org == ddd:
        print ("Broken decode")
        print ("eee:\n", eee)
    else:
        pass
        #print ("Success1 ", end="")

    org2 = [ 22, 444, "data", 123.456, 'a', eee]
    #print ("org2:\n", org2)
    #eee2 = pb.encode_data("ilsfcx", *org2)
    eee2 = pb.encode_data("ilsfcx", *org2)
    #print ("eee2:\n", eee2)
    ddd2 = pb.decode_data(eee2)
    #print ("ddd2:\n", ddd2)

    if not org2 == ddd2:
        print ("Broken decode")
        print ("eee2:\n", eee2)
    else:
        pass
        #print ("Success2 ", end="")

    if sys.version_info[0] > 2:
        eee  = eee.encode("cp437")

    fff = zlib.compress(eee)

    #print("compressed %.2f" % (float(len(fff)) / len(eee)) )

    hhh = zlib.decompress(fff)
    if not eee == hhh:
        print ("Broken unzip")
    else:
        pass
        #print("Unzip OK")

    ddd3 = pb.decode_data(eee2)
    #print("ddd3", ddd3)
    ggg = pb.decode_data(ddd3[5])
    #print("ggg", ggg)

    if not org == ggg:
        print ("Broken decode")
    else:
        print ("Success, compare OK")

# EOF