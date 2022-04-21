import pdb

import gi; #gi.require_version("Gtk", "3.0")

#pdb.run("from gi.repository import Gtk")

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gdk
from gi.repository import Gtk


win = Gtk.Window()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
