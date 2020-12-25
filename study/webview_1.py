#!/usr/bin/env python3

from __future__ import absolute_import, print_function
import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

import webview

class ImageButton(Gtk.EventBox):

    def __init__(self, label):

        Gtk.EventBox.__init__(self)
        self.label = Gtk.Label(label)
        self.add(self.label)

def on_imagebutton_clicked(button, data=None):
        print("Button has been clicked!")

"""
This example demonstrates a webview window with a quit confirmation dialog.
"""

if __name__ == '__main__':

    '''window = Gtk.Window()
    window.connect("destroy", Gtk.main_quit)
    window.set_size_request(120, 120)
    window.add(button)
    '''
    #button = ImageButton(" My label ")
    #button.connect('button-press-event', on_imagebutton_clicked)

    # Create a standard webview window
    winx = webview.create_window('Example',
                          #'https://pywebview.flowrl.com/hello',
                          #'http://google.com',
                          "test.py",
                          confirm_close=False)

    print("wwwW", dir(webview))

    webview.start()

    #window.show_all()
    #Gtk.main()

