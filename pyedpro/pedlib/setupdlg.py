#!/usr/bin/env python

# Action Handler for buffers

from __future__ import absolute_import
from __future__ import print_function

import re, string, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from pedlib import pedconfig
from pedlib.pedutil import *

class SetupDlg(Gtk.Dialog):

    def __init__(self, edwin, curr):

        self.reent = 0
        self.edwin = edwin
        self.curr = curr
        head = "  pyedro: settings  "
        ev_arr = []
        Gtk.Dialog.__init__(self)
        self.set_title(head)
        self.set_modal(True)
        #self.add_buttons(
        #            Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
        #                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.add_button("_Close", Gtk.ResponseType.ACCEPT)
        #warnings.simplefilter("default")

        self.set_default_response(Gtk.ResponseType.ACCEPT)
        self.set_transient_for(edwin.mywin)

        try:
            self.set_icon_from_file(get_img_path("pyedpro_sub.png"))
        except:
            print("Cannot set icon in ", __file__)

        #self.self = self

        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self. area_key)

        vbox = Gtk.VBox()
        lab3 = Gtk.Label(label="     ")
        vbox.pack_start(lab3, False, 0, 0 )

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.connect("change-value", self.scale_val)
        self.scale.set_value(self.edwin.alpha * 100)

        vbox.pack_start(self.scale, False, 0, 0 )

        strx = "Alpha setting needs initial delay"

        lab3a = Gtk.Label(label=strx) #"       ")
        vbox.pack_start(lab3a, False, 0, 0 )

        buttd = Gtk.Button.new_with_mnemonic(" _Restore Default ")
        buttd.connect("clicked", self.defbutt)

        lab4a = Gtk.Label(label="       ")
        vbox.pack_start(lab4a, False , 0, 0)

        lab4 = Gtk.Label(label="       ")
        vbox.pack_start(lab4, False , 0, 0)

        vbox.pack_start(buttd, False, 0, 0 )
        #vbox.pack_start(buttda, False, 0, 0 )

        lab5 = Gtk.Label(label="       ")
        vbox.pack_start(lab5, False , 0, 0)

        self.vbox.add(vbox)
        self.show_all()

    def scale_val(self, win, prop, val):
        if self.reent:
            return
        self.reent = 1
        #print("scale", self.edwin, val/100)
        self.edwin.alpha = val/100
        self.edwin.mywin.set_opacity(self.edwin.alpha)

        #self.curr.grab_focus()
        #usleep(100)
        self.curr.queue_draw()
        #usleep(100)
        #self.edwin.mywin.queue_draw()
        #self.edwin.mywin.grab_focus()
        #usleep(100)
        self.reent = 0

    def defbutt(self, win):
        self.scale.set_value(100)
        self.edwin.alpha = 1
        self.edwin.mywin.set_opacity(self.edwin.alpha)

    def area_key(self, win, event):

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Escape:
                #print "Esc"
                self.response(Gtk.ResponseType.REJECT)

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Return:
                #print "Ret"
                self.response(Gtk.ResponseType.ACCEPT)

            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                self.alt = True;

            if event.keyval == Gdk.KEY_x or \
                    event.keyval == Gdk.KEY_X:
                if self.alt:
                    self.response(Gtk.ResponseType.REJECT)

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                self.alt = False;
# EOF
