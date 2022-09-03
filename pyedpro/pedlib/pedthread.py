#!/usr/bin/env python

'''
    pygi does not like multiple threads on the gui
    this is the one (mostly because of the mac platform)
'''

from __future__ import absolute_import, print_function

import os
import time
import string
import pickle
import re
import platform
import subprocess
import threading

import gi;  gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from pedlib import  pedconfig
from pedlib import  peddraw
from pedlib import  pedxtnd
from pedlib import  pedync
from pedlib import  pedspell
from pedlib import  pedcolor
from pedlib import  pedmenu
from pedlib import  pedundo
from pedlib import  pedmisc
from pedlib import  pedtask
from pedlib import  pedfind
from pedlib import  pedplug

from pedlib.pedutil import *
from pedlib.keywords import *

class PedThread():

    def __init__(self):

        self.stopthread = False
        #self.thread = threading.Thread(target=self.async_updates)
        #self.thread.daemon = True
        #self.thread.start()
        self.arr = []
        self.arr_reg = []
        self.arr_time = []
        self.sema = threading.Lock()

    def async_updates(self):

        Gdk.threads_init()

        while (True):
            time.sleep(.1)
            Gdk.threads_enter()
            self.sema.acquire()
            #print("Async update")
            if len(self.arr):
                try:
                    #self.arr[0][0](self.arr[0][1], self.arr[0][2])
                    pass
                except:
                    print("Cannot exec self.arr[0]", sys.exc_info())
                self.arr = self.arr[1:]
            self.sema.release()

            self.sema.acquire()
            #print("Async update reg")
            if len(self.arr_reg):
                ppp = time.perf_counter()
                ddd = ppp - self.arr_time[0]
                if ddd > 1:
                    self.arr_time[0] = ppp
                    #print("firing at", ddd)
                    try:
                        #self.arr_reg[0][1](self.arr_reg[0][2], self.arr_reg[0][3])
                        pass
                    except:
                        print("Cannot exec reg self.arr[0]", sys.exc_info())
            self.sema.release()
            Gdk.threads_leave()

    def submit_job(self, callable, arg, arg2):
        self.sema.acquire()
        self.arr.append((callable, arg, arg2) )
        self.sema.release()

    def submit_regular(self, wtime, callable, arg, arg2):
        self.sema.acquire()
        self.arr_reg.append((wtime, callable, arg, arg2) )
        self.arr_time.append(time.perf_counter())
        self.sema.release()


# EOF