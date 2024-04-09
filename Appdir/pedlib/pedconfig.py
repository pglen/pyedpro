#!/usr/bin/env python

# Global configuration for pyedpro. Also a place we share globals to the rest
# of the project like the main window, statusbar, keyhandler etc ...
# so the functionality is acessable from the key handler
# or the key handler is acessable from the main window ... etc
# The majority of dynamic vars are inited in pyedpro.py

from __future__ import absolute_import
import signal, os, time, sys

from pedlib.keywords import *
from pedlib import keywords

config_reg = "/apps/pyedpro"

inited = False
conf = None

class Conf():

    def __init__(self):

        global inited

        if inited:
            raise

        #print("init pedconf", inited)
        inited = True

        self.IDLE_TIMEOUT = 15           # Time for a backup save
        self.SYNCIDLE_TIMEOUT = 1        # Time for syncing windows and spelling
        self.UNTITLED = "untitled.txt"   # New (empty) file name

        self.full_screen = False
        self.keyh = None
        self.pedwin = None
        self.pgdebug = 0
        self.show_keys = 0
        self.keylog_on = 0

        # Count down variables
        self.idle = 0; self.syncidle = 0;   self.statuscount = 0

        # Where things live
        self.orig_path = sys.path[0]
        self.orig_dir = os.getcwd()

        # Where things are stored (backups, orgs, macros, logs, temp, tts)
        # Add _dir suffix for pyedpro to create it
        self.config_dir = os.path.expanduser("~/.pyedpro")
        self.macro_dir = os.path.expanduser("~/.pyedpro/macros")
        self.data_dir = os.path.expanduser("~/.pyedpro/data")
        self.log_dir = os.path.expanduser("~/.pyedpro/log")
        self.sess_dir = os.path.expanduser("~/.pyedpro/sess")
        self.temp_dir = os.path.expanduser("~/.pyedpro/tmp")
        self.tts_dir = os.path.expanduser("~/.pyedpro/tts")
        self.plugins_dir  = os.path.expanduser("~/.pyedpro/plugins")
        self.keylog_file  = os.path.expanduser("~/.pyedpro/log/keylog.txt")

        # Set parent as module include path
        current = os.path.dirname(os.path.realpath(__file__))
        self.plugins_dir2 = os.path.expanduser(current + "/plugins")
        #print("plugins_dir2", self.plugins_dir2)

        # The files
        self.sql_data = os.path.expanduser("~/.pyedpro/sql_data")
        self.history  = os.path.expanduser("~/.pyedpro/history")
        self.sessions = os.path.expanduser("~/.pyedpro/sessions")
        self.notes_dir = os.path.expanduser("~/.pyednotes")
        self.web_dir = os.path.expanduser("~/.pyedwebnotes")

        self.config_file = "defaults"

        # Where things are stored (UI x/y pane pos.)
        self.config_reg = "/apps/pyedpro"
        self.verbose = False
        self.recarr = []

        # Which extensions are colored
        self.color_on = color_files

# ------------------------------------------------------------------------

def softmake(ddd):

    if conf.pgdebug > 9:
        print("softmake: ", ddd)

    if not os.path.isdir(ddd):
        if(conf.verbose):
            print("softmake making", ddd)
        os.mkdir(ddd)

# Create config dirs

def ensure_dirs(conf):

    if conf.pgdebug > 5:
        print("ensure_dirs: ")

    # Automate it
    for aa in conf.__dict__:
        zz = conf.__dict__[aa]
        if type(zz) == str:
            if "_dir" in aa:
                if ".pyedpro" in zz:
                    #if conf.pgdebug > 5:
                    #    print("making dir entry", zz)
                    softmake(zz)

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream

   def write(self, data):
       self.stream.write(data)
       self.stream.flush()

   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()

   def __getattr__(self, attr):
       return getattr(self.stream, attr)

# EOF







