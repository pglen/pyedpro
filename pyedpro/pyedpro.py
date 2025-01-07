#!/usr/bin/env python3

__doc__ = \
'''
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

This project is a successor of pyedit, after porting it to GTK3.
PyEdPro  will run anywhere PyGObject runs. This includes
    Linux*; Windows (MSYS2); Mac;

  Working, and tested platforms currently are:

        Win 7 .. Win 10 ...
        Centos 6 .. 7 Ubuntu 14 ... 16 ...  20.x ... 24x
                        (should run on any linux )
        Windows (Native) plus MSYS2, Mingw,
        Raspberry PI 3, Raspberry PI 4, ...
        Mac ** Some functions are disabled - in particular async processing

  I mainly run it on Ubuntu, and in Win / MSYS2, some Fedora, Windows 10,
Windows 10 x64, and the Raspberry-Pi. It behaves consistently on all these
platforms.
  It is an absolute joy to edit in a different platform without the learning
curve of new keystrokes.  If you want an editor that works the same way in
all your workspaces, PyEdPro is the one.

Pyedpro functions near identical on Linux / Windows / Mac / Raspberry PI

 Pyedpro has:

            o  Macro recording/play,
            o  Search/replace,
            o  Functional navigation,
            o  Comment/string spell check,
            o  Full spell check, spell suggestion dialog
            o  Auto backup,
            o  Persistent undo/redo,  (undo beyond last save)
            o  Auto complete, auto correct,
            o
            o  ... and a lot more.

  PyeEdPro is fast, it is extendable. The editor has a table driven key mapping.
 One can easily edit the key map in keyhand.py, and the key actions
 in acthand.py The default key map resembles gedit / wed / etp / brief / Notepad

 ------------------------------------------------------------------------
 ## This project is a successor of pyedit.py

 Pyedpro functions near identical on Linux / Windows / Mac / Raspberry PI

 It is fast, it is extendable. The editor has a table driven key mapping.
 One can easily edit the key map in keyhand.py, and the key actions
 in acthand.py The default key map resembles gedit / wed / etp / brief

History:  (incomplete list, see git log for a more complete list)

    jul/19/2018       Coloring for spell check, Trigger by scroll, more dominant color
    Jul/xx/2018       Update README, KEYS.TXT
    Jun/xx/2018       Log Files for time accounting.
    Jun/08/2020       Menu control / Headerbar / Version update
    Mon 28.Sep.2020   Reshuffled imports pylint
    Fri 25.Dec.2020   Added web view, m4 filter md2html filterRelese ready
    Fri 07.May.2021   Many fixed, installs, new features
    Sun 05.Sep.2021   ported to Mac M1 ... what a pain .. half the things did not work
    Tue 06.Sep.2022   Installation, anchor for search ...
    Thu 27.Oct.2022   Restored menu keymaps for the system to handle it.
    Sun 05.May.2024   Import webView dummySun

 ASCII text editor, requires pyGtk. (pygobject)
 See pygtk-dependencies for easy install of dependencies.
 See also the INSTALL file.

'''

import os, sys, getopt, signal, time, platform, atexit

import gettext
gettext.bindtextdomain('pyedpro', './locale/')
gettext.textdomain('pyedpro')
_ = gettext.gettext
#locale.setlocale(locale.LC_ALL, '')
#print("domain", gettext.textdomain)

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GObject

orgbase = os.getcwd()
#print("cwd", orgbase)
#os.chdir(basedir)

basedir = os.path.dirname(os.path.realpath(__file__))
#print("file dir", basedir)
sys.path.append(basedir + os.sep)
sys.path.append(basedir + os.sep + "pycommon")
sys.path.append(basedir + os.sep + "pedlib")
#sys.path.append(basedir + os.sep + ".." + os.sep + "pycommon")

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

import faulthandler
faulthandler.enable()

def tracer(frame, event, arg):
    if event != "line" and event != "return":
        print(event, frame.f_code.co_filename, frame.f_lineno)
    return tracer

#try:
#    from pkg_resources import resource_filename
#    print (os.path.abspath(resource_filename(__name__.data, 'pedicon.png')) )
#except:
#    print(sys.exc_info())

VERSION     = "3.4.2"
BUILDDATE   = "Tue 07.Jan.2025"
PROGNAME    = "PyEdPro"

# ------------------------------------------------------------------------

class MainPyed(Gtk.Application):

    def __init__(self, projname, strarr):
        super(MainPyed, self).__init__(application_id="pyedpro.py",
                                    #flags=Gio.ApplicationFlags.IS_LAUNCHER)
                                    flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.projname = projname
        self.strarr = strarr
        self.connect("activate", self.on_activate)
        #GObject.signal_list_names(Gtk.Application)
        #print("pyed app", dir(self))

    def on_activate(self, instance):
        #print("Activated:", instance)
        pass

    def do_activate(self):
        if pedconfig.conf.verbose:
            print(PROGNAME, "running on", "'" + os.name + "'", \
                "GTK", Gtk._version, "PyGtk", \
                   "%d.%d.%d" % (Gtk.get_major_version(), \
                        Gtk.get_minor_version(), \
                            Gtk.get_micro_version()))

        signal.signal(signal.SIGTERM, terminate)
        mainwin = pedwin.EdMainWindow(None, None, self.strarr, orgbase)
        self.add_window(mainwin.mywin)
        pedconfig.conf.pedwin = mainwin

        if self.projname:
            mainwin.opensess(self.projname)

def cleanup(mw):

    ''' On exit, remove marked files (mostly temporary files) '''

    #print("Cleanup", mw.cleanit)
    for aa in mw.cleanit:
        bb = os.path.join(pedconfig.conf.temp_dir, os.path.basename(aa))
        if os.path.isfile(bb):
            os.remove(bb)
        #print("Cleaning", aa, bb)
        os.rename(aa, bb)

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
    mainwin.cleanit = []
    atexit.register(cleanup, mainwin)

    if projname:
        mainwin.opensess(projname)
    Gtk.main()

def xversion():
    ''' Offer version number '''
    print("Version", pedconfig.conf.version)
    sys.exit(1)

def xhelp():
    ''' Offer Help '''
    print()
    #print(PROGNAME, _("Version:"), pedconfig.conf.version)
    print(PROGNAME, _("advanced text editor by Peter Glen"))
    print(_("Usage: ") + PROGNAME + _(" [options] [[filename] ... [filename]]"))
    print(_("Option(s):"))
    print(_("            -d level  - Debug level 1-10 (0 silent; 1 some; 10 lots)"))
    print(_("            -j pname  - Load project (pname = saved session name)"))
    print(_("            -v        - Verbose (to stdout and log) repeat for more verbosity"))
    print(_("            -f        - Start Full screen"))
    print(_("            -c        - Dump Config"))
    print(_("            -o        - Use real stdout (for debug strings)"))
    print(_("            -V        - Show version"))
    print(_("            -x        - Clear (eXtinguish) config (will prompt)"))
    print(_("            -g        - Key log on"))
    print(_("            -k        - Show Keys Presses"))
    print(_("            -t        - Set tracer ON (lots of output)"))
    print(_("            -h        - Help (this screen)"))
    print()
    sys.exit(1)

# ------------------------------------------------------------------------

def terminate():

    ''' Termination Handler'''

    if pedconfig.conf.verbose:
        print(_("Terminating pydepro.py, saving files to ~/pydepro"))

    # Save all
    pedconfig.conf.pedwin.activate_quit(None)
    #return signal.SIG_IGN

# ------------------------------------------------------------------------

def mainstart(name = "", args = "", oldpath = ""):

    ''' Start of program. This is the main Entry Point for the editor from
        command line.
    '''

    SHOW_TIMING = 0
    SHOW_CONFIG = 0
    CLEAR_CONFIG = 0
    USE_STDOUT = 0
    KEYLOG_ON = 0

    #print ("cmd opts", sys.argv, os.getcwd(), sys.path[0])

    # Redirect stdout to a fork to real stdout and log. This way messages can
    # be seen even if pydepro is started without a terminal (from the GUI)

    opts = []; args = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h?vVj:fxctoktg",
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
                pname = pedconfig.conf.sess_dir + os.sep + aa[1]
                if not os.path.isfile(pname):
                    pname = pedconfig.conf.sess_dir + os.sep + aa[1] + ".sess"
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
            pedconfig.conf.verbose += 1
        if aa[0] == "-f":
            pedconfig.conf.full_screen = True
        if aa[0] == "-g":
            KEYLOG_ON = True
            pedconfig.conf.keylog_on = True
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

    if pedconfig.conf.pgdebug > 3:
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
        print("Started:", PROGNAME, "in", pedconfig.conf.orig_dir)
        print("From dir", pedconfig.conf.orig_path)

    if pedconfig.conf.pgdebug > 2:
        print("pyedpro sys path:")
        for aa in sys.path:
            print(aa)

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

    ''' Called from the command line scripts '''

    # Create log window
    sys.stdout = pedlog.fake_stdout(sys.stdout)
    sys.stderr = pedlog.fake_stdout(sys.stdout)

    #print("PyEdPro running on", platform.system())

    pedlog.create_logwin()
    pedlog.log("Started PyEdPro", time.ctime(None))

    #print("in main", sys.argv[0])
    mainstart("", [], "")

if __name__ == '__main__':

    ''' Setup needed an entry point for scripts '''

    mainfunc()

# EOF
