#!/usr/bin/env python3

from __future__ import absolute_import, print_function
import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

import webview

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: webwin.py [-d] filename")
        sys.exit(0)

    is_text = False
    #print("argv", sys.argv);
    delmode = 0

    if sys.argv[1] == "-d":
        delmode = 1
        sys.argv = sys.argv[1:]

    newfname = sys.argv[1]
    if not os.path.isfile(newfname):
        is_text = True
        newfname = ""
        for aa in sys.argv[1:]:
            newfname += " " + aa

    #print("newfname", newfname)

    try:
        if is_text:
            webview.create_window("Html Text", html=newfname)
        else:
            webview.create_window(newfname, newfname)

        webview.start()

    except:
        print("Cannot start HTML Win %s" % str(newfname), sys.exc_info())

    print("Ended webview delmode", delmode)

    if delmode:
        os.remove(newfname)