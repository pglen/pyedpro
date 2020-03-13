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
from . import  pedcolor, pedsql, log, utils

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
        self.lastsel = ""

        self.data_dir = os.path.expanduser("~/.pyedcal")
        try:
            if not os.path.isdir(self.data_dir):
                os.mkdir(self.data_dir)
        except:
            print("Cannot make calendar data dir")

        try:
            self.sql = pedsql.pedsql(self.data_dir + os.sep + "caldata.sql")
        except:
            print("Cannot make calendar database")

        self.cal = Gtk.Calendar()
        hbox.pack_start(self.cal, 1, 1, 0)

        self.cal.connect("day-selected", self.daysel)
        self.cal.connect("day-selected-double-click", self.dayseldouble)

        self.pack_start(Gtk.Label(" "), 0, 0, 0)
        self.pack_start(hbox, 0, 0, 0)
        self.pack_start(Gtk.Label(" "), 0, 0, 0)

        hbox2 = Gtk.HBox()
        butt = Gtk.Button("Goto Today")
        butt.connect("pressed", self.today, self.cal)
        hbox2.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox2.pack_start(butt, 1, 1, 0)
        hbox2.pack_start(Gtk.Label(" "), 0, 0, 0)

        butt2 = Gtk.Button("Edit Selection")
        butt2.connect("pressed", self.demand, self.cal)
        hbox2.pack_start(butt2, 1, 1, 0)
        hbox2.pack_start(Gtk.Label(" "), 0, 0, 0)

        self.pack_start(hbox2, 0, 0, 0)
        self.pack_start(Gtk.Label(" "), 0, 0, 0)
        self.edit = Gtk.Entry()

        self.pack_start(self.edit, 0, 0, 2)
        self.treeview2 = SimpleTree(("Hour", "Subject", "Notes"))
        self.treeview2.setcallb(self.treesel)
        self.treeview2.setCHcallb(self.treechange)

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        frame3 = Gtk.Frame(); frame3.add(scroll2)
        self.pack_start(frame3, 1, 1, 2)

        self.edview = SimpleEdit()
        self.edview.setsavecb(self.savetext)

        scroll3 = Gtk.ScrolledWindow()
        scroll3.add(self.edview)
        frame4 = Gtk.Frame(); frame4.add(scroll3)
        #frame4.set_size_request(200, 320)
        self.pack_start(frame4, 1, 1, 2)
        self.pack_start(Gtk.Label(" "), 0, 0, 0)
        self.daysel(self.cal)

    def savetext(self, txt):
        ddd = self.cal.get_date()
        key = "%d-%d-%d %s TXT" % (ddd[0], ddd[1], ddd[2], self.lastsel)
        print("savetext", key, "--",  txt)
        self.sql.put(key, txt)

    def treechange(self, args):
        ddd = self.cal.get_date()
        self.lastsel = args[0]
        #print("treechange", ddd, args)
        key = "%d-%d-%d %s" % (ddd[0], ddd[1], ddd[2], args[0])
        val =  "[%s]~[%s]" % (args[1], args[2])
        self.sql.put(key, val)

    def treesel(self, args):
        print("treesel", args)
        self.lastsel = args[0]
        self.edview.clear()
        strx = ""
        for aa in args:
            strx += aa + "\n";
        self.edview.append(strx)

    def today(self, butt, cal):
        ddd = datetime.datetime.today()
        #print("date",  ddd.year, ddd.month, ddd.day)
        cal.select_month(ddd.month-1, ddd.year)
        cal.select_day(ddd.day)

    def demand(self, butt, cal):
        ddd = datetime.datetime.today()
        print("demand",  ddd.year, ddd.month, ddd.day)

    def daysel(self, cal):
        #print("Day", cal.get_date())
        self.edit.set_text(str(cal.get_date()))
        self.treeview2.clear()
        for aa in range(8, 20):
            #self.treeview2.append((ampmstr(aa), utils.randstr(8), utils.randstr(14)) )
            ddd = self.cal.get_date()
            key = "%d-%d-%d %s" % (ddd[0], ddd[1], ddd[2], ampmstr(aa) )
            val =  self.sql.get(key)
            if val:
                #print("val", val)
                idx = val.find("]~[")
                self.treeview2.append((ampmstr(aa), val[1:idx], val[idx+3:-1]) )
            else:
                self.treeview2.append((ampmstr(aa), "", "") )

    def dayseldouble(self, cal):
        print("Day dbl", cal.get_date())
        pass

# EOF


























