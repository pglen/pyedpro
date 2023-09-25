#!/usr/bin/env python3

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading, warnings
import  string, hashlib

#psutil

import gettext
gettext.bindtextdomain('thisapp', './locale/')
gettext.textdomain('thisapp')
_ = gettext.gettext

import twinchain, pypacker

version = "0.0.1"

#print("hashes", hashlib.algorithms_guaranteed)

# Module variables (pushed to a class)

class _c():
    pgdebug = 0
    verbose = 0
    keyonly = 0
    ncount  = 1
    skipcnt = 0
    append  = 0
    maxx    = 10
    lcount  = twinchain.INT_MAX
    quiet   = 0; writex  = 0
    randx   = 0; skipx   = 0
    offsx   = 0; delx    = 0
    delrx   = 0; delrx2  = 0
    backx   = 0; sdelx   = 0
    vacx    = 0; recx    = 0
    integx  = 0; checkx  = 0
    sizex   = 0; findx   = ""
    retrx   = ""; getit  = ""
    keyx    = ""; datax  = ""
    dkeyx   = ""; dumpx  = 0
    findrec = ""; getrec = 0

    deffile = "data/pydbchain.pydb"

def help():
    print("Usage: pychain.py [options]")
    print("   Options: -a  data   append data to the end of chain")
    print("            -h         help (this screen)")
    print("            -m         dump chain data")
    print("            -c         check chain data")
    print("            -i         check chain integrity")
    print("            -v         increase verbosity")

def mainfunc():

    ''' Exersize funtions of the twinchain library. '''

    opts = []; args = []

    # Old fashioned parsing
    opts_args   = "a:d:e:f:g:k:l:n:o:s:t:u:x:y:p:D:F:G:"
    opts_normal = "mchiVrwzvqURIK?S"
    try:
        opts, args = getopt.getopt(sys.argv[1:],  opts_normal + opts_args)
    except getopt.GetoptError as err:
        print(_("Invalid option(s) on command line:"), err)
        sys.exit(1)

    # Scan twice so verbose shows up early
    for aa in opts:
        if aa[0] == "-h" or aa[0] == "-?":
            help(); exit(1)

        if aa[0] == "-V":
            print("Script Version:", version);
            print("Engine Version:", twincore.version);
            exit(0)

        if aa[0] == "-f":
            _c.deffile = aa[1]

        if aa[0] == "-a":
            _c.append = aa[1]

        if aa[0] == "-m":
            _c.dumpx = True

        if aa[0] == "-v":
            _c.verbose += 1

        if aa[0] == "-c":
            _c.checkx = True

        if aa[0] == "-i":
            _c.integx = True

    #print("Use: pychain.py -h to see options and help")

    # Create our database
    core = twinchain.TwinChain(_c.deffile)
    core.core_verbose = _c.verbose

    if _c.integx:
        #print("Integrity", _c.integx)
        errx = False; cnt = []
        sss = core.getdbsize()
        # Remember record zero is the anchor
        for aa in range(1, sss):
            ppp = core.integrity(aa)
            if _c.verbose:
                print(aa, ppp)
            if not ppp: errx = True; cnt.append(aa)
        if errx:
            print("error on rec", cnt)
        else:
            print("DB integrity checks out OK")

    elif _c.checkx:
        #print("Checking", _c.checkx)
        errx = False; cnt = -1
        sss = core.getdbsize()
        for aa in range(sss):
            ppp = core.check(aa)
            if _c.verbose:
                print(aa, ppp)
            if not ppp: errx = True; cnt = aa
        if errx:
            print("error on rec", cnt)
        else:
            print("DB checks out OK")

    elif _c.dumpx:
        #print("Dumping", _c.dumpx)
        sss = core.getdbsize()
        for aa in range(sss):
            ppp = core.get_payload(aa)
            print(aa, ppp)

    elif _c.append:
        #print("Appending", _c.append)
        core.append(_c.append)
    else:
        print("use: pychain.py -h for info on usage.")

if __name__ == "__main__":

    # Tested with process based lock (OK)
    #twincore.waitlock(gl_lockname)
    mainfunc()

    #twincore.dellock(gl_lockname)

# EOF

