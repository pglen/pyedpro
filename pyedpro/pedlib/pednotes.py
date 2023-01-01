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

        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#444444"))
        #self.prevsel = None;  self.prevkey = None;

        self.lastsel = None;  self.lastkey = None
        self.cnt = 0
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
        self.treeview2.setCHcallb(self.treechange)

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        #scroll2.set_policy (Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vpaned = Gtk.VPaned()

        frame3 = Gtk.Frame();
        frame3.add(scroll2)
        vpaned.add(frame3)

        vpaned.set_position(300)

        #self.edview = pgsimp.TextViewWin()
        self.edview =  pgTextView()
        #self.edview.callb = self.savetext
        self.edview.findcall = self.search, self

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

        self.pack_start(Gtk.Label(label="Font formatting is work in progress."), 0, 0, 0)
        frame4 = Gtk.Frame();
        frame4.set_border_width(3)
        frame4.add(self.edview)

        vpaned.add(frame4)
        self.pack_start(vpaned, 1, 1, 2)

        hbox13 = Gtk.HBox()
        hbox13.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        butt3 = Gtk.Button.new_with_mnemonic("New Item")
        butt3.connect("pressed", self.newitem)
        hbox13.pack_start(butt3, 0, 0, 2)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        butt3 = Gtk.Button.new_with_mnemonic("Find in Text")
        butt3.connect("pressed", self.search)
        hbox13.pack_start(butt3, 0, 0, 2)

        butt3a = Gtk.Button.new_with_mnemonic("Search All")
        butt3a.connect("pressed", self.searchall)
        hbox13.pack_start(butt3a, 0, 0, 2)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        hbox13.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        hbox13a = Gtk.HBox()
        hbox13a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        butt11 = Gtk.Button.new_with_mnemonic("Del Item")
        butt11.connect("pressed", self.delitem)
        hbox13a.pack_start(butt11, 0, 0, 2)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        butt12 = Gtk.Button.new_with_mnemonic("Export")
        butt12.connect("pressed", self.export)
        hbox13a.pack_start(butt12, 0, 0, 2)
        #hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        butt12a = Gtk.Button.new_with_mnemonic("Import")
        butt12a.connect("pressed", self.importx)
        hbox13a.pack_start(butt12a, 0, 0, 2)

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
        self.load()

    def __del__(self):
        # Did not happen automatically
        #print("pednotes __del__")
        self.core.__del__()

    def  letterfilter(self, letter):
        self.savetext()
        ##print("letterfilter", letter)
        #if letter == "All":
        #    self.load()
        #else:
        #    aaa = self.sql.findhead(letter + "%")
        #    self.treeview2.clear()
        #    for aa in aaa:
        #        self.treeview2.append(aa[2:5])

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
        try:
            #datax = self.sql.getall()
            #for aa in datax:
            #    #print(aa)
            #    ddd = self.sql.getdata(aa[1])
            #    #print("ddd", ddd)
            #    if txt in ddd[0]:
            #        #print("    ", ddd)
            #        self.treeview2.append(aa[2:5])
            #        continue
            pass
        except:
            print("exc in search ", sys.exc_info())

    def search(self, arg):
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

    def newitem(self, arg):
        self.savetext()
        rrr = HeadDialog("New Item %d" % self.cnt, None)
        ret = rrr.run()
        if ret != Gtk.ResponseType.OK:
            rrr.destroy()
            return
        ttt = rrr.entry.get_text()
        rrr.destroy()
        itemx = (ttt, "", "")
        self.cnt += 1

        self.treeview2.append(itemx)
        self.treeview2.sel_last()
        newtext = "Enter text here";
        self.edview.set_text(newtext)
        #usleep(10)
        key = str(uuid.uuid4())
        #self.sql.put(key, itemx[0], itemx[1], itemx[2])
        self.core.save_data(ttt, newtext)

        #self.lastsel = None
        #self._assurelast()

    def delitem(self, arg):
        #print ("delitem", self.lastkey, self.lastsel)
        if not self.lastkey:
            print("Nothing to delete")
            pedconfig.conf.pedwin.update_statusbar("Nothing selected for deletion.");
            return

        rrr = yes_no_cancel("   Delete Item ?   ", str(self.lastsel), False)
        if rrr == Gtk.ResponseType.YES:
            #self.sql.rmone(self.lastkey)
            #self.sql.rmonedata(self.lastkey)
            #self.treeview2.clear()
            #self.load()
            #self.treeview2.sel_last()
            pass

    def importx(self, arg):
        #print("Import")
        cnt = 0
        dbsize = self.core.getdbsize()
        for aa in range(dbsize):
            ddd = self.core.get_rec(aa)
            nnn = ddd[0].decode("cp437")
            ppp = nnn.split(",")
            ppp[2] = ppp[2][2:-1]               # Remove quotes
            print(aa, ppp[2])
            cnt += 1

        #print("imported", cnt, "items")
        pedconfig.conf.pedwin.update_statusbar("Imported %d items" % cnt);

    def export(self, arg):

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

    def save(self, arg):
        print ("save unimplemented")

    def find(self, arg):
        #print ("find", self.edit.get_text())
        if not self.edit.get_text():
            self.load()
            return
        #aaa = self.sql.findhead("%" + self.edit.get_text() + "%")
        ##print("all", aaa)
        #self.treeview2.clear()
        #for aa in aaa:
        #    #print("aa", aa)
        #    self.treeview2.append(aa[2:5])

    def _assurelast(self):
        if not self.lastsel:
            sel = self.treeview2.get_selection()
            if not sel:
                treeview2.sel_last()
            sel = self.treeview2.get_selection()
            xmodel, xiter = sel.get_selected()
            if xiter:
                args = []
                for aa in range(1):
                    xstr = xmodel.get_value(xiter, aa)
                    if xstr:
                        args.append(xstr)
                self.treesel(args)

    def ddd(self, arg, arg2):
        #print(arg)
        self.printtag(arg, arg2)

    def printtag(self, arg, arg2):
        for aa in arg.props:
            for bb in arg2.props:
                try:
                    # same tag?
                    if aa.name == bb.name:
                        #print(aa, bb)
                        if arg.get_property(aa.name) != arg2.get_property(bb.name):
                            print("    ", aa.name, "old:", arg.get_property(aa.name),
                                    "  new:", arg2.get_property(bb.name))
                except:
                    pass
                    #print("cannot get:", aa.name)

    def difftags(self, arg):
        self.deftags.foreach(self.ddd, arg)

    def savetext(self):

        # testing
        if not self.edview.get_modified():
            return

        #txt = self.edview.get_text()
        txt = self.edview.ser_buff()

        #self._assurelast()
        print("save", self.lastkey, self.lastsel, txt[0:12])

        #self.core.verbose = 2
        self.core.save_data(self.lastsel[0], txt)
        #self.core.verbose = 0

    # --------------------------------------------------------------------

    def treechange(self, args):
        # Old entry
        print("treechange", args)
        #self.lastsel = args[0][:]
        ## Is there one like this?
        #ddd = self.sql.gethead(args[0])
        ##print("ddd", ddd)
        #
        #if ddd:
        #    self.lastkey = ddd[1]
        #    self.sql.put(self.lastkey, args[0], args[1], args[2])
        ##pedconfig.conf.pedwin.update_statusbar("Saved note item for '%s'" % self.lastsel);

    # --------------------------------------------------------------------

    def treesel(self, args):
        # Old entry

        #print("treesel lastsel", self.lastsel)
        #print("treesel newsel", args)
        #print("lastkey", self.lastkey)

        if self.edview.get_modified():
            print("would save text")
            miself.savetext()

        self.lastsel = args

        #ddd = self.sql.gethead(args[0])
        #if ddd:
        #    self.lastsel = args[0]
        #    self.lastkey = ddd[1]
        #
        #    strx = self.sql.getdata(self.lastkey)
        #    self.edview.set_text(strx[0])

        ddd = self.core.findrec(args[0], 1)
        print("ddd", type(ddd), ddd)
        #print(b"'" + ddd[0][1][:3]) + b"'"

        try:
            # See what kind it is
            if ddd[0][1][:3] == b"GTK":
                self.edview.set_text("")
                print("deser", ddd[0][1])
                self.edview.deser_buff(ddd[0][1])
            else:
                print("load", ddd[0][1])
                self.edview.set_text(ddd[0][1].decode("cp437"))

            self.edview.set_modified(0)

        except:
            print(sys.exc_info())
            pass

    def load(self):

        ''' Load from file;
            This is more complex than it should be ... dealing with old data
        '''

        self.lastsel = None; self.lastkey = None
        datax = []
        try:
            dbsize = self.core.getdbsize()
            for aa in range(dbsize-1, 0, -1):
                ddd = self.core.get_rec(aa)
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
                    self.treeview2.append((qqq, "", ""))
        except:
            put_exception("load")
            print(sys.exc_info())
            print("Cannot load notes Data at", cnt, qqq)

        #self.treeview2.sel_last()
        #self.treeview2.sel_first()

# EOF
