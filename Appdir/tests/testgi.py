#!/usr/bin/python

import gi; gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gdk

win = Gtk.Window()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

# EOF
