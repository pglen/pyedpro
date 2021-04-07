#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings
import inspect

realinc = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pycommon")
sys.path.append(realinc)

from pgutils import  *
from pggui import  *
from pgsimp import  *

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

try:
    gi.require_version('WebKit2', '4.0')
    from gi.repository import WebKit2

except:
    # Define a blank one  -- too complex to work
    #class   WebKit2():
    #    def __init__(self):
    #        pass
    #    class  WebView(Gtk.Label):
    #        def __init__(self):
    #            pass
    #        def load_uri(self, url):
    #            pass
    print("Cannot import webkit2, web functions may not be available.")
    raise

class pgwebw(WebKit2.WebView):

    def __init__(self, xlink=None):
        try:
            GObject.GObject.__init__(self)
        except:
            pass
        self.xlink = xlink

    def do_ready_to_show(self):
        #print("do_ready_to_show() was called")
        pass

    def do_load_changed(self, status):

        #print("do_load_changed() was called", status)
        if self.get_uri():
            if self.xlink:
                self.xlink.status.set_text("Loading ... " + self.get_uri()[:64])

        if status == 3: #WebKit2.LoadEvent.WEBKIT_LOAD_FINISHED:
            #print("got WEBKIT_LOAD_FINISHED")
            if self.get_uri():
                if self.xlink:
                    self.xlink.edit.set_text(self.get_uri()[:64])
                    self.xlink.status.set_text("Finished: " + self.get_uri()[:64])
            self.grab_focus()

    def do_load_failed(self, load_event, failing_uri, error):
        print("do_load_failed() was called", failing_uri)
        if self.xlink:
            self.xlink.status.set_text("Failed: " + failing_uri[:64])

# EOF