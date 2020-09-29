#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import signal, os, time, string, pickle
from threading import Timer

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject

import pedlib.pedconfig as pedconfig

# ------------------------------------------------------------------------

def  suggest(self2, strx):

    arr = []

    xfile = get_exec_path("PyGObject.txt")
    arr2 = readfile(xfile)
    #print ("arr2", arr2[:30])

    try:
        cnt2 = cnt = 0
        for bb in range(len(arr2)):
            sss = arr2[bb]
            if strx in sss:
                if sss[0] == " ":
                    arr.append(sss.strip())
                    cnt += 1
                else:
                    arr.append(sss.strip())
                    cnt += 1
                    for cc in range(50):
                        ssss = arr2[bb + cc + 1].strip()
                        if ssss:
                            arr.append("   " + ssss)
                        cnt += 1

            if cnt > 100:
                break

            cnt2 += 1
    except:
        #print("Exception")
        pass

    #print("searched", cnt2)

    return arr

# EOF





















