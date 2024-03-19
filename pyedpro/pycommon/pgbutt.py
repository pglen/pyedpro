#!/usr/bin/env python

# Drawing operations done here

from __future__ import absolute_import

import signal, os, time, sys, codecs

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GObject

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

realinc = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pycommon")
if realinc not in sys.path:
    sys.path.append(realinc)

import cairo
import pgutils
import pgsimp
import sutil

class smallbutt(Gtk.EventBox):

    __gsignals__ = {
    #"activate": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, () ),
    "pressed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, () ),
    }

    def __init__(self, labx, eventx = None, tooltip = None, *args, **kwds):
        super().__init__(*args, **kwds)

        self.state = 0; self.stat2 = 0
        self.labx = labx;  self.orgtext = ""
        self.accel = "";  self.agroup = None
        self.mark = -1;
        self.mnem = self.omnem = 0
        self.lab = Gtk.Label.new_with_mnemonic(labx)
        self.add(self.lab)
        self.set_above_child(True)

        self.arrow  =  Gdk.Cursor(Gdk.CursorType.ARROW)
        self.hand   =  Gdk.Cursor(Gdk.CursorType.HAND1)
        self.down   = 0

        cnt = 0;
        # Process ACCEL Key
        for aa in labx:
            if aa == "_":
                self.mark = cnt
            else:
                if self.mark != -1 and self.accel != "":
                    self.accel = aa
                self.orgtext += aa
            cnt += 1

        #self.set_mnemonic_widget(self)
        #self.set_use_underline(True)
        if tooltip:
            self.lab.set_tooltip_text(tooltip)

        if eventx:
            self.connect("pressed", eventx)

        self.set_can_focus(True)
        self.set_can_default(True)
        self.set_sensitive(True)

        font = "Sans 10"
        self.override_font(Pango.FontDescription(font))

        #self.set_alignment(0.5, 0.5)
        #self.set_margin_left(0)
        #self.set_margin_right(0)
        #self.set_margin_top(0)
        #self.set_margin_bottom(0)

        self.layoutx = self.create_pango_layout("a")
        self.layoutx.set_font_description(Pango.FontDescription(font))
        self.layoutx.set_text(self.orgtext, self.mark)

        (self.charx, self.chary) =  self.layoutx.get_extents()
        self.charx.width /= Pango.SCALE;  self.charx.height /= Pango.SCALE;
        self.chary.width /= Pango.SCALE;  self.chary.height /= Pango.SCALE;

        self.layout  = self.create_pango_layout("a")
        self.layout.set_font_description(Pango.FontDescription(font))
        self.layout.set_text(self.orgtext, len(self.orgtext))
        (pr, lr) = self.layout.get_extents()
        self.ww = lr.width / Pango.SCALE; self.hh = lr.height / Pango.SCALE;
        #print("ww", self.ww, "hh", self.hh)

        self.set_size_request(self.ww, self.hh)
        self.hand_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.connect("enter_notify_event", self.enter_label)
        self.connect("leave_notify_event", self.leave_label)
        self.connect("mnemonic-activate", self.mactivate)
        self.connect("button-release-event", self.buttrel)
        self.connect("button-press-event", self.buttpress)
        self.connect("key-release-event", self.keyrel)
        self.connect("key-press-event", self.keypress)

        self.show_all()
        GLib.timeout_add(1000, self.stattime, self, 0)

    def keyrel(self, *args):
        #print("keyrel")
        if args[1].keyval == Gdk.KEY_space or args[1].keyval == Gdk.KEY_Return :
            self.down = 0
            self.queue_draw()
            self.emit('pressed')

    def keypress(self, *args):
        #print("keypress")
        if args[1].keyval == Gdk.KEY_space or args[1].keyval == Gdk.KEY_Return :
            self.down = 1
            self.queue_draw()

    def buttrel(self, *args):
        #print("buttrel")
        self.down = 0
        self.queue_draw()
        self.emit('pressed')

    def buttpress(self, *args):
       # print("buttpress")
        self.down = 1
        self.queue_draw()

    def mactivate(self):
        print("mactivate")

    def stattime(self, arg2, arg3):

        # Test if mnemonic key is down
        kmap = Gdk.Keymap().get_default()
        state = kmap.get_modifier_state()
        #print("mods", state)
        if state ==  Gdk.ModifierType.MOD1_MASK:
            self.mnem = True
        else:
            self.mnem = False

        if self.omnem != self.mnem:
            self.omnem = self.mnem
            #print("changed to", self.mnem)
            self.queue_draw()

        GLib.timeout_add(1000, self.stattime, self, 0)

    def mactivate(self, *arg):
        #print("mactivate", arg)
        self.emit('pressed')
        return True

    def enter_label(self, arg, arg2):
        #print("Enter")
        self.get_window().set_cursor(self.hand_cursor)
        self.stat2 = 1
        self.queue_draw()

    def leave_label(self, arg, arg2):
        #print("Leave")
        self.get_window().set_cursor()
        self.stat2 = 0
        self.queue_draw()

    def do_draw (self, cr):

        # paint background
        if self.stat2:
            bg_color2 = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
            bg_color = Gdk.RGBA(.9, .9, .9)
        else:
            if 0: #self.has_focus():
                bg_color = Gdk.RGBA(.75, .75, .75)
            else:
                bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)

        cr.set_source_rgba(*list(bg_color))

        cr.rectangle(1,1, self.ww-1, self.hh-1)
        cr.clip()
        cr.paint()

        if 0: #self.stat2:
            fg_color = self.get_style_context().get_color(Gtk.StateFlags.SELECTED)
        else:
            fg_color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)

        cr.set_source_rgba(*list(fg_color));
        cr.move_to(0, 0)
        PangoCairo.show_layout(cr, self.layout)
        if self.down:
            cr.move_to(1, 1)
            PangoCairo.show_layout(cr, self.layout)


        if self.mnem:
            #print("corr", self.chary.width, self.chary.height)
            cr.move_to( self.chary.width,  self.chary.height-2)
            cr.line_to( self.chary.width + 8, self.chary.height-2)
            cr.stroke()

        if self.has_focus():

            #print("focus")
            cr.set_dash([.5, .9])
            cr.move_to( 1, 1)
            cr.line_to( self.ww-1, 1)
            cr.line_to( self.ww-1, self.hh-1)
            cr.line_to( 1, self.hh-1)
            cr.line_to( 1, 1)

        cr.stroke()

# EOF
