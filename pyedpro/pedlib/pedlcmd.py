#!/usr/bin/env python

# Action Handler for goto

from __future__ import absolute_import

import warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from pedlib import pedconfig

# ------------------------------------------------------------------------

def cmddlg(self2):

    warnings.simplefilter("ignore")

    dialog = Gtk.Dialog("pyedpro: lastCommand",
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                   Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    dialog.set_transient_for(self2.mained.mywin)

    # Spacers
    label1 = Gtk.Label("   ");  label2 = Gtk.Label("   ")
    label3 = Gtk.Label("   ");  label4 = Gtk.Label("   ")
    label5 = Gtk.Label("   ");  label6 = Gtk.Label("   ")
    label7 = Gtk.Label("   ");  label8 = Gtk.Label("   ")

    #warnings.simplefilter("ignore")
    entry = Gtk.Entry();
    #warnings.simplefilter("default")

    entry.set_activates_default(True)

    if  self2.lastcmd == "":
        self2.lastcmd = pedconfig.conf.sql.get_str("lastcmd")
        if  self2.lastcmd == None:
            self2.lastcmd = ""

    entry.set_text(self2.lastcmd)
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

    if response == Gtk.ResponseType.ACCEPT:

        # Save it for later use
        self2.lastcmd = gotxt
        pedconfig.conf.sql.put("lastcmd", gotxt)

        if gotxt == "":
            #self2.mained.update_statusbar("Must specify line to goto.")
            return
        return True

    return False

# EOF




















