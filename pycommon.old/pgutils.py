#!/usr/bin/python

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, string, fnmatch, math, warnings
import random, time, subprocess, traceback, glob, stat

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
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

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


testmode = 0

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed
#
#def  usleep2(msec):
#
#    got_clock = time.clock() + float(msec) / 1000
#    #print( got_clock)
#    while True:
#        if time.clock() > got_clock:
#            break
#        #print ("Sleeping")
#        Gtk.main_iteration_do(False)
#

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

def  usleep2(msec):

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
# Pull up a message box

def message2(strx, title = "Dialog", parent=None):

        dialog = Gtk.MessageDialog()

        # Close dialog on user response
        dialog.add_button("Close", Gtk.ButtonsType.CLOSE)

        if title:
            dialog.set_title(title)

        #box = dialog.get_content_area()
        #box.add(Gtk.Label(strx))

        dialog.set_markup(strx)

        if parent:
            dialog.set_transient_for(parent)

        dialog.connect ("response", lambda d, r: d.destroy())
        dialog.show_all()


def yes_no2(message, title = "Question", parent=None):

        dialog = Gtk.MessageDialog()

        if title:
            dialog.set_title(title)

        dialog.add_button("_Yes", Gtk.ResponseType.YES)
        dialog.add_button("_No", Gtk.ResponseType.NO)

        dialog.set_markup(message)

        img = Gtk.Image.new_from_stock(Gtk.STOCK_DIALOG_QUESTION, Gtk.IconSize.DIALOG)
        dialog.set_image(img)

        if parent:
            dialog.set_transient_for(parent)

        dialog.connect("key-press-event", yn_key, 0)

        #dialog.connect ("response", lambda d, r: d.destroy())

        dialog.show_all()
        response = dialog.run()
        dialog.destroy()

        return response

# ------------------------------------------------------------------------
# Do dialog

def yes_no_cancel2(message, title = "Question", cancel = True, parent=None):

    warnings.simplefilter("ignore")

    dialog = Gtk.Dialog(title,
                   None,
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)

    dialog.set_default_response(Gtk.ResponseType.YES)
    dialog.set_position(Gtk.WindowPosition.CENTER)
    #dialog.set_transient_for(pedconfig.conf.pedwin.mywin)

    sp = "     "
    label = Gtk.Label(message);
    label2 = Gtk.Label(sp);      label3 = Gtk.Label(sp)
    label2a = Gtk.Label(sp);     label3a = Gtk.Label(sp)

    hbox = Gtk.HBox() ;

    hbox.pack_start(label2, 0, 0, 0);
    hbox.pack_start(label, 1, 1, 0);
    hbox.pack_start(label3, 0, 0, 0)

    dialog.vbox.pack_start(label2a, 0, 0, 0);
    dialog.vbox.pack_start(hbox, 0, 0, 0)
    dialog.vbox.pack_start(label3a, 0, 0, 0);

    dialog.add_button("_Yes", Gtk.ResponseType.YES)
    dialog.add_button("_No", Gtk.ResponseType.NO)

    if cancel:
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)

    dialog.connect("key-press-event", _yn_key, cancel)
    #dialog.connect("key-release-event", _yn_key, cancel)
    warnings.simplefilter("default")

    dialog.show_all()
    response = dialog.run()

    # Convert all responses to cancel
    if  response == Gtk.ResponseType.CANCEL or \
            response == Gtk.ResponseType.REJECT or \
                response == Gtk.ResponseType.CLOSE  or \
                    response == Gtk.ResponseType.DELETE_EVENT:
        response = Gtk.ResponseType.CANCEL

    dialog.destroy()

    #print("YNC result:", response);
    return  response

def _yn_key(win, event, cancel):
    #print event
    if event.keyval == Gdk.KEY_y or \
        event.keyval == Gdk.KEY_Y:
        win.response(Gtk.ResponseType.YES)

    if event.keyval == Gdk.KEY_n or \
        event.keyval == Gdk.KEY_N:
        win.response(Gtk.ResponseType.NO)

    if cancel:
        if event.keyval == Gdk.KEY_c or \
            event.keyval == Gdk.KEY_C:
            win.response(Gtk.ResponseType.CANCEL)

# ------------------------------------------------------------------------
# Resolve path name

def respath(fname):

    try:
        ppp = str.split(os.environ['PATH'], os.pathsep)
        for aa in ppp:
            ttt = aa + os.sep + fname
            if os.path.isfile(str(ttt)):
                return ttt
    except:
        print ("Cannot resolve path", fname, sys.exc_info())
    return None

# ------------------------------------------------------------------------
# Random colors

def randcol():
    return random.randint(0, 255)

# ------------------------------------------------------------------------
# Color conversions

def str2col(strx):
    ccc = str2float(strx)
    return float2col(ccc)

def str2float( col):
    return ( float(int(col[1:3], base=16)) / 256,
                    float(int(col[3:5], base=16)) / 256, \
                        float(int(col[5:7], base=16)) / 256 )

def float2col(col):
    aa = min(col[0], 1.)
    bb = min(col[1], 1.)
    cc = min(col[2], 1.)
    return Gdk.Color(aa * 65535, bb * 65535, cc * 65535)

def float2str(col):
    aa = min(col[0], 1.)
    bb = min(col[1], 1.)
    cc = min(col[2], 1.)
    strx = "#%02x%02x%02x" % (aa * 256,  \
                        bb * 256, cc * 256)
    return strx

def col2float(col):
    rrr = [float(col.red) / 65535,
            float(col.green) / 65535,
                float(col.blue) / 65535]
    return rrr

def rgb2str(icol):
    strx = "#%02x%02x%02x" % (int(icol.red) & 0xff,  \
                        int(icol.green) & 0xff, int(icol.blue) & 0xff)
    return strx

def col2str(icol):
    strx = "#%02x%02x%02x" % (int(icol.red / 255),  \
                        int(icol.green / 255), int(icol.blue / 255))
    return strx

def rgb2col(icol):
    #print "rgb2col", icol
    col = [0, 0, 0]
    col[0] = float(icol.red) / 256
    col[1] = float(icol.green) / 256
    col[2] = float(icol.blue) / 256
    return col

def put_debug2(xstr):
    try:
        if os.isatty(sys.stdout.fileno()):
            print( xstr)
        else:
            #syslog.syslog(xstr)
            pass
            print(xstr, file=sys.stderr)

    except:
        print( "Failed on debug output.")
        print( sys.exc_info())

def put_exception_old(xstr):

    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        "  Line: " + str(aa[1]) + "\n" +  \
                        "    Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())

    put_debug2(cumm)
    #syslog.syslog("%s %s %s" % (xstr, a, b))

def decode_bits(numx):
    mask = 0x80
    retx = ""
    for aa in range(8):
        strx = "0"
        if numx & mask:
            strx = "1"
        retx += "B%d=%s  " % (7-aa, strx)
        if aa == 3:
            retx += "\r"
        mask >>= 1

    return retx

def randcolstr(start = 0, endd = 255):
    rr =  random.randint(start, endd)
    gg =  random.randint(start, endd)
    bb =  random.randint(start, endd)
    strx = "#%02x%02x%02x" % (rr, gg, bb)
    return strx

# ------------------------------------------------------------------------
# Remove non printables

def clean_str(strx):

    stry = ""
    for aa in range(len(strx)):
        if strx[aa] == '\r':
            stry += "\\r"
        elif strx[aa] == '\n':
            stry += "\\n"
        elif strx[aa] == '\0':
            stry += "\\0"
        else:
            stry += strx[aa]
    return stry

def clean_str2(strx):
    stry = ""
    skip = False
    for aa in range(len(strx)):
        if skip:
            skip = False;
            continue
        if strx[aa] == '\\' and strx[aa+1] == 'r':
            skip = True
        if strx[aa] == '\\' and strx[aa+1] == 'n':
            skip = True
        if strx[aa] == '\\' and strx[aa+1] == '0':
            skip = True
            pass
        else:
            stry += strx[aa]
    return stry

# This is crafted to Py2 so has clock with the same name

start_time = time.clock()

def  get_time():

    global start_time
    if sys.version_info.major < 3:
        return time.clock()  - start_time
    else:
        return time.process_time()

def get_realtime():

    frac = math.modf(float(get_time()))
    zzz = "%.02f" % frac[0]
    sss = "%s%s" % (time.strftime("%02I:%02M:%02S"), zzz[1:])
    return sss

# Get a list of ports

'''
def serial_ports():

    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """

    ports = []
    if sys.platform.startswith('win'):
        ports2 = serial.tools.list_ports.comports()
        for aa in ports2:
            ports.append(aa[0])
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/ttyU[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        # rely on serial module
        ports2 = serial.tools.list_ports.comports()
        for aa in ports2:
            ports.append(aa[0])
        #raise EnvironmentError('Unsupported platform')

    #print ("ports", ports)
    result = []
    for port in ports:
        try:
            # no testing performed any more
            #s = serial.Serial(port)
            #s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    #print ("result", result)
    return result
'''

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


'''
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
'''

def put_exception2_old(xstr):

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

    put_debug2(cumm)
    #syslog.syslog("%s %s %s" % (xstr, a, b))

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


if __name__ == '__main__':
    print("This file was not meant to run directly")

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
        bb = aa.replace("\r", "");
        cc = bb.replace("\n", "");
        text.append(cc)
    #text2 = []

    return text

# ------------------------------------------------------------------------
# Handle command line. Interpret optarray and decorate the class
# This allows a lot of sub utils to have a common set of options.

class Config:

    def __init__(self, optarr):
        self.optarr = optarr
        self.verbose = False
        self.debug = False

    def comline(self, argv):
        optletters = ""
        for aa in self.optarr:
            optletters += aa[0]
        #print( optletters    )
        # Create defaults:
        err = 0
        for bb in range(len(self.optarr)):
            if self.optarr[bb][1]:
                # Coerse type
                if type(self.optarr[bb][2]) == type(0):
                    self.__dict__[self.optarr[bb][1]] = int(self.optarr[bb][2])
                if type(self.optarr[bb][2]) == type(""):
                    self.__dict__[self.optarr[bb][1]] = str(self.optarr[bb][2])
        try:
            opts, args = getopt.getopt(argv, optletters)
        #except getopt.GetoptError, err:
        except:
            print( "Invalid option(s) on command line:", err)
            #support.put_exception("comline")
            return ()

        #print( "opts", opts, "args", args)
        for aa in opts:
            for bb in range(len(self.optarr)):
                if aa[0][1] == self.optarr[bb][0][0]:
                    #print( "match", aa, self.optarr[bb])
                    if len(self.optarr[bb][0]) > 1:
                        #print( "arg", self.optarr[bb][1], aa[1])
                        if self.optarr[bb][2] != None:
                            if type(self.optarr[bb][2]) == type(0):
                                self.__dict__[self.optarr[bb][1]] = int(aa[1])
                            if type(self.optarr[bb][2]) == type(""):
                                self.__dict__[self.optarr[bb][1]] = str(aa[1])
                    else:
                        #print( "set", self.optarr[bb][1], self.optarr[bb][2])
                        if self.optarr[bb][2] != None:
                            self.__dict__[self.optarr[bb][1]] = 1
                        #print( "call", self.optarr[bb][3])
                        if self.optarr[bb][3] != None:
                            self.optarr[bb][3]()
        return args

# ------------------------------------------------------------------------

def yes_no_cancel(title, message, cancel = True):

    warnings.simplefilter("ignore")

    dialog = Gtk.Dialog(title,
                   None,
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)

    dialog.set_default_response(Gtk.ResponseType.YES)
    dialog.set_position(Gtk.WindowPosition.CENTER)
    #dialog.set_transient_for(pedconfig.conf.pedwin.mywin)

    sp = "     "
    label = Gtk.Label(message);
    label2 = Gtk.Label(sp);      label3 = Gtk.Label(sp)
    label2a = Gtk.Label(sp);     label3a = Gtk.Label(sp)

    hbox = Gtk.HBox() ;

    hbox.pack_start(label2, 0, 0, 0);
    hbox.pack_start(label, 1, 1, 0);
    hbox.pack_start(label3, 0, 0, 0)

    dialog.vbox.pack_start(label2a, 0, 0, 0);
    dialog.vbox.pack_start(hbox, 0, 0, 0)
    dialog.vbox.pack_start(label3a, 0, 0, 0);

    dialog.add_button("_Yes", Gtk.ResponseType.YES)
    dialog.add_button("_No", Gtk.ResponseType.NO)

    if cancel:
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)

    dialog.connect("key-press-event", _yn_key, cancel)
    #dialog.connect("key-release-event", _yn_key, cancel)
    warnings.simplefilter("default")

    dialog.show_all()
    response = dialog.run()

    # Convert all responses to cancel
    if  response == Gtk.ResponseType.CANCEL or \
            response == Gtk.ResponseType.REJECT or \
                response == Gtk.ResponseType.CLOSE  or \
                    response == Gtk.ResponseType.DELETE_EVENT:
        response = Gtk.ResponseType.CANCEL

    dialog.destroy()

    #print("YNC result:", response);
    return  response

def _yn_key(win, event, cancel):
    #print event
    if event.keyval == Gdk.KEY_y or \
        event.keyval == Gdk.KEY_Y:
        win.response(Gtk.ResponseType.YES)

    if event.keyval == Gdk.KEY_n or \
        event.keyval == Gdk.KEY_N:
        win.response(Gtk.ResponseType.NO)

    if cancel:
        if event.keyval == Gdk.KEY_c or \
            event.keyval == Gdk.KEY_C:
            win.response(Gtk.ResponseType.CANCEL)

# ------------------------------------------------------------------------
# Show About dialog:

import platform

def  about(self2):

    dialog = Gtk.AboutDialog()
    dialog.set_name(pedconfig.conf.progname +  " - Python Editor ")

    dialog.set_version(str(pedconfig.conf.version));
    gver = (Gtk.get_major_version(), \
                        Gtk.get_minor_version(), \
                            Gtk.get_micro_version())

    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_transient_for(pedconfig.conf.pedwin.mywin)

    #"\nRunning PyGObject %d.%d.%d" % GObject.pygobject_version +\

    ddd = os.path.join(os.path.dirname(__file__), "../")

    # GLib.pyglib_version
    vvv = gi.version_info
    comm = "Python based easily configurable editor\n"\
        "with time accounting module, spell "\
        "check \n and macro recording.\n"\
        "\nRunning PyGtk %d.%d.%d" % vvv +\
        "\non GTK %d.%d.%d\n" % gver +\
        "\nRunning Python %s" % platform.python_version() +\
        "\non %s %s\n" % (platform.system(), platform.release()) +\
        "\nPyedPro Build Date: %s\n" % pedconfig.conf.build_date +\
        "Exe Path:\n%s\n" % os.path.realpath(ddd)

    dialog.set_comments(comm);
    dialog.set_copyright(pedconfig.conf.progname + " Created by Peter Glen.\n"
                          "Project is in the Public Domain.")
    dialog.set_program_name(pedconfig.conf.progname)
    img_dir = os.path.join(os.path.dirname(__file__), 'images')
    #img_path = os.path.join(img_dir, 'gtk-logo-rgb.gif')
    img_path = os.path.join(img_dir, 'pyedpro.png')

    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(img_path)
        #print "loaded pixbuf"
        dialog.set_logo(pixbuf)

    except:
        print("Cannot load logo for about dialog", img_path);
        print(sys.exc_info())

    #dialog.set_website("")

    ## Close dialog on user response
    dialog.connect ("response", lambda d, r: d.destroy())
    dialog.connect("key-press-event", about_key)

    dialog.show()

def about_key(win, event):
    #print "about_key", event
    if  event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
            if event.state & Gdk.ModifierType.MOD1_MASK:
                win.destroy()

# ------------------------------------------------------------------------
# Show a regular message:

def message(strx, title = None):

    #print("called: message()", strx)

    icon = Gtk.STOCK_INFO
    dialog = Gtk.MessageDialog(buttons=Gtk.ButtonsType.CLOSE,
                               message_type=Gtk.MessageType.INFO)

    dialog.props.text = strx

    #dialog.set_transient_for()

    if title:
        dialog.set_title(title)
    else:
        dialog.set_title("PyEdPro")

    dialog.set_position(Gtk.WindowPosition.CENTER)

    # Close dialog on user response
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.show()
    dialog.run()

# EOF


