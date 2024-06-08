#!/usr/bin/env python3

from __future__ import absolute_import, print_function
import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

try:
    # This will change once the pydbase is out of dev stage
    np = os.path.split(__file__)[0] + os.sep + '..' + os.sep
    #print(np)

    sys.path.append(np)
    #print(sys.path)
    #print(os.getcwd())
    from pyvguicom.browsewin import *
except:
    print("Cannot Load browser window")


import pgwkit


class MainWin(Gtk.Window):

    def __init__(self):

        self.cnt = 0
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        #self = Gtk.Window(Gtk.WindowType.TOPLEVEL)

        #Gtk.register_stock_icons()

        self.set_title("Md viewer")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)


        www = Gdk.Screen.width(); hhh = Gdk.Screen.height();

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print( disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();

        if www / hhh > 2:
            self.set_default_size(5*www/8, 7*hhh/8)
        else:
            self.set_default_size(7*www/8, 7*hhh/8)


        #
        self.connect("destroy", self.exit)

        scrolled_window = Gtk.ScrolledWindow()
        try:
            self.brow_win = browserWin()
            #print("dir", dir(self.brow_win))
            #self.brow_win.load_uri("file://" + self.fname)
        except:
            #self.brow_win = Gtk.Label("No WebView Available.")
            put_exception("WebView load")
            raise

        vbox5 = Gtk.VBox()
        scrolled_window.add(self.brow_win )
        frame4 = Gtk.Frame();
        frame4.add(scrolled_window)
        vbox5.pack_start(frame4, 1,1,0)

        self.add(vbox5)
        self.show_all()
        GLib.timeout_add(200, self.load)

    def exit(self, arg):
        print("exit")
        Gtk.main_quit()

    def load(self):
        with open(newfname) as fd:
            self.brow_win.load_html(fd.read())

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: webwin.py [-d] filename")
        sys.exit(0)

    is_text = False
    #print("argv", sys.argv);
    delmode = 0

    if sys.argv[1] == "-d":
        delmode = 1
        sys.argv = sys.argv[1:]

    newfname = sys.argv[1]
    if not os.path.isfile(newfname):
        is_text = True
        newfname = ""
        for aa in sys.argv[1:]:
            newfname += " " + aa

    #print("newfname", newfname)

    mw = MainWin()
    Gtk.main()

    print("Ended webview delmode", delmode)

    if delmode:
        os.remove(newfname)