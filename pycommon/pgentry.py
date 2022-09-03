#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import sys, traceback, os, time, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

# Expects two tuples of stuff
# labtext, labname, tip, defval = None:

def entryquad(arr, vbox, entry1, entry2):

    hbox2 = Gtk.HBox(False, 2)

    lab1a = Gtk.Label(label="      ")
    hbox2.pack_start(lab1a, False, 0, 0)
    lab1 = Gtk.Label.new_with_mnemonic(entry1[0]) ; lab1.set_alignment(1, 0)
    lab1.set_tooltip_text(entry1[2])
    hbox2.pack_start(lab1, False, 0, 0)
    lab1a = Gtk.Label(label="      ")
    hbox2.pack_start(lab1a, False, 0, 0)
    headx = Gtk.Entry();  headx.set_width_chars(33)
    lab1.set_mnemonic_widget(headx)

    if entry1[3] != None:
        headx.set_text(entry1[3][entry1[1]])
    hbox2.pack_start(headx, True, 0, 0)
    lab3 = Gtk.Label(label="        ")
    hbox2.pack_start(lab3, False, 0, 0)
    arr.append((entry1[1], headx))

    lab1b = Gtk.Label(label="      ")
    hbox2.pack_start(lab1b, False, 0, 0)
    lab2 = Gtk.Label.new_with_mnemonic(entry2[0])  ; lab2.set_alignment(1, 0)
    lab2.set_tooltip_text(entry2[2])
    hbox2.pack_start(lab2, False, 0, 0)
    lab1b = Gtk.Label(label="      ")
    hbox2.pack_start(lab1b, False, 0, 0)
    headx2 = Gtk.Entry();  headx2.set_width_chars(33)
    lab2.set_mnemonic_widget(headx2)
    if entry2[3] != None:
        headx2.set_text(entry2[3][entry2[1]])
    hbox2.pack_start(headx2, True, 0, 0)
    lab3b = Gtk.Label(label="        ")
    hbox2.pack_start(lab3b, False, 0, 0)
    arr.append((entry2[1], headx2))

    #self.vspacer(vbox)
    vbox.pack_start(hbox2, True, True, 0)
    return lab1, lab2

# Create a label entry pair
def entrypair(vbox, labtext, labname, tip, defval = None):

    hbox2 = Gtk.HBox()
    lab1b = Gtk.Label(label="      ")
    hbox2.pack_start(lab1b, False, 0, 0)

    lab1 = Gtk.Label.new_with_mnemonic(labtext) ; lab1.set_alignment(1, 0)
    hbox2.pack_start(lab1, False, 0, 0)

    lab1a = Gtk.Label(label="      ")
    hbox2.pack_start(lab1a, False, 0, 0)

    headx = Gtk.Entry();
    if defval != None:
        headx.set_text(defval[labname])
    lab1.set_mnemonic_widget(headx)

    hbox2.pack_start(headx, True, 0, 0)
    lab3 = Gtk.Label(label="        ")
    hbox2.pack_start(lab3, False, 0, 0)
    arr.append((labname, headx))

    vspacer(vbox)
    vbox.pack_start(hbox2, False, 0, 0)
    lab1.set_tooltip_text(tip)

    return lab1

def textviewpair(arr, vbox, labtext, labname, tip, defval=None, expand=False):

    hbox2 = Gtk.HBox();
    spacer(hbox2)

    lab2a = Gtk.Label(label="     ")
    hbox2.pack_start(lab2a, False , 0, 0)

    lab2 = Gtk.Label.new_with_mnemonic(labtext); lab2.set_alignment(1, 0)
    lab2.set_tooltip_text(tip)
    hbox2.pack_start(lab2, False , 0, 0)
    if defval:
        sw = scrolledtext(arr, labname, defval[labname])
    else:
        sw = scrolledtext(arr, labname, defval)

    lab2.set_mnemonic_widget(sw.textx)

    spacer(hbox2)
    hbox2.pack_start(sw, True, True, 0)
    spacer(hbox2)
    vspacer(vbox)

    lab2b = Gtk.Label(label="     ")
    hbox2.pack_start(lab2b, False , 0, 0)
    vbox.pack_start(hbox2, True, True, 0)
    return lab2

def scrolledtext(arr, name, body = None):
    textx = Gtk.TextView();
    textx.set_border_width(4)
    arr.append((name, textx))
    if body != None:
        #textx.grab_focus()
        buff = Gtk.TextBuffer(); buff.set_text(body)
        textx.set_buffer(buff)

    sw = Gtk.ScrolledWindow()
    sw.textx = textx
    sw.add(textx)
    sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
    sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    return sw


def imgbutt(imgfile, txt, func, win):
    hbb = Gtk.HBox(); vbb = Gtk.VBox();  ic = Gtk.Image();
    ic.set_from_file(imgfile)
    pb = ic.get_pixbuf();
    #pb2 = pb.scale_simple(150, 150, GdkPixbuf.InterpType.BILINEAR)
    pb2 = pb.scale_simple(150, 150, 0)
    ic2 = Gtk.Image.new_from_pixbuf(pb2)
    butt1d = Gtk.Button.new_with_mnemonic(txt)
    butt1d.connect("clicked", func, win)

    vbb.pack_start(Gtk.Label(label=" "), True, True, 0)
    vbb.pack_start(ic2, False, 0, 0)
    vbb.pack_start(Gtk.Label(label=" "), True, True, 0)
    vbb.pack_start(butt1d, False, 0, 0)
    vbb.pack_start(Gtk.Label(label=" "), True, True, 0)

    hbb.pack_start(Gtk.Label(label="  "), True, True, 0)
    hbb.pack_start(vbb, True, True, 0)
    hbb.pack_start(Gtk.Label(label="  "), True, True, 0)

    return hbb

# --------------------------------------------------------------------

def spacer(hbox, xstr = "    ", expand = False):
    lab = Gtk.Label(label=xstr)
    hbox.pack_start(lab, expand, 0, 0)

def vspacer(vbox, xstr = "     ", expand = False):
    lab = Gtk.Label(label=xstr)
    vbox.pack_start(lab, expand , 0, 0)

# eof
