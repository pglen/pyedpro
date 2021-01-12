#!/usr/bin/env python

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, uuid

#from six.moves import range

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib

import pedlib.pedconfig as pedconfig

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedutil import *
from    pedlib.pedync import *

sys.path.append('..')
from pycommon.pggui import *
from pycommon.pgsimp import *

# ------------------------------------------------------------------------

class pgnotes(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self)

        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#444444"))

        hbox = Gtk.HBox()
        self.lastsel = ""
        self.lastkey = None
        self.cnt = 0
        self.data_dir = os.path.expanduser("~/.pyednotes")
        try:
            if not os.path.isdir(self.data_dir):
                os.mkdir(self.data_dir)
        except:
            print("Cannot make notes data dir")

        try:
            self.sql = notesql(self.data_dir + os.sep + "peddata.sql")
        except:
            print("Cannot make notes database")

        #message("Cannot make notes database")

        #self.pack_start(Gtk.Label(""), 0, 0, 0)
        self.pack_start(xSpacer(), 0, 0, 0)
        self.lsel = LetterSel(self.letterfilter)
        self.pack_start(self.lsel, 0, 0, 2)

        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#dd8822"))

        hbox3 = Gtk.HBox()
        #hbox3.pack_start(Gtk.Label(""), 0, 0, 0)
        hbox3.pack_start(xSpacer(4), 0, 0, 0)
        self.edit = Gtk.Entry()
        hbox3.pack_start(Gtk.Label(" Find: "), 0, 0, 0)
        hbox3.pack_start(self.edit, 1, 1, 0)
        butt2 = Gtk.Button.new_with_mnemonic("Find")
        butt2.connect("pressed", self.find)
        hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox3.pack_start(butt2, 0, 0, 0)
        hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)
        butt3 = Gtk.Button.new_with_mnemonic("New")
        butt3.connect("pressed", self.newitem, 1)
        hbox3.pack_start(butt3, 0, 0, 0)
        #hbox3.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#668822"))
        self.pack_start(hbox3, 0, 0, 2)

        self.treeview2 = SimpleTree(("Header", "Subject", "Description"), skipedit=-1)
        self.treeview2.setcallb(self.treesel)
        self.treeview2.setCHcallb(self.treechange)

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        frame3 = Gtk.Frame(); frame3.add(scroll2)
        self.pack_start(frame3, 1, 1, 2)

        self.edview = SimpleEdit()
        self.edview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.edview.setsavecb(self.savetext)

        scroll3 = Gtk.ScrolledWindow()
        scroll3.add(self.edview)
        frame4 = Gtk.Frame(); frame4.add(scroll3)
        #frame4.set_size_request(200, 320)
        self.pack_start(frame4, 1, 1, 2)

        #self.pack_start(Gtk.Label("here"), 0, 0, 0)
        hbox13 = Gtk.HBox()
        hbox13.pack_start(Gtk.Label("  "), 1, 1, 0)

        butt11 = Gtk.Button.new_with_mnemonic("Del Item")
        butt11.connect("pressed", self.delitem)
        hbox13.pack_start(butt11, 0, 0, 0)
        hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        butt12 = Gtk.Button.new_with_mnemonic("Export")
        butt12.connect("pressed", self.export)
        hbox13.pack_start(butt12, 0, 0, 0)
        hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        butt22 = Gtk.Button.new_with_mnemonic("Save")
        butt22.connect("pressed", self.save)
        hbox13.pack_start(butt22, 0, 0, 0)
        hbox13.pack_start(Gtk.Label("  "), 0, 0, 0)

        self.pack_start(hbox13, 0, 0, 0)

        self.pack_start(xSpacer(), 0, 0, 0)
        self.load()

    def  letterfilter(self, letter):
        #print("letterfilter", letter)
        if letter == "All":
            print("Erase selection")
        else:
            aaa = self.sql.getall(letter + "%")
            #print("all", aaa)

            self.treeview2.clear()
            for aa in aaa:
                self.treeview2.append(aa[2:])

    def newitem(self, arg, num):
        #print ("new", arg, num)
        self.cnt += 1
        item = ("New Item %d" % self.cnt, "", "")
        self.treeview2.append(item)
        key = str(uuid.uuid4())
        self.sql.put(key, item[0], item[1], item[2])
        self.treeview2.sel_last()
        pass

    def delitem(self, arg):
        #print ("delitem", self.lastkey, self.lastsel)
        if not self.lastkey:
            print("Nothing to delete")
            return

        rrr = yes_no_cancel("   Delete Item ?   ", str(self.lastsel), False)
        if rrr == Gtk.ResponseType.YES:
            self.sql.rmone(self.lastkey)
            self.sql.rmonedata(self.lastkey)
            self.load()

    def export(self, arg):
        print ("export")
        datax = self.sql.getall()
        for aa in datax:
            print(aa)
        print ("export data")
        datay = self.sql.getalldata()
        for bb in datay:
            print(bb)


    def save(self, arg):
        print ("save unimplemented")

    def find(self, arg):
        print ("find", arg)
        aaa = self.sql.gethead("%" + self.edit.get_text() + "%")
        print("all", aaa)
        self.treeview2.clear()
        for aa in aaa:
            self.treeview2.append(aa[2:])

    def savetext(self, txt):

        print("savetext", self.lastkey, self.lastsel, "--",  txt)
        self.sql.putdata(self.lastkey, txt, "", "")

        pedconfig.conf.pedwin.update_statusbar("Saved note item for '%s'" % txt);

    # --------------------------------------------------------------------

    def treechange(self, args):

        # Old entry
        #print("old", self.lastsel)
        #print("treechange", args)

        self.lastsel = args[0][:]
        # Is there one like this?
        ddd = self.sql.gethead(args[0])
        #print("ddd", ddd)
        if ddd:
            self.lastkey = ddd[1]

        self.sql.put(self.lastkey, args[0], args[1], args[2])
        pedconfig.conf.pedwin.update_statusbar("Saved note item for '%s'" % self.lastsel);

    # --------------------------------------------------------------------

    def treesel(self, args):

        # Old entry
        #print("old", self.lastsel)
        #print("treesel", args)

        self.lastsel = args[0][:]
        self.edview.clear()

        ddd = self.sql.gethead(args[0])
        #print("ddd", ddd)
        if ddd:
            self.lastkey = ddd[1]
            strx = self.sql.getdata(self.lastkey)

        if strx:
            self.edview.append(strx[0])

    def load(self, cal = ""):
        self.treeview2.clear()
        datax = self.sql.getall()
        for aa in datax:
            bb = aa[2]
            # Follow 'New Item' count, update it
            if "New Item" in bb:
                try:
                    cntx = int(bb[9:])
                    if cntx > self.cnt:
                        self.cnt = cntx
                except:
                    pass
            print(aa)
            self.treeview2.append(aa[2:5])

        #print("cnt=", self.cnt)

    def dayseldouble(self, cal):
        #print("Day dbl", cal.get_date())
        pass

# -------------------------------------------------------------------

class notesql():

    def __init__(self, file):

        #self.take = 0
        self.errstr = ""

        try:
            self.conn = sqlite3.connect(file)
        except:
            print("Cannot open/create db:", file, sys.exc_info())
            return
        try:
            self.c = self.conn.cursor()
            # Create table
            self.c.execute("create table if not exists notes \
             (pri INTEGER PRIMARY KEY, key text, val text, val2 text, val3 text)")
            self.c.execute("create index if not exists knotes on notes (key)")
            self.c.execute("create index if not exists pnotes on notes (pri)")
            self.c.execute("create table if not exists notedata \
             (pri INTEGER PRIMARY KEY, key text, val text, val2 text, val3 text)")
            self.c.execute("create index if not exists knotedata on notedata (key)")
            self.c.execute("create index if not exists pnotedata on notedata (pri)")

            self.c.execute("PRAGMA synchronous=OFF")
            # Save (commit) the changes
            self.conn.commit()
        except:
            print("Cannot insert sql data", sys.exc_info())
            self.errstr = "Cannot insert sql data" + str(sys.exc_info())

        finally:
            # We close the cursor, we are done with it
            #c.close()
            pass

    # --------------------------------------------------------------------
    # Return None if no data

    def   get(self, kkk):
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from notes where key = ?", (kkk,))
            else:
                self.c.execute("select * from notes indexed by knotes where key = ?", (kkk,))
            rr = self.c.fetchone()
        except:
            print("Cannot get sql data", sys.exc_info())
            rr = None
            self.errstr = "Cannot get sql data" + str(sys.exc_info())

        finally:
            #c.close
            pass
        return rr

    def   gethead(self, vvv):
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from notes where val = ?", (vvv,))
            else:
                self.c.execute("select * from notes indexed by knotes where val = ?", (vvv,))
            rr = self.c.fetchone()
        except:
            print("Cannot get sql data", sys.exc_info())
            rr = None
            self.errstr = "Cannot get sql data" + str(sys.exc_info())

        finally:
            #c.close
            pass

        return rr

    def   getdata(self, kkk):
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from notedata where key = ?", (kkk,))
            else:
                self.c.execute("select * from notedata indexed by knotedata where key = ?", (kkk,))
            rr = self.c.fetchone()
        except:
            print("Cannot get sql data", sys.exc_info())
            rr = None
            self.errstr = "Cannot get sql data" + str(sys.exc_info())

        finally:
            #c.close
            pass
        if rr:
            return (rr[2], rr[3], rr[4])
        else:
            return None

    # --------------------------------------------------------------------
    # Return False if cannot put data

    def   put(self, key, val, val2, val3):

        #got_clock = time.clock()

        ret = True
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from notes where key = ?", (key,))
            else:
                self.c.execute("select * from notes indexed by knotes where key = ?", (key,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into notes (key, val, val2, val3) \
                    values (?, ?, ?, ?)", (key, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update notes \
                                set val = ? val2 = ?, val3 = ? where key = ?", \
                                      (val, val2, val3, key))
                else:
                    self.c.execute("update notes indexed by knotes \
                                set val = ?, val2 = ?, val3 = ? where key = ?",\
                                     (val, val2, val3, key))
            self.conn.commit()
        except:
            print("Cannot put sql data", sys.exc_info())
            self.errstr = "Cannot put sql data" + str(sys.exc_info())
            ret = False
        finally:
            #c.close
            pass

        #self.take += time.clock() - got_clock

        return ret

    # --------------------------------------------------------------------
    # Return False if cannot put data

    def   putdata(self, key, val, val2, val3):

        #got_clock = time.clock()

        ret = True
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from notedata where key == ?", (key,))
            else:
                self.c.execute("select * from notedata indexed by knotedata where key = ?", (key,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into notedata (key, val, val2, val3) \
                    values (?, ?, ?, ?)", (key, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update notedata \
                                set val = ? val2 = ?, val3 = ? where key = ?", \
                                      (val, val2, val3, key))
                else:
                    self.c.execute("update notedata indexed by knotedata \
                                set val = ?, val2 = ?, val3 = ? where key = ?",\
                                     (val, val2, val3, key))
            self.conn.commit()
        except:
            print("Cannot put sql data", sys.exc_info())
            self.errstr = "Cannot put sql data" + str(sys.exc_info())
            ret = False
        finally:
            #c.close
            pass

        #self.take += time.clock() - got_clock

        return ret

    # --------------------------------------------------------------------
    # Get All

    def   getall(self):

        try:
            #c = self.conn.cursor()
            self.c.execute("select * from notes")
            rr = self.c.fetchall()
        except:
            rr = []
            print("Cannot get all sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass
        return rr

    def   getalldata(self):
        try:
            #c = self.conn.cursor()
            self.c.execute("select * from notedata")
            rr = self.c.fetchall()
        except:
            rr = []
            print("Cannot get all sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass
        return rr

    def   rmone(self, key):
        print("removing one '%s'" % key)
        try:
            #c = self.conn.cursor()
            self.c.execute("delete from notes where key = ?", (key,))
            self.conn.commit()
            rr = self.c.fetchone()
        except:
            rr = []
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot delete sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass

        return rr

    def   rmonedata(self, key):
        print("removing one data '%s'" % key)
        try:
            #c = self.conn.cursor()
            self.c.execute("delete from notedata where key = ?", (key,))
            self.conn.commit()
            rr = self.c.fetchone()
        except:
            rr = []
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot delete sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass

        return rr

# --------------------------------------------------------------------
    # Return None if no data

    def   rmall(self):
        print("removing all")
        try:
            #c = self.conn.cursor()
            self.c.execute("delete from notes")
            rr = self.c.fetchone()
        except:
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot delete sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass
        if rr:
            return rr[1]
        else:
            return None

    def   rmalldata(self):
        print("removing all")
        try:
            #c = self.conn.cursor()
            self.c.execute("delete from notedata")
            rr = self.c.fetchone()
        except:
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass
        if rr:
            return rr[1]
        else:
            return None

# EOF

