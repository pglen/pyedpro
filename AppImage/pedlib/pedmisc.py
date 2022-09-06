#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import sys, signal, os, time, string, pickle, re, platform, subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from pedlib import pedconfig
from pedlib import pedlcmd

def exec_test(self2, testx):

        if self2.lastcmd == "" or self2.shift:

            #print("Asking lastcmd")
            ret = pedlcmd.cmddlg(self2)
            if not ret:
                self2.mained.update_statusbar("Cancelled exec dialog.")
                return

        if self2.lastcmd == "":
            self2.mained.update_statusbar("No command specified.")
            return

        comarr = self2.lastcmd.split(" ")

        if pedconfig.conf.pgdebug > 9:
            print("comarr",  comarr)

        #print("comarr",  comarr)

        proc = None
        try:
            #proc = subprocess.Popen(comarr, shell = True)
            proc = subprocess.Popen(comarr)
            #proc = subprocess.run(comarr)
        except:
             print("Exception in subprocess", sys.exc_info())

        if not proc:
            #self2.mained.update_statusbar("Cannot execute command: " + "'" + self2.lastcmd + "'")
            print("Cannot execute", self2.lastcmd)

        #print("retcode", proc.returncode)
        '''
        try:
            while  True:
                if not proc:
                    break
                if proc.returncode
                    break
                outs, errs = proc.communicate()
                print("com", outs, errs)
                usleep(10)

        except subprocess.TimeoutExpired:
             print("Exception timeout in comm", sys.exc_info())
        except:
             print("Exception in comm", sys.exc_info())
        '''

        if not proc:
            self2.mained.update_statusbar("Cannot execute command: " + "'" + self2.lastcmd + "'")


# EOF



























