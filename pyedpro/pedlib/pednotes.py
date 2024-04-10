#!/usr/bin/env python

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, uuid, copy

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango

#print(sys.path)

realinc = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pycommon")
if realinc not in sys.path:
    sys.path.append(realinc)

#print("import", __file__)

from pedlib import pedconfig

# Into our name space
from pedlib.pedmenu import *
from pedlib.pedui import *
from pedlib.pedutil import *
from pedlib.pedync import *
from pedlib.pedofd import *

#print(sys.path)

from pycommon import pgsimp
from pycommon import pggui
from pycommon import pgbutt
from pycommon import pgtextview

try:
    #from pydbase import dbutils
    #from pydbase import twinbase
    from pydbase import twincore

    #print("pednotes", sys.path)
    #print(os.getcwd())
except:
    try:
        print("local")
        # This will change once the pydbase is out of dev stage
        np = os.path.split(__file__)[0] + os.sep + '..' + os.sep + ".." + os.sep + ".."
        #print(np)
        #np =  '..' + os.sep + "pydbase"
        sys.path.append(np)
        np += os.sep + "pydbase"
        sys.path.append(np)

        np =  os.path.split(__file__)[0] + os.sep + '..' + os.sep + "pydbase"
        sys.path.append(np)

        #print(sys.path[-3:])

        from pydbase import dbutils
        from pydbase import twinbase
        from pydbase import twincore
    except:
        np = os.path.split(__file__)[0]
        sys.path.append(np)
        sys.path.append(np + os.sep + "..")
        print("files2", os.listdir(np))
        print("special2", sys.path)

        import dbutils
        import twinbase
        import twincore

# ------------------------------------------------------------------------

class pgnotes(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.wasin = False
        self.old_iter = None

        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#444444"))
        #self.prevsel = None;  self.prevkey = None;

        self.lastsel = None;  self.lastkey = None
        self.cnt = 0
        self.popwin = None
        self.notes_dir = pedconfig.conf.notes_dir

        try:
            if not os.path.isdir(self.notes_dir):
                os.mkdir(self.notes_dir)
        except:
            print("Cannot make notes notes dir")

        if pedconfig.conf.verbose:
            print("Using notesdir:", self.notes_dir)

        try:
            self.core = twincore.TwinCore(self.notes_dir + os.sep + "peddata.pydb")
            #print("core", self.core, self.core.fname)
            #self.core.pgdebug = 10

        except:
            print("Cannot make notes py database")

        #message("Cannot make notes database")

        #hbox = Gtk.HBox()
        #self.pack_start(Gtk.Label("s"), 0, 0, 0)
        #self.pack_start(pggui.xSpacer(), 0, 0, 0)
        #self.lsel = pgsimp.LetterNumberSel(self.letterfilter, font="Mono 12")
        self.lsel = pgsimp.LetterNumberSel(self.letterfilter)
        self.lsel.set_tooltip_text("Filter entries by letter / number")
        self.pack_start(self.lsel, 0, 0, 0)

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

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        #scroll2.set_policy (Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.vpaned = Gtk.VPaned()

        frame3 = Gtk.Frame();
        frame3.add(scroll2)
        self.vpaned.add(frame3)

        self.vpaned.set_position(200)

        #self.edview = pgsimp.TextViewWin()
        self.edview =  pgtextview.pgTextView()
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
        self.pack_start(self.vpaned, 1, 1, 0)

        hbox13 = Gtk.HBox()
        hbox13.pack_start(pgsimp.zSpacer(), 1, 1, 0)

        hbox13.pack_start(pgsimp.zSpacer(), 0, 0, 0)
        butt3 = pgbutt.smallbutt(" _New Item ", self.newitem, "Create new record")
        hbox13.pack_start(butt3, 0, 0, 0)
        hbox13.pack_start(pgsimp.zSpacer(), 0, 0, 0)

        butt3x = pgbutt.smallbutt(" Find in Text ", self.findx, "Find in text")
        hbox13.pack_start(butt3x, 0, 0, 0)
        hbox13.pack_start(pgsimp.zSpacer(), 0, 0, 0)

        butt3a = pgbutt.smallbutt(" Search All ", self.searchall, "Search ALL data")

        hbox13.pack_start(butt3a, 0, 0, 0)

        hbox13.pack_start(pgsimp.zSpacer(), 0, 0, 0)
        hbox13.pack_start(pgsimp.zSpacer(), 1, 1, 0)

        hbox13a = Gtk.HBox()
        hbox13a.pack_start(pgsimp.zSpacer(), 1, 1, 0)

        hbox13a.pack_start(pgsimp.zSpacer(), 0, 0, 0)
        butt11 = pgbutt.smallbutt(" Del Item ", self.delitem, "Delete item")
        hbox13a.pack_start(butt11, 0, 0, 0)
        hbox13a.pack_start(pgsimp.zSpacer(), 0, 0, 0)

        butt12 = pgbutt.smallbutt(" Export ", self.export, "Export items")
        hbox13a.pack_start(butt12, 0, 0, 0)

        hbox13a.pack_start(pgsimp.zSpacer(), 0, 0, 0)

        butt12a = pgbutt.smallbutt(" Import ", self.importx, "Import items")
        hbox13a.pack_start(butt12a, 0, 0, 0)
        hbox13a.pack_start(pgsimp.zSpacer(), 0, 0, 0)

        butt12b = pgbutt.smallbutt(" Popout ", self.popx, "Pop out window")
        hbox13a.pack_start(butt12b, 0, 0, 0)
        hbox13a.pack_start(pgsimp.zSpacer(), 0, 0, 0)

        hbox13a.pack_start(pgsimp.zSpacer(), 1, 1, 0)

        self.pack_start(hbox13, 0, 0, 0)
        self.pack_start(hbox13a, 0, 0, 0)
        pedconfig.conf.pedwin.mywin.connect("configure-event", self.resize)
        self.load()

    def resize(self, widg, newconf):
        #print("resize", newconf.width, newconf.height)
        self.vpaned.set_position(newconf.height / 6)

    def __del__(self):
        # Did not happen automatically
        #print("pednotes __del__")
        self.savetext()
        #del self.core

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
                print("aa", aa)

                if letter in aa[0]: #.lower():
                    #print("    ", aa)
                    self.treeview2.append((aa, "", ""))

    def searchall(self, arg):
        self.savetext()
        dlg = SearchDialog()
        ret = dlg.run()
        if ret != Gtk.ResponseType.OK:
            dlg.destroy()
            return
        txt = dlg.entry.get_text()
        dlg.destroy()
        self.treeview2.clear()
        self.edview.set_text("")
        cnt = 0
        txt2 = txt.lower()
        arrx = []
        try:
            #datax = self._getall()
            #for aa in datax:
            dbsize = self.core.getdbsize()
            for aa in range(dbsize-1, 0, -1):
                #ddd = self.core.retrieve(aa)
                #ddd = self.core.findrecpos(aa, 1)
                ddd = self.core.get_rec(aa)
                if not ddd:
                    continue
                #print(ddd)
                if type(ddd[0]) != type(""):
                    ddd[0] = ddd[0].decode()
                if type(ddd[1]) != type(""):
                    try:
                        ddd[1] = ddd[1].decode()
                    except:
                        ddd[1] = ddd[1].decode("cp437")

                sss = ddd[1].lower()
                #print("sss", sss)
                if txt2 in sss:
                    print("found:", txt2, "in", ddd[0])
                    if ddd[0] not in arrx:
                        arrx.append(ddd[0])
                        self.treeview2.append((ddd[0], "", ""))
                    cnt += 1
            if not cnt:
                self.treeview2.append(("No records found", "", ""))

            pass
        except:
            #print("exc in search ", sys.exc_info())
            put_exception("search all")


    def findx(self, arg):
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
        if self.old_iter:
            start_iter  =  self.old_iter
        else:
            start_iter  =  textbuffer.get_start_iter()
        found  = start_iter.forward_search(txt, Gtk.TextSearchFlags.CASE_INSENSITIVE, None)
        if found:
           match_start, match_end = found
           self.old_iter = match_end
           textbuffer.select_range(match_start, match_end)
           self.edview.textview.scroll_to_iter(match_start, 0, False, 0, 0)
        else:
            self.old_iter = None
            message("\n'%s' not found or EOF reached. \n" % (txt))

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

    def delitem(self, arg):
        #print ("delitem", self.lastkey, self.lastsel)
        if not self.lastsel:
            print("Nothing to delete")
            pedconfig.conf.pedwin.update_statusbar("Nothing selected for deletion.");
            return

        rrr = yes_no_cancel("   Delete Item ?   ", "'" + str(self.lastsel[0]) + "'", False)
        if rrr != Gtk.ResponseType.YES:
            return

        print("Removing", self.lastsel[0])
        dbsize = self.core.getdbsize()
        # Remove all of them including shadow entried
        delx = self.core.del_rec_bykey(self.lastsel[0], dbsize)
        pedconfig.conf.pedwin.update_statusbar("Removed %d records." % delx)

        # Refresh list in main sel window
        self.treeview2.clear()
        usleep(10)
        self.load()

    def import_one(self, head, body):

        #body = body.strip()

        #print("Head:", head)
        #print("Body:", body[:64] + " ...")
        #print()

        # Convert old format records
        #print("Head:", head)
        if head[:3] == 'b"(':
            #print(" REC ", head)
            sss = head.split(",")
            #print(" sss", headx)
            if len(sss) > 1:
                headx = sss[2]
                #print("Headx2:", headx)
            else:
                print("Bad record", head)
                #raise
        else:
            headx = head
            if headx[:2] == "b'":
                headx = headx[1:]
            #print("Headx2:", headx)

        if type(headx) != str:
            headx = headx.decode()

        headx = headx.strip("' \r\n\t\"")

        #print("Headx:", headx)
        #print("Body:", body[:64] + "...")
        #print()

        if headx not in self.recx:
            self.recx.append(headx)
            self.recy.append(body)

    def importx(self, arg):
        #print("Import")

        cwd = os.getcwd();
        os.chdir(pedconfig.conf.notes_dir)
        fname = ofd("", self)
        os.chdir(cwd)
        if not fname:
            return

        #print("opening", fname)
        try:
            fp = open(fname[0], "rt")
        except:
            print("Cannot read data", sys.exc_info());
            pedconfig.conf.pedwin.update_statusbar("Cannot import notes")
            return

        sep =  "---------------------------------------------------------"
        state = 0
        head = body = ""

        self.recx = [];   self.recy = []

        while True:
            line = fp.readline()
            if not line:
                break

            if sep in line:
                #print("sep", line)
                if state == 0:
                    #if len(line) < 3:
                    #    continue
                    state = 1
                elif state == 1:
                    state = 2;
                elif state == 2:
                    self.import_one(head, body)
                    head = body = ""
                    state = 1;
                else:
                    print("Invalid FSM state")

            elif state == 1:
                #print(state, "line", "'" + line + "'")
                #print(line, end = "")
                #if line[0] != "(":
                head += line
                #    print("UNEXPECTED REC")

            elif state == 2:
                body += line
                #print(state, "line", "'" + line + "'")
                pass

        # Last record:
        if head:
            self.import_one(head, body)
        fp.close()

        self.import_data()

    def import_data(self):
        cnt = 0
        #rrr = self.core.find_key(head)
        #rrr = self.core.retrieve(head)
        #if not rrr:
        #    print("this record patched", head)
        #    #print(rrr)
        dlen = len(self.recx)
        for aa in range(dlen):
            head = self.recx[aa]

            #print("head:", "'" + head + "'")
            #print("data:", len(self.recy), self.recy[aa][:64])

            #self.core.core_verbose = 2
            rrr = self.core.findrec(head, 1)
            #print("rrr", rrr[0].decode())
            #self.core.core_verbose = 0
            if not rrr or rrr[0].decode() != head:
                print("Would import", "'" + head + "'")
                self.core.save_data(head, self.recy[aa])
                cnt += 1

            #if rrr != head:
            #    print("Would import", "'" + head + "'", rrr)
            #    cnt += 1

        self.treeview2.clear()
        self.load()

        print("imported", cnt, "items of", dlen)
        pedconfig.conf.pedwin.update_statusbar(\
                    "Imported %d items of %d " % (cnt, dlen))

    def export(self, arg):

        base = "peddata";  cnt = 0; fff = ""
        while True:
            fff =  "%s%s%s_%d.bak" % (self.notes_dir, os.sep, base, cnt)
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
        pedconfig.conf.pedwin.update_statusbar("Exported %d/%d notes to %s" % \
                                (dbsize, cnt, os.path.basename(fff)))

    def popx(self, arg):

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
        self.savetext()
        pass

    def savetext(self):

        # testing
        if not self.edview.get_modified():
            return

        #txt = self.edview.get_text()
        txt = self.edview.ser_buff()

        print("notes savetext", self.lastkey, self.lastsel, txt[0:12])

        #self.core.core_verbose = 2
        self.core.save_data(self.lastsel[0], txt)
        #self.core.core_verbose = 0

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

        #print("readargs", args)
        ddd = None
        #ddd = self.core.retrieve(args[0])
        for aa in range(self.core.getdbsize()-1, -1, -1):
            rec = self.core.get_rec(aa)
            if not rec:
                continue
            #print("rec", rec[0])
            if rec[0].decode() == args[0]:
                #print("found")
                ddd = rec
                break

        #print("readrec", ddd)

        #for aa in ddd:
        #    print(aa)
        #print("ddd", type(ddd), ddd)
        #print(b"'" + ddd[0][1][:3]) + b"'"

        # See what kind it is
        try:
            if ddd[1][:13] == b"GTKTEXTBUFFER":
                self.edview.set_text("")
                #print("deser", ddd[0][1])
                self.edview.deser_buff(ddd[1])
            else:
                #print("load", ddd[0][1])
                self.edview.set_text(ddd[1].decode())
        except:
            print("treesel", sys.exc_info())
            pass

        self.edview.set_modified(0)

    def _getall(self):
        datax = []
        try:
            dbsize = self.core.getdbsize()
            for aa in range(dbsize-1, -1, -1):
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

        '''
            Load from file;
            This is more complex than it should be ... dealing with old data
        '''

        self.lastsel = None; self.lastkey = None
        try:
            datax = self._getall()
            for qqq in datax:
                self.treeview2.append((qqq, "", ""))
        except:
            put_exception("load")
            #print("Cannot load notes Data at", cnt, qqq)

        #self.treeview2.sel_last()
        #self.treeview2.sel_first()

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
        self.view = pgtextview.pgTextView(True)
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
