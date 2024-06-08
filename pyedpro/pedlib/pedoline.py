#!/usr/bin/env python

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, random

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from pedlib import pedconfig

from pedlib.pedcanv import *

#sys.path.append('..' + os.sep + "pyvguicom")
from pyvguicom.pggui import *
from pyvguicom.pgsimp import *

random.seed()

def genrandrect(maxww, maxhh):

    xx = random.randint(0, maxww // 2)
    yy = random.randint(0, maxhh // 2)

    ww = random.randint(maxww // 8, 3 * maxww // 8)
    hh = random.randint(maxhh // 8, 3 * maxhh // 8)

    rect = Rectangle( (xx, yy, ww, hh) )

    return rect

def genrandcircle(maxww, maxhh):

    xx = random.randint(10, maxww // 2)
    yy = random.randint(10, maxhh // 2)

    ww = 40
    for aa in range(18):
        ww = random.randint(30, maxww // 2)
        if ww < xx and ww < yy:
            break

    return (xx, yy, ww, ww)

# ------------------------------------------------------------------------

#class pgoline(Gtk.Window):

class pgoline(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.init = 0
        #set_testmode(1)

        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#444444"))

        hbox = Gtk.HBox()
        self.lastsel = ""

        self.connect("motion-notify-event", self.motion_event)
        self.connect("configure-event", self.config_event)
        #self.connect("event", self.all_event)

        self.data_dir = os.path.expanduser("~/.pyednotes")
        try:
            if not os.path.isdir(self.data_dir):
                os.mkdir(self.data_dir)
        except:
            print("Cannot make notes data dir")

        self.statbox = Gtk.Label(label=" Idle")
        self.statbox.set_xalign(0); self.statbox.set_yalign(0)

        #self.vbox = Gtk.VBox()
        self.pack_start(xSpacer(), 0, 0, 0)
        #self.toolbox = ToolBox(self.toolcb, pedconfig.conf.pedwin)
        self.toolbox = ToolBox(self.toolcb, self.get_toplevel())
        #self.pack_start(self.toolbox, 0, 0, 2)
        self.canvas = Canvas(self, self.statbox)

        for aa in range(10):
            rstr = randstr(6)
            rrr = random.randint(0, 5)
            if rrr == 0:
                rect = genrandrect(500, 1000)
                self.canvas.add_rect(rect, "Rect_" + rstr, randcolstr() )
            elif rrr == 1:
                rect = genrandrect(500, 1000)
                self.canvas.add_romb(rect, "Romb_" + rstr, randcolstr() )
            elif rrr == 2:
                rect = genrandrect(300, 300)
                self.canvas.add_text(rect, "Text_" + rstr, randcolstr() )
            elif rrr == 3:
                rect = genrandrect(500, 1000)
                self.canvas.add_line(rect, "Line_" + rstr, randcolstr() )
            elif rrr == 4:
                rect = genrandrect(500, 1000)
                self.canvas.add_curve(rect, "Curve_" + rstr, randcolstr() )
            else:
                circ = genrandcircle(500, 500)
                self.canvas.add_circle(circ, "Circ_" + rstr, randcolstr() )

        #self.canvas.show_objects()
        #self.canvas.setsavecb(self.savetext)

        hbox2 = xHBox()
        hbox2.pack(self.statbox, True)

        mbut = MenuButt(("Open", "Save", "Export"), self.main_callb)
        hbox2.pack(mbut)

        scroll3a = Gtk.ScrolledWindow()
        scroll3a.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        scroll3a.add(self.canvas)
        frame5 = Gtk.Frame(); frame5.add(scroll3a)
        self.pack_start(frame5, 1, 1, 2)
        self.pack_start(hbox2, 0, 0, 2)
        #self.add(self.vbox)
        #self.pack_start(xSpacer(), 0, 0, 0)

    def config_event(self, win, event):
        print("config_event", win, event)

    def toolcb(self, butt, num):
        print("toolsb", num)

    def focus_out(self):
        self.toolbox.hide()

    def focus_in(self):
        self.toolbox.show_box(pedconfig.conf.pedwin.mywin)

    def switched(self, pageto):
        #print("SW page signal", pageto)
        if pageto == self:
            #print("me")
            self.toolbox.show_box(pedconfig.conf.pedwin.mywin)
        else:
            self.toolbox.hide()

    def motion_event(self, win, event):
        #print("motion_event", win, event)
        if not self.init:
            pass
            #self.init = True
            #self.toolbox.show_box(pedconfig.conf.pedwin.mywin)

    def all_event(self, win, event):
        if event.type != Gdk.EventType.MOTION_NOTIFY:
            print("all_event", win, event)

    def  letterfilter(self, letter):
        #print("letterfilter", letter)
        if letter == "All":
            print("Erase selection")
        else:
            aaa = self.sql.getall(letter + "%")
            print("all", aaa)

            self.treeview2.clear()
            for aa in aaa:
                self.treeview2.append(aa[2:])

    def  main_callb(self, text, arg):
        #print("main_callb", text, arg)

        if arg == 0:
            fff = getfilename(parent=self) # "Open File", "Load Annotation", [])
            if fff:
                print("fff", fff)

        pass

    def newitem(self, arg, num):
        print ("new", arg, num)
        self.treeview2.append(("New Item", "", ""))
        self.treeview2.sel_last()
        pass

    def find(self, arg):
        print ("find", arg)
        aaa = self.sql.getall("%" + self.edit.get_text() + "%")
        print("all", aaa)
        self.treeview2.clear()
        for aa in aaa:
            self.treeview2.append(aa[2:])

    def savetext(self, txt):
        #ddd = self.cal.get_date()
        #key = "%d-%d-%d %s" % (ddd[0], ddd[1], ddd[2], self.lastsel)
        #print("savetext", key, "--",  txt)
        #self.sql.putdata(key, txt, "", "")
        pedconfig.conf.pedwin.update_statusbar("Saved note item for '%s'" % key);

    def treechange(self, args):
        #ddd = self.cal.get_date()
        ddd = datetime.datetime.today()
        key = "%d-%d-%d %d:%d %s"  % (ddd.year, ddd.month, ddd.day, ddd.hour, ddd.minute, args[0])
        self.lastsel = args[0]
        print("treechange", key, args)
        self.sql.put(key, args[0], args[1], args[2])
        pedconfig.conf.pedwin.update_statusbar("Saved note item for '%s'" % self.lastsel);

    def treesel(self, args):
        print("treesel", args)
        self.edview.clear()
        #ddd = self.cal.get_date()
        #key = "%d-%d-%d %s" % (ddd[0], ddd[1], ddd[2], args[0])
        #strx = self.sql.getdata(key)
        #if strx:
        #    self.edview.append(strx[0])
        self.lastsel = args[0]

    def today(self, butt, cal):
        ddd = datetime.datetime.today()
        #print("date",  ddd.year, ddd.month, ddd.day)
        #cal.select_month(ddd.month-1, ddd.year)
        #cal.select_day(ddd.day)

    def demand(self, butt, cal):
        ddd = datetime.datetime.today()
        #print("demand",  ddd.year, ddd.month, ddd.day)

    def daysel(self, cal):
        return
        #print("Day", cal.get_date())
        #self.edit.set_text(str(cal.get_date()))
        self.treeview2.clear()
        for aa in range(8, 20):
            #self.treeview2.append((ampmstr(aa), randstr(8), randstr(14)) )
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
                pass

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
                self.c.execute("select * from notes where key == ?", (key,))
            else:
                self.c.execute("select * from notes indexed by knotes where key == ?", (key,))
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

    def   getall(self, strx = "", limit = 100):

        #print("getall '" +  strx + "'")

        try:
            #c = self.conn.cursor()
            self.c.execute("select * from notes where val like ? limit  ?", (strx, limit))
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
