#!/usr/bin/python

''' Testing if it is a pango subsystem error (pango GOOD) '''

import sys, time

import gi; gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gdk
from gi.repository import Pango

import cairo

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

class Test_Control(Gtk.DrawingArea):
    def __init__(self, text):
        self.text = text
        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        self.set_size_request(10, 10)
        self.connect("draw", self.draw_event)

        self.layout = None
        self.fd = Pango.FontDescription()

        ctx = self.get_style_context()

        #self.fd.set_family("Arial")
        self.fd = ctx.get_font(Gtk.StateFlags.NORMAL)

        # Will not wotk right on the MAC if simple set_size used
        self.fd.set_absolute_size(16 * Pango.SCALE)
        self.pangolayout = self.create_pango_layout("a")
        self.pangolayout.set_font_description(self.fd)

    def draw_event(self, pdoc, cr):

        rect = self.get_allocation()
        #print("draw", rect.width, rect.height)

        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        bg_color = ctx.get_background_color(Gtk.StateFlags.NORMAL)

        cr.set_source_rgba(*list(bg_color))

        cr.rectangle( 0, 0, rect.width, rect.height)
        cr.fill()

        cr.set_source_rgba(*list(fg_color))
        self.layout = PangoCairo.create_layout(cr)
        self.layout.set_font_description(self.fd)

        self.layout.set_text(self.text, -1)

        (pr, lr) = self.layout.get_extents()
        xx = lr.width / Pango.SCALE; yy = lr.height / Pango.SCALE;

        # Center it
        cr.move_to(rect.width / 2 - xx / 2, 0)

        PangoCairo.show_layout(cr, self.layout)

    def set_text(self, text):
        self.text = text
        self.queue_draw()

win = Gtk.Window()
win.set_size_request(400, 300)
win.connect("destroy", Gtk.main_quit)
intro = Gtk.Label(label= \
        "The Two labels (below) should show the same:")
lab = Gtk.Label(label="Blank")
sep  = Gtk.Label(label=" ----------- ")
sep2 = Gtk.Label(label=" ----------- ")
lab2 = Test_Control("Blank")

vbox = Gtk.VBox()
vbox.pack_start(intro, 0,0,0)
vbox.pack_start(sep, 0,0,0)
vbox.pack_start(lab, 0,0,0)
vbox.pack_start(sep2, 0,0,0)
vbox.pack_start(lab2, 1,1,0)
win.add(vbox)
win.show_all()

#time.sleep(2)

text = ""
with open(sys.argv[1], "rb") as ff:
    #print(ff)
    text = ff.read().decode("UTF-8", "strict")
    #print(text)
    lab.set_text(text)
    lab2.set_text(text)

#win.show_all()
Gtk.main()

# EOF
