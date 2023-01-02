#!/usr/bin/env python

# Prompt Handler for PyEdPro

from __future__ import absolute_import
from __future__ import print_function
import os, sys, string
import warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

from pedlib import pedconfig

# ------------------------------------------------------------------------

def yes_no_cancel(title, message, cancel = True):

    warnings.simplefilter("ignore")

    dialog = Gtk.Dialog(title,
                   None,
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)

    dialog.set_default_response(Gtk.ResponseType.YES)
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_transient_for(pedconfig.conf.pedwin.mywin)

    sp = "     "
    label = Gtk.Label(message);
    label2 = Gtk.Label(sp);      label3 = Gtk.Label(sp)
    label2a = Gtk.Label(sp);     label3a = Gtk.Label(sp)

    hbox = Gtk.HBox() ;

    hbox.pack_start(label2, 0, 0, 0);
    hbox.pack_start(label, 1, 1, 0);
    hbox.pack_start(label3, 0, 0, 0)

    dialog.vbox.pack_start(label2a, 0, 0, 0);
    dialog.vbox.pack_start(hbox, 0, 0, 0)
    dialog.vbox.pack_start(label3a, 0, 0, 0);

    dialog.add_button("_Yes", Gtk.ResponseType.YES)
    dialog.add_button("_No", Gtk.ResponseType.NO)

    if cancel:
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)

    dialog.connect("key-press-event", yn_key, cancel)
    #dialog.connect("key-release-event", yn_key, cancel)
    warnings.simplefilter("default")

    dialog.show_all()
    response = dialog.run()

    # Convert all responses to cancel
    if  response == Gtk.ResponseType.CANCEL or \
            response == Gtk.ResponseType.REJECT or \
                response == Gtk.ResponseType.CLOSE  or \
                    response == Gtk.ResponseType.DELETE_EVENT:
        response = Gtk.ResponseType.CANCEL

    dialog.destroy()

    #print("YNC result:", response);
    return  response

def yn_key(win, event, cancel):
    #print event
    if event.keyval == Gdk.KEY_y or \
        event.keyval == Gdk.KEY_Y:
        win.response(Gtk.ResponseType.YES)

    if event.keyval == Gdk.KEY_n or \
        event.keyval == Gdk.KEY_N:
        win.response(Gtk.ResponseType.NO)

    if cancel:
        if event.keyval == Gdk.KEY_c or \
            event.keyval == Gdk.KEY_C:
            win.response(Gtk.ResponseType.CANCEL)

# ------------------------------------------------------------------------
# Show About dialog:

import platform

def  about(self2):

    dialog = Gtk.AboutDialog()
    dialog.set_name(pedconfig.conf.progname +  " - Python Editor ")

    dialog.set_version(str(pedconfig.conf.version));
    gver = (Gtk.get_major_version(), \
                        Gtk.get_minor_version(), \
                            Gtk.get_micro_version())

    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_transient_for(pedconfig.conf.pedwin.mywin)

    #"\nRunning PyGObject %d.%d.%d" % GObject.pygobject_version +\

    ddd = os.path.join(os.path.dirname(__file__), "../")

    # GLib.pyglib_version
    vvv = gi.version_info
    comm = "Python based easily configurable editor\n"\
        "with time accounting module, spell "\
        "check \n and macro recording.\n"\
        "\nRunning PyGtk %d.%d.%d" % vvv +\
        "\non GTK %d.%d.%d\n" % gver +\
        "\nRunning Python %s" % platform.python_version() +\
        "\non %s %s\n" % (platform.system(), platform.release()) +\
        "\nPyedPro Build Date: %s\n" % pedconfig.conf.build_date +\
        "Exe Path:\n%s\n" % os.path.realpath(ddd)

    dialog.set_comments(comm);
    dialog.set_copyright(pedconfig.conf.progname + " Created by Peter Glen.\n"
                          "Project is in the Public Domain.")
    dialog.set_program_name(pedconfig.conf.progname)
    img_dir = os.path.join(os.path.dirname(__file__), 'images')
    #img_path = os.path.join(img_dir, 'gtk-logo-rgb.gif')
    img_path = os.path.join(img_dir, 'pyedpro.png')

    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(img_path)
        #print "loaded pixbuf"
        dialog.set_logo(pixbuf)

    except:
        print("Cannot load logo for about dialog", img_path);
        print(sys.exc_info())

    #dialog.set_website("")

    ## Close dialog on user response
    dialog.connect ("response", lambda d, r: d.destroy())
    dialog.connect("key-press-event", about_key)

    dialog.show()

def about_key(win, event):
    #print "about_key", event
    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
            if event.state & Gdk.ModifierType.MOD1_MASK:
                win.destroy()

# ------------------------------------------------------------------------
# Show a regular message:

def message(strx, title = None, parent = None):

    #print("called: message()", strx)

    icon = Gtk.STOCK_INFO
    dialog = Gtk.MessageDialog(buttons=Gtk.ButtonsType.CLOSE,
                               message_type=Gtk.MessageType.INFO)

    dialog.props.text = strx

    try:
        if parent:
            dialog.set_transient_for(parent)
        else:
            dialog.set_transient_for(pedconfig.conf.pedwin.mywin)
    except:
        print(sys.exc_info())

    if title:
        dialog.set_title(title)
    else:
        dialog.set_title("PyEdPro")

    dialog.set_position(Gtk.WindowPosition.CENTER)

    # Close dialog on user response
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.show()
    dialog.run()

#EOF





































