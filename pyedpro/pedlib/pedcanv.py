#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, math, pickle

#from six.moves import range

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import cairo

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from pedlib import pedconfig
from pedlib import pedcolor

# Into our name space
from    pedlib.pedmenu import *
from    pedlib.pedui import *
from    pedlib.pedcolor import *
from    pedlib.pedtdlg import *
from    pedlib.pedobjs import *
from    pedlib.pedutil import *
from    pedlib.pedofd import *

#sys.path.append('..' + os.sep + "pyvguicom")
from pyvguicom.pggui import *

canv_testmode = 0

def canv_colsel(oldcol, title):

    csd = Gtk.ColorSelectionDialog(title)
    col = csd.get_color_selection()
    #col.set_current_color(float2col(oldcol))
    response = csd.run()
    color = 0
    if response == Gtk.ResponseType.OK:
        color = col.get_current_color()
        #print ("color", color)
    csd.destroy()
    return col2float(color)

#class ToolBox(Gtk.Toolbar):
#class ToolBox(Gtk.Window):
class ToolBox(Gtk.VBox):

    def __init__(self, callb, parent):
        #Gtk.Window.__init__(self, Gtk.WindowType.POPUP)
        #Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)
        #Gtk.Toolbar.__init__(self)
        super(ToolBox, self).__init__()

        #self.set_size_request(10, 10)
        #self.set_default_size(10, 10)
        #self.set_keep_above(True)
        #self.set_decorated(False)

        self.drag = False
        self.dragpos = (0, 0)
        self.callb = callb
        self.opacity = 1

        self.connect("button-press-event", self.area_button)
        self.connect("button-release-event", self.area_button_rel)
        self.connect("motion-notify-event", self.area_motion)

        vbox = Gtk.VBox()

        self.labelm = Gtk.Label(label=" - ")
        self.labelx = Gtk.Label(label=" x ")
        self.toolt = Gtk.Label(label="Main Toolbox")

        self.hboxt = Gtk.HBox()
        self.hboxt.pack_start(self.labelm, 0, 0, 0)
        self.hboxt.pack_start(self.toolt, 1, 1, 0)
        self.hboxt.pack_start(self.labelx, 0, 0, 0)

        self.hbox = Gtk.HBox()
        tarr = ((Gtk.STOCK_OPEN, "Open"), (Gtk.STOCK_SAVE, "Save"),
                    (Gtk.STOCK_COPY, "Copy"), (Gtk.STOCK_PASTE, "Paste"),
                    (Gtk.STOCK_NO, "None"), (Gtk.STOCK_CLEAR, "Clear"),
                    (Gtk.STOCK_DELETE, "Delete"), (Gtk.STOCK_PROPERTIES , "Proerties"),
                     )
        cnt = 0
        for aa in tarr:
            butt = Gtk.ToolButton().new_from_stock(aa[0])
            butt.set_tooltip_text(aa[1])
            butt.connect("clicked", self.callb, cnt)
            cnt += 1
            self.hbox.add(butt)

        self.hbox2 = Gtk.HBox()
        tarr2 = ( (Gtk.STOCK_UNDO, "Undo"), (Gtk.STOCK_REDO, "Redo"),
                    (Gtk.STOCK_COLOR_PICKER, "Color"), (Gtk.STOCK_YES , "yes?"),
                    (Gtk.STOCK_SELECT_ALL , "SelAll"), (Gtk.STOCK_SELECT_FONT , "Font"),
                    (Gtk.STOCK_ZOOM_100 , "Zoom100"), (Gtk.STOCK_ZOOM_FIT , "ZoomFit"),
                     )
        for aa in tarr2:
            butt = Gtk.ToolButton().new_from_stock(aa[0])
            butt.set_tooltip_text(aa[1])
            butt.connect("clicked", self.callb, cnt)
            cnt += 1
            self.hbox2.add(butt)

        vbox.add(self.hboxt)
        vbox.add(self.hbox)
        vbox.add(self.hbox2)
        self.add(vbox)

        '''openbtn = Gtk.ToolButton(Gtk.STOCK_OPEN)
        self.insert(openbtn, 0)
        self.show_all()
        '''

    def area_motion(self, area, event):
        #print ("motion event", event.state, event.x, event.y)
        if self.drag:
            #print ("drag toolbox", event.state, event.x, event.y)
            #print("delta:", event.x - self.dragpos[0],  event.y - self.dragpos[1])
            pos = self.get_position()
            self.move(pos[0] + event.x - self.dragpos[0],
                pos[1] + event.y - self.dragpos[1])

    def area_button_rel(self, area, event):
        self.drag = False

    def area_button(self, area, event):

        #return
        #print("moudown", event.x, event.y)
        hit = Rectangle(event.x, event.y, 2, 2)

        rr = self.labelm.get_allocation()
        rrr = Rectangle(rr.x, rr.y, rr.width, rr.height)
        if rrr.intersect(hit)[0]:
            #print("objl", rr.x, rr.y)
            if self.opacity == 1:
                self.opacity = 0.5
            else:
                self.opacity = 1
            self.set_opacity(self.opacity)

        rr = self.toolt.get_allocation()
        rrr = Rectangle(rr.x, rr.y, rr.width, rr.height)
        if rrr.intersect(hit)[0]:
            #print("objhead", rr.x, rr.y)
            self.dragpos = event.x, event.y
            self.drag = True

        rr = self.labelx.get_allocation()
        rrr = Rectangle(rr.x, rr.y, rr.width, rr.height)
        if rrr.intersect(hit)[0]:
            print("objx", rr.x, rr.y)
            self.hide()

        return True

    def show_box(self, parent):
        self.parent = parent
        self.set_transient_for (self.parent)
        #self.set_parent(parent)
        sxx, syy = self.parent.get_position()
        self.move(sxx + 30, syy + 180)
        self.show_all()

class Canvas(Gtk.DrawingArea):

    def __init__(self, parent, statbox = None):
        Gtk.DrawingArea.__init__(self)
        self.statbox = statbox
        self.parewin = parent
        self.set_can_focus(True)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.connect("draw", self.draw_event)
        self.connect("motion-notify-event", self.area_motion)
        self.connect("button-press-event", self.area_button)
        self.connect("button-release-event", self.area_button)
        self.connect("key-press-event", self.area_key)
        #self.connect("focus-in-event", self.focus_in)

        self.coll = []
        self.cnt = 0
        self.drag = None
        self.curl = None
        self.resize = None
        self.dragcoord = (0,0)
        self.size2 = (0,0)
        self.noop_down = False
        self.drawline = False
        self.stroke = []
        self.hand = Gdk.Cursor(Gdk.CursorType.HAND1)
        self.arrow = Gdk.Cursor(Gdk.CursorType.ARROW)
        self.sizing =  Gdk.Cursor(Gdk.CursorType.SIZING)
        self.cross =  Gdk.Cursor(Gdk.CursorType.TCROSS)
        self.hair =  Gdk.Cursor(Gdk.CursorType.CROSSHAIR)
        self.curve =  Gdk.Cursor(Gdk.CursorType.TARGET)
        self.pencil =  Gdk.Cursor(Gdk.CursorType.PENCIL)
        self.fname = "untitled.ped"

    def area_key(self, area, event):
        print ("area_key", event.keyval)
        if event.keyval == Gdk.KEY_Delete or event.keyval == Gdk.KEY_KP_Delete:
            #print("Del key")
            for bb in self.coll:
                if bb.selected:
                    #print("would delete", bb)
                    self.coll.remove(bb)
            self.queue_draw()

        if event.keyval == Gdk.KEY_Up:
            print("UP key")

        if event.keyval == Gdk.KEY_Down:
            print("DN key")

        return True

    '''
    def show_status(self, strx):
        if self.statusbar:
            self.statusbar.set_text(strx)

    '''

    def area_motion(self, area, event):
        #print ("motion event", event.state, event.x, event.y)
        if self.drag:
            gdk_window = self.get_root_window()
            gdk_window.set_cursor(self.hand)
            #print ("drag coord", self.dragcoord[0],  self.dragcoord[1], event.x, event.y)
            xd = int(self.dragcoord[0] - event.x)
            yd = int(self.dragcoord[1] - event.y)
            #print ("delta", xd, yd)
            for aa in self.coll:
                if aa.selected:
                    aa.rect.x = aa.orgdrag.x  - xd
                    aa.rect.y = aa.orgdrag.y  - yd
                    # Also move whole group IN NOT SHIFT
                    if aa.groupid and not (event.state & Gdk.ModifierType.SHIFT_MASK) :
                        for bb in self.coll:
                            if aa.groupid == bb.groupid:
                                bb.rect.x = bb.orgdrag.x  - xd
                                bb.rect.y = bb.orgdrag.y  - yd
            self.queue_draw()

        elif self.curl:
            gdk_window = self.get_root_window()
            gdk_window.set_cursor(self.pencil)
            xd = int(self.dragcoord[0] - event.x)
            yd = int(self.dragcoord[1] - event.y)
            #print ("curl rdelta", xd, yd)
            self.queue_draw()

        elif self.resize:
            gdk_window = self.get_root_window()
            gdk_window.set_cursor(self.sizing)
            #print ("resize", self.resize.text,  event.x, event.y)
            xd = int(self.dragcoord[0] - event.x)
            yd = int(self.dragcoord[1] - event.y)
            #print ("rdelta", xd, yd)

            #if self.size2[0] - xd > 2:
            self.resize.rect.w = self.size2[0] - xd
            #if self.size2[1] - yd > 2:
            self.resize.rect.h = self.size2[1] - yd

            #print("resize rect", self.resize.rect.w, self.resize.rect.h)
            #if self.resize.rect.h < 0:
            #    self.resize.rect.y -= 2 * abs(self.resize.rect.h)
            #    self.resize.rect.h = abs(self.resize.rect.h)

            self.queue_draw()
        else:
            onmarker = 0 #False
            hit = Rectangle(event.x, event.y, 2, 2)
            # Check if on marker
            for cc in self.coll:
                mark = cc.hitmarker(hit)
                if mark:
                    onmarker = mark
                    break

            gdk_window = self.get_root_window()
            if onmarker == 5:
                gdk_window.set_cursor(self.pencil)
            elif onmarker:
                gdk_window.set_cursor(self.cross)
            elif self.noop_down:
                gdk_window.set_cursor(self.hair)
            else:
                gdk_window.set_cursor(self.arrow)

            '''if event.state & Gdk.ModifierType.SHIFT_MASK:
                print( "Shift ButPress x =", event.x, "y =", event.y)
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                print( "Ctrl ButPress x =", event.x, "y =", event.y)
            if event.state & Gdk.ModifierType.MOD1_MASK :
                print( "Alt ButPress x =", event.x, "y =", event.y)
            else:'''

            if event.state & Gdk.ModifierType.BUTTON1_MASK:
                #print( "But Drag", event.state, "x =", int(event.x), "y =", int(event.y))
                self.stroke.append((int(event.x), int(event.y)))
                self.queue_draw()

    def area_button(self, area, event):

        self.grab_focus()

        self.mouse = Rectangle(event.x, event.y, 4, 4)
        #print( "Button", event.button, "state", event.state, " x =", event.x, "y =", event.y)

        mods = event.state & Gtk.accelerator_get_default_mod_mask()
        if(mods & Gdk.ModifierType.MOD1_MASK):
            print("Modifier ALT",  event.state)

        if event.state & Gdk.ModifierType.CONTROL_MASK:
            print( "Ctrl ButPress x =", event.x, "y =", event.y)

        if  event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            print("DBL click", event.button)

        if  event.type == Gdk.EventType.BUTTON_RELEASE:
            self.curl = None
            self.drag = None
            self.resize = None
            self.noop_down = False
            if self.drawline:
                self.drawline = False
                #print (self.stroke)
                rstr = "" #randstr(6)
                coord = Rectangle(stroke_dims(self.stroke))
                self.add_stroke(coord, rstr, randcolstr(), arr = self.stroke)
                self.stroke = []

            self.get_root_window().set_cursor(self.arrow)

        if  event.type == Gdk.EventType.BUTTON_PRESS:
            hit = Rectangle(event.x, event.y, 2, 2)
            hitx = None
            if event.button == 1:
                if not event.state & Gdk.ModifierType.SHIFT_MASK and \
                            not event.state & Gdk.ModifierType.CONTROL_MASK:
                    # Operate on pre selected
                    if not self.drag:
                        for bb in self.coll:
                            if bb.selected:
                                hitx = bb.hittest(hit)
                                hity = bb.hitmarker(hit)
                                #print("Operate on selected", bb.id)
                                if hity == 5:
                                    #print("Hit on curve marker")
                                    self.resize = None
                                    self.drag = None
                                    self.curl = bb
                                    self.dragcoord  = (event.x, event.y)
                                elif hity:
                                    #print("Hit on marker")
                                    self.resize = bb
                                    self.drag = None
                                    self.dragcoord  = (event.x, event.y)
                                    self.size2 = (self.resize.rect.w, self.resize.rect.h)
                                    return
                                elif hitx:
                                    self.drag = bb
                                    self.dragcoord  = (event.x, event.y)
                                    for cc in self.coll:
                                        if cc.selected:
                                            cc.orgdrag = cc.rect.copy()
                                            # Also move whole group
                                            if cc.groupid:
                                                for bb in self.coll:
                                                    if cc.groupid == bb.groupid:
                                                        bb.orgdrag = bb.rect.copy()
                                else:
                                    pass

                    if self.drag:
                        return

                sortx = sorted(self.coll, reverse = True, key = lambda item: item.zorder)

                # Execute new hit test on drag immidiate
                #for aa in self.coll:
                for aa in sortx:
                    if aa.hittest(hit): # and aa.selected:
                        hitx = aa
                        self.drag = aa
                        self.dragcoord  = (event.x, event.y)
                        aa.orgdrag = aa.rect.copy()
                        # Also move whole group
                        if aa.groupid:
                            for bb in self.coll:
                                if bb.groupid == aa.groupid:
                                    bb.orgdrag = bb.rect.copy()
                        break

                #for bb in self.coll:
                for bb in sortx:
                    if bb == hitx:
                        if event.state & Gdk.ModifierType.CONTROL_MASK:
                            bb.selected = not bb.selected
                        else:
                            bb.selected = True
                            #break
                    else:
                        if event.state & Gdk.ModifierType.SHIFT_MASK or \
                            event.state & Gdk.ModifierType.CONTROL_MASK:
                            pass
                        else:
                            bb.selected = False

                if not hitx:
                    self.noop_down = True
                    gdk_window = self.get_root_window()
                    gdk_window.set_cursor(self.hair)

                    # Turn on draw
                    self.drawline = True

                self.queue_draw()

            elif event.button == 3:
                #print("Right click")
                bb = None
                # Execute new hit test
                for aa in self.coll:
                    if aa.hittest(hit):
                        bb = aa
                        break
                if bb:
                    cnt = 0
                    for aa in self.coll:
                        if aa.selected:
                            cnt += 1

                    mms = ("Alignment",
                            "Align Left","Align Right",
                            "Align Top","Align Buttom",
                            "Align Mid X","Align Mid Y",)
                    sss = Menu(mms, self.menu_sss, event, True)

                    mmz = ( "Z-Order",
                            "To Front","To Back",
                            "One forward","One Backward",)
                    zzz = Menu(mmz, self.menu_zzz, event, True)

                    ccs = ( "Connect",
                            "Connect Objects (Reg)", "Connect Objects (Yes)",
                            "Connect Objects (No)", "Disconnect Objects",)

                    ccc = Menu(ccs, self.menu_ccc, event, True)

                    if cnt > 1:
                        mmm = (bb.text, ccc,
                        "Group Objects", "Ungroup Objects", sss, zzz)

                        Menu(mmm, self.menu_action, event)

                    else:
                        mmm = (bb.text, "Object Properties", "Text",
                                "FG Color", "BG Color", "Ungroup", "Delete", zzz)
                        Menu(mmm, self.menu_action2, event)

                    self.queue_draw()
                else:
                    mmm = ("Main Menu", "Dump Objects", "Add Rectangle",
                                "Add Rombus", "Add Circle", "Add Text", "Add Line",
                                    "Save Objects", "Load Objects", "-", "Clear Canvas", "-",
                                        "Export",  "-", "Open", "-", "Save", "Save As")
                    Menu(mmm, self.menu_action3, event)
            else:
                print("??? click", event.button)

    def writeout(self):
        print( "writeout", self.fname)
        sum = []
        for aa in self.coll:
            sum.append(aa.dump())
        ff = open(self.fname, "wb")
        pickle.dump(sum, ff)
        ff.close()

    def done_fc(self, win, resp):
        #print( "done_fc", win, resp)
        if resp == Gtk.ResponseType.OK:
            fname = win.get_filename()
            if not fname:
                print("Must have filename")
            else:
                if os.path.isfile(fname):
                    resp = pedync.yes_no_cancel("Overwrite File Prompt",
                                "Overwrite existing file?\n '%s'" % fname, False)
                    print("resp", resp)
                    if resp == Gtk.ResponseType.YES:
                        self.fname = fname
                        self.writeout()
                        self.mained.update_statusbar("Saved under new filename '%s'" % fname)
                    else:
                        self.mained.update_statusbar("No new file name supplied, cancelled 'Save As'")
                else:
                    self.fname = fname
                    self.writeout()
                    pass
                pedconfig.conf.pedwin.mywin.set_title("pyedpro: " + self.fname)

        win.destroy()

    def file_dlg(self, resp):
        #print "File dialog"
        if resp == Gtk.ResponseType.YES:
            but =   "Cancel", Gtk.ResponseType.CANCEL,   \
                            "Save File", Gtk.ResponseType.OK
            fc = Gtk.FileChooserDialog("Save file as ... ", None,
                    Gtk.FileChooserAction.SAVE, but)
            #fc.set_do_overwrite_confirmation(True)
            fc.set_current_name(os.path.basename(self.fname))
            fc.set_current_folder(os.path.dirname(self.fname))
            fc.set_default_response(Gtk.ResponseType.OK)
            fc.connect("response", self.done_fc)
            fc.run()

    def menu_ccc(self, item, num):
        print ("Connect", item, num)
        if num == 1:
            #print ("Conn obj", item, num)
            ccc = []
            for aa in self.coll:
                if aa.selected:
                    ccc.append(aa)
            for aa in ccc[1:]:
                ccc[0].other.append(aa.id)

        if num == 4:
            ccc = []
            for aa in self.coll:
                if aa.selected:
                    ccc.append(aa)

            if len(ccc) == 2:
                #print("Please select two objects to disconnect")
                print("disconnecting", ccc[0].text, ccc[1].text)
                try:    ccc[0].other.remove(ccc[1].id)
                except: pass
            else:
                for dd in ccc:
                    dd.other = []

            self.queue_draw()

    def menu_zzz(self, item, num):

        #print ("Z order", item, num)
        global globzorder
        if num == 1:
            for aa in self.coll:
                if aa.selected:
                    globzorder = globzorder + 1
                    aa.zorder = globzorder
                    break

        if num == 2:
            for aa in self.coll:
                aa.zorder += 1
            for aa in self.coll:
                if aa.selected:
                    aa.zorder = 0
                    break

        self.queue_draw()

    def menu_sss(self, item, num):
            print ("Align", item, num)

    def menu_action(self, item, num):

        # Group
        if num == 2:
            global globgroup
            globgroup += 1
            for aa in self.coll:
                if aa.selected:
                    aa.groupid = globgroup

        # Ungroup
        if num == 3:
            for aa in self.coll:
                if aa.selected:
                    for bb in self.coll:
                        if aa.groupid == bb.groupid:
                            bb.groupid = 0
                        aa.groupid = 0
        # Align
        if num == 5:
            for aa in self.coll:
                if aa.selected:
                    for bb in self.coll:
                        if bb.selected:
                            bb.rect.x = aa.rect.x
                    break
        self.queue_draw()

    def menu_action2(self, item, num):

        if num == 2:
            #print("Getting text")
            bb = None
            for aa in self.coll:
                    if aa.selected:
                        bb = aa
            if bb:
                #print("Getting text", bb)
                response, txt = textdlg(bb.text, self.get_toplevel())
                if response == Gtk.ResponseType.ACCEPT:
                    #print("Got text", txt)
                    bb.text = txt
                    self.queue_draw()

        if num == 3:
            ccc = canv_colsel(0, "Foreground Color")
            for aa in self.coll:
                if aa.selected:
                    aa.col2 = ccc
            self.queue_draw()

        if num == 4:
            ccc = canv_colsel(0, "Background Color")
            for aa in self.coll:
                if aa.selected:
                    aa.col1 = ccc
            self.queue_draw()

        if num == 5:
            for aa in self.coll:
                if aa.selected:
                    for bb in self.coll:
                        if aa.groupid == bb.groupid:
                            bb.groupid = 0
                        aa.groupid = 0
            self.queue_draw()

        if num == 6:
            #print("Delete")
            for bb in self.coll:
                if bb.selected:
                    #print("would delete", bb)
                    self.coll.remove(bb)
            self.queue_draw()


    def menu_action3(self, item, num):

        #print("menu action ", item, num)

        if num == 1:
            for aa in self.coll:
                print(aa.dump())

        if num == 2:
            rstr = randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 120, 120)
            self.add_rect(coord, rstr, randcolstr())

        if num == 3:
            rstr = randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 120, 120)
            self.add_romb(coord, rstr, randcolstr())

        if num == 4:
            rstr = randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 70, 70)
            self.add_circle(coord, rstr, randcolstr())

        if num == 5:
            rstr = randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 40, 40)
            self.add_text(coord, rstr, randcolstr())

        if num == 6:
            rstr = randstr(6)
            coord = Rectangle(self.mouse.x, self.mouse.y, 40, 40)
            self.add_line(coord, rstr, randcolstr())

        if num == 7:
            fff = "outline.pickle"
            #print("Saving to:", fff)
            sum = []
            for aa in self.coll:
                sum.append(aa.dump())
            ff = open(fff, "wb")
            pickle.dump(sum, ff)
            ff.close()

        if num == 8:
            fff = "outline.pickle"
            #print("Loading:", fff)
            self.readfile(fff)

        if num == 9:
            pass

        if num == 10:
            # Clear canvas
            self.coll = []
            self.queue_draw()

        if num == 11:
            # crate PNG
            for aa in self.coll:
                aa.selected = False
            self.queue_draw()
            usleep(10)
            rect = self.get_allocation()

            #pixbuf = Gdk.pixbuf_get_from_window(self.get_window(), 0, 0, rect.width, rect.height)
            #self.surface = cairo.create_for_rectangle(0, 0, width, height)
            #self.surface = cairo.create_similar_image(cairo.Format.ARGB32, rect.width, rect.height)
            #cr =  self.get_window().cairo_create()
            #cr =  cairo.Context(self.surface)

            cr = Gdk.cairo_create(self.get_window())
            self.draw_event(self, cr)
            pixbuf = Gdk.pixbuf_get_from_surface(cr.get_target(), 0, 0, rect.width, rect.height)
            pixbuf.savev("buff.png", "png", [None], [])

        if num == 12:
            print("Export")

        if num == 14:
            #print("Open")
            filter =  Gtk.FileFilter.new()
            filter.add_pattern("*.ped"); filter.set_name("PED files (*.ped)")
            filter2 =  Gtk.FileFilter.new()
            filter2.add_pattern("*.*"); filter2.set_name("ALL files (*.*)")
            filters = (filter2, filter)
            ofn = OpenFname(self.parewin.get_toplevel(), filters)
            fff = ofn.run()
            if not fff.fc_code:
                return
            print("Open filename", fff.fname)

            # Clear canvas
            self.coll = []
            self.queue_draw()

            self.readfile(fff.fname)

        if num == 16:
            #print("Save")
            if self.fname == "untitled.ped":
                fff = self.file_dlg(Gtk.ResponseType.YES)
            else:
                self.writeout()

        if num == 17:
            #print("Save As")
            fff = self.file_dlg(Gtk.ResponseType.YES)

    def show_objects(self):
        for aa in self.coll:
            print ("GUI Object", aa)

    def readfile(self, fname):
        ff = open(fname, "rb")
        sum2  = pickle.load(ff)
        ff.close()
        #print(sum2)

        for aa in sum2:
            obj = None
            rectx = Rectangle(aa[5])
            if aa[2] == "Rect":
                obj = self.add_rect(rectx, aa[1], aa[7], aa[6])
            if aa[2] == "Circ":
                obj = self.add_circle(rectx, aa[1], aa[7], aa[6])
            if aa[2] == "Text":
                obj = self.add_text(rectx, aa[1], aa[7], aa[6])
            if aa[2] == "Romb":
                obj = self.add_romb(rectx, aa[1], aa[7], aa[6])

            if obj:
                obj.id = aa[0]
                obj.zorder = int(aa[3])
                obj.groupid = int(aa[4])
                obj.other  = list(aa[8])

    # Add rectangle to collection of objects
    def add_rect(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = pedcolor.str2float(crb);    col2 = pedcolor.str2float(crf)
        rob = RectObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_line(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = pedcolor.str2float(crb);    col2 = pedcolor.str2float(crf)
        rob = LineObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_curve(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = pedcolor.str2float(crb);    col2 = pedcolor.str2float(crf)
        rob = CurveObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_text(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = pedcolor.str2float(crb);    col2 = pedcolor.str2float(crf)
        rob = TextObj(coord, text, col1, col2, border, fill)

        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_circle(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = pedcolor.str2float(crb);    col2 = pedcolor.str2float(crf)
        rob = CircObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_stroke(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False, arr = []):
        col1 = pedcolor.str2float(crb);    col2 = pedcolor.str2float(crf)
        rob = StrokeObj(coord, text, col1, col2, border, fill, arr)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def add_romb(self, coord, text, crf, crb = "#ffffff", border = 2, fill = False):
        col1 = pedcolor.str2float(crb);    col2 = pedcolor.str2float(crf)
        rob = RombObj(coord, text, col1, col2, border, fill)
        self.coll.append(rob)
        self.queue_draw()
        return rob

    def draw_event(self, doc, cr):

        #print ("Painting .. ", self.cnt)
        self.cnt += 1
        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        #bg_color = ctx.get_background_color(Gtk.StateFlags.NORMAL)

        self.layout = PangoCairo.create_layout(cr)
        self.rect = self.get_allocation()
        self.cr = cr
        self.crh = CairoHelper(cr)

        # Paint white, ignore system BG
        border = 4
        cr.set_source_rgba(255/255, 255/255, 255/255)
        cr.rectangle( border, border, self.rect.width - border * 2, self.rect.height - border * 2);
        cr.fill()

        # Draw connections
        cr.set_source_rgba(55/255, 55/255, 55/255)
        for aa in self.coll:
            for cc in aa.other:
                for bb in self.coll:
                    if cc == bb.id:
                        #print("connect draw", aa.text, bb.text)
                        aac = aa.center()
                        cr.move_to(aac[0], aac[1])
                        bbc = bb.center()
                        cr.line_to(bbc[0], bbc[1])
                        cr.stroke()

        #for aa in self.coll:
        #    aa.dump()

        sortx = sorted(self.coll, reverse = False, key = lambda item: item.zorder)

        # Draw objects
        #for aa in self.coll:
        for aa in sortx:
            try:
                aa.draw(cr, self)
            except:
                put_exception("Cannot draw " + str(type(aa)))
                #aa.dump()

        init = 0;
        for aa, bb in self.stroke:
            if init == 0:
                self.cr.move_to(aa, bb)
            else:
                self.cr.line_to(aa, bb)
            init += 1
        self.cr.stroke()


def set_canv_testmode(flag):
    global canv_testmode
    canv_testmode = flag

# EOF