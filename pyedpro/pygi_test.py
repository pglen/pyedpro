#!/usr/bin/env python3

import os, sys, getopt, signal, random, time, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

class myWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

ww = myWindow()
ww.connect("delete-event", Gtk.main_quit)
ww.connect("destroy", Gtk.main_quit)
ww.set_default_size(300, 400)
ww.add(Gtk.Label(label="Hello"))
try:
    ww.set_icon_from_file("pedlib/images/pyedpro.png")
except:
    pass

ww.show_all()
Gtk.main()
