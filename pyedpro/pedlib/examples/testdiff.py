#!/usr/bin/env python

# !!!!! TEST FILE !!!!

# This is used when testing the editor. (like undo redo tests)       diff here


# ------------------------------------------------------------------------
# This is open source text editor. Written on python. The motivation for
# this project was to create a modern mufti-platform editor.
# Simple, powerful, configurable, extendable.
#
# This project is a successor of pyedit.py
#
# Pyedpro functions well on Linux / Windows / Mac / Raspberry PI

#
# Pyedpro has:
#
#    o  macro recording/play,
#    o  search/replace,
#    o  functional navigation,
#    o  comment/string spell check,
#    o  auto backup,
#    o  persistent undo/redo,  (undo beyond last save)
#    o  auto complete, auto correct,
#    o
#    o  ... and a lot more.
#
# It is fast, it is extendable. The editor has a table driven key mapping.
# One can easily edit the key map in keyhand.py, and the key actions
# in acthand.py The default key map resembles gedit / wed / etp / brief

# History:  (recent first, incomplete list)
#
# jul/19/2018   Coloring for spell check, Trigger by scroll, more dominant color
# Jul/xx/2018   Update README, KEYS.TXT
# Jun/xx/2018   Log Files for time accounting.
# Jun/08/2020   Menu control / Headerbar / Version update

# ASCII test editor, requires pyGtk. (pygobject)
# See pygtk-dependencied for easy access to dependencies.

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal

import traceback, gettext, locale

#locale.setlocale(locale.LC_ALL, '')

import gettext
gettext.bindtextdomain('pyedpro', './locale/')
gettext.textdomain('pyedpro')

_ = gettext.gettext

#print("domain", gettext.textdomain)

VERSION = 1.4
BUILDDATE = "Mon 08.Jun.2020"
PROGNAME = "PyEdPro"

12345678

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# So it is universally found
#sys.path.append(os.path.abspath(__file__))

import pedlib.pedconfig as pedconfig
import pedlib.pedlog as pedlog
import pedlib.pedync   as  pedync

def main(strarr):

    mainwin = pyedlib.pedwin.EdMainWindow(None, None, strarr)
    pyedlib.pedconfig.conf.pedwin = mainwin

    # Create log window
    pyedlib.pedlog.create_logwin()

    Gtk.main()

def help(): #// diff

    print()
    print(PROGNAME, _("Version: "), pyedlib.pedconfig.conf.version)
    print(_("Usage: ") + PROGNAME + _(" [options] [[filename] ... [filename]]"))
    print(_("Option(s):"))
    print(_("            -d level  - Debug level 1-10 (0 silent; 1 some; 10 lots)"))
    print(_("            -v        - Verbose (to stdout and log)"))
    print(_("            -f        - Start Full screen"))
    print(_("            -c        - Dump Config"))
    print(_("            -o        - Use real stdout (for debug strings)"))
    print(_("            -V        - Show version"))
    print(_("            -x        - Clear (eXtinguish) config (will prompt)"))
    print(_("            -h        - Help"))
    print()

# ------------------------------------------------------------------------

def terminate(arg1, arg2):

    if(pyedlib.pedconfig.conf.verbose):
        print(_("Terminating pydepro.py, saving files to ~/pydepro"))

    # Save all
    pyedlib.pedconfig.conf.pedwin.activate_quit(None)
    #return signal.SIG_IGN

# ------------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    # Redirect stdout to a fork to real stdout and log. This way messages can
    # be seen even if pydepro is started without a terminal (from the GUI)

    opts = []; args = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h?fvxctVo")
    except getopt.GetoptError as err:
        print(_("Invalid option(s) on command line:"), err)
        sys.exit(1)

    #print "opts", opts, "args", args

    pyedlib.pedconfig.conf.version = VERSION
    pyedlib.pedconfig.conf.build_date = BUILDDATE
    pyedlib.pedconfig.conf.progname = PROGNAME

    for aa in opts:
        if aa[0] == "-d":
            try:
                pyedlib.pedconfig.conf.pgdebug = int(aa[1])
                print( PROGNAME, _("Running at debug level"),  pyedlib.pedconfig.conf.pgdebug)
            except:
                pyedlib.pedconfig.conf.pgdebug = 0

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-?": help();  exit(1)
        if aa[0] == "-V": print("Version", pyedlib.pedconfig.conf.version); \
            exit(1)
        if aa[0] == "-f": pyedlib.pedconfig.conf.full_screen = True
        if aa[0] == "-v": pyedlib.pedconfig.conf.verbose = True
        if aa[0] == "-x": clear_config = True
        if aa[0] == "-c": show_config = True
        if aa[0] == "-t": show_timing = True
        if aa[0] == "-o": use_stdout = True

    for aa in opts:
        if aa[0] == "-d":
            try:
                pyedlib.pedconfig.conf.pgdebug = int(aa[1])
                print( PROGNAME, _("Running at debug level"),  pyedlib.pedconfig.conf.pgdebug)
            except:
                pyedlib.pedconfig.conf.pgdebug = 0

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-?": help();  exit(1)
        if aa[0] == "-V": print("Version", pyedlib.pedconfig.conf.version); \
            exit(1)
        if aa[0] == "-f": pyedlib.pedconfig.conf.full_screen = True
        if aa[0] == "-v": pyedlib.pedconfig.conf.verbose = True
        if aa[0] == "-x": clear_config = True
        if aa[0] == "-c": show_config = True
        if aa[0] == "-t": show_timing = True
        if aa[0] == "-o": use_stdout = True

    try:
        if not os.path.isdir(pyedlib.pedconfig.conf.config_dir):
            if(pyedlib.pedconfig.conf.verbose):
                print("making", pyedlib.pedconfig.con.config_dir)
            os.mkdir(pyedlib.pedconfig.conf.config_dir)
    except: pass

    # Let the user know if it needs fixin'
    if not os.path.isdir(pyedlib.pedconfig.conf.config_dir):
        print(_("Cannot access config dir:"), pyedlib.pedconfig.conf.config_dir)
        sys.exit(1)

    pyedlib.pedconfig.ensure_dirs(pyedlib.pedconfig.conf)

    if(pyedlib.pedconfig.conf.verbose):
        print(_("Data stored in "), pyedlib.pedconfig.conf.config_dir)

    # Initialize sqlite to load / save preferences & other info
    sql = pyedlib.pedsql.pedsql(pyedlib.pedconfig.conf.sql_data)

    # Initialize pedconfig for use
    pyedlib.pedconfig.conf.sql = sql
    pyedlib.pedconfig.conf.keyh = pyedlib.keyhand.KeyHand()
    pyedlib.pedconfig.conf.mydir = os.path.abspath(__file__)

    # To clear all config vars
    if clear_config:
        print(_("Are you sure you want to clear config ? (y/n)"))
        sys.stdout.flush()
        aa = sys.stdin.readline()
        if aa[0] == "y":
            print(_("Removing configuration ... "), end=' ')
            sql.rmall()
            print("OK")
        sys.exit(0)

    # To check all config vars
    if show_config:
        print("Dumping configuration:")
        ss = sql.getall();
        for aa in ss:
            print(aa)
        sys.exit(0)

    # Uncomment this for silent stdout
    if use_stdout or pyedlib.pedconfig.conf.pgdebug or \
                    pyedlib.pedconfig.conf.verbose:
        # Do not hide console
        #print("Using real stdout")
        pyedlib.pedwin.hidden = True    # Already hidden no hide
    else:
        pyedlib.pedwin.hidden = False   # Take action, hide

    sys.stdout = pyedlib.pedlog.fake_stdout(sys.stdout)
    sys.stderr = pyedlib.pedlog.fake_stdout(sys.stdout)

    # Uncomment this for buffered output
    if pyedlib.pedconfig.conf.verbose:
        print("Started", PROGNAME)

    main(args[0:])

# EOF













