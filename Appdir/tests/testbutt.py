#!/usr/bin/env python3

import pdb
import sys, os

import gi; gi.require_version("Gtk", "3.0")

#pdb.run("from gi.repository import Gtk")

from gi.repository import Gtk

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gdk

sys.path.append('.' + os.sep + "pycommon")

from pycommon.pgbutt import *

def newitem(arg, arg2):
    print("newitem", arg, arg2)

def closure(arg, arg2, arg3, arg4):
    print("closure", arg, arg2, arg3, arg4)

def eventmn1(arg, arg2):
    print("eventmn1", arg, arg2)

def eventmn2():
    print("eventmn2")

def eventmn3(arg):
    print("eventmn3", arg)

win = Gtk.Window()

win.connect("event", eventmn1)
win.connect("mnemonic-activate", eventmn2)
win.connect("accel-closures-changed", eventmn3)

accel2 = Gtk.AccelGroup.new()

butt = smallbutt(" _New Item ", newitem, "Create new item / record")
#print(dir(butt))
win.add_accel_group(accel2)

key, mod = Gtk.accelerator_parse("<Alt>M")
accel2.connect(key, mod,  Gtk.AccelFlags.VISIBLE, closure)

butt.agroup = accel2

vbox = Gtk.VBox()
vbox.pack_start(Gtk.Label.new("Empty"),1,1,0)

hbox = Gtk.HBox()
hbox.pack_start(Gtk.Label.new(" "), 1,1,0)
hbox.pack_start(Gtk.Label.new("| "), 0,0,0)
hbox.pack_start(butt,0,0,0)
hbox.pack_start(Gtk.Label.new("| "), 0,0,0)
hbox.pack_start(Gtk.Label.new(" "), 1,1,0)

vbox.pack_start(hbox,0,0,0)
vbox.pack_start(Gtk.Label.new("Empty"),1,1,0)

win.add_accel_group(accel2)
win.connect("destroy", Gtk.main_quit)
win.add(vbox)
win.set_default_size(300, 200)

win.show_all()

#butt.add_accel()

Gtk.main()
