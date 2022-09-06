#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import time, sys, os, re, stat
import string, pickle, site

import distutils.sysconfig

# This is a very old install

#installerdir = sys.argv[0][:sys.argv[0].rfind("/")] + "/"

depfailed = False
install = True

PROJNAME    = "pyedpro"
PROJLIB     = "pyedlib"
PROJLIB_I   = "pyedlib/images"
PROJLIB_D   = "pyedlib/data"
PROJLIB2    = "panglib"
PROGNAME    = "'" + PROJNAME+ ".py'"

if len (sys.argv) > 1:
    #print ("Argv", sys.argv)
    if "remove" in sys.argv[1]:
        install = False

# ------------------------------------------------------------------------
# Return True if exists

def isdir(fname):

    try:
        ss = os.stat(fname)
    except:
        return False
    if stat.S_ISDIR(ss[stat.ST_MODE]):
        return True
    return False

# ------------------------------------------------------------------------
# Make dir if it does not exist

def softmkdir(dirx):
    if not isdir(dirx):
        #print( "Creating directory '" + dirx + "'")
        os.mkdir(dirx, 0o755)
        if not isdir(dirx):
            return False
    return True

# See if path contains user dirs:
home = os.environ['HOME']
user = os.environ['USER']

#print( "home", home, "user", user)

stream = os.popen("whoami"); output = stream.read()
if output.strip() != "root":
    print( "FAILED: You must be root to install / remove", PROGNAME)
    print( PROGNAME, "can be run from any directory that has pyedlib as subdir.")
    sys.exit()

#print( "Verifying dependencies .... ")

def check_dep():
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        #gi.require_version("Gtk", "4.0")
        #from gi.repository import Gtk

    except ImportError:
        print( "  >>>  Missing Dependencies: Python GTK+ bindings")
        #depfailed = True

    try:
        import gnome.ui
    except ImportError:
        print( "  >>>  Warn: Missing Dependencies: Python GNOME bindings (python-gnome2).")
        #depfailed = True

    # not stricly needed, just a validity check

    prefix = sys.prefix
    if not isdir(prefix):
        print( "  >>>  Missing Dependencies: sys prefix dir does not exist.")
        depfailed = True

    # ------------------------------------------------------------------------

    print( "All dependencies have been met.")

shared   =  "/usr/share"
xshared  = "/usr/share" + "/" + PROJNAME
bindir   = "/usr/local/bin"

pylib = distutils.sysconfig.get_python_lib()
if not isdir(pylib):
    print( "  >>>  Missing Dependencies: Python Library dir does not exist.")
    depfailed = True

#print( "prefix:", prefix)
#print( "libdir:", libdir)

    # --- file  ---  target dir ---- exec flag ----
filelist = \
    ['pyedpro.py',      bindir,          True ],     \
    ['pangview.py',     bindir,          True ],     \
    ['README.md',       xshared,         False ],     \
    ['HISTORY',         xshared,         False ],     \

    # --- dir  ---  target dir ---- root owner flag ----
dirlist = \
    [ PROJLIB2,      pylib,          True ], \
    [ PROJLIB,       pylib,          True ], \
    [ PROJLIB_I,     pylib,          False ], \
    [ PROJLIB_D,     pylib,          False ], \

# Copy all to target:
#print( "Making target directories:")

if install:

    check_dep()

    if depfailed:
        print( "FAILED: Dependencies not met. Exiting.")
        sys.exit(1)

    softmkdir(xshared)

    for source, dest, exe in dirlist:
        targ = dest + "/" + source
        #print( "mkdir   '" + targ + "'" )
        softmkdir(targ)

    print( "Copying files:")

    for source, dest, exe in filelist:
        try:
            targ =  dest +  "/" + source
            spp = " " * (16 - len(source))
            print( "   '" + source + "'" + spp, "-> " + targ + "'")
            # Do not overwrite newer stuff
            #commands.getoutput("cp -u " + source + " " + targ)
            stream = os.popen("cp " + source + " " + targ)
            output = stream.read()

            if exe:
                os.chmod(targ, 0o755) # Root can rwx; can rx
            else:
                os.chmod(targ, 0o644) # Root can rw; others r
        except:
            print( sys.exc_info())

    print( "Copying directories:")

    for source, dest, exe in dirlist:
        try:
            spp = " " * (16 - len(source))
            print( "   '" + source + "'" + spp, "-> " + dest + "'")
            os.popen("cp -a " + source + " " + dest)
            if exe:
                os.popen(" chown root.root " + dest + "/" + source + "/*")
        except:
            print( sys.exc_info())

    print( )
    print( "You may now use the", PROGNAME, "utility on your system.")
    print()

else:

    print("Removing files:")

    for source, dest, exe in filelist:
        try:
            targ =  dest +  "/" + source
            if os.path.isfile(targ):
                print( "   '" + targ + "'")
                os.popen("rm " + targ)
        except:
            print( sys.exc_info())


    print( "Removing directories:")

    for aa in range(len(dirlist)-1, -1, -1):
        source, dest, exe = dirlist[aa]
        try:
            rrr = dest + os.sep + source
            if os.path.isdir(rrr):
                print( "   '" + rrr + "'")
                os.popen("rm -r " + rrr)

        except:
            print( sys.exc_info())

















