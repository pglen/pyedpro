#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import time
import string
import pickle
import random
import stat
import traceback
import subprocess
import warnings

#mained = None

if sys.version_info.major < 3:
    pass
else:
    import inspect
    if inspect.isbuiltin(time.process_time):
        time.clock = time.process_time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from pedlib import pedconfig
from pedlib import pedync

(TARGET_ENTRY_TEXT, TARGET_ENTRY_PIXBUF) = range(2)
(COLUMN_TEXT, COLUMN_PIXBUF) = range(2)

# Cut leading space in half

def cut_lead_space(xstr, divi = 2):
    res = ""; cnt = 0; idx = 0; spcnt = 0
    xlen = len(xstr)
    while True:
        if cnt >= xlen: break
        chh = xstr[idx]
        if chh == " ":
            spcnt += 1
            if spcnt >= divi:
                spcnt = 0; res += " "
        else:
            res += xstr[idx:]
            break
        idx += 1
    return res

# ------------------------------------------------------------------------
# Let the higher level deal with errors.

def  readfile(strx, sep = None):

    text = []

    if strx == "":
        return text

    # Now read and parse
    f = open(strx, "rb");  buff2 = f.read();  f.close()
    if sys.version_info.major < 3:
        buff = buff2
    else:
        try:
            buff = buff2.decode('UTF-8')
        except UnicodeDecodeError:
            buff = buff2.decode('cp437')

    buff2 = ""

    if not sep:
        # Deteremine separator, use a partial length search
        if buff.find("\r\n", 0, 300) >= 0:
            sep = "\r\n"
        elif buff.find("\n\r", 0, 300) >= 0:
            sep = "\n\r"
        elif buff.find("\r", 0, 300) >= 0:
            sep = "\r"
        else:
            sep = "\n"

    text2 = str.split(buff, sep)

    #if "Makefile" in strx:
    #    print(strx, "sep: '"+ sep + "'", ord(sep[0]), ord(sep[1]))

    # Clean out spuriously occurring \r and \n
    # Example: ST Microelectronics Makefiles

    text = []
    for aa in text2:
        #print("'%s\n" % aa)
        bb = aa.replace("\r", "")
        cc = bb.replace("\n", "")
        text.append(cc)
    #text2 = []

    return text

# ------------------------------------------------------------------------
# Return an array of lines found

def findinfile(nnn, ffff, nocase = False):

    rrr = []
    try:
        text = readfile(ffff)

        # See if text file
        cnt = 0
        try:
            line = text[0] + text[1]
            for ccc in line:
                chh = ord(ccc)
                if chh < 32 or chh > 127:
                    #print("bin", ccc, ord(ccc) )
                    cnt += 1
        except:
            #print("except in search",  sys.exc_info())
            pass

        if cnt > 3:
            #print ("Not a text file:", ffff)
            return rrr
    except:
        print("Cannot read file", ffff)
        text = ""

    unnn = nnn.lower()
    for aa in text:
        if nocase:
            if unnn in aa.lower():
                rrr.append(aa)
        else:
            if nnn in aa:
                rrr.append(aa)

    return rrr

# ------------------------------------------------------------------------
# Propagate exceptions to higher level

def  writefile(strx, buff, sep = "\n", mode = "w"):
    #print ("writefile", strx, sep)
    ret = True, ""
    if strx != "":
        try:
            fp = open(strx, mode)
            cnt = 0; sepx = ""
            for aa in buff:
                if cnt:
                    sepx = sep
                fp.write(sepx + aa.rstrip())
                cnt += 1
            fp.close()
        except:
            ret = False, sys.exc_info()[1]
            try:
                fp.close()
            except:
                pass
            pass
    return ret

# Expand image name to image path:

def get_img_path(fname):

    img_dir = os.path.dirname(__file__)
    img_path = os.path.join(img_dir, "images/", fname)
    #if pedconfig.conf.verbose:
    #    print( "img_path", img_path)
    return img_path

# Expand file name to file path in the exec dir:
# We now deliver module data directory

def get_exec_path(fname):

    #exec_dir = os.path.dirname(pedconfig.conf.mydir)
    exec_dir = os.path.dirname(__file__)
    exec_path2 = os.path.join(exec_dir, "data")
    exec_path = os.path.join(exec_path2, fname)

    if pedconfig.conf.verbose:
        print( exec_path)

    return exec_path

def get_pangview_path():

    fname = "pangview.py"
    exec_dir = os.path.dirname(__file__)
    pname = exec_dir + os.sep + ".." +  os.sep + fname
    if not os.path.isfile(pname):
        pname = fname

    if pedconfig.conf.verbose:
        print("Pangview path", pname)

    return pname

# ------------------------------------------------------------------------

def launch_pangview(docx):

    ret = 0
    pname = get_pangview_path()

    if pname == "pangview.py":
        # we are running in pip
        arr =  ['pangview',  docx]
    else:
        arr = ["python", pname,  docx]

    if pedconfig.conf.verbose:
        print("Launching pangview:", arr) # pname, "with", docx)
    try:
        ret = subprocess.Popen(arr)
    except:
        print("except on pang",  sys.exc_info())
        pedync.message("\n   Cannot launch the pangview.py utility.   \n\n"
                       "              (Please install)\n")
    return ret

# It's totally optional to do this, you could just manually insert icons
# and have them not be themeable, especially if you never expect people
# to theme your app.

def register_stock_icons():
    ''' This function registers our custom toolbar icons, so they
        can be themed.
    '''
    items = [('demo-gtk-logo', '_GTK!', 0, 0, '')]
    # Register our stock items
    #Gtk.stock_add(items)

    # Add our custom icon factory to the list of defaults
    factory = Gtk.IconFactory()
    factory.add_default()

    img_dir = os.path.join(os.path.dirname(__file__), 'images')
    img_path = os.path.join(img_dir, 'gtk-logo-rgb.gif')

    #print( img_path)
    try:
        #pixbuf = Gdk.pixbuf_new_from_file(img_path)
        # Register icon to accompany stock item

        # The gtk-logo-rgb icon has a white background, make it transparent
        # the call is wrapped to (gboolean, guchar, guchar, guchar)
        #transparent = pixbuf.add_alpha(True, chr(255), chr(255),chr(255))
        #icon_set = Gtk.IconSet(transparent)
        #factory.add('demo-gtk-logo', icon_set)
        pass
    except GObject.GError as error:
        #print( 'failed to load GTK logo ... trying local')
        try:
            #img_path = os.path.join(img_dir, 'gtk-logo-rgb.gif')
            xbuf = Gdk.pixbuf_new_from_file('gtk-logo-rgb.gif')
            #Register icon to accompany stock item
            #The gtk-logo-rgb icon has a white background, make it transparent
            #the call is wrapped to (gboolean, guchar, guchar, guchar)
            transparent = xbuf.add_alpha(True, chr(255), chr(255),chr(255))
            icon_set = Gtk.IconSet(transparent)
            factory.add('demo-gtk-logo', icon_set)

        except GObject.GError as error:
            print('failed to load GTK logo for toolbar')


# ------------------------------------------------------------------------
# Utility functions for action handlers

def genstr(strx, num):
    ret = ""
    while num:
        ret += strx; num -= 1
    return ret

def cntleadchar(strx, chh):
    xlen = len(strx); pos = 0; ret = ""
    if xlen == 0: return ret
    while pos < xlen:
        if strx[pos] != chh:
            break
        ret += chh
        pos = pos + 1
    return ret

# Find next char
def nextchar(strx, xchar, start):
    idx = start; end =  len(strx) - 1
    while True:
        if idx > end: break
        chh = strx[idx]
        if chh == xchar: break
        idx += 1
    return idx

# Find next not char
def xnextchar( strx, xchar, start):
    idx = start; end =  len(strx) - 1
    while True:
        if idx > end: break
        chh = strx[idx]
        if chh != xchar:
            break
        idx += 1
    return idx

# Find next not in str
def xnextchar2( strx, xchar, start):
    idx = start; end =  len(strx) - 1
    while True:
        if idx > end: break
        chh = strx[idx]
        if xchar.find(chh) == -1:
            break
        idx += 1
    return idx

# Find prev char
def prevchar( strx, xchar, start):
    idx = start
    idx = min(len(strx) - 1, idx)
    while True:
        if idx < 0: break
        chh = strx[idx]
        if chh == xchar: break
        idx -= 1
    return idx

# Find prev not char
def xprevchar( strx, xchar, start):
    idx = start
    idx = min(len(strx) - 1, idx)
    while True:
        if idx < 0: break
        chh = strx[idx]
        if chh != xchar:
            break
        idx -= 1
    return idx

def shortenstr(xstr, xlen):
    ret = ""; zlen = len(xstr)
    if zlen > xlen:
        if xlen < 5: raise ValueError
        xlen -= 5
        ret = xstr[:xlen // 2] + "..." + xstr[zlen - xlen // 2:]
    else:
        ret = xstr

    return ret

def handle_keys(host, event):

    ret = 0

    # Do key down:
    if  event.type == Gdk.KEY_PRESS:
        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            #print( "Alt down")
            host.alt = True
        elif event.keyval == Gdk.KEY_Control_L or \
                event.keyval == Gdk.KEY_Control_R:
            #print( "Ctrl down")
            host.ctrl = True; ret = True
        if event.keyval == Gdk.KEY_Shift_L or \
              event.keyval == Gdk.KEY_Shift_R:
            #print( "shift down")
            host.shift = True

    # Do key up
    elif  event.type == Gdk.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            #print( "Alt up")
            host.alt = False
        if event.keyval == Gdk.KEY_Control_L or \
              event.keyval == Gdk.KEY_Control_R:
            #print( "Ctrl up")
            host.ctrl = False
        if event.keyval == Gdk.KEY_Shift_L or \
              event.keyval == Gdk.KEY_Shift_R:
            #print( "shift up")
            host.shift = False

    return ret

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

def  usleep(msec):

    if sys.version_info[0] < 3 or \
        (sys.version_info[0] == 3 and sys.version_info[1] < 3):
        timefunc = time.clock
    else:
        timefunc = time.process_time

    got_clock = timefunc() + float(msec) / 1000
    #print( got_clock)
    while True:
        if timefunc() > got_clock:
            break
        #print ("Sleeping")
        Gtk.main_iteration_do(False)

# -----------------------------------------------------------------------
# Create a one way hash of a name. Not cryptographically secure,
# but it can make a good unique name in hex.

def hash_name(strx):

    lenx = len(strx);  hashx = int(0)
    for aa in strx:
        bb = ord(aa)
        hashx +=  int((bb << 12) + bb)
        hashx &= 0xffffffff
        hashx = int(hashx << 8) + int(hashx >> 8)
        hashx &= 0xffffffff

    return "%x" % hashx

# Expand tabs in string
def untab_str(strx, tabstop = 4):
    res = ""; idx = 0; cnt = 0
    xlen = len(strx)
    while True:
        if idx >= xlen: break
        chh = strx[idx]
        if  chh == "\t":
            # Generate string
            spaces = tabstop - (cnt % tabstop)
            ttt = ""
            for aa in range(spaces):
                ttt += " "
            res += ttt
            cnt += spaces
        else:
            cnt += 1
            res += chh
        idx += 1
    return res

# Calculate tabs up to till count
def calc_tabs(strx, till, tabstop = 4):
    idx = 0; cnt = 0
    xlen = min(len(strx), till)
    while True:
        if idx >= xlen: break
        chh = strx[idx]
        if  chh == "\t":
            cnt += tabstop - (cnt % tabstop)
        else:
            cnt += 1
        idx += 1
    return cnt

# Calculate tabs up to till count, include full length
def calc_tabs2(strx, till, tabstop = 4):
    idx = 0; cnt = 0; slen = len(strx)
    xlen = min(slen, till)
    while True:
        if idx >= xlen: break
        chh = strx[idx]
        if  chh == "\t":
            cnt += tabstop - (cnt % tabstop)
        else:
            cnt += 1
        idx += 1

    # Pad full lengh
    if till > slen:
        cnt += till - slen
    return cnt

# -----------------------------------------------------------------------
# Untangle str pos from screen pos
# ----------oooooo--------
#                 ^
# ----------\t

def decalc_tabs(strx, pos, tabstop = 4):

    idx = cnt = 0; slen = len(strx)
    while True:
        if idx >= slen: break
        chh = strx[idx]
        if  chh == "\t":
            cnt += tabstop - (cnt % tabstop)
        else:
            cnt += 1
        if cnt >= pos: break
        idx += 1

    return idx

# Remove up to num leading spaces
def rmlspace(strx, num):
    idx = 0;    xlen = len(strx)
    while True:
        if idx >= xlen:  break
        if strx[idx] != " ": break
        if idx >= num: break
        idx += 1
    return strx[idx:]

# ------------------------------------------------------------------------
# Select word - Return tuple of begin and end index

def  selword(strx, xidx):

    #print( "selword:", strx, xidx)

    xlen = len(strx)
    if xlen == 0: return 0, 0
    if xidx >= xlen: return xlen, xlen

    if strx[xidx] == " ":
        return xidx, xidx

    cnte = xidx; cntb = xidx

    # Find space to end
    while True:
        if cnte >= xlen: break
        if strx[cnte] == " " or strx[cnte] == "\t":
            break
        cnte += 1
    # Find space to begin
    while True:
        if cntb < 0:
            cntb += 1
            break
        if strx[cntb] == " " or strx[cntb] == "\t":
            cntb += 1               # Already on space, back off
            break
        cntb -= 1

    return cntb, cnte

# ------------------------------------------------------------------------
# Select an ascii word - Return tuple of begin and end index

def  selasci(strx, xidx, additional = None):

    #print( "selasci:", "'" + strx + "'", xidx)

    xlen = len(strx)
    if xlen == 0: return 0, 0
    if xidx >= xlen: return xlen, xlen
    if strx[xidx] == " ":
        return xidx, xidx

    cnte = xidx; cntb = xidx

    # Find space to end
    while True:
        if cnte >= xlen:    break
        if not strx[cnte].isalnum():
            break
        cnte += 1
    # Find space to begin
    while True:
        if cntb < 0:
            cntb += 1
            break
        if not strx[cntb].isalnum():
            cntb += 1
            break
        cntb -= 1

    #print( cntb, cnte)
    #print(  "'" + strx[cntb:cnte] + "'")

    return cntb, cnte

# ------------------------------------------------------------------------
# Select an ascii word - Return tuple of begin and end index
# You may specify additional characters to see as part of the word

def  selasci2(strx, xidx, addi = ""):

    #print( "selasci2:", "'" + strx + "'", xidx)

    xlen = len(strx)
    if xlen == 0: return 0, 0
    if xidx >= xlen: return xlen, xlen
    if strx[xidx] == " ":
        if xidx:
            xidx -= 1
        if strx[xidx-1] == " ":
            return xidx, xidx

    cnte = xidx; cntb = xidx

    # Find space to end
    while True:
        if cnte >= xlen:  break
        if not strx[cnte].isalnum() and addi.find(strx[cnte]) < 0:
            break
        cnte += 1
    # Find space to begin
    while True:
        #print( cntb,)
        if cntb < 0:
            cntb += 1
            break

        if not strx[cntb].isalnum() and addi.find(strx[cntb]) < 0:
            cntb += 1
            break
        cntb -= 1

    #print( cntb, cnte)
    #print(  "'" + strx[cntb:cnte] + "'")

    return cntb, cnte

# ------------------------------------------------------------------------
# Convert tabs into apprporiate spaces:

'''def untab(strx):

    xlen = len(strx); cnt = 0; ret = ""

    while True:
        if cnt >= xlen: break
        chh = strx[cnt]
        if chh == "\t":
            ret += "    "
        else:
            ret += chh
        cnt += 1

    return ret'''

# Search one line, return array

def src_line(line, cnt, srctxt, regex, boolcase, boolregex):

    idx = 0; idx2 = 0
    mlen = len(srctxt)
    accum = []

    while True:
        if boolcase:
            idx = line.lower().find(srctxt.lower(), idx)
            idx2 = idx
        elif boolregex:
            line2 = line[idx:]
            #print( "line2", line2)
            if line2 == "":
                idx = -1
                break
            res = regex.search(line2)
            #print( res, res.start(), res.end())
            if res:
                idx = res.start() + idx
                # Null match, ignore it ('*' with zero length match)
                if res.end() == res.start():
                    #print( "null match", idx, res.start(), res.end())
                    # Proceed no matter what
                    if res.end() != 0:
                        idx = res.end() + 1
                    else:
                        idx += 1
                    continue

                idx2 = res.end() + idx
                mlen = res.end() - res.start()
                #print( "match", line2[res.start():res.end()])
            else:
                idx = -1
                break
        else:
            idx = line.find(srctxt, idx)
            idx2 = idx

        if  idx >= 0:
            line2 =  str(idx) + ":"  + str(cnt) +\
                     ":" + str(mlen) + " " + line
            accum.append(line2)
            idx = idx2 + 1
        else:
            break

    return accum

# Save session file

def done_sess_fc(win, resp, fc):

    #print  ("done_sess_fc", resp)
    # Back to original dir
    if resp == Gtk.ButtonsType.OK:
        try:
            fname = win.get_filename()
            if not fname:
                print("Must have filename")
            else:
                #print("Saving session file under:", fname)
                fh = open(fname, "wb")
                pickle.dump(fc.sesslist, fh)
                fh.close()
                pedconfig.conf.pedwin.os.add(fname)

        except:
            print("Cannot save session file", sys.exc_info())
    else:
        pass
        #print("Cancelled")

    os.chdir(os.path.dirname(fc.old))
    win.destroy()

# ------------------------------------------------------------------------
# Save session to file in the config dir

def save_sess(sesslist):

    fc = Gtk.FileChooserDialog(title="Save Session", transient_for=None, \
                            action=Gtk.FileChooserAction.SAVE)
    but =   "Cancel", Gtk.ButtonsType.CANCEL, "Save Session", Gtk.ButtonsType.OK
    fc.add_buttons(*but)

    filter2 = Gtk.FileFilter()
    filter2.add_pattern ("*.sess");  filter2.add_pattern ("*")

    fc.sesslist = sesslist
    fc.old = os.getcwd()
    fc.set_filter(filter2)
    fc.set_current_folder(pedconfig.conf.sess_dir)
    fc.set_current_name(os.path.basename("Untitled.sess"))
    fc.set_default_response(Gtk.ButtonsType.OK)
    fc.connect("response", done_sess_fc, fc)
    fc.run()

# ------------------------------------------------------------------------
# Load session file

def done_sess2_fc(win, resp, fc):

    #print  ("done_sess2_fc", resp)
    ddd = fc.old
    sesslist = []

    # Gather list of files
    if resp == Gtk.ButtonsType.OK:
        try:
            fname = win.get_filename()
            if not fname:
                print("Must have filename.")
            else:
                pedconfig.conf.pedwin.opensess(fname)
        except:
            print("Cannot load session file", sys.exc_info())
            pedync.message("Cannot load session file")
    else:
        pass
        #print("Cancelled")

    win.destroy()


# Load session from file in the config dir

def     load_sess():

    but =   "Cancel", Gtk.ButtonsType.CANCEL, "Load Session", Gtk.ButtonsType.OK
    fc = Gtk.FileChooserDialog(title="Load Session", transient_for=None, \
                        action=Gtk.FileChooserAction.OPEN)

    fc.add_button("Cancel", Gtk.ButtonsType.CANCEL)
    fc.add_button("Load Session", Gtk.ButtonsType.OK)

    filter = Gtk.FileFilter()
    filter.add_pattern ("*.sess")
    filter.add_pattern ("*")

    fc.old = os.getcwd()
    fc.set_filter(filter)
    fc.set_current_folder(pedconfig.conf.sess_dir)
    #fc.set_current_name(os.path.basename("Untitled.sess"))
    fc.set_default_response(Gtk.ButtonsType.OK)
    fc.connect("response", done_sess2_fc, fc)
    fc.run()

# ------------------------------------------------------------------------
# Open file dialog

def    _done_fcd(win, resp, fc):

    #print  ("_done_fcd", fc, resp)
    fc.resp = resp
    # Gather list of files
    if resp == Gtk.ButtonsType.OK:
        fc.fname = fc.get_filename()
        #print("OK")
    else:
        fc.fname = ""
        #print("Cancelled")

    # Back to original dir
    os.chdir(os.path.dirname(fc.old))
    fc.done = True

# ------------------------------------------------------------------------

def  getfilename(title = "Open File", save = False, oktext = "OK", filter = [], parent = None ):

    if save:
        fc = Gtk.FileChooserDialog(title, None, Gtk.FileChooserAction.SAVE)
    else:
        fc = Gtk.FileChooserDialog(title, None, Gtk.FileChooserAction.OPEN)

    but =   "Cancel", Gtk.ButtonsType.CANCEL, title, Gtk.ButtonsType.OK

    if not parent:
        fc.set_transient_for(fc.get_toplevel())
    else:
        fc.set_transient_for(parent.get_toplevel())

    fc.add_button("Cancel", Gtk.ButtonsType.CANCEL)
    fc.add_button(oktext, Gtk.ButtonsType.OK)

    filter2 = Gtk.FileFilter()
    for aa in filter:
        filter2.add_pattern (aa)
    filter2.add_pattern ("*")

    fc.old = os.getcwd()
    fc.set_filter(filter2)
    fc.set_current_folder(fc.old)
    #fc.set_current_name(os.path.basename("Untitled.sess"))
    fc.set_default_response(Gtk.ButtonsType.OK)
    fc.connect("response", _done_fcd, fc)
    fc.done = False
    fc.run()
    while 1:
        if fc.done:  break
        usleep(200)
    fname =  fc.fname
    fc.destroy()
    #print("resp", fc.resp, "fname", fc.fname)
    return  fname

# ------------------------------------------------------------------------
# Get am pm version of a number

def ampmstr(bb):

    dd = "AM"
    if bb == 12:
       dd = "PM"
    elif bb > 12:
        bb -= 12
        dd = "PM"

    return "%02d %s" % (bb, dd)


# Add the new line twice for more balaced string

allcr =    " " + "\r" + "\n" + \
            "\r" + "\n"

                   #string.punctuation +

allstr =    " " + \
            string.ascii_lowercase +  string.ascii_uppercase +  \
                string.digits

allasc =      string.ascii_lowercase +  string.ascii_uppercase +  \
                string.digits + "_"

alllett =      string.ascii_lowercase +  string.ascii_uppercase

# ------------------------------------------------------------------------
# Get random str

def randstr(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(allstr)-1)
        rr = allstr[ridx]
        strx += str(rr)

    return strx

def randasc(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(allasc)-1)
        rr = allasc[ridx]
        strx += str(rr)

    return strx

def randlett(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(alllett)-1)
        rr = alllett[ridx]
        strx += str(rr)

    return strx

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

    try:
        unichr
    except NameError:
        unichr = chr

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

        if chh == '\\':
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
    logfile = pedconfig.conf.log_dir + os.sep + logfname
    try:
        fp = open(logfile, "a+")
    except:
        try:
            fp = open(logfile, "w+")
            fp.seek(0, os.SEEK_END)
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
    logfile = pedconfig.conf.log_dir + os.sep + logfname
    try:
        fp = open(logfile, "a+")
    except:
        try:
            fp = open(logfile, "w+")
            fp.seek(0, os.SEEK_END)
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

    cumm = "Exception: " + xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                sss = aa[0].split(os.sep)
                cumm += "File: " + os.sep.join(sss[-3:]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())

    #put_debug(cumm)
    print(cumm)
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


def prompt_for_text(self2, message, fill):

    dialog = Gtk.Dialog(message,
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                   Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    dialog.set_transient_for(self2.mained.mywin)

    # Spacers
    label1 = Gtk.Label("   ");  label2 = Gtk.Label("   ")
    label3 = Gtk.Label("   ");  label4 = Gtk.Label("   ")
    label5 = Gtk.Label("   ");  label6 = Gtk.Label("   ")
    label7 = Gtk.Label("   ");  label8 = Gtk.Label("   ")

    entry = Gtk.Entry();

    entry.set_activates_default(True)

    if  self2.lastcmd == "":
        self2.lastcmd = pedconfig.conf.sql.get_str("lastcmd")
        if  self2.lastcmd == None:
            self2.lastcmd = ""

    entry.set_text(fill)
    entry.set_width_chars(24)
    dialog.vbox.pack_start(label4, 0, 0, 0)

    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, 0, 0, 0)
    hbox2.pack_start(entry, 0, 0, 0)
    hbox2.pack_start(label7, 0, 0, 0)
    dialog.vbox.pack_start(hbox2, 0, 0, 0)
    dialog.vbox.pack_start(label5, 0, 0, 0)

    hbox = Gtk.HBox()
    dialog.vbox.pack_start(hbox, 0, 0, 0)
    dialog.vbox.pack_start(label8, 0, 0, 0)

    dialog.show_all()
    response = dialog.run()
    gotxt = entry.get_text()
    dialog.destroy()

    if response != Gtk.ResponseType.ACCEPT:
        gotxt = ""

    return gotxt

# ------------------------------------------------------------------------
# Traditional (blocking) open file

class OpenFname():

    def __init__(self, mywin, filters = None):
        self.fc_done = False
        self.fc_code = 0
        self.fname = ""

        warnings.simplefilter("ignore")
        but =   "Cancel", Gtk.ButtonsType.CANCEL,\
         "Open File", Gtk.ButtonsType.OK
        self.fc = Gtk.FileChooserDialog("Open file", mywin, \
             Gtk.FileChooserAction.OPEN  \
            #Gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
            , but)
        warnings.simplefilter("default")

        if filters:
            for aa in filters:
                self.fc.add_filter(aa)

        self.fc.set_default_response(Gtk.ButtonsType.OK)
        self.fc.set_current_folder(os.getcwd())

        self.fc.connect("response", self._done_openfname)
        #self.fc.connect("current-folder-changed", self.folder_ch )
        #self.fc.set_current_name(self.fname)

    def run(self):
        try:
            self.fc.run()
        except:
            self.fc_done = True

        while True:
            if self.fc_done:
                break
            #time.sleep(.3)
            usleep(400)
        return self

    def _done_openfname(self, win, resp):
        #print "done_openfname", win, resp
        if resp == Gtk.ButtonsType.OK:
            fname = self.fc.get_filename()
            if not fname:
                #print "Must have filename"
                #self.update_statusbar("No filename specified")
                pass
            elif os.path.isdir(fname):
                #self.update_statusbar("Changed to %s" % fname)
                os.chdir(fname)
                self.fc.set_current_folder(fname)
                return
            else:
                #self.openfile(fname)
                self.fname = fname
                self.fc_code = True
        win.destroy()
        self.fc_done = True


# Arbitrary string to number

def atoi(strx):
    rtr=0
    for cc in strx:
        occ = ord(cc)
        if occ < ord('0') or occ > ord('9'):
            break
        rtr = rtr*10 + (occ - ord('0'))

    return rtr


class HeadDialog(Gtk.Dialog):

    def __init__(self, initstr, parent = None):
        Gtk.Dialog.__init__(
            self, title="Name for Note", transient_for=parent, modal=True,
        )
        self.add_buttons(
            Gtk.STOCK_OK,
            Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
        )
        self.set_default_response(Gtk.ResponseType.OK)

        box = self.get_content_area()
        label = Gtk.Label(label="        ")
        box.add(label)

        self.entry = Gtk.Entry()
        self.entry.set_text(initstr)
        self.entry.set_activates_default(True)

        self.hbox = Gtk.HBox()
        self.hbox.pack_start(Gtk.Label(label="   Note Header:  "), 0, 0, 0)
        self.hbox.pack_start(self.entry, 1, 1, 0)
        self.hbox.pack_start(Gtk.Label(label="                 "), 0, 0, 0)

        box.add(self.hbox)
        self.show_all()

class SearchDialog(Gtk.Dialog):

    def __init__(self, parent = None):
        Gtk.Dialog.__init__(
            self, title=" Search ", transient_for=parent, modal=True,
        )
        self.add_buttons(
            Gtk.STOCK_FIND,
            Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
        )
        self.set_default_response(Gtk.ResponseType.OK)
        box = self.get_content_area()

        #label = Gtk.Label(label="  Enter text you want to search for:  ")
        label = Gtk.Label(label="   ")
        box.add(label)

        self.hbox = Gtk.HBox()
        self.hbox.pack_start(Gtk.Label(label="   Search for:  "), 0, 0, 0)
        self.entry = Gtk.Entry()
        self.entry.set_activates_default(True)
        self.hbox.pack_start(self.entry, 1, 1, 0)
        self.hbox.pack_start(Gtk.Label(label="            "), 0, 0, 0)

        box.add(self.hbox)

        #box.add(self.entry)
        self.show_all()

# EOF
