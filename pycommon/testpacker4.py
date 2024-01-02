#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from  pypacker import *

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    #print(dir(pypacker))

    pp = packbin()
    print(dir(pp))

    #print(dir(pypacker.__all__))

    #print("ddd3", ddd3)
    #ggg = pb.decode_data(ddd3[5])
    ##print("ggg", ggg)
    #
    #if not org == ggg:
    #    print ("Broken decode")
    #else:
    #    print ("Success, compare OK")

# EOF