#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import signal, os, time, sys, subprocess, platform
import ctypes, datetime

import warnings

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

from . import  peddoc, pedconfig, pedofd
from . import  pedync, pedspell, pedfont
from . import  pedcolor, log, utils

# Into our name space
from    .pedmenu import *
from    .pedui import *
from    .pedutil import *

# ------------------------------------------------------------------------

class pgcal(Gtk.VBox):

    def __init__(self):

        #vbox = Gtk.VBox()
        Gtk.VBox.__init__(self)

        hbox = Gtk.HBox()

        self.cal = Gtk.Calendar()
        hbox.pack_start(self.cal, 1, 1, 0)
        #self.cal.set_property("show-details", True)

        self.cal.connect("day-selected", self.daysel)
        self.cal.connect("day-selected-double-click", self.dayseldouble)

        #cal.set_detail_func(detfunc, "none")

        self.pack_start(Gtk.Label(" "), 0, 0, 0)
        self.pack_start(hbox, 0, 0, 0)
        self.pack_start(Gtk.Label(" "), 0, 0, 0)

        hbox2 = Gtk.HBox()
        butt = Gtk.Button("Today")
        butt.connect("pressed", self.today, self.cal)
        hbox2.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox2.pack_start(butt, 1, 1, 0)
        hbox2.pack_start(Gtk.Label(" "), 0, 0, 0)

        self.pack_start(hbox2, 0, 0, 0)

        self.pack_start(Gtk.Label(" "), 0, 0, 0)
        #lab = Gtk.Label("Calendar")
        #self.pack_start(lab, 0, 0, 0)
        #self.pack_start(Gtk.Label(" "), 0, 0, 0)

        self.edit = Gtk.Entry()

        self.pack_start(self.edit, 0, 0, 2)
        #self.pack_start(Gtk.Label(" "), 0, 0, 0)

        self.treeview2 = SimpleTree(("Hour", "Subject", "Notes"))

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        frame3 = Gtk.Frame(); frame3.add(scroll2)
        #frame3.set_size_request(100, 100)
        self.pack_start(frame3, 1, 1, 2)
        #self.pack_start(Gtk.Label(" "), 0, 0, 0)

        # Pre fill day box
        dd = "AM"
        for aa in range(8, 20):
            bb = aa
            if bb == 12:
               dd = "PM"
            elif bb > 12:
                bb -= 12
                dd = "PM"
            self.treeview2.append( ("%02d %s" % (bb, dd), "", "") )

        #self.edview = Gtk.TextView()
        self.edview = SimpleEdit()
        scroll3 = Gtk.ScrolledWindow()
        scroll3.add(self.edview)
        frame4 = Gtk.Frame(); frame4.add(scroll3)
        #frame4.set_size_request(200, 320)
        self.pack_start(frame4, 1, 1, 2)
        self.pack_start(Gtk.Label(" "), 0, 0, 0)

        #return vbox

    def today(self, butt, cal):
        ddd = datetime.datetime.today()
        print("date",  ddd.year, ddd.month, ddd.day)
        cal.select_month(ddd.month-1, ddd.year)
        cal.select_day(ddd.day)

    def ampmstr(self, bb):
        dd = "AM"
        if bb == 12:
           dd = "PM"
        elif bb > 12:
            bb -= 12
            dd = "PM"
        return "%02d %s" % (bb, dd)

    def daysel(self, cal):
        #print("Day", cal.get_date())
        self.edit.set_text(str(cal.get_date()))
        self.edview.clear()
        self.edview.append(utils.randstr(123))

        self.treeview2.clear()
        for aa in range(8, 20):
            self.treeview2.append((self.ampmstr(aa), utils.randstr(8), utils.randstr(14)) )

        pass

    def dayseldouble(self, cal):
        print("Day dbl", cal.get_date())
        pass

    def detfunc(self, cal, yy, mm, dd, det = None):
        print("Detfunc", yy, mm, dd)
        return None































































































