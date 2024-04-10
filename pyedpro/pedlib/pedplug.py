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
#from pedlib import peddoc
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

    if not os.path.isdir(pedconfig.conf.plugins_dir):
        os.mkdir(pedconfig.conf.plugins_dir)

    sys.path.append(pedconfig.conf.plugins_dir)

    for aa in os.listdir(pedconfig.conf.plugins_dir):
        if aa[-3:] == ".py":
            modname =  aa[:-3]
            if pedconfig.conf.verbose:
                print("Loading user plugin:", modname);
            try:
                ppp = importlib.import_module(modname)
                plugin_list.append(ppp)
                ppp.name = modname
            except:
                print("Exception on plugin", modname, sys.exc_info())

    sys.path.append(pedconfig.conf.plugins_dir2)
    for aa in os.listdir(pedconfig.conf.plugins_dir2):
        if aa == "__init__.py":
            continue

        dup = 0
        if aa[-3:] == ".py":
            modname =  aa[:-3]
            for aa in plugin_list:
                # user plugins override
                if aa.name == modname:
                    dup = 1
            if dup:
                print("Duplicate plugin, not loading: '" + aa.name + "'")
                print("Plugin location:", pedconfig.conf.plugins_dir2)
                continue

            if pedconfig.conf.verbose:
                print("Loading sys plugin:", modname);
            try:
                ppp = importlib.import_module(modname)
                plugin_list.append(ppp)
                ppp.name = modname
            except:
                print("Exception on plugin", modname, sys.exc_info())

    # Call init on all:
    for aa in plugin_list:
        try:
            aa.init()
            #print("Called init for:", aa.name);
        except:
            print("Plugin:", "'" + aa.name + "'", "has no init function", sys.exc_info())

# ---------------------------------------------------------------------------

def     keypress(disp, keypress = " "):

    # Call keypress on all:
    for aa in plugin_list:

        if "keypress" not in  dir(aa):
            continue
        try:
            aa.keypress(disp, keypress)
        except:
            print("Plugin named:", "'" + aa.name + "'", sys.exc_info())
            pass

def     display(disp, cr):

    #print("display plugin call:", disp, cr)

    # Call on all:
    for aa in plugin_list:

        if "display" not in  dir(aa):
            continue
        try:
            aa.display(disp, cr)
        except:
            print("Plugin", "'" + aa.name + "'", "display()", sys.exc_info())
            pass

def     syntax(disp, cr):

    # Call on all:
    for aa in plugin_list:
        if "syntax" not in  dir(aa):
            continue
        try:
            aa.syntax(disp, cr)
        except:
            print("Plugin named:", "'" + aa.name + "'", sys.exc_info())
            pass

def     clsyntax(disp, cr):

    # Call on all:
    for aa in plugin_list:
        if "syntax" not in  dir(aa):
            continue
        try:
            aa.syntax(disp, cr)
        except:
            print("Plugin named:", "'" + aa.name + "'", sys.exc_info())
            pass

def     predraw(disp, cr):

    #print("predraw plugin call:", cr)

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