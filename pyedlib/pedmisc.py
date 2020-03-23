#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import signal, os, time, string, pickle, re, platform, subprocess

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from . import pedcolor, pedspell, pedmenu, utils
from . import peddraw

from .pedlcmd import *
from .pedutil import *

def exec_test(self2, testx):

        if self2.lastcmd == "" or self2.shift:

            #print("Asking lastcmd")
            ret = cmddlg(self2)
            if not ret:
                self2.mained.update_statusbar("Cancelled exec dialog.")
                return

        if self2.lastcmd == "":
            self2.mained.update_statusbar("No command specified.")
            return

        comarr = self2.lastcmd.split(" ")
        if pedconfig.conf.pgdebug > 9:
            print("comarr",  comarr)

        print("comarr",  comarr)

        ret = subprocess.Popen(comarr)
        if ret:
            self2.mained.update_statusbar("Cannot execute command: " + self2.lastcmd)








