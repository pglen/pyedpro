#!/usr/bin/env python

import gi; gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk

def area_key(area, event):
    strx = "Rel "
    if event.type ==  Gdk.EventType.KEY_PRESS:
        strx = "Pre "
    print("key", strx, event.keyval, event.string, event.state)

mywin = Gtk.Window()
mywin.connect("destroy", Gtk.main_quit)
mywin.connect("key-press-event", area_key)
mywin.connect("key-release-event", area_key)

mywin.show_all()
print("Showing keystrokes")
Gtk.main()

