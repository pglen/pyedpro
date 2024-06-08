#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from pgsimp import *
from pgutils import *

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

        self.treeview = SimpleTree(("Hour", "Subject", "Alarm", "Notes"))
        frame2 = wrapscroll(self.treeview)
        hbox.pack_start(frame2, 1, 1, 2)

        self.editor = SimpleEdit()
        frame3 = wrapscroll(self.editor)
        hbox.pack_start(frame3, 1, 1, 2)

        self.selector = LetterNumberSel(self.letterfilter, "Mono 16")
        hbox2.pack_start(self.selector , 1, 1, 2)

        vbox.pack_start(hbox3, 0, 0, 2)
        vbox.pack_start(hbox2, 0, 0, 2)
        vbox.pack_start(hbox4, 0, 0, 2)
        vbox.pack_start(hbox, 1, 1, 2)
        vbox.pack_start(hbox5, 0, 0, 2)

        self.add(vbox)
        self.show_all()

    def  letterfilter(self, letter):
        #print("letterfilter", letter)
        self.label.set_text(letter)

tw = pgtestwin()

#print("test")

def fillrand():
    aaa = []
    for aa in range(10):
        aaa.append( (randstr(12), randstr(12), randstr(12), randstr(12)) )
    return aaa

aaa = fillrand()
tw.treeview.clear()
for aa in aaa:
    try:
        tw.treeview.append(aa)
    except:
        print(sys.exc_info())

tw.editor.clear()

for aa in aaa:
    try:
        tw.editor.append(str(aa) + "\n")
    except:
        print(sys.exc_info())


Gtk.main()

