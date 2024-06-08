#!/usr/bin/env python

''' This encapsulates the browser window wit the webkia an toolbars '''

import os, sys, getopt, signal, random, time, warnings

realinc = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pycommon")
if realinc not in sys.path:
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

from pedlib import pedconfig

import pgwkit
#print("pgwkit:", pgwkit)

class  browserWin(Gtk.VBox):

    ''' Collection of URL bar, toolbar, status bar '''

    def __init__(self):

        try:
            Gtk.VBox.__init__(self)
        except:
            pass

        # TEST Mnemonic Label
        #bbb = Gtk.Button.new_with_mnemonic("_Hello")
        #self.pack_start(bbb, 0, 0, 0)

        hbox3 = self.urlbar()
        self.pack_start(hbox3, 0, 0, 0)

        #if not conf.kiosk:
        #    vbox.pack_start(hbox3, False, False, 2)

        self.scroll_win = Gtk.ScrolledWindow()

        try:
            self.webview = pgwkit.pgwebw(self)
        except:
            print("Please install WebKit2", sys.exc_info())
            #if pedconfig.conf.verbose:
            put_exception("start webview")
            #sys.exit(1)
            #raise

        #self.old_html = ""
        self.scroll_win.add(self.webview)
        self.webview.editor = self.webview

        self.toolbar2 = self.webview.ui.get_widget("/toolbar_format")
        self.pack_start(self.toolbar2, False, False, 0)

        self.pack_start(self.scroll_win, 1, 1, 2)

        hbox5 = Gtk.HBox()
        hbox5.pack_start(Gtk.Label("  "), 0, 0, 0)
        self.status = Gtk.Label(" Idle ");
        self.status.set_xalign(0)

        hbox5.pack_start(self.status, 1, 1, 0)
        hbox5.pack_start(Gtk.Label("  "), 0, 0, 0)
        self.set_status(" Idle State ")

        self.pack_start(hbox5, 0, 0, 2)

        #self.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
        #self.set_sensitive(True)

        # Receive key presses
        self.set_can_focus(True)
        #self.grab_focus()

    def load_html(self, strx):
        self.webview.load_html(strx)

    def cut(self):
        #print("cut")
        self.webview.on_action("cut")

    def copy(self):
        #print("copy")
        self.webview.on_action("copy")

    def paste(self):
        #print("paste")
        self.webview.on_paste()
        #self.webview.on_action("paste")

    def open(self):
        dialog = Gtk.FileChooserDialog("Open an HTML file", None,
                Gtk.FileChooserAction.OPEN,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        ret = dialog.run()
        fn = dialog.get_filename()
        dialog.destroy()

        if ret == Gtk.ResponseType.OK:
            if not fn:
                return
            if os.path.exists(fn):
                self.fname = fn
                with open(fn) as fd:
                    self.webview.load_html(fd.read(), "file:///")

    def save(self):

        #print("brow_win", "save", self.fname)
        def completion(html, user_data):
            #print("len html", len(html), len(self.webview.old_html) )
            #print("html", html, "old", self.webview.old_html )
            #if self.webview.old_html == html:

            if not self.webview.modified:
                self.set_status("File NOT modified.") # '%s'" % self.fname)
            else:
                #self.webview.old_html = html
                open_mode = user_data
                with open(self.fname, open_mode) as fd:
                    fd.write(html)
                self.set_status("Saved file '%s'" % self.fname)
                self.webview.modified = False
        self.webview.get_html(completion, 'w')

    def is_modified(self):
        return self.webview.modified

    def _completion(self, html, user_data):
        self.ret = html
        self.done = True
        self.webview.modified = False
        #print("retx", ret)

    def get_content(self):
        self.done = 0; self.ret = ""
        self.webview.get_html(self._completion, "w")
        # Wait until done is set
        for aa in range(1000):
            if self.done:
                break
            Gtk.main_iteration_do(False)
        return self.ret

    def saveas(self):
        def completion(html, user_data):
            open_mode = user_data
            with open(self.fname, open_mode) as fd:
                fd.write(html)
            self.set_status("Saved as '%s'" % self.fname)

        dialog = Gtk.FileChooserDialog("Select an HTML file", None,
                Gtk.FileChooserAction.SAVE,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            self.fname = dialog.get_filename()
            #print("Saving", self.fname)
            self.webview.get_html(completion, "w+")
        dialog.destroy()

    def url_callb(self, xtxt):
        self.webview.go(xtxt)

    def url_callb(self, xtxt):
        self.go(xtxt)

    def backurl(self, url, parm, buff):
        self.webview.go_back()

    def baseurl(self, url, parm, buff):
        self.webview.load_uri("file://" + self.fname)

    def forwurl(self, url, parm, buff):
        self.webview.go_forward()

    #def gourl(self, url, parm, buff):
    def gourl(self, *url):
        print("gourl", *url)
        self.go(self.edit.get_text())

    def go(self, xstr):
        print("go", xstr)

        #  Leave known URL scemes alone
        if xstr[:7] == "file://":
            sss = os.path.realpath(xstr[7:])
            xstr = "file://" + sss
            pass
        elif xstr[:7] == "http://":
            pass
        elif xstr[:8] == "https://":
            pass
        elif xstr[:6] == "ftp://":
            pass
        elif str.isdecimal(xstr[0]):
            #print("Possible IP")
            pass
        else:
            # Yeah, padd it
            xstr = "https://" + xstr

        self.webview.load_uri(xstr)

    def stattime(self, *arg):
        self.status.set_text("Idle.")

    def set_status(self, xtxt):
        self.status.set_text(xtxt)
        GLib.timeout_add(3000, self.stattime, self, 0)

    def urlbar(self):

        self.edit = SimpleEdit();
        self.edit.setsavecb(self.url_callb)
        self.edit.single_line = True

        hbox3 = Gtk.HBox()
        uuu  = Gtk.Label("  URL:  ")
        uuu.set_tooltip_text("Current / New URL; press Enter to go")
        hbox3.pack_start(uuu, 0, 0, 0)

        hbox3.pack_start(self.edit, True, True, 2)

        bbb = LabelButt(" _Go ", self.gourl, "Go to speified URL")
        #bbb = Gtk.Button.new_with_mnemonic(" _Go ") #, self.gourl, "Go to speified URL")
        #bbb.connect("clicked", self.gourl)

        #bbb = LabelButt(" _Go ", self.gourl, "Go to speified URL")
        ccc = LabelButt(" <-_Back  ", self.backurl, "Go Back")
        ddd = LabelButt("  For_w-> ", self.forwurl, "Go Forw")
        eee = LabelButt("   B_ase  ", self.baseurl, "Go to base URL")

        hbox3.pack_start(Gtk.Label("  "), 0, 0, 0)

        hbox3.pack_start(bbb, 0, 0, 0)
        hbox3.pack_start(ccc, 0, 0, 0)
        hbox3.pack_start(ddd, 0, 0, 0)
        hbox3.pack_start(eee, 0, 0, 0)

        #hbox3.pack_start(Gtk.Label("  ^  "), 0, 0, 0)
        hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)

        return hbox3

# EOF