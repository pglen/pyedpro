#!/usr/bin/env python

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, uuid, copy

#from six.moves import range

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango

from pedlib import pedconfig

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedutil import *
from    pedlib.pedync import *

from pycommon.pggui import *
from pycommon.pgsimp import *
from pycommon.pgtextview import *

#print("pednotes", __file__)

#sys.path.append('..' + os.sep + "pycommon")
#sys.path.append('..' + os.sep + ".." + os.sep + "pycommon")

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

class pgnotes(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.wasin = False

        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#444444"))
        #self.prevsel = None;  self.prevkey = None;

        self.lastsel = None;  self.lastkey = None
        self.cnt = 0
        self.popwin = None
        self.data_dir = os.path.expanduser("~/.pyednotes")
        try:
            if not os.path.isdir(self.data_dir):
                os.mkdir(self.data_dir)
        except:
            print("Cannot make notes data dir")

        #try:
        #    if pedconfig.conf.verbose:
        #        print(self.data_dir + os.sep + "peddata.sql")
        #    self.sql = notesql(self.data_dir + os.sep + "peddata.sql")
        #except:
        #    print("Cannot make notes database")

        try:
            self.core = twincore.TwinCore(self.data_dir + os.sep + "peddata.pydb")
            #print("core", self.core, self.core.fname)
        except:
            print("Cannot make notes py database")

        #message("Cannot make notes database")

        #hbox = Gtk.HBox()
        #self.pack_start(Gtk.Label("s"), 0, 0, 0)
        #self.pack_start(pggui.xSpacer(), 0, 0, 0)
        #self.lsel = pgsimp.LetterNumberSel(self.letterfilter, font="Mono 12")
        self.lsel = pgsimp.LetterNumberSel(self.letterfilter)
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

        self.vpaned = Gtk.VPaned()

        frame3 = Gtk.Frame();
        frame3.add(scroll2)
        self.vpaned.add(frame3)

        self.vpaned.set_position(200)

        #self.edview = pgsimp.TextViewWin()
        self.edview =  pgTextView()
        #self.edview.callb = self.savetext
        self.edview.findcall = self.findx, self

        self.edview.textview.set_margin_left(2)
        self.edview.textview.set_margin_right(2)
        self.edview.textview.set_margin_top(2)
        self.edview.textview.set_margin_bottom(2)

        self.fd = Pango.FontDescription()
        pg = Gtk.Widget.create_pango_context(self.edview.textview)
        myfd = pg.get_font_description()
        mysize = myfd.get_size() / Pango.SCALE
        self.fd.set_size((mysize + 2) * Pango.SCALE)
        self.edview.textview.modify_font(self.fd)

        self.deftags = self.edview.textbuffer.get_tag_table()

        #self.pack_start(Gtk.Label(label="Font formatting is work in progress."), 0, 0, 0)
        frame4 = Gtk.Frame();
        frame4.set_border_width(3)
        frame4.add(self.edview)

        self.vpaned.add(frame4)
        self.pack_start(self.vpaned, 1, 1, 2)

        hbox13 = Gtk.HBox()
        hbox13.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        #butt3 = Gtk.Button.new_with_mnemonic("New Item")
        #butt3.connect("pressed", self.newitem)
        butt3 = smallbutt("| New Item ", self.newitem, "Create new record")
        hbox13.pack_start(butt3, 0, 0, 0)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        #butt3 = Gtk.Button.new_with_mnemonic("Find in Text")
        #butt3.connect("pressed", self.search)

        butt3x = smallbutt("| Find in Text ", self.findx, "Find in text")
        hbox13.pack_start(butt3x, 0, 0, 0)

        #butt3a = Gtk.Button.new_with_mnemonic("Search All")
        #butt3a.connect("pressed", self.searchall)

        butt3a = smallbutt("| Search All |", self.searchall, "Search ALL data")

        hbox13.pack_start(butt3a, 0, 0, 0)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        hbox13.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        hbox13a = Gtk.HBox()
        hbox13a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        #butt11 = Gtk.Button.new_with_mnemonic("Del Item")
        #butt11.connect("pressed", self.delitem)

        butt11 = smallbutt(" | Del Item ", self.delitem, "Delete item")
        hbox13a.pack_start(butt11, 0, 0, 0)

        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        #butt12 = Gtk.Button.new_with_mnemonic("Export")
        #butt12.connect("pressed", self.export)

        butt12 = smallbutt("| Export ", self.export, "Export items")
        hbox13a.pack_start(butt12, 0, 0, 0)

        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        #butt12a = Gtk.Button.new_with_mnemonic("Import")
        #butt12a.connect("pressed", self.importx)

        butt12a = smallbutt("| Import ", self.importx, "Import items")
        hbox13a.pack_start(butt12a, 0, 0, 0)

        butt12b = smallbutt("| Popout |", self.popx, "Pop out window")
        hbox13a.pack_start(butt12b, 0, 0, 0)

        #butt14 = Gtk.Button.new_with_mnemonic("ExpData")
        #butt14.connect("pressed", self.exportd)
        #hbox13.pack_start(butt14, 0, 0, 2)
        #hbox13.pack_start(Gtk.Label(" "), 0, 0, 0)

        hbox13a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        #butt22 = Gtk.Button.new_with_mnemonic("Save")
        #butt22.connect("pressed", self.save)
        #hbox13.pack_start(butt22, 0, 0, 0)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        self.pack_start(hbox13, 0, 0, 2)
        self.pack_start(hbox13a, 0, 0, 2)
        pedconfig.conf.pedwin.mywin.connect("configure-event", self.resize)
        self.load()

    def resize(self, widg, newconf):
        #print("resize", newconf.width, newconf.height)
        self.vpaned.set_position(newconf.height / 6)

    def __del__(self):
        # Did not happen automatically
        #print("pednotes __del__")
        self.savetext()
        self.core.__del__()

    def switched(self, pageto):
        #print("SW page signal web", pageto)
        if pageto == self:
            #print("Notes in")
            self.wasin = True
        else:
            if self.wasin:
                self.wasin = False
                #print("Notes out")
                self.savetext()

    def  letterfilter(self, letter):
        self.savetext()
        #print("letterfilter", letter)

        if letter == "All":
            self.load()
        else:
            ddd = self._getall()
            self.treeview2.clear()
            for aa in ddd:
                if letter in aa[0].lower():
                    #print("    ", aa)
                    self.treeview2.append((aa, "", ""))

    def searchall(self, arg, arg2):
        self.savetext()
        dlg = SearchDialog()
        ret = dlg.run()
        if ret != Gtk.ResponseType.OK:
            dlg.destroy()
            return
        txt = dlg.entry.get_text()
        dlg.destroy()
        self.treeview2.clear()
        try:
            datax = self._getall()
            for aa in datax:
                #print(aa)
                if txt in aa:
                    #print("    ", aa)
                    self.treeview2.append((aa, "", ""))

            pass
        except:
            print("exc in search ", sys.exc_info())

    def findx(self, arg, arg2):
        self.savetext()
        dlg = SearchDialog() #self.edview.textview)
        ret = dlg.run()
        if ret != Gtk.ResponseType.OK:
            dlg.destroy()
            return
        txt = dlg.entry.get_text()
        dlg.destroy()
        #print("Searching for:", txt)

        textbuffer  =  self.edview.textview.get_buffer()
        start_iter  =  textbuffer.get_start_iter()
        found       =  start_iter.forward_search(txt, Gtk.TextSearchFlags.CASE_INSENSITIVE, None)
        if found:
           match_start,match_end = found #add this line to get match_start and match_end#try:
           textbuffer.select_range(match_start,match_end)#    datax = self.sql.getall()
           self.edview.textview.scroll_to_iter(match_start, 0, False, 0, 0)

    def newitem(self, arg, arg2):
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
            try:
                #rootwin = self.get_root_window()
                #xxx, yyy = rootwin.get_root_coords(0, 0)
                #xxxx, yyyy = rootwin.get_root_origin()
                #print("root",  xxx, yyy, xxxx, yyyy)
                #windowx = self.get_window()
                #xxx, yyy = windowx.get_root_coords(0, 0)
                #xxxx, yyyy = windowx.get_root_origin()
                #print("this",  xxx, yyy, xxxx, yyyy)
                #Gdk.Window
                #windowx = self.get_window()
                #xx, yy = windowx.get_position()
                #print("window", windowx, xx, yy,)
                #xx, yy = self.get_pointer()
                #print(xx, yy)
                #rrr = self.get_allocation()
                #print(rrr.x, rrr.y, rrr.width, rrr.height)
                #    #pos = self.get_parent().get_parent().get_position()
                #print("pos", pos)
                pass
            except:
                print("newitem", sys.exc_info())

            message("\nThis record already exists. \n\n %s" % ttt)
            return

        itemx = (ttt, "", "")
        self.cnt += 1

        #self.treeview2.append(itemx)
        self.treeview2.insert(None, 0, itemx)
        self.treeview2.sel_first()

        newtext = ""  #Enter text here";
        self.edview.set_text(newtext)
        self.core.save_data(ttt, newtext)

    def delitem(self, arg, arg2):
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

    def importx(self, arg, arg2):
        #print("Import")
        cnt = 0
        dbsize = self.core.getdbsize()
        for aa in range(dbsize):
            ddd = self.core.get_rec(aa)
            if len(ddd) < 2:
                continue
            try:
                nnn = ddd[0].decode("cp437")
                ppp = nnn.split(",")
                ppp[2] = ppp[2][2:-1]               # Remove quotes
                print(aa, ppp[2])
                cnt += 1
            except:
                print("importx", sys.exc_info())

        #print("imported", cnt, "items")
        pedconfig.conf.pedwin.update_statusbar("Imported %d items" % cnt);

    def export(self, arg, arg2):

        base = "peddata";  cnt = 0; fff = ""
        while True:
            fff =  "%s%s%s_%d.bak" % (self.data_dir, os.sep, base, cnt)
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

        #datax = self.sql.getall()
        #for aa in datax:
        #    #print(aa)
        #    ddd = self.sql.getdata(aa[1])
        #    #print("ddd", ddd)
        #    try:
        #       fp.write("\n ------------------------------------------------------------------\n")
        #       fp.write(str(aa))
        #       fp.write("\n ------------------------------------------------------------------\n")
        #       fp.write(str(ddd[0]) + "\n")
        #    except:
        #        print("exc in export ", ddd, sys.exc_info())

        try:
            datax = []
            cnt = 0
            try:
                dbsize = self.core.getdbsize()
                for aa in range(dbsize-1, 0, -1):
                    ddd = self.core.get_rec(aa)
                    #print("Item", type(ddd[0]), ddd[0], "Data:", ddd[1][:16] + b" ..." )
                    fp.write("\n ------------------------------------------------------------------\n")
                    fp.write(str(ddd))
                    fp.write("\n ------------------------------------------------------------------\n")
            except:
                print("Cannot backup record\n", aa);

        except:
            print("Cannot backup database\n");

        fp.close()
        pedconfig.conf.pedwin.update_statusbar("Exported notes to %s" % os.path.basename(fff))

    def popx(self, arg, arg2):

        txt = self.edview.ser_buff()
        #print ("popx txt", txt)

        # Create if not there

        if self.popwin:
            self.popwin.destroy()

        self.popwin = PopWin()
        self.popwin.lastsel = self.lastsel
        self.popwin.savefunc = self.savefunc
        self.popwin.set_popwin_text(txt)
        self.popwin.show_all()

    def savefunc(self, item, text):
        #print("savefunc", item, text[:12])
        self.core.save_data(item[0], text)
        if item[0] == self.lastsel[0]:
            #print("re-read current")
            self._readrec(item)

    def save(self, arg):
        #print ("save automatic (unimplemented)")
        pass

    def savetext(self):

        # testing
        if not self.edview.get_modified():
            return

        #txt = self.edview.get_text()
        txt = self.edview.ser_buff()

        print("save", self.lastkey, self.lastsel, txt[0:12])

        #self.core.verbose = 2
        self.core.save_data(self.lastsel[0], txt)
        #self.core.verbose = 0

    # --------------------------------------------------------------------

    def treechange(self, args):
        # Old entry
        #print("treechange", args)
        #self.lastsel = args[0][:]
        ## Is there one like this?
        #ddd = self.sql.gethead(args[0])
        ##print("ddd", ddd)
        #if ddd:
        #    self.lastkey = ddd[1]
        #    self.sql.put(self.lastkey, args[0], args[1], args[2])
        ##pedconfig.conf.pedwin.update_statusbar("Saved note item for '%s'" % self.lastsel);
        pass

    # --------------------------------------------------------------------

    def treesel(self, args):

        # Old entry
        #print("treesel lastsel", self.lastsel)
        # New entry
        #print("treesel newsel", args)

        if self.edview.get_modified():
            #print("would save text")
            self.savetext()

        self.lastsel = args
        self._readrec(args)

    def _readrec(self, args):

        ddd = self.core.findrec(args[0], 1)
        #print("ddd", type(ddd), ddd)
        #print(b"'" + ddd[0][1][:3]) + b"'"

        try:
            # See what kind it is
            try:
                if ddd[0][1][:13] == b"GTKTEXTBUFFER":
                    self.edview.set_text("")
                    #print("deser", ddd[0][1])
                    self.edview.deser_buff(ddd[0][1])
            except:
                #print("treesel", sys.exc_info())
                pass

        except:
                #print("load", ddd[0][1])
                self.edview.set_text(ddd[0][1].decode("cp437"))

        self.edview.set_modified(0)


    def _getall(self):
        datax = []
        try:
            dbsize = self.core.getdbsize()
            for aa in range(dbsize-1, 0, -1):
                ddd = self.core.get_rec(aa)
                if len(ddd) < 2:
                    continue        # Deleted record
                #print("ddd", ddd)
                #print("Item:", ddd[0], "Data:", ddd[1][:16] + b" ..." )
                try:
                    ppp = ddd[0].split(b",")
                except:
                    print("Cannot split",sys.exc_info(), ddd[0])
                    ppp = ddd[0]

                if len(ppp) > 1:
                    qqq = ppp[2]            # Old data
                else:
                    qqq = ppp[0]               # New data

                #print("qqq", qqq)
                qqq = qqq.decode("cp437").strip()

                # remove quotes
                if qqq[0] == '\'':
                    qqq = qqq[1:-1]

                if qqq not in datax:
                    datax.append(qqq)
                    #print(aa, qqq)
        except:
            put_exception("_getall")

        return datax

    def load(self):

        ''' Load from file;
            This is more complex than it should be ... dealing with old data
        '''

        self.lastsel = None; self.lastkey = None
        try:
            ddd = self._getall()
            for qqq in ddd:
                self.treeview2.append((qqq, "", ""))
        except:
            put_exception("load")
            #print("Cannot load notes Data at", cnt, qqq)

        #self.treeview2.sel_last()
        #self.treeview2.sel_first()


class   PopWin(Gtk.Window):

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
        self.view = pgTextView(True)
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

    #def close(self):
    #    self.win2.destroy()

    def _area_destroy(self, area):
        #print("destroy", area)
        #print("Saving", self.lastsel)
        if self.view.get_modified():
            txt = self.view.ser_buff()
            self.savefunc(self.lastsel, txt)
        # if we do not want it to close
        #return True

    #def _area_focus(self, area, event, dialog):
    #    print("focus", event)

    def set_popwin_text(self, text):
        self.view.deser_buff(text)

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
