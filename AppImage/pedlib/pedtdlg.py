#!/usr/bin/env python

# Action Handler for goto

from __future__ import absolute_import
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import warnings

from pedlib import pedconfig

def textdlg(oldtext = "", parent = None):

    warnings.simplefilter("ignore")

    dialog = Gtk.Dialog("pyedpro: Get text",
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                   Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)

    if parent:
        dialog.set_transient_for(parent)

    # Spacers
    label1 = Gtk.Label("   ");  label2 = Gtk.Label("   ")
    label3 = Gtk.Label("   ");  label4 = Gtk.Label("   ")
    label5 = Gtk.Label("   ");  label6 = Gtk.Label("   ")
    label7 = Gtk.Label("   ");  label8 = Gtk.Label("   ")

    #warnings.simplefilter("ignore")
    entry = Gtk.Entry();
    entry.set_text(oldtext)
    #warnings.simplefilter("default")

    entry.set_activates_default(True)

    #if  self2.oldgoto == "":
    #    self2.oldgoto = pedconfig.conf.sql.get_str("goto")
    #    if  self2.oldgoto == None:
    #        self2.oldgoto = ""
    #
    #entry.set_text(self2.oldgoto)

    entry.set_width_chars(24)
    dialog.vbox.pack_start(label4, 0, 0, 0)

    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, 0, 0, 0)
    hbox2.pack_start(entry, 0, 0, 0)
    hbox2.pack_start(label7, 0, 0, 0)
    dialog.vbox.pack_start(hbox2, 0, 0, 0)
    dialog.vbox.pack_start(label5, 0, 0, 0)

    hbox = Gtk.HBox()
    dialog.vbox.pack_start(hbox, 0, 0, 0)
    dialog.vbox.pack_start(label8, 0, 0, 0)

    dialog.show_all()
    response = dialog.run()
    gotxt = entry.get_text()
    dialog.destroy()
    warnings.simplefilter("default")

    #if response != Gtk.ResponseType.ACCEPT:
    #    gotxt = ""

    return (response, gotxt)

# EOF

























