#!/usr/bin/env python3

import os, sys, getopt, signal, random, time, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

ww = Gtk.Window()
ww.connect("delete-event", Gtk.main_quit)
ww.connect("destroy", Gtk.main_quit)

ww.show_all()
Gtk.main()
