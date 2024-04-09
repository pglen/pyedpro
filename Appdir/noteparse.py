#!/usr/bin/env python3

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

import gettext
gettext.bindtextdomain('thisapp', './locale/')
gettext.textdomain('thisapp')
_ = gettext.gettext

core = None

try:
    sys.path.append('..' + os.sep + ".." )
    from pydbase import twincore
except:
    print("Cannot import twincore")

pgdebug = 0
verbose = 0
version = "1.0"

sep = " ------------------------------------------------------------------"

def main(fname):

    state = 0
    print("fname",  fname)
    data_file = os.path.split(fname)[0] + os.sep + "peddata.pydb"
    print("data_file",  data_file)

    fp = open(fname, "rt")

    try:
        global core
        core = twincore.TwinCore(data_file)
        print("core", core, core.fname)
    except:
        print("Cannot make notes py database")

    arr = []
    cnt = 0
    head = ""
    body = ""

    while 1:

        #if cnt >= 10:
        #    break

        line = fp.readline()
        if line == "":
            break

        line = line.rstrip()
        #print(line)

        if line == sep:
            if state == 0:
                state = 1       # Head

            elif state == 1:
                state = 2       # body

            elif state == 2:
                #arr.append( "    " + str(len(body)) + "     " + body[:12])
                arr.append((head, body))

                try:
                    core.save_data(head, body)
                except:
                    print("error on", head)
                    #print(sys.exc_info())
                    pass

                body = ""
                head = ""
                state = 1       # body

            #print("sep,", state)
            continue

        if state == 1:
            head += line
            #print("[" + line + "]")

        if state == 2:
            pass
            body += line
            #print("{" + line + "}")

        cnt += 1

    # leftover head body here
    core.save_data(head, body)
    arr.append((head, body))

    #for aa in arr:
    #    print (aa)

    print(len(arr), "records")


def help():
    print("Helping")

if __name__ == "__main__":

    opts = []; args = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h?fvxctVo")
    except getopt.GetoptError as err:
        print(_("Invalid option(s) on command line:"), err)
        sys.exit(1)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
                #print( sys.argv[0], _("Running at debug level"),  pgdebug)
            except:
                pgdebug = 0

        if aa[0] == "-h" or aa[0] == "-?":
            help(); exit(1)

        if aa[0] == "-V":
            print("Version", version);  exit(1)

        if aa[0] == "-v":
            #print("Verbose")
            verbose = True

    #print("args", args)
    if(len(args) < 1):
        print("usage: noteparse filename")
        sys.exit(2)

    main(args[0])

# EOF


