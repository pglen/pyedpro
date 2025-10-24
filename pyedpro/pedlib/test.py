#!/usr/bin/env python3

'''123456
This is open source text editor. Written on python. The motivation for
this project was to create a modern multi-platform editor. Simple,
powerful, configurable, extendable. To run this module without
installation put the supporting files in the 'pedlib'
subdirectory under the main file's direcory. Hello Keylog. 12345678
'''

from __future__ import absolute_import
from __future__ import print_function

import osx
import sys
import getopt
import signal

# ------------------------------------------------------------------------
# This is open source text editor. Written on python. The motivation for
# this project was to create a modern multi-platform editor.
# Simple, powerful, configurable, extendable.
#
# This project is a successor of pyedit.py
#
# Pyedpro functions near identical on Linux / Windows / Mac / Raspberry PI
#
# Pyedpro has:
#
#    o  macro recording/play,
#    o  search/replace,
#    o  functional navigation,
#    o  comment/string spell check,
#    o  full spell check, spell suggestion dialog
#    o  auto backup,
#    o  persistent undo/redo,  (undo beyond last save)
#    o  auto complete, auto correct,
#    o
#    o  ... and a lot more.
#
# It is fast, it is extendable. The editor has a table driven key mapping.
# One can easily edit the key map in keyhand.py, and the key actions
# in acthand.py The de fault key map resembles gedit / wed / etp / brief

# History:  (recent first, incomplete list)
#
# jul/19/2018 Coloring for spell check, Trigger by scroll, more dominant color
# Jul/xx/2018       Update README, KEYS.TXT
# Jun/xx/2018       Log Files for time accounting.
# Jun/08/2020       Menu control / Headerbar / Version update
# Mon 28.Sep.2020   Reshuffled imports pylint
# Fri 25.Dec.2020   Added web view, m4 filter md2html filterRelese ready

# ASCII text editor, requires pyGtk. (pygobject)
# See pygtk-dependencies for easy install of dependencies.
# See also the INSTALL file.

import gettext
gettext.bindtextdomain('pyedpro', './locale/')
gettext.textdomain('pyedpro')
_ = gettext.gettext
#locale.setlocale(locale.LC_ALL, '')

base = os.path.realpath(__file__)
#print("file", os.path.dirname(base))
os.chdir(os.path.dirname(base))

import pedlib.pedconfig as pedconfig
import pedlib.pedwin as pedwin
import pedlib.pedsql as pedsql
import pedlib.pedlog as pedlog

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

#print("domain", gettext.textdomain)

VERSION = 1.9
BUILDDATE = "Fri 25.Dec.2020"
PROGNAME  = "PyEdPro"

SHOW_TIMING = 0
SHOW_CONFIG = 0
CLEAR_CONFIG = 0
USE_STDOUT = 0

class test_1():
    def __init__(self):
        pass
    def aa():
        pass

class test_2():
    def __init__(self):
        pass
    def bb():
        pass

class test_3():
    def __init__(self):
        pass

# ------------------------------------------------------------------------

def main(strarr):

    ''' Rotate around this axis '''

    if pedconfig.conf.verbose:
        print(PROGNAME, "running on", "'" + os.name + "'", \
            "GTK", Gtk._version, "PyGtk", \
               "%d.%d.%d" % (Gtk.get_major_version(), \
                    Gtk.get_minor_version(), \
                        Gtk.get_micro_version()))

    signal.signal(signal.SIGTERM, terminate)
    mainwin = pedwin.EdMainWindow(None, None, strarr)
    pedconfig.conf.pedwin = mainwin

    # Create log window
    pedlog.create_logwin()

    Gtk.main()

def xversion():
    ''' Offer version number '''
    print("Version", pedconfig.conf.version)
    sys.exit(1)

def xhelp():
    ''' Offer Help '''
    print()
    print(PROGNAME, _("Version: "), pedconfig.conf.version)
    print(_("Usage: ") + PROGNAME + _(" [options] [[filename] ...[filename]]"))
    print(_("Option(s):"))
    print(_(" -d level - Debug level 1-10 (0 silent; 1 some; 10 lots)"))
    print(_("            -v        - Verbose (to stdout and log)"))
    print(_("            -f        - Start Full screen"))
    print(_("            -c        - Dump Config"))
    print(_("            -o        - Use real stdout (for debug strings)"))
    print(_("            -V        - Show version"))
    print(_(" -x - Clear (eXtinguish) config (will prompt)"))
    print(_("            -k        - Show Keys Presses"))
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


if __name__ == '__main__':

    ''' Main Entry Point for the editor '''

    # Redirect stdout to a fork to real stdout and log. This way messages can
    # be seen even if pydepro is started without a terminal (from the GUI)

    opts = []; args = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h?fvVxctok",
                        ["debug=", "help", "help", "verbose", "version"])
    except getopt.GetoptError as err:
        print(_("Invalid option(s) on command line:"), err)
        sys.exit(1)

    #print ("opts", opts, "args", args)

    pedconfig.conf.version = VERSION
    pedconfig.conf.build_date = BUILDDATE
    pedconfig.conf.progname = PROGNAME

    # Outdated parsing ... for now, leave it as is
    for aa in opts:
        #print("opt", aa[0])
        if aa[0] == "-d" or aa[0] == "--debug":
            try:
                pedconfig.conf.pgdebug = int(aa[1])
                print( PROGNAME, _("Running at debug level:"), pedconfig.conf.pgdebug)
            except:
                pedconfig.conf.pgdebug = 0

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
            #print("Showing keys")

