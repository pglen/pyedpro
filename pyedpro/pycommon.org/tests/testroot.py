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
#from gi.repository import WebKit2

from pgbutt import *
from pggui import *

# Allow the core to search pydbase
#fff = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pydbase/")
fff =  "../pydbase/"
#print(fff)

sys.path.append(fff)
from  pydbase import twincore
#from  pydbase.twincore import *

#print( dir() )
#print(dir(twincore))

class PopWin():

    def __init__(self, randx = 0):
        popup = Gtk.Window.new( Gtk.WindowType.TOPLEVEL)
        #popup = Gtk.Window.new( Gtk.WindowType.POPUP)
        popup.set_title("Hello")

        self.randx = randx
        if not self.randx:
            self.randx = random.randint(1, 0xffffffff)

        popup.set_resizable(True)
        #popup.set_transient_for(self)

        #hb = Gtk.HeaderBar()
        #hb.set_decoration_layout(None)
        #hb.set_title("No title")
        #hb.set_border_width(0)
        #hb.set_size_request(-1, 10)
        #hb.set_show_close_button(True)

        popup.set_default_size(200, 300)
        Gtk.Label.new("Titlebar")
        popup.set_decorated(True)
        popup.set_skip_pager_hint(True)
        popup.set_skip_taskbar_hint(True)
        popup.set_type_hint(Gdk.WindowTypeHint.TOOLBAR)

        self.popup = popup
        self.label = Gtk.Label.new("Hello")
        #print("lab", self.popup.get_toplevel())
        popup.add(self.label)
        popup.connect("delete-event", self.deletevent)
        popup.show_all()
        core = twincore.TwinCore()


    def deletevent(self, arg, arg2):
        #print("deletevent called", arg, arg2)
        self.savepos()

    def post(self):
        xx, yy = self.popup.get_position()
        #xx += random.randint(-xx//2, xx//2)
        #xx += random.randint(-xx//2, xx//2)
        yy += random.randint(-300, 300)
        xx += random.randint(-200, 200)
        self.popup.move(xx, yy)
        #print("lab", self.popup.get_toplevel())
        #print("att", self.popup.props.decorated)
        #print("def", self.popup.get_default_widget())

    def dest(self):
        self.savepos()
        self.popup.destroy()

    def savepos(self):
        tl = self.popup.get_toplevel()
        xx, yy = tl.get_position()
        print("dest xx",  xx, "yy", yy, hex(self.randx))


class testWin(Gtk.Window):

    def __init__(self, *args, **kwargs):
        super(testWin, self).__init__(*args, **kwargs)

        self.connect("destroy", self.dest)

        vbox13 = Gtk.VBox()

        #vbox13.pack_start(vspacer(), 0, 0, 0)
        vbox13.pack_start(Gtk.Label.new("  Test root entry window implementation  "), 1, 1, 0)

        #popup.set_titlebar(Gtk.Button())
        #popup.set_titlebar(hb)

        self.arr = []
        for aa in range(3):
            self.arr.append(PopWin())
        vbox13.pack_start(vspacer(), 1, 1, 0)

        hbox14 = Gtk.HBox()
        hbox14.pack_start(vspacer(), 1, 1, 0)
        butt3y = smallbutt("E_xit", self.exit_prog, "Exit program")
        hbox14.pack_start(butt3y, 0, 0, 0)
        hbox14.pack_start(vspacer(), 1, 1, 0)

        vbox13.pack_start(hbox14, 0, 0, 0)
        vbox13.pack_start(vspacer(12), 0, 0, 0)

        self.set_size_request(300, 200)
        self.add(vbox13)
        self.show_all()

        for bb in self.arr:
            bb.post()

        # Gtk.Label
        #print("children", butt3x.get_children())

    def dest(self, win):
        for aa in self.arr:
            aa.dest()
        Gtk.main_quit()

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