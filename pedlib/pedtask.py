#!/usr/bin/env python

from __future__ import absolute_import, print_function

import os
import time
import string
import pickle
import re
import platform
import subprocess

import gi;  gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

import pedlib.pedconfig as pedconfig
import pedlib.peddraw as  peddraw
import pedlib.pedxtnd as  pedxtnd
import pedlib.pedync   as  pedync
import pedlib.pedspell as  pedspell
import pedlib.pedcolor as  pedcolor
import pedlib.pedmenu  as  pedmenu
import pedlib.pedundo  as  pedundo
import pedlib.pedmisc  as  pedmisc

from pedlib.pedutil import *
from pedlib.keywords import *

import webview

class pedtask():
    def __init__(self):
        print("Pedtask started", pedtask)

    # Pass in two lists, one for linux and one for windows
    def start_external(self, linprog, winprog):

        #print("start_external", linprog)

        try:
            if platform.system().find("Win") >= 0:
                ret = subprocess.Popen(winprog)
                #if not ret.returncode:
                #    raise OSError
            else:
                ret = subprocess.Popen(linprog)
                #if not ret.returncode:
                #    raise OSError
        except:
            print("Cannot launch %s" % str(linprog), sys.exc_info())
            pedync.message("\n   Cannot launch %s \n\n"  % str(linprog) +
                                     str(sys.exc_info()))

    def start_edit(self):

        old = os.getcwd()
        fdir = os.path.dirname(os.path.realpath(__file__))
        #print("fdir:", fdir)
        mydir = os.path.dirname(os.path.join(fdir, "../"))
        #print("mydir:", mydir)
        os.chdir(mydir)
        myscript = os.path.realpath(os.path.join(mydir, 'pyedpro.py'))
        #print("myscript:", myscript)

        ret = 0
        try:
            if platform.system().find("Win") >= 0:
                print("No exe function on windows. (TODO)")
            else:
                # Stumble until editor found
                ret = subprocess.Popen(["python3", myscript])
                if ret.returncode:
                    ret = subprocess.Popen(["python", myscript])
                    if not ret.returncode:
                        raise OSError
        except:
            print("Cannot launch editor instance", sys.exc_info())
            pedync.message("\n   Cannot launch new editor instance \n\n")

        # Back to original dir
        os.chdir(os.path.dirname(old))

    # --------------------------------------------------------------------
    def start_mdfilter(self):

        #print("MD Filter called.", os.getcwd())

        comline = ["md2html", "-s", "default.yml", self.fname,]
        try:
            ret = subprocess.Popen(comline, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except:
            print("Cannot start MD filter %s" % str(comline), sys.exc_info())
            pedync.message("\n   Cannot filter %s \n\n"  % str(comline) +
                       str(sys.exc_info()) )
            return
        try:
            outs, errs = ret.communicate()
        except:
            print("Cannot communicate with MD filter %s" % str(comline), sys.exc_info())
            return

        newfname = os.path.splitext(self.fname)[0] + ".html"
        #print("processed:", self.fname, newfname)

        if not os.path.isfile(newfname):
            print("No conversion on %s" % self.fname)
            pedync.message("\n   Cannot convert '%s' \n"
                "   to MD / HTML file\n\n"  % self.fname )
            return

        self.start_htmlwin(newfname)

    def start_browser(self, newfname):
        comline2 = ["firefox", newfname,]
        try:
            ret = subprocess.Popen(comline2)
        except:
            print("Cannot start browser %s" % str(comline2), sys.exc_info())
            pedync.message("\n   Cannot start %s \n\n"  % str(comline2) +
                       str(sys.exc_info()) )
            return

    def start_htmlwin(self, newfname):
        try:
            #self.webwin = webview.create_window(newfname, newfname)
            #webview.start(newfname)

            xfname = os.path.dirname(__file__) + os.sep + "webwin.py"
            #print("xfname", )
            comline3 = ["python", xfname, newfname,]
            try:
                ret = subprocess.Popen(comline3)
            except:
                print("Cannot start browser %s" % str(comline3), sys.exc_info())
                pedync.message("\n   Cannot start %s \n\n"  % str(comline3) +
                           str(sys.exc_info()) )
                return
        except:
            print("Cannot start HTML Win %s" % str(newfname), sys.exc_info())
            pedync.message("\n   Cannot start %s \n\n"  % str(newfname) +
                       str(sys.exc_info()) )
            return

    def start_htmlstr(self):
        try:
            xfname = os.path.dirname(__file__) + os.sep + "webwin.py"

            sumstr = ""
            for bb in self.text:
                sumstr += bb + "\n"

            comline3 = ["python", xfname, sumstr, ]
            try:
                ret = subprocess.Popen(comline3)
            except:
                print("Cannot start browser %s" % str(comline3), sys.exc_info())
                pedync.message("\n   Cannot start %s \n\n"  % str(comline3) +
                           str(sys.exc_info()) )
                return
        except:
            print("Cannot start HTML Win %s" % str(newfname), sys.exc_info())
            pedync.message("\n   Cannot start %s \n\n"  % str(newfname) +
                       str(sys.exc_info()) )
            return

    def start_m4filter(self):

        #print("Filter called.")
        comline = ["m4", self.fname,]
        try:
            ret = subprocess.Popen(comline, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except:
            print("Cannot filter %s" % str(comline), sys.exc_info())
            pedync.message("\n   Cannot filter %s \n\n"  % str(comline) +
                       str(sys.exc_info()) )
            return
        try:
            outs, errs = ret.communicate()
        except:
            print("Cannot communicate with filter %s" % str(comline), sys.exc_info())
            return

        res = outs.decode("cp437")
        #print("res", res)

        www = self.mained.get_width()
        if self.mained.hpaned3.get_position() > www - 20:
            self.mained.hpaned3.set_position(www - www / 4)
            self.mained.update_statusbar("Filter output active")

        newfname = os.path.splitext(self.fname)[0] + ".html"

        pppp = self.notebook3.get_nth_page(0)
        self.notebook3.set_tab_label(pppp,
                    self.mained.make_label("Filter on M4 '" +
                             os.path.basename(newfname) + "'"))
        arrx = res.split("\n")
        self.mained.diffpane.area.loadbuff(arrx)
        self.mained.diffpane.area.fname = newfname
        self.mained.update_statusbar("M4 filter output activated.")
        self.start_htmlwin(res)

# EOF
