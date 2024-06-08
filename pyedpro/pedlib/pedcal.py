#!/usr/bin/env python3

from __future__ import absolute_import, print_function
import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

from pedlib import pedconfig

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedutil import *

#sys.path.append('..' + os.sep + "pyvguicom")

from pyvguicom import pgutils
fff = os.path.dirname(pgutils.__file__)
#print("fff", fff)
sys.path.append(fff)

from pyvguicom.pggui import *
from pyvguicom.pgsimp import *
from pyvguicom import pggui
from pyvguicom import pgsel

# ------------------------------------------------------------------------

class pgcal(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self)

        hbox = Gtk.HBox()
        self.lastsel = ""

        self.data_dir = os.path.expanduser("~/.pyedcal")
        try:
            if not os.path.isdir(self.data_dir):
                os.mkdir(self.data_dir)
        except:
            print("Cannot make calendar data dir")

        try:
            self.sql = calsql(self.data_dir + os.sep + "caldata.sql")
        except:
            print("Cannot make calendar database")

        sp = pggui.ySpacer()
        self.pack_start(xSpacer(), 0, 0, 0)
        self.lsel = pgsel.LetterNumberSel(self.letterfilter, font="Mono 12")
        self.pack_start(self.lsel, 0, 0, 2)

        self.cal = Gtk.Calendar()
        hbox.pack_start(self.cal, 1, 1, 0)

        self.cal.connect("day-selected", self.daysel)
        self.cal.connect("day-selected-double-click", self.dayseldouble)

        self.pack_start(Gtk.Label(label=" "), 0, 0, 0)
        self.pack_start(hbox, 0, 0, 0)
        #self.pack_start(Gtk.Label(label=" "), 0, 0, 0)

        self.hbox2 = Gtk.HBox()
        butt = Gtk.Button.new_with_mnemonic("Goto Today")
        butt.connect("pressed", self.today, self.cal)

        self.hbox2.pack_start(Gtk.Label(label=" "), 0, 0, 0)
        self.hbox2.pack_start(butt, 1, 1, 0)
        self.hbox2.pack_start(Gtk.Label(label=" "), 0, 0, 0)

        butt2 = Gtk.Button.new_with_mnemonic("Edit Selection")
        butt2.connect("pressed", self.demand, self.cal)
        self.hbox2.pack_start(butt2, 1, 1, 0)
        self.hbox2.pack_start(Gtk.Label(" "), 0, 0, 0)

        self.pack_start(self.hbox2, 0, 0, 2)
        #self.pack_start(Gtk.Label(""), 0, 0, 0)

        self.hbox3 = Gtk.HBox()
        self.edit = Gtk.Entry()
        self.hbox3.pack_start(Gtk.Label(label=" Find: "), 0, 0, 0)
        self.hbox3.pack_start(self.edit, 1, 1, 0)
        butt2 = Gtk.Button("Find")
        butt2.connect("pressed", self.find)
        self.hbox3.pack_start(Gtk.Label(label=" "), 0, 0, 0)
        self.hbox3.pack_start(butt2, 0, 0, 0)
        self.hbox3.pack_start(Gtk.Label(label=" "), 0, 0, 0)
        self.pack_start(self.hbox3, 0, 0, 2)

        self.treeview2 = SimpleTree(("Hour", "Subject", "Alarm", "Notes"))
        self.treeview2.setcallb(self.treesel)
        self.treeview2.setCHcallb(self.treechange)

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        scroll2.set_min_content_height(1)
        frame3 = Gtk.Frame();
        frame3.add(scroll2)
        self.hbox4 = Gtk.HBox()
        self.hbox4.add(frame3)
        self.pack_start(self.hbox4, 1, 1, 2)

        self.edview = SimpleEdit()
        self.edview.setsavecb(self.savetext)

        scroll3 = Gtk.ScrolledWindow()
        scroll3.add(self.edview)
        frame4 = Gtk.Frame(); frame4.add(scroll3)
        self.pack_start(Gtk.Label(" "), 0, 0, 0)
        self.daysel(self.cal)


        self.pangolayout = self.create_pango_layout("a")
        #self.pangolayout.set_font_description(self.fd)

        # Get Pango steps
        #self.cxx, self.cyy = self.pangolayout.get_pixel_size()
        (pr, lr) = self.pangolayout.get_extents()
        #print("pix", pr.height / Pango.SCALE)
        self.chh = lr.height / Pango.SCALE

        GLib.timeout_add(10, self.initial_load, self, 0)

    # This was needed as the calendar took to much space

    def resize(self, widgx, newconf):
        #print("resize", widgx, newconf)
        #print("rrr", newconf.height,  newconf.height / self.chh)

        while 1:
            if newconf.height < self.chh * 50:
                self.hbox3.hide()
            else:
                self.hbox3.show()

            if newconf.height <  self.chh *  45:
                self.hbox2.hide()
            else:
                self.hbox2.show()

            if newconf.height <  self.chh *  40:
                self.lsel.hide()
            else:
                self.lsel.show()
            break

    def  initial_load(self, arg, arg2):

        #for aa in range(100):
        #    if self.get_toplevel():
        #        break
        #    print("waiting ...", aa)
        #    usleep(10)
        #
        #print("initial_load" , arg, arg2, self.get_realized())

        try:
            ttt = self.get_toplevel()
            ttt.connect("configure-event", self.resize)

        except:
            print("width", sys.exc_info())

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

    def find(self, arg):
        print ("find", self.edit.get_text() )
        aaa = self.sql.getall("%" + self.edit.get_text() + "%")
        print("all ... ", aaa)
        self.treeview2.clear()
        for aa in aaa:
            self.treeview2.append(aa[1:])

    def savetext(self, txt):
        ddd = self.cal.get_date()
        key = "%d-%d-%d %s" % (ddd[0], ddd[1], ddd[2], self.lastsel)
        #print("savetext", key, "--",  txt)
        self.sql.putdata(key, txt, "", "")
        pedconfig.conf.pedwin.update_statusbar("Saved calendar item for '%s'" % key);

    def treechange(self, args):
        ddd = self.cal.get_date()
        self.lastsel = args[0]
        #print("treechange", ddd, args)
        key = "%d-%d-%d %s" % (ddd[0], ddd[1], ddd[2], args[0])
        val =  "[%s]~[%s]" % (args[1], args[2])
        self.sql.put(key, args[1], args[2], args[3])

    def treesel(self, args):
        #print("treesel", args)
        self.edview.clear()
        ddd = self.cal.get_date()
        key = "%d-%d-%d %s" % (ddd[0], ddd[1], ddd[2], args[0])
        strx = self.sql.getdata(key)
        if strx:
            self.edview.append(strx[0])
        self.lastsel = args[0]

    def today(self, butt, cal):
        ddd = datetime.datetime.today()
        #print("date",  ddd.year, ddd.month, ddd.day)
        cal.select_month(ddd.month-1, ddd.year)
        cal.select_day(ddd.day)

    def demand(self, butt, cal):
        ddd = datetime.datetime.today()
        #print("demand",  ddd.year, ddd.month, ddd.day)

    def daysel(self, cal):
        #print("Day", cal.get_date())
        #self.edit.set_text(str(cal.get_date()))
        self.treeview2.clear()
        for aa in range(8, 20):
            #self.treeview2.append((ampmstr(aa), pedutil.randstr(8), pedutil.randstr(14)) )
            ddd = self.cal.get_date()
            key = "%d-%d-%d %s" % (ddd[0], ddd[1], ddd[2], ampmstr(aa) )
            try:
                val =  self.sql.get(key)
                if val:
                    #print("val", val)
                    self.treeview2.append((ampmstr(aa), val[0], val[1], val[2]) )
                else:
                    self.treeview2.append((ampmstr(aa), "", "", "") )
            except:
                print(sys.exc_info())
                pass

    def dayseldouble(self, cal):
        #print("Day dbl", cal.get_date())
        pass

# -------------------------------------------------------------------

class calsql():

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
            self.c.execute("create table if not exists calendar \
             (pri INTEGER PRIMARY KEY, key text, val text, val2 text, val3 text)")
            self.c.execute("create index if not exists kcalendar on calendar (key)")
            self.c.execute("create index if not exists pcalendar on calendar (pri)")
            self.c.execute("create table if not exists caldata \
             (pri INTEGER PRIMARY KEY, key text, val text, val2 text, val3 text)")
            self.c.execute("create index if not exists kcaldata on caldata (key)")
            self.c.execute("create index if not exists pcaldata on caldata (pri)")

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
                self.c.execute("select * from calendar where key = ?", (kkk,))
            else:
                self.c.execute("select * from calendar indexed by kcalendar where key = ?", (kkk,))
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

    def   getdata(self, kkk):
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from caldata where key = ?", (kkk,))
            else:
                self.c.execute("select * from caldata indexed by kcaldata where key = ?", (kkk,))
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
                self.c.execute("select * from calendar where key == ?", (key,))
            else:
                self.c.execute("select * from calendar indexed by kcalendar where key == ?", (key,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into calendar (key, val, val2, val3) \
                    values (?, ?, ?, ?)", (key, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update calendar \
                                set val = ? val2 = ?, val3 = ? where key = ?", \
                                      (val, val2, val3, key))
                else:
                    self.c.execute("update calendar indexed by kcalendar \
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
                self.c.execute("select * from caldata where key == ?", (key,))
            else:
                self.c.execute("select * from caldata indexed by kcaldata where key == ?", (key,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into caldata (key, val, val2, val3) \
                    values (?, ?, ?, ?)", (key, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update caldata \
                                set val = ? val2 = ?, val3 = ? where key = ?", \
                                      (val, val2, val3, key))
                else:
                    self.c.execute("update caldata indexed by kcaldata \
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

    def   getall(self, strx = "", limit = 1000):

        #print("getall '" +  strx + "'")

        try:
            #c = self.conn.cursor()
            self.c.execute("select * from calendar where val like ? or val2 like ? or val3 like ? limit  ?",
                                            (strx, strx, strx, limit))
            rr = self.c.fetchall()
        except:
            rr = []
            print("Cannot get all sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
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
            self.c.execute("delete from calendar")
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
            self.c.execute("delete from caldata")
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

