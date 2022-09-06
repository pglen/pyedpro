#!/usr/bin/env python3

'''! \mainpage

## Welcome to PyEdPro.

This is modern multi-platform editor. Simple, powerful,
configurable, extendable. Goodies like macro recording / playback, spell check,
column select, multiple clipboards, unlimited undo ... makes it an editor
that I use every day.

This is an open source text editor. Written in python. The motivation for
this project was to create a modern multi-platform editor. Simple,
powerful, configurable, extendable. To run this module without
installation put the supporting files in the 'pedlib'
subdirectory under the main file's direcory.

(like 'cp -a * to_target')

 This project is a successor of pyedit, after porting it to GTK3. PyEdPro
 will run anywhere PyGObject can run.

  Working and tested platforms currently are:

        Win 7 .. Win 10 ...
        Centos 6 .. 7 Ubuntu 14 ... 16 ...  20.x (should run on any linux )
        Windows (Native) plus MSYS2, Mingw,
        Raspberry PI 3, Raspberry PI 4, ...
        Mac ** Some functions are disabled - in particular async processing

  I mainly run it on Ubuntu, and in Win32 / MSYS2, some Fedora, Windows 10,
and the Raspberry-Pi. It behaves consistently on all these platforms,
it is an absolute joy to edit in a different platform without the learning
curve of new keystrokes.  If you want an editor  that works the same way in
all your workspaces, PyEdPro is the one.

Pyedpro functions near identical on Linux / Windows / Mac / Raspberry PI

 Pyedpro has:

            o  macro recording/play,
            o  search/replace,
            o  functional navigation,
            o  comment/string spell check,
            o  full spell check, spell suggestion dialog
            o  auto backup,
            o  persistent undo/redo,  (undo beyond last save)
            o  auto complete, auto correct,
            o
            o  ... and a lot more.

 It is fast, it is extendable. The editor has a table driven key mapping.
 One can easily edit the key map in keyhand.py, and the key actions
 in acthand.py The default key map resembles gedit / wed / etp / brief

 ASCII text editor, requires pyGtk. (pygobject)
 See pygtk-dependencies for easy install of dependencies.
 See also the INSTALL file.

'''

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import getopt
import signal
import time
import platform

'''

 ------------------------------------------------------------------------
 This project is a successor of pyedit.py

 Pyedpro functions near identical on Linux / Windows / Mac / Raspberry PI

 It is fast, it is extendable. The editor has a table driven key mapping.
 One can easily edit the key map in keyhand.py, and the key actions
 in acthand.py The default key map resembles gedit / wed / etp / brief

 History:  (incomplete list)

 Sun 05.Sep.2021   ported to Mac M1 ... what a pain .. half the things did not work
 jul/19/2018       Coloring for spell check, Trigger by scroll, more dominant color
 Jul/xx/2018       Update README, KEYS.TXT
 Jun/xx/2018       Log Files for time accounting.
 Jun/08/2020       Menu control / Headerbar / Version update
 Mon 28.Sep.2020   Reshuffled imports pylint
 Fri 25.Dec.2020   Added web view, m4 filter md2html filterRelese ready
 Fri 07.May.2021   Many fixed, installs, new features

 ASCII text editor, requires pyGtk. (pygobject)
 See pygtk-dependencies for easy install of dependencies.
 See also the INSTALL file.
'''

import gettext
gettext.bindtextdomain('pyedpro', './locale/')
gettext.textdomain('pyedpro')
_ = gettext.gettext
#locale.setlocale(locale.LC_ALL, '')

orgbase = os.getcwd()
#print("cwd", orgbase)

#base    = os.path.realpath(__file__)
#basedir = os.path.dirname(base)
#print("file", os.path.dirname(base))
#os.chdir(basedir)

#modbase = ""
#for aa in sys.path:
#    if "pyedpro-" in aa:
#        #print("aa", aa)
#        modbase = aa

#sys.path.append(basedir + os.sep + "panglib")
#sys.path.append(basedir + os.sep + "pedlib")
#sys.path.append(basedir + os.sep + "pycommon")

# Also add pyedpro's EGG module dependencies

#sys.path.append(modbase + os.sep + "panglib")
#sys.path.append(modbase + os.sep + "pedlib")
#sys.path.append(modbase + os.sep + "pycommon")

#sys.path.append("panglib")
#sys.path.append("pedlib")
#sys.path.append("pycommon")

#print(sys.path)

from pedlib import pedconfig
from pedlib import pedync

# Commit global crap here
pedconfig.conf = pedconfig.Conf()

from pedlib import keyhand
from pedlib import acthand
from pedlib import pedsql

pedconfig.conf.acth = acthand.ActHand()
pedconfig.conf.keyh = keyhand.KeyHand(pedconfig.conf.acth)
pedconfig.conf.orig_path = orgbase

from pedlib import pedwin
from pedlib import pedlog
from pedlib import pedutil
from pedlib import pedplug

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio

import faulthandler
faulthandler.enable()

def tracer(frame, event, arg):
    if event != "line" and event != "return":
        print(event, frame.f_code.co_filename, frame.f_lineno)
    return tracer

#print("domain", gettext.textdomain)

#try:
#    from pkg_resources import resource_filename
#    print (os.path.abspath(resource_filename(__name__.data, 'pedicon.png')) )
#except:
#    print(sys.exc_info())

VERSION     = "2.9.5"
BUILDDATE   = "Fri 02.Sep.2022"
PROGNAME    = "PyEdPro"

# ------------------------------------------------------------------------

class MainPyed(Gtk.Application):

    def __init__(self, projname, strarr):
        super(MainPyed, self).__init__(application_id="pyedpro.py",
                                    flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.projname = projname
        self.strarr = strarr

    def do_activate(self):
        if pedconfig.conf.verbose:
            print(PROGNAME, "running on", "'" + os.name + "'", \
                "GTK", Gtk._version, "PyGtk", \
                   "%d.%d.%d" % (Gtk.get_major_version(), \
                        Gtk.get_minor_version(), \
                            Gtk.get_micro_version()))

        #signal.signal(signal.SIGTERM, terminate)
        mainwin = pedwin.EdMainWindow(None, None, self.strarr)
        self.add_window(mainwin.mywin)
        pedconfig.conf.pedwin = mainwin

        if self.projname:
            mainwin.opensess(self.projname)

        #pedync.message("\n   Start?.   \n\n")

        #if strarr:
        #    print("opening files", strarr)
        #    for aa in strarr:
        #        if os.path.isfile(aa):
        #            mainwin.openfile(aa)


def run_main(projname, strarr):

    if pedconfig.conf.verbose:
        print(PROGNAME, "running on", "'" + os.name + "'", \
            "GTK", Gtk._version, "PyGtk", \
               "%d.%d.%d" % (Gtk.get_major_version(), \
                    Gtk.get_minor_version(), \
                        Gtk.get_micro_version()))

    signal.signal(signal.SIGTERM, terminate)

    mainwin = pedwin.EdMainWindow(None, None, strarr, orgbase)
    pedconfig.conf.pedwin = mainwin

    if projname:
        mainwin.opensess(projname)

    #if strarr:
    #    print("opening files", strarr)
    #    for aa in strarr:
    #        if os.path.isfile(aa):
    #            mainwin.openfile(aa)

    Gtk.main()

    #while True:
    #    ret = Gtk.main_iteration()
    #    if not ret:
    #        break

def xversion():
    ''' Offer version number '''
    print("Version", pedconfig.conf.version)
    sys.exit(1)

def xhelp():
    ''' Offer Help '''
    print()
    print(PROGNAME, _("Version: "), pedconfig.conf.version)
    print(_("Usage: ") + PROGNAME + _(" [options] [[filename] ... [filename]]"))
    print(_("Option(s):"))
    print(_("            -d level  - Debug level 1-10 (0 silent; 1 some; 10 lots)"))
    print(_("            -j pname  - Load project (saved session)"))
    print(_("            -v        - Verbose (to stdout and log)"))
    print(_("            -f        - Start Full screen"))
    print(_("            -c        - Dump Config"))
    print(_("            -o        - Use real stdout (for debug strings)"))
    print(_("            -V        - Show version"))
    print(_("            -x        - Clear (eXtinguish) config (will prompt)"))
    print(_("            -k        - Show Keys Presses"))
    print(_("            -t        - Set tracer ON (lots of output)"))
    print(_("            -h        - Help"))
    print()
    sys.exit(1)

# ------------------------------------------------------------------------

#def terminate(arg1 = None, arg2 = None):
def terminate():
    ''' Termination Handler'''
    if pedconfig.conf.verbose:
        print(_("Terminating pydepro.py, saving files to ~/pydepro"))

    # Save all
    pedconfig.conf.pedwin.activate_quit(None)
    #return signal.SIG_IGN

# ------------------------------------------------------------------------
# Start of program:

def mainstart(name = "", args = "", oldpath = ""):

    ''' Main Entry Point for the editor '''

    SHOW_TIMING = 0
    SHOW_CONFIG = 0
    CLEAR_CONFIG = 0
    USE_STDOUT = 0

    #print ("cmd opts", sys.argv, os.getcwd(), sys.path[0])

    # Redirect stdout to a fork to real stdout and log. This way messages can
    # be seen even if pydepro is started without a terminal (from the GUI)

    opts = []; args = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h?vVj:fxctokt",
                        ["debug=", "help", "help", "verbose", "version", "project="])

    except getopt.GetoptError as err:
        print(_("Invalid option(s) on command line:"), err)
        sys.exit(1)

    #print ("opts", opts, "args", args)
    #sys.exit(0)

    pedconfig.conf.version = VERSION
    pedconfig.conf.build_date = BUILDDATE
    pedconfig.conf.progname = PROGNAME

    pname = ""
    # Outdated parsing ... for now, leave it as is
    for aa in opts:
        #print("opt", aa[0])
        if aa[0] == "-d" or aa[0] == "--debug":
            try:
                pedconfig.conf.pgdebug = int(aa[1])
                print( PROGNAME, _("Running at debug level:"),  pedconfig.conf.pgdebug)
            except:
                pedconfig.conf.pgdebug = 0

        if aa[0] == "-j" or aa[0] == "--project":
            rrr = False
            try:
                if pedconfig.conf.verbose:
                    print( PROGNAME, "Loading sess/project", aa[1])
                pname = pedconfig.conf.sess_data + os.sep + aa[1]
                if not os.path.isfile(pname):
                    pname = pedconfig.conf.sess_data + os.sep + aa[1] + ".sess"
                    if not os.path.isfile(pname):
                        rrr = True
            except:
                print("Exception on loading project", sys.exc_info())
                #pedutil.put_exception("load proj")

            if rrr:
                print( PROGNAME, "Error on loading project", pname)
                sys.exit(1)

        if aa[0] == "-h" or  aa[0] == "--help" or aa[0] == "-?":
            xhelp()
        if aa[0] == "-V" or aa[0] == "--version":
            xversion()
        if aa[0] == "-v" or aa[0] == "--verbose":
            pedconfig.conf.verbose = True
        if aa[0] == "-f":
            pedconfig.conf.full_screen = True
        if aa[0] == "-v":
            pedconfig.conf.verbose = True
        if aa[0] == "-x":
            CLEAR_CONFIG = True
        if aa[0] == "-c":
            SHOW_CONFIG = True
        if aa[0] == "-t":
            SHOW_TIMING = True
        if aa[0] == "-o":
            USE_STDOUT = True
        if aa[0] == "-k":
            pedconfig.conf.show_keys = True
        if aa[0] == "-t":
            print("Tracing ON")
            sys.settrace(tracer)

    if pedconfig.conf.pgdebug > 0:
        print("Running '{}'".format(os.path.abspath(sys.argv[0])) )

    try:
        if not os.path.isdir(pedconfig.conf.config_dir):
            if pedconfig.conf.verbose:
                print("making", pedconfig.conf.config_dir)
            os.mkdir(pedconfig.conf.config_dir)
    except:
        pass

    # Let the user know if it needs fixin'
    if not os.path.isdir(pedconfig.conf.config_dir):
        print(_("Cannot access config dir:"), pedconfig.conf.config_dir)
        sys.exit(1)


    if pedconfig.conf.verbose:
        print("sys.path", sys.path)

    pedconfig.ensure_dirs(pedconfig.conf)

    pedconfig.conf.sql = pedsql.pedsql(pedconfig.conf.sql_data)

    if pedconfig.conf.verbose:
        print(_("Data stored in "), pedconfig.conf.config_dir)

    # Initialize sqlite to load / save preferences & other info
    # Initialize pedconfig for use

    #pedconfig.conf.sql = pedsql.pedsql(pedconfig.conf.sql_data)
    pedconfig.conf.mydir = os.path.abspath(__file__)
    #print("Exe path:",  pedconfig.conf.mydir)

    # To clear all config vars
    if CLEAR_CONFIG:
        print(_("Are you sure you want to clear config ? (y/n)"))
        sys.stdout.flush()
        aa = sys.stdin.readline()
        if aa[0] == "y":
            print(_("Removing configuration ... "), end=' ')
            pedconfig.conf.sql.rmall()
            print("OK")
        sys.exit(0)

    # To check all config vars
    if SHOW_CONFIG:
        print("Dumping configuration:")
        ss = pedconfig.conf.sql.getall()
        for aa in ss:
            print(aa)
        sys.exit(0)

    # Uncomment this for silent stdout
    if USE_STDOUT or pedconfig.conf.pgdebug or \
                    pedconfig.conf.verbose:
        # Do not hide console
        #print("Using real stdout")
        pedwin.hidden = True    # Already hidden no hide
    else:
        pedwin.hidden = False   # Take action, hide

    #print("pyedpro started", sys.argv)

    # Uncomment this for buffered output
    if pedconfig.conf.verbose:
        print("Started", PROGNAME, "in",
                    pedconfig.conf.orig_dir, "from",
                        pedconfig.conf.orig_path)
    # Init plugins
    try:
        pedplug.load_plugins()
    except:
        print("Cannot load plugins", sys.exc_info())

    run_main(pname, args[0:])

    #app = MainPyed(pname, args[0:])
    #app.run()

# ------------------------------------------------------------------------

def mainfunc():

    # Create log window
    sys.stdout = pedlog.fake_stdout(sys.stdout)
    sys.stderr = pedlog.fake_stdout(sys.stdout)

    #print("PyEdPro running on", platform.system())

    pedlog.create_logwin()
    pedlog.log("Started PyEdPro", time.ctime(None))

    #print("in main", sys.argv[0])
    mainstart("", [], "")

# Setup needed it for scripts

if __name__ == '__main__':
    mainfunc()

# EOF