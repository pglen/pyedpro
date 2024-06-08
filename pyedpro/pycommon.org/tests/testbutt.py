#!/usr/bin/env python

import sys

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

#gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

from pgbutt import *
from pggui import *

class testWin(Gtk.Window):

    def __init__(self, *args, **kwargs):
        super(testWin, self).__init__(*args, **kwargs)

        self.connect("destroy", Gtk.main_quit)

        vbox13 = Gtk.VBox()

        vbox13.pack_start(vspacer(), 0, 0, 0)
        vbox13.pack_start(Gtk.Label.new("Test smallbutt TEST implementation"), 1, 1, 0)
        #vbox13.pack_start(vspacer(), 1, 1, 0)

        hbox13 = Gtk.HBox()
        hbox13.pack_start(vspacer(), 1, 1, 0)
        butt3x = smallbutt(" _Find in Text ", self.findx, "")
        hbox13.pack_start(butt3x, 0, 0, 0)
        hbox13.pack_start(vspacer(), 0, 0, 0)
        butt3z = smallbutt(" _Search All ", self.findx, "")
        hbox13.pack_start(butt3z, 0, 0, 0)
        hbox13.pack_start(vspacer(), 1, 1, 0)

        hbox16 = Gtk.HBox()
        hbox16.pack_start(vspacer(), 1, 1, 0)
        butt3x = smallbutt("_Align in Text", self.findx, "")
        hbox16.pack_start(butt3x, 0, 0, 0)
        hbox16.pack_start(vspacer(), 0, 0, 0)
        butt3z = smallbutt("_Delete All", self.delx, "")
        hbox16.pack_start(butt3z, 0, 0, 0)
        hbox16.pack_start(vspacer(), 1, 1, 0)

        hbox14 = Gtk.HBox()
        hbox14.pack_start(vspacer(), 1, 1, 0)
        butt3y = smallbutt("E_xit", self.exit_prog, "Exit program")
        hbox14.pack_start(butt3y, 0, 0, 0)
        hbox14.pack_start(vspacer(), 1, 1, 0)

        hbox15 = Gtk.HBox()
        hbox15.pack_start(vspacer(), 1, 1, 0)
        butt3z = Gtk.Button.new_with_mnemonic("Regular _Button")
        butt3z.set_relief(Gtk.ReliefStyle.NONE)
        butt3z.connect("clicked", self.regbutt)
        hbox15.pack_start(butt3z, 0, 0, 0)
        hbox15.pack_start(vspacer(), 1, 1, 0)

        vbox13.pack_start(hbox13, 0, 0, 0)
        vbox13.pack_start(hbox16, 0, 0, 0)
        #vbox13.pack_start(hbox15, 0, 0, 0)
        vbox13.pack_start(hbox14, 0, 0, 0)
        vbox13.pack_start(vspacer(), 1, 1, 0)

        self.set_size_request(300, 200)
        self.add(vbox13)
        self.show_all()

        # Gtk.Label
        #print("children", butt3x.get_children())

    def regbutt(self, arg):
        print("regbutt pressed", arg)

    def exit_prog(self, arg):
        print("exit butt", arg)
        self.destroy()
        #Gtk.main_exit()

    def findx(self, arg):
        print("Findx", arg)

    def delx(self, arg):
        print("Delx", arg)

if __name__ == "__main__":
    Gtk.init(sys.argv)
    testwin = testWin()
    Gtk.main()

# EOF