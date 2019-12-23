#!/usr/bin/env python

import os, sys

while True:

    try:
        chh = sys.stdin.read(1)
        print (chh, end="")
    except:
        print (sys.exc_info())
