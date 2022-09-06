# This is loaded dynamically into PyEdPro

import os, sys

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

verbose = 0

# ------------------------------------------------------------------------
# Demo plugin, display SHADOWED text on the LOWER RIGHT corner:
# Could be used as a customization logo

def display(disp, cr):

    # Disable for now
    return

    txt = "Hello PyEdPro plugin."
    disp.layout.set_text(txt, len(txt))

    (pr, lr) = disp.layout.get_extents()
    xx = lr.width / Pango.SCALE; yy = lr.height / Pango.SCALE;
    #print("xx", xx, "yy", yy)

    cr.move_to(disp.get_width() - xx - 1, disp.get_height() - yy - 1)
    cr.set_source_rgba(0.05, 0.5, 0.5)
    PangoCairo.show_layout(cr, disp.layout)

    cr.move_to(disp.get_width() - xx, disp.get_height() - yy)
    cr.set_source_rgba(0.0, 0.0, 1.0)
    PangoCairo.show_layout(cr, disp.layout)

# Print the eventkey details

def keypress(disp, keyx):
    #aprint("Keypress", disp, keyx)
    #if 1: #keyx.string ==qqwWWWwwWWA 'a':
    #    print(qwerrfvbnmkeyx.type, keyx.string, keyx.keyval, keyx.state)
    pass

# This is a placeholder for init; Define to prevent a plugin
# loader to print an error string on 'missing init' like this ...
# def init():
#   pass

def init():
    base = os.path.basename(__file__)
    if verbose:
        print("Called init function for plugin:", base)
    pass

# EOF