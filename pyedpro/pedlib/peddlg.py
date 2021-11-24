#!/usr/bin/env python3

# Action Handler for find

from __future__ import absolute_import
from __future__ import print_function

import re, string, warnings, sys

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango

def  _keypress(area, event):
    #print( arg1, arg2)
    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.state  & Gdk.ModifierType.MOD1_MASK:
            #print("stridx", stridx)
            #for aa in strhist:
            #    print (aa)
            if event.keyval == Gdk.KEY_Up or \
                    event.keyval == Gdk.KEY_Right:
                #print   ("find dlg keypress, alt UP or right key", stridx)
                if stridx < len(strhist) - 1:
                    stridx += 1
                    myentry.set_text(strhist[stridx]);

            if event.keyval == Gdk.KEY_Down or \
                    event.keyval == Gdk.KEY_Left:
                #print   ("find dlg keypress, alt DOWN or left", stridx)
                if stridx > 0:
                    stridx -= 1
                    myentry.set_text(strhist[stridx]);

            if event.state  & Gdk.ModifierType.MOD1_MASK:
                if event.keyval == Gdk.KEY_X or \
                    event.keyval == Gdk.KEY_x:
                    area.destroy()
        pass


def  config_dlg(title, head, clip, parent = None):

    dialog = Gtk.Dialog(title,
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    #dialog.set_transient_for(self2.mained.mywin)
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_size_request(800, 600)

    '''try:
        dialog.set_icon_from_file(get_img_path("pyedpro_sub.png"))
    except:
        print("Cannot load find dialog icon", sys.exc_info())
    '''

    # Spacers
    label1 = Gtk.Label("   ");  label2 = Gtk.Label("   ")
    label3 = Gtk.Label("   ");  label4 = Gtk.Label("   ")
    label5 = Gtk.Label("   ");  label6 = Gtk.Label("   ")
    label7 = Gtk.Label("   ");  label8 = Gtk.Label("   ")

    entry = Gtk.Entry(); entry.set_max_width_chars(64);
    entry.set_text(head)

    #entry2 = Gtk.Entry();
    #entry2.set_activates_default(True)
    #entry2.set_text(clip)

    tview = Gtk.TextView();
    tview.modify_font(Pango.FontDescription("Mono 13"))

    #tview.set_buffer(Gtk.TextBuffer(clip))
    tview.get_buffer().set_text(clip)

    scroll = Gtk.ScrolledWindow()
    scroll.set_size_request(500, 400)
    scroll.add(tview)

    dialog.vbox.pack_start(label4, 0, 0, 0)

    spacer(dialog.vbox, "Button text:")
    spacer(dialog.vbox)

    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, 0, 0, 0)
    hbox2.pack_start(entry, True, True, 0)
    hbox2.pack_start(label7, 0, 0, 0)
    dialog.vbox.pack_start(hbox2, 0, 0, 0)
    spacer(dialog.vbox)

    dialog.vbox.pack_start(Gtk.Label.new("Macros expanded: %PROJECT%, %DATE% %TIME% %FILE%"), 1, 1, 2)
    spacer(dialog.vbox, "Pasted Contents:")
    spacer(dialog.vbox)

    hbox3 = Gtk.HBox()
    hbox3.pack_start(Gtk.Label("   "), 0, 0, 0)
    #hbox3.pack_start(entry2, True, True, 0)
    #hbox3.pack_start(tview, True, True, 0)
    hbox3.pack_start(scroll, True, True, 0)
    hbox3.pack_start(Gtk.Label("   "), 0, 0, 0)
    dialog.vbox.pack_start(hbox3, 0, 0, 0)
    spacer(dialog.vbox)

    hbox = Gtk.HBox()
    hbox.pack_start(label1, 0, 0, 0)

    #hbox.pack_start(dialog.checkbox, 0, 0, 0)
    #hbox.pack_start(label2, 0, 0, 0)
    #hbox.pack_start(dialog.checkbox2, 0, 0, 0)
    #hbox.pack_start(label3, 0, 0, 0)
    #dialog.vbox.pack_start(hbox, 0, 0, 0)
    #dialog.vbox.pack_start(label8, 0, 0, 0)

    label30 = Gtk.Label("   ");  label31 = Gtk.Label("   ")
    label32 = Gtk.Label("   ");  label33 = Gtk.Label("   ")
    label34 = Gtk.Label("   ");  label35 = Gtk.Label("   ")

    #dialog.checkbox3 = Gtk.CheckButton.new_with_mnemonic("Search _All Buffers")
    #dialog.checkbox4 = Gtk.CheckButton("Hello")
    #hbox4 = Gtk.HBox()
    #hbox4.pack_start(label30, 0, 0, 0);
    #hbox4.pack_start(dialog.checkbox3, 0, 0, 0)
    #hbox4.pack_start(label31, 0, 0, 0);
    #hbox4.pack_start(dialog.checkbox4, 0, 0, 0)
    #hbox4.pack_start(label32, 0, 0, 0);
    #dialog.vbox.pack_start(hbox4, 0, 0, 0)
    #dialog.vbox.pack_start(label33, 0, 0, 0)

    #dialog.connect("key-press-event", _keypress)

    dialog.show_all()
    response = dialog.run()

    eee = entry.get_text()[:]
    #ccc = entry2.get_text()[:]
    startt = tview.get_buffer().get_start_iter()
    endd = tview.get_buffer().get_end_iter()
    ccc = tview.get_buffer().get_text(startt, endd, False)[:]

    dialog.destroy()

    if response != Gtk.ResponseType.ACCEPT:
        #print ("aborted entry")
        return None, None

    # saving ...
    #print ("butt", eee, "clip", ccc)
    return eee, ccc

def     spacer(vbox, txt = "   "):

    hbox = Gtk.HBox()
    hbox.pack_start(Gtk.Label(" " + txt + " "), 0, 0, 0)
    vbox.pack_start(hbox, 0, 0, 0)
    return hbox




