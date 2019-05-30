#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import sys, os, re, time, stat
import string,  traceback

from . import pedconfig
#from six import unichr

# ------------------------------------------------------------------------
# Convert octal string to integer

def oct2int(strx):
    retx = 0
    for aa in strx:
        num = ord(aa) - ord("0")
        if num > 7 or num < 0:
            break
        retx <<= 3; retx += num
    #print "oct:", strx, "int:", retx
    return retx

# ------------------------------------------------------------------------
# Convert unicode sequence to unicode char

def uni(xtab):

    #print str.format("{0:b}",  xtab[0])

    cc = 0
    try:
        if xtab[0] & 0xe0 == 0xc0:  # two numbers
            cc = (xtab[0] & 0x1f) << 6
            cc += (xtab[1] & 0x3f)
        elif xtab[0] & 0xf0 == 0xe0: # three numbers
            cc = (xtab[0] & 0x0f) << 12
            cc += (xtab[1] & 0x3f) << 6
            cc += (xtab[2] & 0x3f)
        elif xtab[0] & 0xf8 == 0xf0: # four numbers
            cc = (xtab[0] & 0x0e)  << 18
            cc += (xtab[1] & 0x3f) << 12
            cc += (xtab[2] & 0x3f) << 6
            cc += (xtab[3] & 0x3f)
        elif xtab[0] & 0xfc == 0xf8: # five numbers
            cc = (xtab[0] & 0x03)  << 24
            cc += (xtab[1] & 0x3f) << 18
            cc += (xtab[2] & 0x3f) << 12
            cc += (xtab[3] & 0x3f) << 6
            cc += (xtab[4] & 0x3f)
        elif xtab[0] & 0xfe == 0xf8: # six numbers
            cc = (xtab[0] & 0x01)  << 30
            cc += (xtab[1] & 0x3f) << 24
            cc += (xtab[2] & 0x3f) << 18
            cc += (xtab[3] & 0x3f) << 12
            cc += (xtab[4] & 0x3f) << 6
            cc += (xtab[5] & 0x3f)

        ccc = unichr(cc)
    except:
        pass

    return ccc

def is_ascii(strx):

    pos = 0; lenx = len(strx)
    while True:
        if pos >= lenx:
            break

        chh = strx[pos]
        #print (ord(chh))
        if ord(chh) > 127:
            #print (ord(chh))
            if pos == 0: pos += 1
            return pos
        pos+= 1

    return 0

def kill_non_ascii(strx):

    str2 = ""
    pos = 0; lenx = len(strx)
    while True:
        if pos >= lenx:
            break

        chh = strx[pos]
        #print (ord(chh))
        if ord(chh) <= 127:
            str2 += chh
        else:
            str2 += "*"
        pos+= 1

    return str2

# ------------------------------------------------------------------------
# Unescape unicode into displayable sequence

xtab = []; xtablen = 0

def unescape(strx):

    #print " x[" + strx + "]x "

    global xtab, xtablen
    retx = u""; pos = 0; lenx = len(strx)

    while True:
        if pos >= lenx:
            break

        chh = strx[pos]

        if(chh == '\\'):
            #print "backslash", strx[pos:]
            pos2 = pos + 1; strx2 = ""
            while True:
                if pos2 >= lenx:
                    # See if we accumulated anything
                    if strx2 != "":
                        xtab.append(oct2int(strx2))
                    if len(xtab) > 0:
                        #print "final:", xtab
                        if xtablen == len(xtab):
                            retx += uni(xtab)
                            xtab = []; xtablen = 0
                    pos = pos2 - 1
                    break
                chh2 = strx[pos2]
                if chh2  >= "0" and chh2 <= "7":
                    strx2 += chh2
                else:
                    #print "strx2: '"  + strx2 + "'"
                    if strx2 != "":
                        octx = oct2int(strx2)
                        if xtablen == 0:
                            if octx & 0xe0 == 0xc0:
                                #print "two ",str.format("{0:b}", octx)
                                xtablen = 2
                                xtab.append(octx)
                            elif octx & 0xf0 == 0xe0: # three numbers
                                #print "three ",str.format("{0:b}", octx)
                                xtablen = 3
                                xtab.append(octx)
                            elif octx & 0xf8 == 0xf0: # four numbers
                                print("four ",str.format("{0:b}", octx))
                                xtablen = 4
                                xtab.append(octx)
                            elif octx & 0xfc == 0xf8: # five numbers
                                print("five ",str.format("{0:b}", octx))
                                xtablen = 5
                                xtab.append(octx)
                            elif octx & 0xfe == 0xfc: # six numbers
                                print("six ",str.format("{0:b}", octx))
                                xtablen = 6
                                xtab.append(octx)
                            else:
                                #print "other ",str.format("{0:b}", octx)
                                #retx += unichr(octx)
                                retx += chr(octx)
                        else:
                            xtab.append(octx)
                            #print "data ",str.format("{0:b}", octx)
                            if xtablen == len(xtab):
                                retx += uni(xtab)
                                xtab = []; xtablen = 0

                    pos = pos2 - 1
                    break
                pos2 += 1
        else:

            if xtablen == len(xtab) and xtablen != 0:
                retx += uni(xtab)
            xtab=[]; xtablen = 0

            try:
                retx += chh
            except:
                pass
        pos += 1

    #print "y[" + retx + "]y"
    return retx

# ------------------------------------------------------------------------
# Give the user the usual options for true / false - 1 / 0 - y / n

def isTrue(strx):
    if strx == "1": return True
    if strx == "0": return False
    uuu = strx.upper()
    if uuu == "TRUE": return True
    if uuu == "FALSE": return False
    if uuu == "Y": return True
    if uuu == "N": return False
    return False

# ------------------------------------------------------------------------
# Return True if file exists

def isfile(fname):

    try:
        ss = os.stat(fname)
    except:
        return False

    if stat.S_ISREG(ss[stat.ST_MODE]):
        return True
    return False

# Append to log
def logentry(kind, startt, fname):
    logfname = "account.txt"
    logfile = pedconfig.conf.log_dir + "/" + logfname
    try:
        fp = open(logfile, "a+")
    except:
        try:
            fp = open(logfile, "w+")
            fp.seek(0, os.SEEK_END);
        except:
            print("Cannot open/create log file", logfile)
            return

    log_clock = time.time()

    print("Action:", "%s %s" % (kind, os.path.realpath(fname)), file=fp)
    print("On:", time.ctime(log_clock), file=fp)
    print("Delta:", "%.0f" % (log_clock - startt), file=fp)
    print("Date:", "%.0f %s %s\n" % \
                        (log_clock, os.path.basename(fname), kind.split()[0]), file=fp)
    fp.close()

# Append to timesheet
def timesheet(kind, startt, endd):

    logfname = "timesheet.txt"
    logfile = pedconfig.conf.log_dir + "/" + logfname
    try:
        fp = open(logfile, "a+")
    except:
        try:
            fp = open(logfile, "w+")
            fp.seek(0, os.SEEK_END);
        except:
            print("Cannot open/create log file", logfile)
            return

    log_clock = time.time()

    print("Action:", "%s" % (kind), file=fp)
    print("On:", time.ctime(log_clock), file=fp)
    if endd:
        td = endd - startt
        print("Time diff:", "%.0f %d:%d" % (td, td / 3600, (td % 3600) / 60), file=fp)

    print(file=fp)
    fp.close()

def put_debug(xstr):

    print( xstr)

    '''try:
        if os.isatty(sys.stdout.fileno()):
            print( xstr)
        else:
            syslog.syslog(xstr)
    except:
        print( "Failed on debug output.")
        print( sys.exc_info())
    '''

def put_exception(xstr):

    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())

    put_debug(cumm)
    #syslog.syslog("%s %s %s" % (xstr, a, b))

def put_exception2(xstr):

    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())

    put_debug(cumm)
    #syslog.syslog("%s %s %s" % (xstr, a, b))

# EOF




