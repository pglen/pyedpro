#!/usr/bin/env python

#from __future__ import absolute_import, print_function

import os
import time
import sys
import ctypes
import warnings
import stat
import collections
import platform
import datetime
import importlib

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio

from pedlib import pedconfig
from pedlib import peddoc
from pedlib import pedync
from pedlib import pedlog
from pedlib import pedcal
from pedlib import pednotes
from pedlib import pedoline
from pedlib import pedfont
from pedlib import pedcolor
from pedlib import pedfind
from pedlib import pedweb
from pedlib import peddlg

#sys.path.append('..' + os.sep + "pycommon")

from pycommon.pggui import *
from pycommon.pgsimp import *

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedutil import *

plugin_list = []

def     load_plugins():

    sys.path.append(pedconfig.conf.plugins_dir)
    for aa in os.listdir(pedconfig.conf.plugins_dir):
        if aa[-3:] == ".py":
            modname =  aa[:-3]
            try:
                ppp = importlib.import_module(modname)
                plugin_list.append(ppp)
                ppp.name = modname
            except:
                print("Exc", sys.exc_info())

    # Call init on all:
    for aa in plugin_list:
        try:
            aa.init()
        except:
            print("Plugin named:", "'" + aa + "'", "has no init function")

# ---------------------------------------------------------------------------

def     keypress(keypress = " "):

    # Call keypress on all:
    for aa in plugin_list:

        if "keypress" not in  dir(aa):
            return
        try:
            aa.keypress(keypress)
        except:
            #print("Plugin named:", "'" + aa + "'", "keypress error")
            pass

def     display(disp, cr):

    # Call on all:
    for aa in plugin_list:

        if "display" not in  dir(aa):
            return

        try:
            aa.display(disp, cr)
        except:
            print("Plugin named:", "'" + aa.name + "'", "display error")
            pass

def     syntax(disp, cr):

    # Call on all:
    for aa in plugin_list:
        if "syntax" not in  dir(aa):
            return
        try:
            aa.syntax(disp, cr)
        except:
            print("Plugin named:", "'" + aa.name + "'", sys.exc_info())
            pass

def     predraw(disp, cr):

    # Call on all:
    for aa in plugin_list:
        if "predraw" not in dir(aa):
            return
        try:
            aa.predraw(disp, cr)
        except:
            print("Plugin named:", "'" + aa.name + "'", sys.exc_info())
            pass

# EOF