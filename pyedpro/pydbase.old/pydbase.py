#!/usr/bin/env python3

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading, warnings
import  string

#psutil

import gettext
gettext.bindtextdomain('thisapp', './locale/')
gettext.textdomain('thisapp')
_ = gettext.gettext

import twincore, pypacker

# ------------------------------------------------------------------------

gl_lockname = "pydbase.main.lock"

# Module variables (pushed to a class)

class _m():
    pgdebug = 0
    verbose = 0
    keyonly = 0
    ncount  = 1
    skipcnt = 0
    maxx    = 10
    lcount  = twincore.INT_MAX
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

    deffile = "data/pydbase.pydb"

version = "0.9.3"
vdate   =  "Sat 11.Feb.2023"
allstr  =    " " + \
                string.ascii_lowercase +  string.ascii_uppercase +  \
                    string.digits

# ------------------------------------------------------------------------

# Return a random string based upon length

def randstr(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(allstr)-1)
        rr = allstr[ridx]
        strx += str(rr)
    return strx

def help():
    print("Usage: pydebase.py [options] [arg_key arg_data]")
    print(" Options: -h         help (this screen)   -|-  -i  show deleted on dump")
    print("          -V         print version        -|-  -q  quiet on")
    print("          -d         debug level (0-10)   -|-  -v  increment verbosity level")
    print("          -r         randomize data       -|-  -w  write fixed record(s)")
    print("          -z         dump backwards(s)    -|-  -i  show deleted record(s)")
    print("          -U         Vacuum DB            -|-  -R  reindex / recover DB")
    print("          -I         DB Integrity check   -|-  -c  set check integrity flag")
    print("          -s         Skip to count recs   -|-  -K  list keys only")
    print("          -y  key    find by key          -|-  -m  dump data to console")
    print("          -o  offs   get data from offset -|-  -e  offs   delete at offset")
    print("          -u  rec    delete at position   -|-  -g  num    get number of recs.")
    print("          -k  key    key to save          -|-  -a  str    data to save ")
    print("          -S         print num recs       -|-  -D  key    delete by key ")
    print("          -n  num    number of records    -|-  -t  key    retrieve by key")
    print("          -p  num    skip number of recs  -|-  -F  subkey find by sub str")
    print("          -l  lim    limit number of recs -|-  -G  num  get record number ")
    print("          -x  max    limit max number of records to get")
    print("          -f  file   input or output file (default: 'data/pydbase.pydb')")
    print("The verbosity level influences the amount of data presented.")
    print("On the command line, use quotes for multi word arguments.")

def mainfunc():

    ''' Exersize all funtions of the twincore library '''

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
        if aa[0] == "-v":
            _m.verbose += 1
        if aa[0] == "-d":
            try:
                _m.pgdebug = int(aa[1])
                #print( sys.argv[0], _("Running at debug level"),  pgdebug)
            except:
                _m.pgdebug = 0

    for aa in opts:
        if aa[0] == "-V":
            print("Script Version:", version);
            print("Engine Version:", twincore.version);

            if _m.verbose > 0:
                print("Compiled:", vdate);
            exit(1)

        # Action flags, one at a time
        if aa[0] == "-z":
            _m.backx = True
        if aa[0] == "-u":
            _m.delrx2 = 1
            _m.delrx = int(aa[1])
        if aa[0] == "-w":
            _m.writex = True
        if aa[0] == "-i":
            _m.sdelx = True
        if aa[0] == "-q":
            _m.quiet = True
        if aa[0] == "-n":
            _m.ncount = int(aa[1])
        if aa[0] == "-t":
            _m.retrx = aa[1]
        if aa[0] == "-l":
            _m.lcount = int(aa[1])
        if aa[0] == "-x":
            _m.maxx = int(aa[1])
        if aa[0] == "-s":
            _m.skipcnt = int(aa[1])
        if aa[0] == "-f":
            _m.deffile = aa[1]
        if aa[0] == "-g":
            _m.getit = aa[1]
        if aa[0] == "-G":
            _m.getrec = aa[1]
        if aa[0] == "-k":
            _m.keyx = aa[1]
        if aa[0] == "-D":
            _m.dkeyx = aa[1]
        if aa[0] == "-a":
            _m.datax = aa[1]
        if aa[0] == "-r":
            _m.randx = True
        if aa[0] == "-U":
            _m.vacx = True
        if aa[0] == "-K":
            _m.keyonly = True
        if aa[0] == "-R":
            _m.recx = True
        if aa[0] == "-p":
            _m.skipx = int(aa[1])
        if aa[0] == "-y":
            _m.findx = aa[1]
        if aa[0] == "-o":
            _m.offsx = aa[1]
        if aa[0] == "-e":
            _m.delx = aa[1]
        if aa[0] == "-c":
            _m.checkx = True
        if aa[0] == "-S":
            _m.sizex = True
        if aa[0] == "-I":
            _m.integx = True
        if aa[0] == "-m":
            _m.dumpx = True
        if aa[0] == "-F":
            _m.findrec = aa[1]

    #print("args", len(args), args)

    if len(args) == 1:
        print("Must have zero or two arguments. Use -h for help.")
        sys.exit(1)

    # Set some flags
    twincore.core_quiet     = _m.quiet
    twincore.core_pgdebug   = _m.pgdebug
    twincore.core_showdel   = _m.sdelx
    twincore.core_integrity = _m.checkx
    twincore.core_pgdebug   = _m.pgdebug

    # Create our database
    core = twincore.TwinCore(_m.deffile)
    core.core_verbose   = _m.verbose

    # See if we have arguments, save it as data
    if len(args) == 2:
        #print("args", args)
        curr = core.save_data(args[0], args[1])
        sys.exit(0)

    #print(dir(core))

    # Correct maxx
    if _m.maxx == 0 : _m.maxx = 1

    dbsize = core.getdbsize()
    #print("DBsize", dbsize)

    if _m.keyx and _m.datax:
        curr = 0
        if _m.verbose:
            print("adding", _m.keyx, _m.datax)
        for aa in range(_m.ncount):
            curr = core.save_data(_m.keyx, _m.datax)
        #print("curr", curr)
    elif _m.keyx:
        curr = 0
        if verbose:
            print("adding", keyx)
        for aa in range(ncount):
            curr = core.save_data(keyx, "dddd dddd")
        #print("curr", curr)
    elif _m.writex:
        curr = 0;
        if _m.randx:
            for aa in range(_m.ncount):
                curr = core.save_data(
                    randstr(random.randint(2, 10)),
                        randstr(random.randint(10, 20)))
        else:
            for aa in range(_m.ncount):
                curr = core.save_data("111 222", "333 444")
        #print("curr", curr)
    elif _m.findx:
        if _m.lcount == 0: _m.lcount = 1
        ddd = core.find_key(_m.findx, _m.lcount)
        print("Found records:", ddd)
    elif _m.getrec:
        ddd = core.get_rec(int(_m.getrec))
        print("Got:", ddd)

    elif _m.keyonly:
        cnt = 0
        if _m.lcount + _m.skipx > dbsize:
            _m.lcount = _m.dbsize - _m.skipx
        for aa in range(skipx, lcount):
            ddd = core.get_rec(aa)
            print(aa, ddd[0])
            cnt += 1

    elif _m.getit:
        getx = int(_m.getit)
        #skipx = dbsize - skipx
        if getx + _m.skipx > dbsize:
            getx = dbsize - _m.skipx
        if _m.skipx < 0:
            _m.skipx = 0
            print("Clipping to dbsize of", dbsize)
        if _m.verbose:
            print("Getting %d records" % getx);
            if _m.skipx:
                print("With skipping %d records" % skipx);

        for aa in range(_m.skipx, getx + _m.skipx):
            ddd = core.get_rec(aa)
            print(aa, ddd)

    elif _m.retrx != "":
        if _m.ncount == 0: _m.ncount = 1
        ddd = core.retrieve(_m.retrx, _m.ncount)
        if not ddd:
            print("Record:", "'" + _m.retrx + "'", "is not found.")
        else:
            print(ddd)
    elif _m.sizex:
        print("Database size:", core.getdbsize())
    elif _m.offsx:
        ddd = core.get_rec_offs(int(_m.offsx))
        print(ddd)
    elif _m.delx:
        ddd = core.del_rec_offs(int(_m.delx))
        print(ddd)
    elif _m.delrx2:
        ddd = core.del_rec(int(_m.delrx))
        print(ddd)
    elif _m.dkeyx:
        ddd = core.del_rec_bykey(_m.dkeyx)
        print("Deleted:", ddd, "records.")
    elif _m.recx:
        ddd = core.reindex()
        print("Reindexed:", ddd, "record(s)")
    elif _m.vacx:
        ddd = core.vacuum()
        print("Vacuumed:", ddd[0], "saved", ddd[1], "record(s)")
    elif _m.integx:
        ddd = core.integrity_check()
        print("Integrity check found good:", ddd[0], "of", ddd[1], "record(s)")
    elif _m.dumpx:
        if _m.backx:
            core.dump_data(_m.lcount, _m.skipx)
        else:
            core.revdump_data(_m.lcount, _m.skipx)
    elif _m.findrec:
            ret = core.findrec(_m.findrec, _m.lcount, _m.skipx)
            if _m.verbose:
                print("Found:", end = "")
            print(ret)
    else:
        print("Use: pydbase.py -h to see options and help")

if __name__ == "__main__":

    # Tested with process based lock (OK)
    #twincore.waitlock(gl_lockname)
    mainfunc()
    #twincore.dellock(gl_lockname)

# EOF
