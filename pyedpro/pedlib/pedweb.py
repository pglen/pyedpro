#!/usr/bin/env python3

from __future__ import absolute_import, print_function
import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings

import gi;

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

#    gi.require_version('WebKit2', '4.0')

from pedlib import pedconfig

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedutil import *

#sys.path.append('..' + os.sep + "pycommon")

from pycommon.pggui import *
from pycommon.pgsimp import *
from pycommon.pgbutt import *

try:
    from  pycommon import pgwkit
    if pedconfig.conf.pgdebug > 0:
        print("Loaded pgwkit")

except:
    if pedconfig.conf.verbose:
        print("Cannot load pgwkit")

try:
    # This will change once the pydbase is out of dev stage
    np = os.path.split(__file__)[0] + os.sep + '..' + os.sep + ".." + os.sep + ".."
    #print(np)
    sys.path.append(np)
    #print(sys.path)
    #print(os.getcwd())
    from pydbase import twincore
except:
    print("Cannot import twincore", sys.exc_info())

# ------------------------------------------------------------------------

class pgweb(Gtk.VBox):

    def __init__(self):

        self. wasin = True

        #vbox = Gtk.VBox()
        Gtk.VBox.__init__(self)

        self.lastsel = None;  self.lastkey = None
        self.cnt = 0

        self.web_dir = pedconfig.conf.web_dir

        if pedconfig.conf.verbose:
            print("Using webdir:", self.web_dir)

        try:
            if not os.path.isdir(self.web_dir):
                os.mkdir(self.web_dir)
        except:
            print("Cannot make web notes data dir")

        try:
            self.core = twincore.TwinCore(self.web_dir + os.sep + "pedweb.pydb")
            if pedconfig.conf.pgdebug > 2:
                print("core", self.core, self.core.fname)
        except:
            print("Cannot open / make web notes py database", sys.exc_info())

        #message("Cannot make notes database")

        #hbox = Gtk.HBox()
        self.pack_start(Gtk.Label(""), 0, 0, 0)
        #self.pack_start(pggui.xSpacer(), 0, 0, 0)
        self.lsel = pgsimp.LetterNumberSel(self.letterfilter, font="Mono 12")
        self.lsel.set_tooltip_text("Filter entries by letter / number")
        self.pack_start(self.lsel, 0, 0, 2)

        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#dd8822"))

        hbox3 = Gtk.HBox()
        #hbox3.pack_start(Gtk.Label(""), 0, 0, 0)
        #hbox3.pack_start(pggui.xSpacer(4), 0, 0, 0)
        #hbox3.pack_start(Gtk.Label(""), 0, 0, 0)
        #self.edit = Gtk.Entry()
        #hbox3.pack_start(Gtk.Label(" Find: "), 0, 0, 0)
        #hbox3.pack_start(self.edit, 1, 1, 0)
        #butt2 = Gtk.Button.new_with_mnemonic("Find")
        #butt2.connect("pressed", self.find)
        #hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)
        #hbox3.pack_start(butt2, 0, 0, 0)
        #hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)
        #hbox3.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#668822"))
        #self.pack_start(hbox3, 0, 0, 2)

        self.treeview2 = pgsimp.SimpleTree(("Header", "Subject", "Description"), skipedit=0)
        self.treeview2.setcallb(self.treesel)
        #self.treeview2.setCHcallb(self.treechange)

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        #scroll2.set_policy (Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vpaned = Gtk.VPaned()

        frame3 = Gtk.Frame();
        frame3.add(scroll2)
        vpaned.add(frame3)

        vpaned.set_position(300)
        self.pack_start(vpaned, 1, 1, 2)

        #self.edview = pgsimp.TextViewWin()
        #self.edview =  pgTextView()

        self.fname = os.path.dirname(__file__) + os.sep + "home.html"
        #print("fname", self.fname)

        hbox = Gtk.HBox()
        self.lastsel = ""

        hbox3 = Gtk.HBox()
        #scroll12 = Gtk.ScrolledWindow()
        self.edit = Gtk.Entry()
        #scroll12.add(self.edit)
        self.edit.set_width_chars(12)
        #self.edit.set_size_request(96,96)

        self.edit.set_activates_default(True)
        self.edit.connect("activate", self.go)

        hbox3.pack_start(Gtk.Label(" URL: "), 0, 0, 0)
        hbox3.pack_start(self.edit, 1, 1, 0)
        #hbox3.pack_start(scroll12, 1, 1, 0)
        hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)

        butt2 = Gtk.Button("Go")
        butt2.connect("pressed", self.go)
        hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox3.pack_start(butt2, 0, 0, 0)

        self.pack_start(hbox3, 0, 0, 2)

        hbox4 = Gtk.HBox()
        lab1  = Gtk.Label("  Note: This is a Live Browser ")
        lab1.set_halign(Gtk.Align.END)
        hbox4.pack_start(lab1,  1, 1, 0)

        butt3 = Gtk.Button("<")
        butt3.connect("pressed", self.backurl)
        butt3.set_tooltip_text("Back")
        hbox4.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox4.pack_start(butt3, 0, 0, 0)

        butt4 = Gtk.Button(">")
        butt4.connect("pressed", self.forwurl)
        butt4.set_tooltip_text("Forward")
        hbox4.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox4.pack_start(butt4, 0, 0, 0)

        butt5 = Gtk.Button("~")
        butt5.connect("pressed", self.anchor)
        butt5.set_tooltip_text("Goto local anchor page")
        hbox4.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox4.pack_start(butt5, 0, 0, 0)

        #hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)

        self.pack_start(hbox4, 0, 0, 2)

        self.treeview3 = SimpleTree(("Hour", "Subject", "Alarm", "Notes"))
        self.treeview3.setcallb(self.treesel)

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview3)
        frame3 = Gtk.Frame(); frame3.add(scroll2)
        #self.pack_start(frame3, 1, 1, 2)

        #self.edview = SimpleEdit()
        #self.edview.setsavecb(self.savetext)

        #scroll3 = Gtk.ScrolledWindow()
        #scroll3.add(self.edview)
        #frame4 = Gtk.Frame(); frame4.add(scroll3)

        scrolled_window = Gtk.ScrolledWindow()
        try:
            #self.webview = WebKit2.WebView()
            self.webview = pgwkit.pgwebw(self)
            #print("dir", dir(self.webview))
            #self.webview.load_uri("file://" + self.fname)
        except:
            self.webview = Gtk.Label("No WebView Available.")
            print("WebView Load Error", sys.exc_info())

        #webview.load_uri("https://google.com")
        scrolled_window.add(self.webview)
        self.pack_start(scrolled_window, 1, 1, 2)

        self.status = Gtk.Label(" Status: ")
        self.pack_start(self.status, 0, 0, 2)

        hbox13 = Gtk.HBox()
        hbox13.pack_start(Gtk.Label(label=""), 1, 1, 0)

        hbox13.pack_start(Gtk.Label(" | "), 0, 0, 0)
        butt3 = smallbutt(" _New Item ", self.newitem, "Create new item / record")

        hbox13.pack_start(butt3, 0, 0, 2)
        hbox13.pack_start(Gtk.Label(" | "), 0, 0, 0)

        butt3a = smallbutt(" Find in Text ", self.search, "Search this record")
        hbox13.pack_start(butt3a, 0, 0, 0)
        hbox13.pack_start(Gtk.Label(" | "), 0, 0, 0)

        butt3b = smallbutt(" Search in All ", self.searchall, "Search all records")

        hbox13.pack_start(butt3b, 0, 0, 0)
        hbox13.pack_start(Gtk.Label(" | "), 0, 0, 0)

        hbox13.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        hbox13a = Gtk.HBox()
        hbox13a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        hbox13a.pack_start(Gtk.Label(" | "), 0, 0, 0)
        butt11 = smallbutt(" Del Item ", self.searchall, "Delete One Rec")
        hbox13a.pack_start(butt11, 0, 0, 0)

        hbox13a.pack_start(Gtk.Label(" | "), 0, 0, 0)

        butt12 = smallbutt(" Export ", self.searchall, "Export all items")
        hbox13a.pack_start(butt12, 0, 0, 2)
        hbox13a.pack_start(Gtk.Label(" | "), 0, 0, 0)

        butt12a = smallbutt(" Import ", self.searchall, "Import items")
        hbox13a.pack_start(butt12a, 0, 0, 0)
        hbox13a.pack_start(Gtk.Label(" | "), 0, 0, 0)

        butt12a = smallbutt(" PopOut ", self.searchall, "Pop Out to window")
        hbox13a.pack_start(butt12a, 0, 0, 0)

        hbox13a.pack_start(Gtk.Label(" | "), 0, 0, 0)

        hbox13a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        #butt22 = Gtk.Button.new_with_mnemonic("Save")
        #butt22.connect("pressed", self.save)
        #hbox13.pack_start(butt22, 0, 0, 0)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        self.pack_start(hbox13, 0, 0, 2)
        self.pack_start(hbox13a, 0, 0, 2)
        try:
            self.load()
        except:
            print("Cannot load", sys.exc_info())

    def switched(self, pageto):
        #print("SW page signal web", pageto)
        if pageto == self:
            #print("Web in")
            self.wasin = True
        else:
            if self.wasin:
                self.wasin = False
                self.savetext()
                #print("Web out")

    def __del__(self):
        # Did not happen automatically
        #if pedconfig.conf.verbose:
        #    print("pedweb __del__")
        self.savetext()
        if self.core:
            self.core.__del__()

    def newitem(self, arg):
        self.savetext()
        rrr = HeadDialog("New Item %d" % self.cnt, None)
        ret = rrr.run()
        if ret != Gtk.ResponseType.OK:
            rrr.destroy()
            return

        ttt = rrr.entry.get_text()
        rrr.destroy()
        #print("store", self.treeview2.treestore)

        ret = self.treeview2.find_item(ttt)
        if ret:
            message("\nThis record already exists. \n\n %s" % ttt)
            return

        itemx = (ttt, "", "")
        self.cnt += 1
        self.treeview2.insert(None, 0, itemx)

        newtext = "Enter text here";
        self.core.save_data(ttt, newtext)

        #self.edview.set_text(newtext)
        self.treeview2.sel_first()

    def delitem(self, arg):
        #print ("delitem", self.lastkey, self.lastsel)
        if not self.lastsel:
            print("Nothing to delete")
            pedconfig.conf.pedwin.update_statusbar("Nothing selected for deletion.");
            return

        rrr = yes_no_cancel("   Delete Item ?   ", "'" + str(self.lastsel[0]) + "'", False)
        if rrr != Gtk.ResponseType.YES:
            return

        #print("Removing", self.lastsel[0])
        # Remove all of them including shadow entried
        delx = self.core.del_recs(self.lastsel[0].encode("cp437"), 0, twincore.INT_MAX)
        pedconfig.conf.pedwin.update_statusbar("Removed %d records." % delx)

        # Refresh list in main sel window
        self.treeview2.clear()
        usleep(10)
        self.load()

    def search(self, arg):
        print("search", time.time())
        pass

    def searchall(self, arg):
        #print("searchall", arg)
        print("searchall", time.time())
        pass

    def load(self):

        ''' Load from file;
            This is more complex than it should be ... dealing with old data
        '''

        self.lastsel = None; self.lastkey = None
        datax = []
        try:
            dbsize = self.core.getdbsize()
            if not dbsize:
                return

            for aa in range(dbsize-1, 0, -1):
                ddd = self.core.get_rec(aa)
                if len(ddd) < 2:
                    continue        # Deleted record
                #print("ddd", ddd)
                hhh = ddd[0].decode()
                if hhh not in datax:
                    datax.append(hhh)
                    #print("adding", hhh)
                    self.treeview2.append((hhh, "", ""))
        except:
            put_exception("load web data")
            print("Cannot load notes Data at", cnt, qqq)

        try:
            self.treeview2.sel_first()
        except:
            pass


    def backurl(self, arg1): #, url, parm, buff):
        self.webview.go_back()

    def forwurl(self, arg1): #, url, parm, buff):
        self.webview.go_forward()

    def  letterfilter(self, letter):
        #print("letterfilter", letter)
        if letter == "All":
            self.treeview2.clear()
            print("Erase selection")
        else:
            aaa = self.sql.getall(letter + "%")
            print("all->", aaa)

            self.treeview2.clear()
            for aa in aaa:
                try:
                    #aa.append("ddd")
                    #aa.append("eee")
                    #aa.append("fff")
                    self.treeview2.append(aa[1:])
                except:
                    print(sys.exc_info())

    def go(self, arg):
        txt = self.edit.get_text()
        #print ("go", txt)
        self.webview.load_uri(txt)

    def anchor(self, arg):
        self.webview.load_uri("file://" + self.fname)

    def _completion_function(self, html, user_data):

        #print("completion:", html)

        if not html:
            return

        #print( "Save ttt:", ttt, "html:", html)

        try:
            self.core.save_data(user_data, html)
        except:
            print(sys.exc_info())
        pedconfig.conf.pedwin.update_statusbar("Saved item for '%s'" % user_data[:12])

    # --------------------------------------------------------------------

    def savetext(self):

        try:
            ttt = self.lastsel[0]
        except:
            return
            pass

        #print("Savetext", ttt)

        if not hasattr(self.webview, "get_html"):
            print("Cannot exec savetext without webview")

        try:
            self.webview.get_html(self._completion_function, ttt)
        except:
            if pedconfig.conf.verbose:
                put_exception("savetext", sys.exc_info())
            pass

    # --------------------------------------------------------------------

    def treesel(self, args):

        #print("treesel", args[0])

        self.savetext()
        self.lastsel = args

        ddd = self.core.retrieve(args[0])[0]
        hhh = ddd[1].decode()
        #print("hhh", hhh)

        try:
            self.webview.load_html(hhh)
        except:
            print(sys.exc_info())
            pass

        #if args:
        #    pedconfig.conf.pedwin.update_statusbar("Saved item for '%s'" % args[0][:12])

# EOF
