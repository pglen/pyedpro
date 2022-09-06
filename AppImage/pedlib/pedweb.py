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

try:
    from  pycommon import pgwkit
except:
    pass
    #print("Cannot load pgwkit")

def load_html(window):
    sleep(5)
    window.load_html('<h1>This is dynamically loaded HTML</h1>')

# ------------------------------------------------------------------------

class pgweb(Gtk.VBox):

    def __init__(self):

        #vbox = Gtk.VBox()
        Gtk.VBox.__init__(self)

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
        hbox4.pack_start(Gtk.Label(" "), 1, 1, 0)

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

        self.treeview2 = SimpleTree(("Hour", "Subject", "Alarm", "Notes"))
        self.treeview2.setcallb(self.treesel)
        self.treeview2.setCHcallb(self.treechange)

        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.treeview2)
        frame3 = Gtk.Frame(); frame3.add(scroll2)
        #self.pack_start(frame3, 1, 1, 2)

        self.edview = SimpleEdit()
        self.edview.setsavecb(self.savetext)

        scroll3 = Gtk.ScrolledWindow()
        scroll3.add(self.edview)
        frame4 = Gtk.Frame(); frame4.add(scroll3)

        scrolled_window = Gtk.ScrolledWindow()
        try:
            #self.webview = WebKit2.WebView()
            self.webview = pgwkit.pgwebw(self)
            #self.webview.load_uri("file://" + self.fname)
        except:
            self.webview = Gtk.Label("No WebView Available.")


        #webview.load_uri("https://google.com")
        scrolled_window.add(self.webview)
        self.pack_start(scrolled_window, 1, 1, 2)

        self.status = Gtk.Label(" Status ")
        self.pack_start(self.status, 0, 0, 2)

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

