#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import signal, os, time, sys, pickle, subprocess

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

#import pedwin
from . import pedconfig
from . import pedync

# Cut leading space in half

def cut_lead_space(xstr, divi = 2):
    res = ""; cnt = 0; idx = 0; spcnt = 0
    xlen = len(xstr);
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

def     readfile(strx, sep = None):

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
        bb = aa.replace("\r", "");
        cc = bb.replace("\n", "");
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
            print("except",  sys.exc_info())

        if cnt > 3:
            #print ("Not a text file:", ffff)
            return rrr
    except:
        print("Cannot read file", ffff);
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

def  writefile(strx, buff, sep = "\n"):
    #print ("writefile", strx, sep)
    ret = True, ""
    if strx != "":
        try:
            f = open(strx, "w")
            for aa in buff:
                f.write(aa.rstrip() + sep)
            f.close()
        except:
            ret = False, sys.exc_info()[1]
            pass
    return ret

# Expand image name to image path:

def get_img_path(fname):

    img_dir = os.path.dirname(__file__)
    img_dir2 = os.path.join(img_dir, "images")
    img_path = os.path.join(img_dir2, fname)

    if(pedconfig.conf.verbose):
        print( "img_path", img_path)

    return img_path

# Expand file name to file path in the exec dir:
# We now deliver module data directory

def get_exec_path(fname):

    #exec_dir = os.path.dirname(pedconfig.conf.mydir)
    exec_dir = os.path.dirname(__file__)

    exec_path2 = os.path.join(exec_dir, "data")
    exec_path = os.path.join(exec_path2, fname)

    if(pedconfig.conf.verbose):
        print( exec_path)

    return exec_path

def get_pangview_path():

    fname = "pangview.py"
    pname = get_exec_path(".." +  os.sep +  ".." + os.sep + fname)
    if not os.path.isfile(pname):
        pname = fname

    return pname

# ------------------------------------------------------------------------

def launch_pangview(docx):

    pname = get_pangview_path()

    if(pedconfig.conf.verbose):
        print("launching pangview:", pname, "with", docx)
    try:
        ret = subprocess.Popen([pname,  docx])

    except:
        print("except on pang",  sys.exc_info())
        pedync.message("\n   Cannot launch the pangview.py utility.   \n\n"
                       "              (Please install)\n")


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
            transparent = pixbuf.add_alpha(True, chr(255), chr(255),chr(255))
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
    idx = start;
    idx = min(len(strx) - 1, idx)
    while True:
        if idx < 0: break
        chh = strx[idx]
        if chh == xchar: break
        idx -= 1
    return idx

# Find prev not char
def xprevchar( strx, xchar, start):
    idx = start;
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
    if(zlen > xlen):
        if xlen < 5: raise Valuerror;
        xlen -= 5
        ret = xstr[:xlen / 2] + "..." + xstr[zlen - xlen / 2:]
    else:
        ret = xstr

    return ret

def handle_keys(host):

    # Do key down:
    if  event.type == Gdk.KEY_PRESS:
        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            #print( "Alt down")
            host.alt = True;
        elif event.keyval == Gdk.KEY_Control_L or \
                event.keyval == Gdk.KEY_Control_R:
            #print( "Ctrl down")
            self.ctrl = True; ret = True
        if event.keyval == Gdk.KEY_Shift_L or \
              event.keyval == Gdk.KEY_Shift_R:
            #print( "shift down")
            host.shift = True;

    # Do key up
    elif  event.type == Gdk.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            #print( "Alt up")
            host.alt = False;
        if event.keyval == Gdk.KEY_Control_L or \
              event.keyval == Gdk.KEY_Control_R:
            #print( "Ctrl up")
            host.ctrl = False;
        if event.keyval == Gdk.KEY_Shift_L or \
              event.keyval == Gdk.KEY_Shift_R:
            #print( "shift up")
            host.shift = False;

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

def  usleep(msec):

    got_clock = time.clock() + float(msec) / 1000
    #print( got_clock)
    while True:
        if time.clock() > got_clock:
            break
        #print ("Sleeping")
        Gtk.main_iteration_do(False)

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
            ttt = "";
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
    xlen = min(len(strx), till);
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
    xlen = min(slen, till);
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

    xlen = len(strx);
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

    xlen = len(strx);
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

    xlen = len(strx);
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

    idx = 0; idx2 = 0;
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

    but =   "Cancel", Gtk.ButtonsType.CANCEL, "Save Session", Gtk.ButtonsType.OK
    fc = Gtk.FileChooserDialog("Save Session", None, Gtk.FileChooserAction.SAVE, \
        but)

    filter = Gtk.FileFilter()
    filter.add_pattern ("*.sess");  filter.add_pattern ("*");

    fc.sesslist = sesslist
    fc.old = os.getcwd()
    fc.set_filter(filter)
    fc.set_current_folder(pedconfig.conf.sess_data)
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
                print("Must have filename")
            else:
                #print("Loading session file under:", fname)
                fh = open(fname, "rb")
                try:
                    sesslist = pickle.load(fh)
                except:
                    pass
                fh.close()
        except:
            print("Cannot load session file", sys.exc_info())
            pedync.message("Cannot load session file")
    else:
        pass
        #print("Cancelled")

    win.destroy()

    if sys.version_info.major < 3:
        sesslist =  sesslist.decode(decode('UTF-8'))

    for fff in sesslist.split("\n"):
        #print ("Session opening file:", "'" + fff + "'")
        if fff != "":
            pedconfig.conf.pedwin.openfile(fff)
            usleep(30)

    # Back to original dir
    #os.chdir(os.path.dirname(fc.old))

# Load session from file in the config dir

def     load_sess():

    but =   "Cancel", Gtk.ButtonsType.CANCEL, "Load Session", Gtk.ButtonsType.OK
    fc = Gtk.FileChooserDialog("Load Session", None, Gtk.FileChooserAction.OPEN)

    fc.add_button("Cancel", Gtk.ButtonsType.CANCEL)
    fc.add_button("Load Session", Gtk.ButtonsType.OK)

    filter = Gtk.FileFilter()
    filter.add_pattern ("*.sess");
    filter.add_pattern ("*");

    fc.old = os.getcwd()
    fc.set_filter(filter)
    fc.set_current_folder(pedconfig.conf.sess_data)
    #fc.set_current_name(os.path.basename("Untitled.sess"))
    fc.set_default_response(Gtk.ButtonsType.OK)
    fc.connect("response", done_sess2_fc, fc)
    fc.run()

# ------------------------------------------------------------------------

# EOF


















