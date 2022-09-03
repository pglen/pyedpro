#!/usr/bin/env python

# Action Handler for goto

from __future__ import absolute_import

import warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

from pedlib import pedconfig

# ------------------------------------------------------------------------

def gotodlg(self2):

    warnings.simplefilter("ignore")

    dialog = Gtk.Dialog("pyedpro: Goto Line",
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                   Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    dialog.set_transient_for(self2.mained.mywin)
    dialog.self2 = self2
    dialog.alt = self2.keyh.alt

    # Spacers
    #label1 = Gtk.Label("   ");  label2 = Gtk.Label("   ")
    #label3 = Gtk.Label("   ");  label4 = Gtk.Label("   ")
    label5 = Gtk.Label("   ");  label6 = Gtk.Label("   ")
    label7 = Gtk.Label("   ");  label8 = Gtk.Label("   ")
    label9 = Gtk.Label("   ");

    labela = Gtk.Label("   ")
    labelb = Gtk.Label("  Top of File: ALT-A   End of File: ALT-Z  ");
    labelc = Gtk.Label("  Line Start: ALT-S    Line End: ALT-E  ");
    labeld = Gtk.Label("  Exit Dialog: ESC or ALT-X  ");
    labele = Gtk.Label("   ")

    dialog.connect("key-press-event", area_key)
    dialog.connect("key-release-event", area_key)

    #warnings.simplefilter("ignore")
    entry = Gtk.Entry();
    #warnings.simplefilter("default")

    entry.set_activates_default(True)

    if  self2.oldgoto == "":
        self2.oldgoto = pedconfig.conf.sql.get_str("goto")
        if  self2.oldgoto == None:
            self2.oldgoto = ""

    entry.set_text(self2.oldgoto)
    entry.set_width_chars(24)

    # Assemble it all

    dialog.vbox.pack_start(labela, 0, 0, 0)
    dialog.vbox.pack_start(labelb, 0, 0, 0)
    dialog.vbox.pack_start(labelc, 0, 0, 0)
    dialog.vbox.pack_start(labele, 0, 0, 0)

    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, 0, 0, 0)
    hbox2.pack_start(entry, 1, 1, 0)
    hbox2.pack_start(label7, 0, 0, 0)
    dialog.vbox.pack_start(hbox2, 0, 0, 0)
    dialog.vbox.pack_start(label5, 0, 0, 0)

    hbox = Gtk.HBox()
    dialog.vbox.pack_start(hbox, 0, 0, 0)
    #dialog.vbox.pack_start(label8, 0, 0, 0)
    dialog.vbox.pack_start(labeld, 0, 0, 0)

    dialog.show_all()
    response = dialog.run()
    gotxt = entry.get_text()
    dialog.destroy()

    if response == Gtk.ResponseType.ACCEPT:
        # Save it for later use
        self2.oldgoto = gotxt
        pedconfig.conf.sql.put("goto", gotxt)

        if gotxt == "":
            self2.mained.update_statusbar("Must specify line to goto.")
            return
        try:
            num = int(gotxt)
        except:
            self2.mained.update_statusbar("Invalid line number.")
            return

        if num > len(self2.text):
            num = len(self2.text)
            self2.gotoxy(0, num - 1)
            self2.mained.update_statusbar("Goto line passed end, landed on %d" %  num)
        else:
            self2.gotoxy(self2.xpos + self2.caret[0], num -1)
            self2.mained.update_statusbar("Done goto line %d" % num)

    warnings.simplefilter("default")

def  area_key(dialog, event):
    #print(keypress)
    if  event.type == Gdk.EventType.KEY_PRESS:
       if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            dialog.alt = True;

    elif  event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            dialog.alt = False;
    else:
        print("Unk keytype")

    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_x or \
                event.keyval == Gdk.KEY_X:
            if dialog.alt:
                dialog.destroy()

        if event.keyval == Gdk.KEY_a or \
                event.keyval == Gdk.KEY_A:
            if dialog.alt:
                dialog.self2.gotoxy(0, 0)
                dialog.destroy()

        if event.keyval == Gdk.KEY_Z or \
                event.keyval == Gdk.KEY_z:
            if dialog.alt:
                last = len(dialog.self2.text) - 1
                xlen = len(dialog.self2.text[last])
                dialog.self2.set_caret(xlen, last)
                dialog.destroy()

        if event.keyval == Gdk.KEY_E or \
                event.keyval == Gdk.KEY_e:
            if dialog.alt:
                xidx = dialog.self2.caret[0] + dialog.self2.xpos;
                yidx = dialog.self2.caret[1] + dialog.self2.ypos
                xlen = len(dialog.self2.text[yidx])
                dialog.self2.set_caret(xlen, yidx)
                dialog.destroy()

        if event.keyval == Gdk.KEY_S or \
                event.keyval == Gdk.KEY_s:
            if dialog.alt:
                xidx = dialog.self2.caret[0] + dialog.self2.xpos;
                yidx = dialog.self2.caret[1] + dialog.self2.ypos
                dialog.self2.set_caret(0, yidx)
                dialog.destroy()

# EOF
