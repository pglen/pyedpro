#!/usr/bin/env python3

from __future__ import absolute_import, print_function
import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings

#import gi;
#from gi.repository import Gtk
#from gi.repository import Gdk
#from gi.repository import GObject
#from gi.repository import GLib

#gi.require_version('WebKit2', '4.0')

from pedlib import pedconfig

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedutil import *

from pyvguicom.pggui import *
from pyvguicom.pgsimp import *
from pyvguicom.pgbutt import *
from pyvguicom.pgsel import *
from pyvguicom.browsewin import *

try:
    # This will change once the pydbase is out of dev stage
    np = os.path.split(__file__)[0] + os.sep + '..' + os.sep + ".." + os.sep + ".."
    #print(np)
    #np =  '..' + os.sep + "pydbase"
    sys.path.append(np)
    np += os.sep + "pydbase"
    sys.path.append(np)

    #print(sys.path)
    #print(os.getcwd())
    from pydbase import twincore
except:
    np =  os.path.split(__file__)[0] + os.sep + '..' + os.sep + "pydbase"
    sys.path.append(np)
    print(sys.path[-3:])

    from pydbase import twincore
    #put_exception("Cannot Load twincore")

# ------------------------------------------------------------------------

class pgweb(Gtk.VBox):

    def __init__(self):

        self. wasin = True

        #vbox = Gtk.VBox()
        Gtk.VBox.__init__(self)

        self.popwin = None
        self.lastsel = None;  self.lastkey = None
        self.cnt = 0
        self.web_dir = pedconfig.conf.web_dir
        if pedconfig.conf.verbose:
            print("Using webdir:", self.web_dir)
        try:
            if not os.path.isdir(self.web_dir):
                os.mkdir(self.web_dir)
        except:
            print("Cannot make web data dir")
        try:
            self.core = twincore.TwinCore(self.web_dir + os.sep + "pedweb.pydb")
            if pedconfig.conf.pgdebug > 2:
                print("core", self.core, self.core.fname)
        except:
            put_exception("Cannot open / make web notes py database")

        #message("Cannot make  database")

        self.popwin = None

        #hbox = Gtk.HBox()
        #self.pack_start(Gtk.Label("ccc"), 0, 0, 0)
        #self.pack_start(pggui.xSpacer(), 0, 0, 0)
        self.lsel = LetterNumberSel(self.letterfilter, font="Mono 12")
        self.lsel.set_tooltip_text("Filter entries by letter / number")
        self.pack_start(self.lsel, 0, 0, 2)

        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#dd8822"))

        #hbox3 = Gtk.HBox()
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

        #self.treeview2 = pgsimp.SimpleTree(("Header", "Subject", "Description"), skipedit=0)
        self.treeview2 = pgsimp.SimpleTree(("Header",))
        self.treeview2.setcallb(self.treesel)
        #self.treeview2.setCHcallb(self.treechange)

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        #scroll2.set_policy (Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vpaned = Gtk.VPaned()

        frame3 = Gtk.Frame();
        frame3.add(scroll2)
        vpaned.add(frame3)

        vpaned.set_position(150)

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

        #self.pack_start(hbox3, 0, 0, 2)

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
        #self.pack_start(hbox4, 0, 0, 2)

        self.treeview3 = SimpleTree(("Hour", "Subject", "Alarm", "Notes"))
        self.treeview3.setcallb(self.treesel)

        scroll2a = Gtk.ScrolledWindow()
        scroll2a.add(self.treeview3)
        frame3 = Gtk.Frame(); frame3.add(scroll2a)
        #self.pack_start(frame3, 1, 1, 2)

        #self.edview = SimpleEdit()
        #self.edview.setsavecb(self.savetext)
        #scroll3 = Gtk.ScrolledWindow()
        #scroll3.add(self.edview)
        #frame4 = Gtk.Frame(); frame4.add(scroll3)

        scrolled_window = Gtk.ScrolledWindow()
        try:
            #self.brow_win = WebKit2.WebView()
            #self.brow_win = pgwkit.pgwebw(self)
            self.brow_win = browserWin()
            #self.brow_win = Gtk.Label("No WebView Available.")
            #print("dir", dir(self.brow_win))
            #self.brow_win.load_uri("file://" + self.fname)
            pass
        except:
            #self.brow_win = Gtk.Label("No WebView Available.")
            #put_exception("WebView load")
            pass

        vbox5 = Gtk.VBox()
        frame4 = Gtk.Frame();
        frame4.add(scrolled_window)
        vbox5.pack_start(frame4, 1, 1, 0)
        vpaned.add(vbox5)

        #self.brow_win.override_background_color(
        #                Gtk.StateFlags.NORMAL, Gdk.RGBA(1, .5, .5) )

        #webview.load_uri("https://google.com")
        scrolled_window.add(self.brow_win)
        #self.pack_start(scrolled_window, 1, 1, 2)
        #self.status = Gtk.Label(" Status: ")
        #self.pack_start(self.status, 0, 0, 2)

        hbox13 = Gtk.HBox()
        hbox13.pack_start(Gtk.Label(label=""), 1, 1, 0)

        #hbox13.pack_start(Gtk.Label(" | "), 0, 0, 0)
        butt3 = smallbutt(" _New Item ", self.newitem, "Create new item / record")

        hbox13.pack_start(butt3, 0, 0, 2)

        butt3a = smallbutt(" _Find in Text ", self.search, "Search this record")
        hbox13.pack_start(butt3a, 0, 0, 0)

        butt3b = smallbutt(" Search in All ", self.searchall, "Search all records")

        hbox13.pack_start(butt3b, 0, 0, 0)
        hbox13.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        hbox13a = Gtk.HBox()
        hbox13a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        butt11 = smallbutt(" Del Item ", self.delitem, "Delete One Rec")
        hbox13a.pack_start(butt11, 0, 0, 0)

        butt12 = smallbutt(" _Export ", self.export, "Export all items")
        hbox13a.pack_start(butt12, 0, 0, 2)

        butt12a = smallbutt(" Impo_rt ", self.searchall, "Import items")
        hbox13a.pack_start(butt12a, 0, 0, 0)

        butt12a = smallbutt(" PopOu_t ", self.popx, "Pop Out to window")
        hbox13a.pack_start(butt12a, 0, 0, 0)

        hbox13a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        #butt22 = Gtk.Button.new_with_mnemonic("Save")
        #butt22.connect("pressed", self.save)
        #hbox13.pack_start(butt22, 0, 0, 0)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        vbox5.pack_start(hbox13, 0, 0, 0)
        vbox5.pack_start(hbox13a, 0, 0, 0)

        try:
            self.load()
        except:
            put_exception("Cannot load")

        #Gtk.connect
        #self.connect("window_state_event", self.eventx)

    def popx(self, arg):

        txt = self.brow_win.get_content()
        print ("popx txt", txt)

        # Create if not there
        if self.popwin:
            self.popwin.destroy()

        self.popwin = PopWebWin()
        self.popwin.lastsel = self.lastsel
        self.popwin.savefunc = self.savefunc
        self.popwin.set_popwin_text(txt)
        self.popwin.show_all()

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
        # Did not happen automatically ... force it from outside
        if pedconfig.conf.verbose:
            print("pedweb __del__")
        #self.savetext()
        #if self.core:
        #    self.core.__del__()

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

        #itemx = (ttt, "", "")
        itemx = (ttt, )
        self.cnt += 1
        self.treeview2.insert(None, 0, itemx)

        #newtext = "Enter text here";
        #self.core.save_data(ttt, newtext)

        #self.edview.set_text(newtext)
        #self.treeview2.sel_first()

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
        #delx = self.core.del_recs(self.lastsel[0].encode(""), 0, twincore.INT_MAX)

        dbsize = self.core.getdbsize()
        # Remove all of them including shadow entried
        delx = self.core.del_rec_bykey(self.lastsel[0], dbsize)

        pedconfig.conf.pedwin.update_statusbar("Removed %s %d records." % \
                            (self.lastsel[0], delx) )

        # Refresh list in main sel window
        self.treeview2.clear()
        usleep(10)
        self.load()

    def savefunc(self, item, text):
        #print("savefunc", item, text[:12])
        self.core.save_data(item[0], text)
        if item[0] == self.lastsel[0]:
            #print("re-read current")
            self._readrec(item)

    def search(self, arg):
        print("search", time.time())
        pass

    def searchall(self, arg):
        #print("searchall", arg)
        print("searchall", time.time())
        pass

    def export(self, arg):
        #print("Exporting", arg)

        base = "pedwebdata";  cnt = 0; fff = ""
        while True:
            fff =  "%s%s%s_%d.bak" % (self.web_dir, os.sep, base, cnt)
            #print("trying:", fff)
            if not os.path.isfile(fff):
                break
            cnt += 1

        try:
            fp = open(fff, "wt")
        except:
            print("Cannot backup notes data", sys.exc_info());
            pedconfig.conf.pedwin.update_statusbar("Cannot export notes")
            return

        try:
            datax = []
            cnt = 0
            dbsize = self.core.getdbsize()
            for aa in range(dbsize-1, 0, -1):
                try:
                    ddd = self.core.get_rec(aa)
                    if len(ddd) > 1:
                        kkk = ddd[0]
                        vvv = ddd[1]
                    #print("Item", type(ddd[0]), ddd[0], "Data:", ddd[1][:16] + b" ..." )
                    fp.write("\n ------------------------------------------------------------------\n")
                    fp.write(str(kkk))
                    fp.write("\n ------------------------------------------------------------------\n")
                    fp.write(str(vvv))
                    cnt += 1
                except:
                    print("Cannot backup record\n", aa, sys.exc_info());
        except:
            print("Cannot backup database\n");

        fp.close()
        pedconfig.conf.pedwin.update_statusbar("Exported %d/%d web notes to %s" % \
                                (dbsize, cnt, os.path.basename(fff)))


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

            try:
                self.treeview2.freeze_child_notify()
                for aa in range(dbsize-1, 0, -1):
                    ddd = self.core.get_rec(aa)
                    if len(ddd) < 2:
                        continue        # Deleted record
                    #print("ddd", ddd)
                    hhh = ddd[0].decode()
                    if hhh not in datax:
                        datax.append(hhh)
                        #print("adding", hhh)
                        #self.treeview2.append((hhh, "", ""))
                        self.treeview2.append((hhh,))
            finally:
                self.treeview2.thaw_child_notify()

        except:
            put_exception("load web data")
            print("Cannot load notes Data at", cnt, qqq)

        #try:
        #    self.treeview2.sel_first()
        #    print("Select first")
        #except:
        #    if pedconfig.conf.verbose:
        #        put_exception("sel firs")
        #    pass

        # Update new counter
        for aa in datax:
            if aa[:9] == "New Item ":
                try:
                    ccc = int(aa[9:])
                    #print("new", ccc)
                    if ccc > self.cnt:
                        self.cnt = ccc
                except:
                    pass
        self.cnt += 1
        #print("self.cnt", self.cnt)

    def backurl(self, arg1): #, url, parm, buff):
        self.brow_win.go_back()

    def forwurl(self, arg1): #, url, parm, buff):
        self.brow_win.go_forward()

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
                    put_exception("Letter Filter")


    def go(self, arg):
        txt = self.edit.get_text()
        #print ("go", txt)
        self.brow_win.load_uri(txt)

    def anchor(self, arg):
        self.brow_win.load_uri("file://" + self.fname)

    def _completion_function(self, html, user_data):

        #print("completion:", html)

        if not html:
            return

        #print( "Save ttt:", ttt, "html:", html)

        try:
            self.core.save_data(user_data, html)
        except:
            put_exception("Cannot load")

        pedconfig.conf.pedwin.update_statusbar("Saved item for '%s'" % user_data[:12])

    # --------------------------------------------------------------------

    def  microsleep(msec, flag = [0,]):

        if sys.version_info[0] < 3 or \
            (sys.version_info[0] == 3 and sys.version_info[1] < 3):
            timefunc = time.clock
        else:
            timefunc = time.process_time

        got_clock = timefunc() + float(msec) / 1000
        #print( got_clock)
        while True:
            if timefunc() > got_clock:
                break
            if flag[0]:
                break
            #print ("Sleeping")
            Gtk.main_iteration_do(False)

    def save(self):
        #print ("web save automatic (unimplemented)")
        self.savetext()
        pass

    def savetext(self):

        if not self.lastsel:
            return

        try:
            ttt = self.lastsel[0]
        except:
            if pedconfig.conf.verbose:
                put_exception("savetext")
            return

        if self.brow_win.is_modified():
            newtext =  self.brow_win.get_content()
            #print("web Savetext", ttt, "nt:", newtext)
            self.core.save_data(ttt, newtext)
            #print("newtext", newtext)
        else:
            #print("Not saving", ttt)
            pass

        try:
            #self.brow_win.load_html(self._completion_function, ttt)
            self.brow_win.load_html(ttt)
        except:
            if pedconfig.conf.verbose:
                put_exception("savetext")

    # --------------------------------------------------------------------

    def treesel(self, args):

        #print("treesel", args[0])

        self.savetext()
        self.lastsel = args

        hhh = ""

        try:
            #ddd = self.core.retrieve(args[0])[0]
            dbsize = self.core.getdbsize()
            for aa in range(dbsize-1, 0, -1):
                #ddd = self.core.retrieve(aa)
                #ddd = self.core.findrecpos(aa, 1)
                ddd = self.core.get_rec(aa)
                if not ddd:
                    continue
                #print(ddd)
                if ddd[0].decode() == args[0]:
                    #print("found", ddd[0])
                    #print(ddd[0], args[0])
                    hhh = ddd[1].decode()
                    break
        except:
            if pedconfig.conf.verbose:
                put_exception("treesel")
            pass

        #print("Content", hhh)

        try:
            self.brow_win.load_html(hhh)
            #usleep(10)
            #self.treeview2.grab_focus()
            #usleep(10)

        except:
            put_exception("Load Data")
            pass

        #if args:
        #    pedconfig.conf.pedwin.update_statusbar("Saved item for '%s'" % args[0][:12])

# ------------------------------------------------------------------------

class   PopWebWin(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self)

        #self.win2 = Gtk.Window()
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 600)

        tit = "pyedpro:title"
        self.set_title(tit)
        try:
            self.set_icon_from_file(get_img_path("pyedpro_sub.png"))
        except:
            print( "Cannot load log icon:", "pyedpro_sub.png", sys.exc_info())

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        self.connect("key-press-event", self._area_key, self)
        self.connect("key-release-event", self._area_key, self)
        self.connect("destroy", self._area_destroy)

        #self.connect("focus-out-event", self._focus)
        #self.view = pgTextView(True)
        self.view = brow_win()
        #self.view.textview.set_editable(False)

        self.scroll = Gtk.ScrolledWindow();
        self.scroll.add(self.view)
        frame = Gtk.Frame(); frame.add(self.scroll)
        self.add(frame)
        self.show_all()

    # Gdk.EventFocus
    def _focus(self, win, to):
        #print("focusx", win, to.window)
        pass

    def closewin(self, win):
        #print("close", win)
        pass

    def _area_destroy(self, area):
        #print("destroy", area)
        #print("Saving", self.lastsel)
        if self.view.is_modified():
            txt = self.view.get_content()
            self.savefunc(self.lastsel, txt)
        # if we do not want it to close
        #return True

    #def _area_focus(self, area, event, dialog):
    #    print("focus", event)

    def set_popwin_text(self, text):
        #self.view.deser_buff(text)
        self.view.load_html(text)

    # ------------------------------------------------------------------------

    def _area_key(self, area, event, dialog):

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Escape:
                #print "Esc"
                area.destroy()

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Return:
                #print "Ret"
                area.destroy()

            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                area.alt = True;

            if event.keyval == Gdk.KEY_x or \
                    event.keyval == Gdk.KEY_X:
                if area.alt:
                    area.destroy()

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                area.alt = False;

# EOF
