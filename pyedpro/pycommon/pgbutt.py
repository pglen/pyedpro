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

import cairo
from sutil import *

class smallbutt(Gtk.Widget):

    __gsignals__ = {
      "xmnemonic-activate": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
                        (GObject.TYPE_BOOLEAN,GObject.TYPE_OBJECT,)),
      "test-activate": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, () ),

      "activate": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, () ),
    }

    #__gsignals__ = {
    #    'activate': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_OBJECT,)   ),
    #}

    #def __init__(self, ):

    def __init__(self, labx, eventx, tooltip = None, *args, **kwds):

        #GObject.GObject.__init__(self)
        #Gtk.Widget.__init__(self)
        #super().__init__()
        super().__init__(*args, **kwds)

        self.state = 0; self.stat2 = 0
        self.labx = ""; self.accel = ""; mark = 0
        self.agroup = None

        # Process ACCEL Key
        for aa in labx:
            if aa == "_":
                mark = 1
            else:
                if mark:
                    #print("Accel", aa)
                    self.accel = aa
                    mark = 0
                self.labx += aa
        self.eventx = eventx

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.akey = 0

        self.set_can_focus(True)
        self.set_can_default(True)
        self.set_sensitive(True)
        self.add_mnemonic_label(self)

        self.layout = self.create_pango_layout("a")
        self.layout.set_text(self.labx, len(self.labx))
        (pr, lr) = self.layout.get_extents()
        xx = lr.width / Pango.SCALE; yy = lr.height / Pango.SCALE;
        #print("xx", xx, "yy", yy)

        self.set_size_request(xx, yy)
        self.hand_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)

        if tooltip:
            self.set_tooltip_text(tooltip)

        self.connect("mnemonic-activate", self.eventmn)
        self.connect("xmnemonic-activate", self.eventmn2)
        self.connect("test-activate", self.eventmn3)
        self.connect("activate", self.eventmn4)

        self.connect("button-press-event", self.event_press)
        self.connect("button-release-event", self.event_release)

        self.connect("enter_notify_event", self.enter_label)
        self.connect("leave_notify_event", self.leave_label)

        self.show_all()
        #self.emit('mnemonic-activate', 0)
        #self.emit('xmnemonic-activate', 0, self)
        self.emit('test-activate')
        self.emit('activate')

    def add_accel(self):

        if self.accel:
            self.akey = Gdk.keyval_from_name(self.accel.lower())
            print("akey", self.akey)

            #self.agroup = Gtk.AccelGroup()

            #accel.connect(self.akey,
            #    Gdk.ModifierType.MOD1_MASK, 0, self.on_accel_pressed)
            #
            key, mod = Gtk.accelerator_parse("<Alt>N")
            print("key, mod", key, mod)
            self.add_accelerator("activate",
                     self.agroup,
                     key, mod,
                     #self.akey, Gdk.ModifierType.MOD1_MASK,
                        Gtk.AccelFlags.VISIBLE)

            #self.get_toplevel().add_mnemonic()
            #self.add_accel_group(self.agroup)

        #usleep(100)

    def  on_accel_pressed(self):
        print("on_accel_pressed")

    def do_draw(self, cr):

        # paint background
        if self.stat2:
            bg_color2 = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
            #print(bg_color2)
            #bg_color = Gdk.RGBA(bg_color2.red-0.1, bg_color2.green-0.1, bg_color2.blue -0.1)
            #bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)

            bg_color = Gdk.RGBA(.9, .9, .9)
            #print(bg_color)
        else:
            bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)

        cr.set_source_rgba(*list(bg_color))
        cr.paint()

        #sss = self.get_state()
        #if sss ==  Gtk.StateFlags.SELECTED:

        if 0: #self.stat2:
            fg_color = self.get_style_context().get_color(Gtk.StateFlags.SELECTED)
        else:
            fg_color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)

        #print(fg_color)

        # draw a diagonal line
        #allocation = self.get_allocation()
        cr.set_source_rgba(*list(fg_color));
        cr.move_to(0, 0)
        PangoCairo.show_layout(cr, self.layout)

        if self.state:
            cr.move_to(1, 1)
            PangoCairo.show_layout(cr, self.layout)
        cr.stroke()

    def do_realize(self):
        allocation = self.get_allocation()
        attr = Gdk.WindowAttr()
        attr.window_type = Gdk.WindowType.CHILD
        attr.x = allocation.x
        attr.y = allocation.y
        attr.width = allocation.width
        attr.height = allocation.height
        attr.visual = self.get_visual()
        attr.event_mask = self.get_events() | Gdk.EventMask.EXPOSURE_MASK
        WAT = Gdk.WindowAttributesType
        mask = WAT.X | WAT.Y | WAT.VISUAL
        window = Gdk.Window(self.get_parent_window(), attr, mask);
        self.set_window(window)
        self.register_window(window)
        self.set_realized(True)
        window.set_background_pattern(None)

    def  event_press(self, arg1, arg2):
        #print("widget press", arg1, arg2)
        self.state = 1
        self.queue_draw()
        #self.set_state(Gtk.StateFlags.SELECTED)
        #self.eventx(arg1, arg2)

    def  event_release(self, arg1, arg2):
        #print("widget release", arg1, arg2)
        #self.set_state(Gtk.StateFlags.NORMAL)
        self.state = 0
        self.queue_draw()
        xx, yy =  self.get_pointer()
        rrr = self.get_allocation()
        #print(xx, yy, "vvv", rrr.x, rrr.y, rrr.width, rrr.height)

        # If release was outside, cancel action
        if xx < 0 or xx > rrr.width:
            #print("xx over")
            return
        if yy < 0 or yy > rrr.height:
            #print("yy over")
            return
        self.eventx(arg1, arg2)

    def  eventmn(self, arg1, arg2):
        #print("widget mnemonic activate", arg1, arg2)
        pass

    def  eventmn2(self, arg1, arg2, arg3):
        pass
        #print("widget mnemonic activate", arg1, arg2, arg3)

    def  eventmn3(self, arg):
        pass
        #print("widget test mnemonic activate", arg)

    def  eventmn4(self, arg):
        pass
        #print("widget test activate", arg)

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


