#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

from pgsimp import *
from pgutils import *
from pggui import *
from pgbox import *

#def OnExit(arg1, arg2):
#    #print("Exiting", arg1, arg2)
#    Gtk.main_quit()

# ------------------------------------------------------------------------
class testwin(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_default_size(1024, 768)
        #self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("unmap", Gtk.main_quit)

def wrapscroll(what):

    scroll2 = Gtk.ScrolledWindow()
    scroll2.add(what)
    frame2 = Gtk.Frame()
    frame2.add(scroll2)
    return frame2

# ------------------------------------------------------------------------

class pgtestwin(testwin):

    def __init__(self):

        testwin.__init__(self)

        hbox  = Gtk.HBox(); hbox3 = Gtk.HBox()
        hbox2 = Gtk.HBox(); hbox4 = Gtk.HBox()
        hbox5 = Gtk.HBox()

        self.label = Gtk.Label.new("Test strings here")
        hbox5.pack_start(self.label, 1, 1, 2)

        vbox  = Gtk.VBox()

        vbox.pack_start(hbox2, 0, 0, 2)

        hbox3.pack_start(Label("       Hour:  "), 0, 0, 2)

        self.hs2 = Spinner(0, 23, 0, self.change_hs2);
        hbox3.pack_start(self.hs2, 0, 0, 2)

        hbox3.pack_start(Label("       Min:  "), 0, 0, 2)
        self.ms2 = Spinner(0, 59, 0, self.change_ms2);
        hbox3.pack_start(self.ms2, 0, 0, 2)

        hbox3.pack_start(Label(" "), 0, 0, 2)

        hbox4.pack_start(Label(" "), 0, 0, 2)
        self.ts4 = HourSel(self.change_ts4);
        hbox4.pack_start(self.ts4, 0, 0, 2)

        hbox4.pack_start(Label(" "), 0, 0, 2)
        self.ts4a = MinSel(self.change_ts4a);
        hbox4.pack_start(self.ts4a, 0, 0, 2)

        vbox.pack_start(hbox3, 0, 0, 2)
        vbox.pack_start(hbox4, 0, 0, 2)
        vbox.pack_start(hbox, 1, 1, 2)
        vbox.pack_start(hbox5, 0, 0, 2)

        self.add(vbox)
        self.show_all()

    def  letterfilter(self, letter):
        #print("letterfilter", letter)
        self.label.set_text(letter)

    def change_hs2(self, val):
        #print("change_hs2", val)
        self.label.set_text("hour: " + str(val))
        pass

    def change_ms2(self, val):
        #print("change_ms2", val)
        self.label.set_text("minute: " + str(val))
        pass

    def change_ts4(self, val):
        #print("change_ms2", val)
        self.label.set_text("H click: " + str(val))
        pass

    def change_ts4a(self, val):
        #print("change_ms2", val)
        self.label.set_text("M click: " + str(val))
        pass

tw = pgtestwin()

cnt = 0;

def  handler_tick(ww):

    global cnt
    #print("handler_tick", ww)

    if cnt % 2 == 0:
        tw.hs2.set_value(cnt)
    else:
        tw.ms2.set_value(cnt)

    cnt += 1
    GLib.timeout_add(1000, handler_tick, ww)


GLib.timeout_add(1000, handler_tick, tw)

Gtk.main()
