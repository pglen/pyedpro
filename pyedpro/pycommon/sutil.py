#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import print_function

import sys, traceback, os, time, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

disp = Gdk.Display.get_default()
scr = disp.get_default_screen()

#print( "num_mon",  scr.get_n_monitors()    )
#for aa in range(scr.get_n_monitors()):
#    print( "mon", aa, scr.get_monitor_geometry(aa);)

# ------------------------------------------------------------------------
# Get current screen (monitor) width and height

def get_screen_wh():

    ptr = disp.get_pointer()
    mon = scr.get_monitor_at_point(ptr[1], ptr[2])
    geo = scr.get_monitor_geometry(mon)
    www = geo.width; hhh = geo.height
    if www == 0 or hhh == 0:
        www = Gdk.get_screen_width();
        hhh = Gdk.get_screen_height();
    return www, hhh

# ------------------------------------------------------------------------
# Get current screen (monitor) upper left corner xx / yy

def get_screen_xy():

    ptr = disp.get_pointer()
    mon = scr.get_monitor_at_point(ptr[1], ptr[2])
    geo = scr.get_monitor_geometry(mon)
    return geo.x, geo.y

# ------------------------------------------------------------------------
# Print( an exception as the system would print it)

def print_exception(xstr):
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
            print("Could not print trace stack. ", sys.exc_info())
    print( cumm)


# ------------------------------------------------------------------------
# Show a regular message:

def message(strx, parent = None, title = None, icon = Gtk.MessageType.INFO):

    dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
        icon, Gtk.ButtonsType.CLOSE, strx)

    dialog.set_modal(True)

    if title:
        dialog.set_title(title)
    else:
        dialog.set_title("DBGui Message")

    # Close dialog on user response
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.show()


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


# ------------------------------------------------------------------------
# Create temporary file, return name. Empty string ("") if error.

def tmpname(indir, template):

    fname = ""
    if not os.access(indir, os.W_OK):
        print( "Cannot access ", indir)
        return fname

    cnt = 1;
    while True:
        tmp = indir + "/" + template + "_" + str(cnt)
        if not os.access(tmp, os.R_OK):
            fname = tmp
            break
        # Safety valve
        if cnt > 10000:
            break
    return fname

# ------------------------------------------------------------------------
# Execute man loop

def mainloop():
    while True:
        ev = Gdk.event_peek()
        #print( ev)
        if ev:
            if ev.type == Gdk.EventType.DELETE:
                break
            if ev.type == Gdk.EventType.UNMAP:
                break
        if Gtk.main_iteration_do(True):
            break

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream

   def write(self, data):
       self.stream.write(data)
       self.stream.flush()

   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()

   def __getattr__(self, attr):
       return getattr(self.stream, attr)

# Time to str and str to time

def time_n2s(ttt):
    sss = time.ctime(ttt)
    return sss

def time_s2n(sss):
    rrr = time.strptime(sss)
    ttt = time.mktime(rrr)
    return ttt

def yes_no_cancel(title, message, cancel = True, parent = None):

    #warnings.simplefilter("ignore")
    dialog = Gtk.Dialog(title,
                   None,
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)


    dialog.set_default_response(Gtk.ResponseType.YES)
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_transient_for(parent)

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

    dialog.connect("key-press-event", yn_key, cancel)
    #dialog.connect("key-release-event", yn_key, cancel)
    #warnings.simplefilter("default")

    dialog.show_all()
    response = dialog.run()
    # Convert all responses to cancel
    if  response == Gtk.ResponseType.CANCEL or \
        response == Gtk.ResponseType.REJECT or \
        response == Gtk.ResponseType.CLOSE  or \
        response == Gtk.ResponseType.DELETE_EVENT:
        response = Gtk.ResponseType.CANCEL
    dialog.destroy()

    return  response

def yn_key(win, event, cancel):
    #print( event)
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

def opendialog(parent=None):

    # We create an array, so it is passed around by reference
    fname = [""]

    def makefilter(mask, name):
        filter =  Gtk.FileFilter.new()
        filter.add_pattern(mask)
        filter.set_name(name)
        return filter

    def done_open_fc(win, resp, fname):
        #print "done_open_fc", win, resp
        if resp == Gtk.ButtonsType.OK:
            fname[0] = win.get_filename()
            if not fname[0]:
                #print "Must have filename"
                pass
            elif os.path.isdir(fname[0]):
                os.chdir(fname[0])
                win.set_current_folder(fname[0])
                return
            else:
                #print("OFD", fname[0])
                pass
        win.destroy()

    but =   "Cancel", Gtk.ButtonsType.CANCEL,\
            "Open File", Gtk.ButtonsType.OK

    fc = Gtk.FileChooserDialog("Open file", parent, \
         Gtk.FileChooserAction.OPEN  \
        , but)

    filters = []
    filters.append(makefilter("*.mup", "MarkUp files (*.py)"))
    filters.append(makefilter("*.*", "All files (*.*)"))

    if filters:
        for aa in filters:
            fc.add_filter(aa)

    fc.set_default_response(Gtk.ButtonsType.OK)
    fc.set_current_folder(os.getcwd())
    fc.connect("response", done_open_fc, fname)
    #fc.connect("current-folder-changed", self.folder_ch )
    #fc.set_current_name(self.fname)
    fc.run()
    #print("OFD2", fname[0])
    return fname[0]

def savedialog(resp):

    #print "File dialog"
    fname = [""]   # So it is passed around as a reference

    def makefilter(mask, name):
        filter =  Gtk.FileFilter.new()
        filter.add_pattern(mask)
        filter.set_name(name)
        return filter

    def done_fc(win, resp, fname):
        #print( "done_fc", win, resp)
        if resp == Gtk.ResponseType.OK:
            fname[0] = win.get_filename()
            if not fname[0]:
                print("Must have filename")
            else:
                pass
        win.destroy()

    but =   "Cancel", Gtk.ResponseType.CANCEL,   \
                    "Save File", Gtk.ResponseType.OK
    fc = Gtk.FileChooserDialog("Save file as ... ", None,
            Gtk.FileChooserAction.SAVE, but)

    #fc.set_do_overwrite_confirmation(True)

    filters = []
    filters.append(makefilter("*.mup", "MarkUp files (*.py)"))
    filters.append(makefilter("*.*", "All files (*.*)"))

    if filters:
        for aa in filters:
            fc.add_filter(aa)

    fc.set_current_name(os.path.basename(fname[0]))
    fc.set_current_folder(os.path.dirname(fname[0]))
    fc.set_default_response(Gtk.ResponseType.OK)
    fc.connect("response", done_fc, fname)
    fc.run()
    return fname[0]

# EOF
