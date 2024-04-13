#!/usr/bin/env python

from __future__ import absolute_import, print_function

import os
import time
import string
import pickle
import re
import platform
import subprocess
import threading

import py_compile

import gi;  gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import cairo

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from pedlib import  pedconfig
from pedlib import  peddraw
from pedlib import  pedxtnd
from pedlib import  pedync
from pedlib import  pedspell
from pedlib import  pedcolor
from pedlib import  pedmenu
from pedlib import  pedundo
from pedlib import  pedmisc
from pedlib import  pedtask
from pedlib import  pedfind
from pedlib import  pedplug

from pedlib.pedutil import *
from pedlib.keywords import *

(TARGET_ENTRY_TEXT, TARGET_ENTRY_PIXBUF) = range(2)
(COLUMN_TEXT, COLUMN_PIXBUF) = range(2)
DRAG_ACTION = Gdk.DragAction.COPY

VSCROLLGAP  = 2             # Gap between the page boundary and ver. scroll
HSCROLLGAP  = 4             # Gap between the page boundary and hor. scroll
PAGEUP      = 20            # One page worth of scroll

# Do not redefine this here, as it is determined by the gtk (pango) lib
#TABSTOP = 8                 # One tab stop worth of spaces

# On version 0.21 (and after) we force GTK to assume our idea of tabstop.
# Even though we do not draw the tabs with GTK it is cleaner (simpler)
# this way. (See mess on tabs before V21)
TABSTOP = 4                 # One tab stop worth of spaces

# Profile line, use it on bottlenecks Widget set_a
#got_clock = time.clock()
# profiled code here
#print(  "Str", time.clock() - got_clock)

# Globals

last_scanned = None

# Colors for the text, configure the defaults here

FGCOLOR     = "#000000"
FGCOLORRO   = "#888888"
RFGCOLOR    = "#fefefe"
BGCOLOR     = "#fefefe"
RBGCOLOR    = "#aaaaff"
CBGCOLOR    = "#ff8888"
KWCOLOR     = "#88aaff"
CLCOLOR     = "#880000"
COCOLOR     = "#4444ff"
STCOLOR     = "#ee44ee"
STRIPCOLOR  = "#eeeeee"

CARCOLOR = "#4455dd"

# UI specific values:

DRAGTRESH = 3                   # This many pixels for drag highlight

# ------------------------------------------------------------------------
# We create a custom class for display, as we want a text editor that
# can take thousands of lines.

class pedDoc(Gtk.DrawingArea, peddraw.peddraw, pedxtnd.pedxtnd, pedtask.pedtask):

    def __init__(self, buff, mained, readonly = False):

        # Save params
        self.mained = mained
        self.readonly = readonly
        self.ext = ""
        # Gather globals
        self.keyh = pedconfig.conf.keyh
        self.acth = pedconfig.conf.acth

        self.lastkey = ' '
        self.second = False
        self.strip = 50
        # Init vars
        self.xpos = 0; self.ypos = 0
        self.changed = False
        self.src_changed = False
        self.needscan = True
        self.record = False
        self.recarr = []                # Macros
        self.undoarr = []               # Undo
        self.redoarr = []               # Redo
        self.queue = []                 # Idle tasks
        self.colsel = False
        self.oldsearch = ""
        self.oldgoto = ""
        self.oldrep = ""
        self.doidle = 0
        self.xsel = -1; self.ysel = -1
        self.xsel2 = -1; self.ysel2 = -1
        self.mx = -1; self.my = -1
        self.caret = []; self.caret.append(0); self.caret.append(0)
        self.focus = False
        self.insert = True
        self.startxxx = -1;  self.startyyy = -1
        self.hex = False
        self.colflag = True
        self.acorr = False
        self.scol = False
        self.accum = []
        self.tokens = []
        self.ularr = []
        self.bigcaret = False
        self.stab = False
        self.oneshot = False
        self.honeshot = False
        self.caretshot = False
        self.initial_undo_size = 0
        self.initial_redo_size = 0
        self.spell = False
        self.spellmode = False
        self.start_time = time.time()
        self.shift = False
        # Init configurables
        self.vscgap = VSCROLLGAP
        self.hscgap = HSCROLLGAP
        self.pgup  = PAGEUP
        self.tabstop = TABSTOP
        # Process buffer into list
        self.text = buff
        self.maxlinelen = 0
        self.maxlines = 0
        self.fired = 0
        self.countup = 0
        self.nokey = False
        self.newword = False
        self.scrtab = False
        self.stat = None
        self.sep = "\n"
        self.tts = None
        self.lastcmd = ""
        self.caps = False
        self.scr = False
        self.lastevent = None
        self.hhh = self.www = 0
        self.diffmode = 0
        self.diffpane = False
        self.webwin = None
        self.nomenu = False
        self.FGCOLOR    = FGCOLOR
        self.FGCOLORRO  = FGCOLORRO
        self.RFGCOLOR   = RFGCOLOR
        self.BGCOLOR    = BGCOLOR
        self.RBGCOLOR   = RBGCOLOR
        self.CBGCOLOR   = CBGCOLOR
        self.KWCOLOR    = KWCOLOR
        self.CLCOLOR    = CLCOLOR
        self.COCOLOR    = COCOLOR
        self.STCOLOR    = STCOLOR
        self.STRIPCOLOR = STRIPCOLOR
        self.currback  =  0

        self.drag = False
        self.text_fillcol = 40
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        #self.stopthread = False

        # Parent widget
        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        peddraw.peddraw.__init__(self, self)

        # Our font
        fsize  =  pedconfig.conf.sql.get_int("fsize")
        fname  =  pedconfig.conf.sql.get_str("fname")
        if fsize == 0: fsize = 20
        if fname == "": fname = "Monospace"

        self.setfont(fname, fsize)

        if self.readonly:
            self.set_tooltip_text("Read only buffer")

        # Create scroll items
        sm = len(self.text) + self.get_height() / self.cyy + 10
        self.hadj = Gtk.Adjustment(value=0, lower=0, upper=self.maxlinelen,
                            step_increment = 1, page_increment = 15, page_size = 25)
        self.vadj = Gtk.Adjustment(value=0, lower=0, upper=sm,
                            step_increment = 1, page_increment = 15, page_size = 25)

        self.vscroll = Gtk.VScrollbar(adjustment=self.vadj)
        self.hscroll = Gtk.HScrollbar(adjustment=self.hadj)

        # We connect scrollers after construction
        self.hadj.connect("value-changed", self.hscroll_cb)
        self.vadj.connect("value-changed", self.vscroll_cb)

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        #self.colormap = Gtk.widget_get_default_colormap()
        self.setcol()

        # Set default background color
        if self.readonly:
            #color = self.colormap.alloc_color("#d8d8d8")
            #self.modify_bg(Gtk.STATE_NORMAL, color)
            pass

        #self.connect("expose-event", self.area_expose_cb)
        self.connect("draw", self.draw_event)
        self.connect("motion-notify-event", self.area_motion)
        self.connect("button-press-event", self.area_button)
        self.connect("button-release-event", self.area_button)

        # This was needed ad ALT-a and ALT-b ....
        # .... misteriousely stopped working;
        # Now getting key from main window
        #self.connect("key-press-event", self.area_key)
        #self.connect("key-release-event", self.area_key)

        self.connect("focus", self.area_focus)
        self.connect("configure_event", self.configure_event)
        #self.connect("size-request", self.)
        self.connect("size-allocate", self.size_alloc)
        self.connect("scroll-event", self.scroll_event)
        self.connect("focus-in-event", self.focus_in_cb)
        self.connect("focus-out-event", self.focus_out_cb)

        self.drag_dest_set(0, [], 0)
        self.connect('drag-motion', self.on_drag_motion)
        self.connect('drag-drop', self.on_drag_drop)
        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("drag-data-get", self.on_drag_data_get)
        self.connect("destroy", self.destroy_cb)

    def run_keytime(self):
        global last_scanned
        last_scanned = ""
        if not self.mained.mac:
            GLib.timeout_add(300, keytime, self, 0)
        pass

    def destroy_cb(self, arg):
        #print("dest", arg)
        #self.stopthread = True
        pass

    def on_drag_data_get(self, widget, drag_context, data, info, time):
        #print("Drag data get entry")
        if self.xsel == -1 or self.ysel == -1:
            return
        # Normalize
        xssel = min(self.xsel, self.xsel2)
        xesel = max(self.xsel, self.xsel2)
        yssel = min(self.ysel, self.ysel2)
        yesel = max(self.ysel, self.ysel2)

        cnt = yssel; cnt2 = 0; cumm = ""
        while True:
            if cnt > yesel: break

            #self.pad_list(self, cnt)
            line = self.text[cnt]
            if self.colsel:
                frag = line[xssel:xesel]
            else :                                  # startsel - endsel
                if cnt == yssel and cnt == yesel:   # sel on the same line
                    frag = line[xssel:xesel]
                elif cnt == yssel:                  # start line
                    frag = line[xssel:]
                elif cnt == yesel:                  # end line
                    frag = line[:xesel]
                else:
                    frag = line[:]

            if cnt2: frag = "\n" + frag
            cumm += frag
            cnt += 1; cnt2 += 1

        data.set_text(cumm, -1)

    def on_drag_motion(self, widgt, context, c, y, time):
        Gdk.drag_status(context, Gdk.DragAction.COPY, time)
        return True

    def on_drag_drop(self, widget, context, xx, yy, time):
        #print("xy", xx // self.cxx , yy // self.cyy);
        self.set_caret(self.xpos + xx // self.cxx, self.ypos + yy // self.cyy)
        widget.drag_get_data(context, context.list_targets()[-1], time)

    # Insert text at current point
    def inserttext(self, xtext):

        newtxt = xtext.split("\n") + []
        ycoord = self.ypos + self.caret[1]
        #ycoord = self.ypos + y

        xidx = self.caret[0] + self.xpos;
        yidx = self.caret[1] + self.ypos

        tmptext = self.text[:ycoord]
        self.undoarr.append((xidx, yidx, pedundo.NOOP, ""))
        for aa in newtxt:
            self.undoarr.append((xidx, yidx, pedundo.ADDED  \
                + pedundo.CONTFLAG, aa))
            yidx += 1
            tmptext.append(aa)
        tmptext += self.text[ycoord:]
        self.text = tmptext

        self.changed = True
        self.set_caret(self.xpos + self.caret[0],
                    self.ypos + self.caret[1] + len(newtxt))

        mlen = self.calc_maxline()

        # Set up scroll bars
        self.set_maxlinelen(mlen, False)
        #self.set_maxlines(len(self.text), False)
        self.invalidate()

    # Drag and drop here
    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        #print("Received data:", data, data.get_data_type(), x, y, info)
        if info == TARGET_ENTRY_TEXT:
            if str(data.get_data_type()) == "text/plain":
                xtext = data.get_text()
                if xtext:
                    #print("Received text: %s" % xtext[:48])
                    self.inserttext(xtext)

            if str(data.get_data_type()) == "text/uri-list":
                xuris = data.get_uris()
                #print("got uri", xuris)
                uuu = "file://"
                for aa in xuris:
                    if aa[:7] != uuu:
                        continue
                    try:
                        xfname = aa[7:]
                        try:
                            xstat = os.stat(xfname)
                        except:
                            pass
                        print("drop xfname", xfname, xstat)
                        if xstat.st_size > 100000:
                            pedync.message("\nDragged file is too big.\n"
                                "To open anyway, use the regular open function\n\n"  )
                            continue

                        fp = open(xfname)
                        xtext = fp.read()
                        fp.close()
                        self.inserttext(xtext)
                    except:
                        print("Cannot open dragged file.")
                        self.mained.update_statusbar("Cannot open dragged file. '%s'" % xfname)


        elif info ==  TARGET_ENTRY_PIXBUF:
            pixbuf = data.get_pixbuf()
            width = pixbuf.get_width()
            height = pixbuf.get_height()
            print("Received pixbuf with width %spx and height %spx" % (width, height))

        Gtk.drag_finish(drag_context, True, False, time)

    # Customize your colors here
    def setcol(self):
        ccc = pedconfig.conf.sql.get_str("fgcolor")
        if ccc == "":
            self.fgcolor  = pedcolor.str2float(FGCOLOR)
        else:
            self.fgcolor  = pedcolor.str2float(ccc)
        #print( "fgcol", self.fgcolor, ccc)

        ccc = pedconfig.conf.sql.get_str("fgcolorro")
        if ccc == "":
            self.fgcolorro  = pedcolor.str2float(FGCOLORRO)
        else:
            self.fgcolorro  = pedcolor.str2float(ccc)
        #print( "fgcolro", self.fgcolorro, ccc)

        ccc = pedconfig.conf.sql.get_str("rbgcolor")
        if ccc == "":
            self.rbgcolor = pedcolor.str2float(RBGCOLOR)
        else:
            self.rbgcolor = pedcolor.str2float(ccc)
        #print( "rgbcolor", self.rbgcolor, ccc)

        ccc = pedconfig.conf.sql.get_str("bgcolor")
        if ccc == "":
            self.bgcolor = pedcolor.str2float(BGCOLOR)
        else:
            self.bgcolor = pedcolor.str2float(ccc)
        #print( "bgcolor", self.bgcolor, ccc)

        ccc = pedconfig.conf.sql.get_str("cbgcolor")
        if ccc == "":
            self.cbgcolor = pedcolor.str2float(CBGCOLOR)
        else:
            self.cbgcolor = pedcolor.str2float(ccc)
        #print( "cbgcolor", self.cbgcolor, ccc)

        self.stripcolor = pedcolor.str2float(STRIPCOLOR)

        ccc = pedconfig.conf.sql.get_str("kwcolor")
        if ccc == "":
            self.kwcolor = pedcolor.str2float(KWCOLOR)
        else:
            self.kwcolor = pedcolor.str2float(ccc)
        #print( "load kwcolor", self.kwcolor, ccc)

        ccc = pedconfig.conf.sql.get_str("clcolor")
        if ccc == "":
            self.clcolor = pedcolor.str2float(CLCOLOR)
        else:
            self.clcolor = pedcolor.str2float(ccc)

        ccc = pedconfig.conf.sql.get_str("cocolor")
        if ccc == "":
            self.cocolor = pedcolor.str2float(COCOLOR)
        else:
            self.cocolor = pedcolor.str2float(ccc)

        ccc = pedconfig.conf.sql.get_str("stcolor")
        if ccc == "":
            self.stcolor = pedcolor.str2float(STCOLOR)
        else:
            self.stcolor = pedcolor.str2float(ccc)

        ccc = pedconfig.conf.sql.get_str("carcolor")
        if ccc == "":
            self.carcolor = pedcolor.str2float(CARCOLOR)
        else:
            self.carcolor = pedcolor.str2float(ccc)

    #def printrect(self, ttt,  rrr):
    #    print("rect", ttt, rrr.x / Pango.SCALE, rrr.y /Pango.SCALE,
    #            rrr.width / Pango.SCALE, rrr.height / Pango.SCALE)

    def setfont(self, fam, size):

        self.fd = Pango.FontDescription()

        self.fd.set_family(fam)
        # Will not wotk right on the MAC if simple set_size used
        self.fd.set_absolute_size(size * Pango.SCALE)

        self.pangolayout = self.create_pango_layout("a")
        self.pangolayout.set_font_description(self.fd)

        #print("pc", dir(PangoCairo))
        #print()
        #fm = Pango.FontMap()
        #ccc = Pango.create_context(fm)
        # Get Pango steps
        #self.cxx, self.cyy = self.pangolayout.get_pixel_size()
        (pr, lr) = self.pangolayout.get_extents()
        #self.printrect("pix", pr)
        #self.printrect("log", lr)

        self.cxx = lr.width / Pango.SCALE; self.cyy = lr.height / Pango.SCALE

        # Get Pango tabs
        self.tabarr = Pango.TabArray(80, False)
        #for aa in range(self.tabarr.get_size()):
        #    self.tabarr.set_tab(aa, Pango.TAB_LEFT, aa * TABSTOP * self.cxx * Pango.SCALE)

        self.pangolayout.set_tabs(self.tabarr)
        ts = self.pangolayout.get_tabs()

        '''if ts != None:
            al, self.tabstop = ts.get_tab(1)
        self.tabstop /= self.cxx * Pango.SCALE'''

        # Also set stip offset
        self.strip = 4 * self.cxx + 8

    def  set_maxlinelen(self, mlen = -1, ignore = True):
        if mlen == -1: self.calc_maxline()
        self.maxlinelen = mlen
        self.oneshot = ignore
        #value, lower, upper, step_increment, page_increment, page_size)
        #self.hadj.set_all(0, 0, self.maxlinelen * 2, 1, 15, 25)
        self.hadj.set_value(0)
        self.hadj.set_lower(0)
        self.hadj.set_upper(self.maxlinelen * 2)
        self.hadj.set_step_increment(1)
        self.hadj.set_page_increment(15)
        self.hadj.set_page_size(25)

    def  set_maxlines(self, lines = 0, ignore = True):
        self.maxlines = len(self.text) + self.get_height() / self.cyy + 25
        self.oneshot = ignore
        #self.vadj.set_all(0, 0, self.maxlines, 1, 15, 25)
        self.vadj.set_value(0)
        self.vadj.set_lower(0)
        self.vadj.set_upper(self.maxlines)
        self.vadj.set_step_increment(1)
        self.vadj.set_page_increment(15)
        self.vadj.set_page_size(25)

    def locate(self, xstr):
        #print( "locate '" + xstr +"'")
        cnt = 0; cnt2 = 0; idx = 0; found = 0
        for line in self.text:
            if xstr == line:
                self.gotoxy(idx, cnt, len(xstr), True)
                found = 1
                break
            cnt += 1
        if not found:
            xstr2 = xstr.lstrip().replace("\t", " ")
            for line2 in self.text:
                idx2 = line2.find(xstr2)
                if idx2 >= 0:
                    self.gotoxy(idx2, cnt2, len(xstr2), True)
                    break
                cnt2 += 1

    def focus_out_cb(self, widget, event):
        #print( "focus_out_cb", widget, event)
        self.focus = False

    def focus_in_cb(self, widget, event):
        #print ("focus_in_cb", self.fname)
        self.focus = True
        try:
            os.chdir(os.path.dirname(self.fname))
            xstat = os.stat(self.fname)
            if not self.readonly:
                #print(self.fname, "stat", self.stat.st_mtime, "xstat", xstat.st_mtime)
                if self.stat.st_mtime !=  xstat.st_mtime:
                    rrr = pedync.yes_no_cancel("File changed outside PyEdPro",
                        "'%s'\n" \
                        "changed outside PyEdPro." \
                        "Reload?" % self.fname, False)
                    if rrr == Gtk.ResponseType.YES:
                        if pedconfig.conf.verbose:
                           print("Reloading", self.fname)
                        self.savebackup()
                        self.saveparms()

                        # Is it already loaded? ... close
                        #nn = self.notebook.get_n_pages()
                        #fname2 = os.path.realpath(self.fname)
                        #for aa in range(nn):
                        #    vcurr = self.notebook.get_nth_page(aa)
                        #    if vcurr.area.fname == fname2:
                        #        if pedconfig.conf.verbose:
                        #            print("Closing '"+ fname2 + "'")
                        #        #vcurr.area.closedoc(noprompt = True)
                        #        #self.mained.close_document(self)

                        #usleep(100)
                        self.loadfile(self.fname, reload = True)
                        self.loadparms()

            # Update stat info
            self.stat = xstat
        except:
            put_exception("cmp mtime")
            pass

        self.update_bar2()
        self.needscan = True
        self.do_chores()
        #self.fired = 3

    def grab_focus_cb(self, widget):
        #print( "grab_focus_cb", widget)
        pass

    def area_enter(self, widget, event):
        #print( "area_enter")
        pass

    def area_leave(self, widget, event):
        #print( "area_leave")
        pass

    def scroll_event(self, widget, event):
        #print( "scroll_event", event, event.direction)
        xidx = self.xpos + self.caret[0]
        yidx = self.ypos + self.caret[1]
        if event.direction == Gdk.ScrollDirection.SMOOTH:
            flag, directx, directy = event.get_scroll_deltas()
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                yidx += 10 * int(directy)
            elif event.state & Gdk.ModifierType.SHIFT_MASK:
                yidx += 5 * int(directy)
            else:
                yidx += int(directy)
        else:
            #print( "type", type(event.type))
            #print("truth", isinstance(event.type, Gdk.EventType))
            if event.direction == Gdk.ScrollDirection.UP:
                yidx -= int(self.pgup / 2)
            else:
                yidx += int(self.pgup / 2)

        self.set_caret(xidx, yidx)
        self.invalidate()

    def hscroll_cb(self, widget):
        #print( "hscroll_cb", widget.get_value())

        # Skip one callback
        if self.honeshot:
            self.honeshot = False; return
        xidx = int(widget.get_value())

        #print( "hscroll_cb ok", widget.get_value())
        self.set_caret(xidx, self.ypos + self.caret[1])
        self.invalidate()

        #print( "vscroll_cb", widget.get_value())
        # Skip one callback
        if self.oneshot:
            self.oneshot = False; return
        #print( "vscroll_cb ok", widget.get_value())
        yidx = int(widget.get_value())
        self.set_caret(self.xpos + self.caret[0], yidx + self.caret[1])
        self.invalidate()

    def vscroll_cb(self, widget):
        #print( "vscroll_cb", widget.get_value())
        # Skip one callback
        if self.oneshot:
            self.oneshot = False; return
        #print( "vscroll_cb ok", widget.get_value())
        yidx = int(widget.get_value())
        self.set_caret(self.xpos + self.caret[0], yidx + self.caret[1])
        self.invalidate()

    def size_request(self, widget, req):
        #print( "size_request", req)
        pass

    def size_alloc(self, widget, req):
        #print( "size_alloc", req)
        pass

    def configure_event(self, widget, event):
        #print( "configure_event", event)
        #self.grab_focus()
        #self.width = 0; self.height = 0
        #self.invalidate()
        #print( self, event)
        pass

    def draw_event(self, pdoc, cr):

        self.hhh = self.get_height();  self.www = self.get_width()
        self.xlen = len(self.text)

        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        #bg_color = ctx.get_background_color(Gtk..NORMAL)

        # Paint white, ignore system BG
        #cr.set_source_rgba(255, 255, 255)
        # Paint prescribed color
        if self.readonly:
            # Slightly darker / lighter
            newcol =  list(self.bgcolor)
            for aa in range(len(newcol)):
                if newcol[aa] > 0.5: newcol[aa] -= .08
                else: newcol[aa] += .2
            cr.set_source_rgba(*list(newcol))
        else:
            cr.set_source_rgba(*list(self.bgcolor))

        cr.rectangle( 0, 0, self.www, self.hhh)
        cr.fill()

        cr.set_source_rgba(*list(self.stripcolor))
        cr.rectangle( 0, 0, self.strip - 2, self.hhh)
        cr.fill()

        try:
            pedplug.predraw(self, cr)
        except:
            print("plugin failed", sys.exc_info())

        # Pre set for drawing
        #cr.set_source_rgba(*list(fg_color))
        # Paint prescribed color
        cr.set_source_rgba(*list(self.fgcolor))

        cr.move_to(0, 0)
        self.layout = PangoCairo.create_layout(cr)
        self.layout.set_font_description(self.fd)

        self.draw_maintext(cr)

        if not self.hex:
            # Do the text drawing in stages ...
            try:
                self.draw_selection(cr)
                self.draw_syntax(cr)
                self.draw_clsyntax(cr)
                self.draw_comments(cr)
                self.draw_spellerr(cr)
            except:
                print("Failed to draw colors", sys.exc_info())

        if self.startxxx != -1:
            self.gotoxy(self.startxxx, self.startyyy)
            self.startxxx = -1; self.startyyy = -1

        self.draw_caret(cr)

    def idle_queue(func):
        self.queue.append(func)
        #print( queue)

    def area_button(self, area, event):

        self.lastevent = event

        #if pedconfig.conf.pgdebug > 5:
        #    print( "Button press  ", self, event.type, " x=", event.x, " y=", event.y)

        event.x = int(event.x) - self.strip
        event.y = int(event.y)

        if  event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:
                #print( "Left Click at x=", event.x, "y=", event.y)
                self.mx = int(event.x); self.my = int(event.y)
                xxx = int(event.x / self.cxx); yyy = int(event.y / self.cyy)
                # Find current pos, gather tabs, adjust back
                try:
                    line = self.text[self.ypos + yyy]
                except:
                    line = ""
                offs = calc_tabs2(line, xxx)

                # Are we in selection?
                #print( "xxx", self.xpos + xxx, "yyy", self.ypos + yyy)
                #rp = xxx + self.xpos
                #print( "xpos", self.xpos, "xxx", xxx, "rp", rp)
                #print( line)
                #print( "line part", "'" + line[rp:rp+8] + "'")

                # Are we in selection?
                if self.xsel != -1:
                    #print("xsel", self.xsel, "ysel", self.ysel)
                    #print("xsel2", self.xsel2, "ysel2", self.ysel2)

                    xssel = min(self.xsel, self.xsel2)
                    xesel = max(self.xsel, self.xsel2)
                    yssel = min(self.ysel, self.ysel2)
                    yesel = max(self.ysel, self.ysel2)

                    if (self.ypos + yyy >= yssel and self.ypos + yyy <= yesel) and \
                         (self.xpos + xxx >= xssel and self.xpos + xxx <= xesel):
                        #print("in selection")
                        self.drag = True
                    else:
                        # Erase selection, pos cursor
                        self.clearsel()
                        self.set_caret(self.xpos + xxx - (offs - xxx),
                                     self.ypos + yyy )
                else:
                    self.set_caret(self.xpos + xxx - (offs - xxx),
                                 self.ypos + yyy )

                self.fired += 1
                self.run_keytime()
                #self.mained.threads.submit_job(keytime, self, None)

            if event.button == 3:
                #print( "Right Click at x=", event.x, "y=", event.y)
                flag = False; xx = 0; yy = 0; zz = 0
                if self.spell:
                    yyy = int(self.ypos + self.get_height() / self.cyy)
                    for xaa, ybb, lcc in self.ularr:
                        # Look within visible range
                        if ybb >= self.ypos and ybb < yyy:
                            ybb -= self.ypos
                            xaa -= self.xpos; lcc -= self.xpos
                            xaa *= self.cxx ; ybb *= self.cyy
                            lcc *= self.cxx
                            yy2 = ybb + self.cyy

                            if self.intersect(xaa, ybb, lcc, yy2, event):
                                xx = int(xaa / self.cxx + self.xpos)
                                yy = int(ybb / self.cyy + self.ypos)
                                zz = int(lcc / self.cxx + self.xpos)
                                flag = True
                if flag:
                    line = self.text[yy]
                    #print( "Spell delimit: '" + line[xx:zz] + "'")
                    self.xsel = xx;
                    self.xsel2 = zz

                    self.ysel = self.ysel2 = yy
                    self.spellstr = line[int(xx):int(zz)]
                    self.popspell(area, event, self.spellstr)
                else:
                    if event.state & Gdk.ModifierType.SHIFT_MASK:
                        if self.xsel == -1:
                            yyy = int(event.y / self.cyy + self.ypos)
                            xxx = int(event.x / self.cxx + self.xpos)
                            line = self.text[yyy]
                            self.xsel, self.xsel2 = selasci2(line, xxx, "_-")
                            self.ysel = self.ysel2 = yyy
                        else:
                            line = self.text[self.ysel]

                        strx = line[int(self.xsel):int(self.xsel2)]
                        #print("'" + strx + "'")
                        if strx:
                            self.poprclick2(area, event, strx)
                    else:
                        self.poprclick(area, event)

        elif  event.type == Gdk.EventType.BUTTON_RELEASE:
            #print( "button release", event.button)
            self.mx = -1; self.my = -1
            self.scrtab = False
            self.drag = False
            ttt = "Release"
            xxx = int(event.x / self.cxx); yyy = int(event.y / self.cyy)
            # Find current pos, gather tabs, adjust back
            try:
                line = self.text[self.ypos + yyy]
            except:
                line = ""
            offs = calc_tabs2(line, xxx)
            self.set_caret(self.xpos + xxx - (offs - xxx),
                                     self.ypos + yyy )

        elif  event.type == Gdk.EventType._2BUTTON_PRESS:

            if pedconfig.conf.pgdebug > 2:
                print ("Double click %.2f %.2f" % (event.x, event.y))

            self.mx = int(event.x); self.my = int(event.y)
            xxx = int(event.x / self.cxx)
            yyy = int(event.y / self.cyy)

            # Find current pos, gather tabs, adjust back
            try:
                line = self.text[self.ypos + yyy]
            except:
                line = ""

            # Find current pos on tabbed line
            offs = calc_tabs2(line, xxx)
            self.set_caret(self.xpos + xxx - (offs - xxx), self.ypos + yyy )
            #self.set_caret(len(xxx2), yyy)

            # Erase selection
            if self.xsel != -1:
                self.clearsel()

            # Select word
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                pedconfig.conf.keyh.acth.ctrl_b(self)
            else:
                pedconfig.conf.keyh.acth.alt_v(self)
            # Copy to clip

            if event.state & Gdk.ModifierType.SHIFT_MASK:
                pedconfig.conf.keyh.acth.ctrl_c(self)

        else:
            print("Unexpected mouse op.")

        self.grab_focus()
        return True

    # See if point in rect
    def intersect(self, xx, yy, xx2, yy2, event):
        # Does X intersect?
        if event.x > xx and event.x < xx2:
            #print( "x inter", xaa, lcc)
            # Does Y intersect?
            if event.y > yy and event.y < yy2:
                return True
        return False

    # Normalize
    def normsel(self):
        xssel = min(self.xsel, self.xsel2)
        xesel = max(self.xsel, self.xsel2)
        yssel = min(self.ysel, self.ysel2)
        yesel = max(self.ysel, self.ysel2)

        self.xsel  = xssel;  self.ysel  = yssel
        self.xsel2 = xesel;  self.ysel2 = yesel

    def pix2xpos(self, xx):
        return int(self.xpos + (xx-self.strip) / self.cxx)

    def pix2ypos(self, yy):
        return int(self.ypos + yy / self.cyy)

    def pix2pos(self, xx, yy):
        return int(self.xpos + (xx-self.strip) / self.cxx), int(self.ypos + yy / self.cyy)

    def area_motion(self, area, event):
        #print ("motion event", event.state, event.x, event.y)
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            #print( "motion event butt 1", event.state, event.x, event.y)
            if self.drag:
                #print ("drag motion event", event.state, event.x, event.y)
                targ = Gtk.TargetList(); targ.add_text_targets(0)
                self.drag_begin(targ, Gdk.DragAction.COPY, 0, event)
                self.drag = False
                return

            if self.xsel == -1 and self.scrtab != True:
                begsel = False
                # Horiz drag - regular sel
                if abs(event.x - self.mx) > DRAGTRESH:
                    self.colsel = False; begsel = True

                if begsel:
                    self.xsel = self.xsel2 = self.xpos + self.caret[0]
                    self.ysel = self.ysel2 = self.ypos + self.caret[1]
                    #print( "colsel xsel, ysel", self.colsel, self.xsel, self.ysel)
                if self.scrtab == False:
                    # Vert drag - colsel
                    if abs(event.y - self.my) > DRAGTRESH:
                        self.scrtab  = True
                        self.colsel = True

            if self.scrtab  == True:
                self.xsel = self.xsel2 = self.xpos + self.caret[0]
                self.ysel = self.ysel2 = self.ypos + self.caret[1]
                xidx = self.xpos + self.caret[0]
                yidx = self.ypos + self.caret[1]
                if  event.y >  self.my:
                    yidx += 1
                if  event.y >  self.my:
                    yidx -= 1
                self.set_caret(xidx, yidx)
                self.my = event.y

            if self.xsel != -1:
                # Already selected, mark
                self.ysel2 = self.pix2ypos(event.y)
                if self.ysel2 < self.ysel:
                    self.xsel    = self.pix2xpos(event.x)
                else:
                    self.xsel2 = self.pix2xpos(event.x)

            self.invalidate()

        if event.state & Gdk.ModifierType.SHIFT_MASK and \
            event.state & Gdk.ModifierType.BUTTON1_MASK:
            #print( "Shift Drag", event.x, event.y)
            pass
        pass

    def gotoxy(self, xx, yy, sel = None, mid = False):

        #print ("gotoxy", xx, yy)
        #xx +=  30
        # Contain
        ylen = len(self.text)
        xx2 = max(xx, 0);  yy2 = max(yy, 0)
        xx2 = min(xx, self.maxlinelen);  yy2 = min(yy, ylen)

        if sel:
            self.xsel = xx2; self.xsel2 = xx2 + sel
            self.ysel = yy2; self.ysel2 = yy2
            self.invalidate()
        #else:
        #    self.xsel = xx2; self.xsel2 = xx2
        #    self.ysel = yy2; self.ysel2 = yy2

        if mid:
            self.set_caret_middle(xx, yy)
        else:
            self.set_caret(xx, yy)

        self.invalidate()

    # --------------------------------------------------------------------
    # Goto position, and place it to upper half / quarter

    def set_caret_middle(self, xx, yy, sel = None, quart = 2):

        xx = int(xx); yy = int(yy)

        # Needs scroll?
        #xxx, yyy = self.get_size()
        xlen = len(self.text)

        # Put it back in view:
        off = (self.get_height() / self.cyy) / quart
        if yy > off:
            self.ypos = int(yy - off)
        else:
            self.ypos = 0

        self.set_caret(xx, yy)
        self.invalidate()

    # Dimenswions in character cell
    def get_height_char(self):
        return self.get_height()  / self.cyy

    def get_width_char(self):
        return self.get_width() / self.cxx

    # --------------------------------------------------------------------
    # Goto position, put caret (cursor) back to view, [vh]scrap
    # distance from ends. This function was a difficult to write. :-{
    # Note the trick with comparing old cursor pos for a hint on scroll
    # direction.
    # xx, yy - absolute position in the text buffer

    def set_caret(self, xx, yy, ignore = False):

        if self.caretshot:
            self.caretshot = False; return
        self.caretshot = ignore

        #print( "set_caret", xx, yy)
        xx = int(xx); yy = int(yy)

        # Needs scroll?
        need_inval = False
        cww = self.get_width_char()
        chh = self.get_height_char()
        xlen = len(self.text)

        # ----------------------------------------------------------------
        # Put it back in view yyy:

        off = chh - self.vscgap
        if yy - self.ypos > off:
            #print( "Scroll from caret down")
            if yy > self.ypos + self.caret[1]:
                #print( "move d", "ypos", self.ypos, "yy", yy)
                self.ypos = int(yy - off)
                need_inval = True
                # Force new spell check
                self.fired += 1
                self.run_keytime()
                #self.mained.threads.submit_job(keytime, self, None)

        if yy - self.ypos < self.vscgap and self.ypos:
            #print( "Scroll from caret up")
            if yy < self.ypos + self.caret[1]:
                #print( "move u", "ypos", self.ypos, "yy", yy)
                self.ypos = int(yy - self.vscgap)
                self.ypos = int(max(self.ypos, 0))
                need_inval = True
                # Force new spell check
                self.fired += 1
                self.run_keytime()
                #self.mained.threads.submit_job(keytime, self, None)

        yy -= self.ypos
        if self.ypos < 0: self.ypos = 0

        # ----------------------------------------------------------------
        # Put it back in view xxx:

        xoff = cww - self.hscgap - self.strip / self.cxx
        if  xx - self.xpos  > xoff:
            #print( "Scroll from caret right", "xx", xx, "xpos", self.xpos)
            if self.xpos + self.caret[0] < xx:
                #print( "moved r",  xx, self.caret[0], self.xpos)
                self.xpos =  int(xx - xoff)
                self.xpos = int(max(self.xpos, 0))
                need_inval = True

        if  xx - self.xpos <  self.hscgap:
            #print( "Scroll from caret left ", xx, self.xpos)
            if self.xpos + self.caret[0] > xx:
                #print( "moved l", "xx", xx, "caret", self.caret[0], "xpos", self.xpos)
                self.xpos = int(xx - self.hscgap)
                self.xpos = int(max(self.xpos, 0))
                need_inval = True

        xx -= self.xpos
        if self.xpos < 0: self.xpos = 0

        oldx = self.caret[0] * self.cxx
        oldy = self.caret[1] * self.cyy

        # Cheat - invalidate all if tab is involved at old line
        try:
            line = self.text[oldy]
        except:
            line = ""; need_inval = True
        if line.find("\t") >= 0:
            need_inval = True

        self.caret[0] = xx; self.caret[1] = yy

        # Low limit
        if self.caret[0] < 0: self.caret[0] = 0
        if self.caret[1] < 0: self.caret[1] = 0

        wxx = self.caret[0] * self.cxx
        wyy = self.caret[1] * self.cyy

        # Cheat - invalidate all if tab is involoved
        try:
            line = self.text[self.ypos + self.caret[1]]
        except:
            line = ""; need_inval = True
        if line.find("\t") >= 0:
            need_inval = True

        # Optimize cursor movement invalidation
        '''if  not need_inval :
            rect = Gdk.Rectangle(wxx, wyy, self.cxx * self.cxx /2, self.cyy + 1)
            self.invalidate(rect)

            rect = Gdk.Rectangle(oldx, oldy, self.cxx + self.cxx /2 , self.cyy + 1)
            self.invalidate(rect)
        '''
        #self.invalidate(None)

        # Update scroll bars, prevent them from sending scroll message:
        self.oneshot = True; self.vscroll.set_value(self.ypos)
        self.honeshot = True; self.hscroll.set_value(self.xpos)

        self.update_bar2()

        if  need_inval or self.bigcaret:
            self.invalidate()

    def update_bar2(self):
        clip = pedconfig.conf.keyh.acth.currclip
        self.mained.update_statusbar2(self.caret[0] + self.xpos, \
                self.caret[1] + self.ypos, self.insert, len(self.text), clip,
                    self.caps, self.scr, self.colsel)

    def clearsel(self):
        old = self.xsel
        self.xsel  =  self.ysel = -1
        self.xsel2 =  self.ysel2 = -1
        if old != -1:
            self.invalidate()


    # Return True if 'C' like file
    # This is fooled by non extension items; not a big deal
    # colors may get turned on ...

    def is_c_like(self):
        #print("c like", self.fname)
        for aa in c_like_exts:
            eee = self.fname[-(len(aa)):]
            #print("eee", eee, aa)
            if aa == eee:
                #print("C Match", self.fname)
                return True

        return False

    def walk_func(self):

        #print( "walk func")

        # ts2 ---------------------------------------------------
        sumw2 = []
        if self.text:
            sline = self.caret[1] + int(self.ypos)
            sline = max(sline, 0); sline = min(sline, len(self.text))
            #print( "Start point", sline, self.text[sline])

            # Walk back to last function
            if self.is_c_like():
                try:
                    aa = 0; bb = 0
                    regex = re.compile(ckeywords)
                    for aa in range(sline - 1, 0, -1):
                        line = self.text[aa]
                        res = regex.search(line)
                        if res:
                            #print( "start", line, res.start(), res.end())
                            sumw2.append(line)
                            break
                    if aa > 0:
                        for bb in range(aa + 1, len(self.text)):
                            line = self.text[bb]
                            res = regex.search(line)
                            if res:
                                #print( "end", line, res.start(), res.end())
                                break

                        regex2 = re.compile(localkwords)
                        for cc in range(aa + 1, bb - 1):
                            line = self.text[cc]
                            res = regex2.search(line)
                            if res:
                                #print( "match", line, res.start(), res.end())
                                sumw2.append(line)

                except:
                    print("Exception in c func handler", sys.exc_info())
                    pass
            if ".bas" in self.fname.lower():
                try:
                    regex = re.compile(basekeywords)
                    for line in win.text:
                        res = regex.search(line)
                        if res:
                            #print( res, res.start(), res.end())
                            sumw.append(line)
                except:
                    print("Exception in bas func extraction handler", sys.exc_info())
                    pass
            if ".py" in self.fname.lower():
                try:
                    aa = 0; bb = 0
                    regex = re.compile("class")
                    for aa in range(int(sline) - 1, 0, -1):
                        line = self.text[aa]
                        res = regex.search(line)
                        if res:
                            #print( "start", line, res.start(), res.end())
                            sumw2.append(line)
                            break

                    regex = re.compile(pykeywords2)
                    for aa in range(int(sline) - 1, 0, -1):
                        line = self.text[aa]
                        res = regex.search(line)
                        if res:
                            #print( "start", line, res.start(), res.end())
                            sumw2.append(line)
                            break

                    if aa > 0:
                        for bb in range(aa + 1, len(self.text)):
                            line = self.text[bb]
                            res = regex.search(line)
                            if res:
                                #print( "end", line, res.start(), res.end())
                                break

                        regex2 = re.compile(localpywords)
                        for cc in range(aa + 1, bb - 1):
                            line = self.text[cc]
                            res = regex2.search(line)
                            if res:
                                #print( "match", line, res.start(), res.end())
                                sumw2.append(line)

                except:
                    print("Exception in py func handler", sys.exc_info())
                    raise
                    pass
            else:
                pass

            # Always show todo
            got_todo = 0
            for line in self.text:
                if "TODO" in line:
                    if not got_todo:
                        got_todo = 1
                        sumw2.append("----------- TODO List ----------")
                    sumw2.append(line)

        try:
            self.mained.update_treestore2(sumw2)
        except:
            # This is normal, ignore it
            print("walk2", sys.exc_info())
            pass

    # Call key handler
    def area_key(self, area, event):

        #print ("peddoc area_key", event.keyval)
        #return True # TEST

        # Restart timer ticks
        pedconfig.conf.idle = pedconfig.conf.IDLE_TIMEOUT
        pedconfig.conf.syncidle = pedconfig.conf.SYNCIDLE_TIMEOUT

        # Maintain a count of events, only fire only fire on the last one
        self.fired += 1
        self.run_keytime()

        #if not self.fired:
        #    self.mained.threads.submit_job(keytime, self, None)

        # The actual key handler
        try:
            self.keyh.handle_key(self, area, event)
        except:
            print("Key handler died at key", event.keyval, sys.exc_info())
            put_exception("key handler")

        #if event.type == Gdk.KEY_RELEASE:
        #    self.source_id = GObject.idle_add(self.idle_callback)

        # We handled it
        return True

     # Invalidate current line
    def inval_line(self):
        rect = Gdk.Rectangle()
        xx = self.caret[0] * self.cxx
        yy = self.caret[1] * self.cyy
        ww = self.get_width()
        hh = self.cyy
        #self.invalidate(rect)
        xx = 0
        self.queue_draw_area(xx, yy, ww, hh)

    def invalidate(self, rect = None):
        #print( "Invalidate:", rect)
        if rect == None:
            self.queue_draw()
        else:
            self.queue_draw_area(rect.x, rect.y,
                            rect.width, rect.height)

    def area_focus(self, area, event):
        #print( "ped doc area focus", event)
        return False

    # Add to user dictionary:
    def addict(self, widget, string, arg):
        #print( "addict", arg)
        if not pedspell.append_user_dict(self, arg):
            self.mained.update_statusbar("Cannot append to user dict")
        else:
            self.mained.update_statusbar("Added '%s' to user dict" % arg)
            self.newword = True

        # Force new spell check
        self.fired += 1
        self.run_keytime()
        #self.mained.threads.submit_job(keytime, self, None)

    def popspell(self, widget, event, xstr):
        # Create a new menu-item with a name...
        self.menu2 = Gtk.Menu()
        self.menu2.append(self.create_menuitem("Checking '%s'" % xstr, None))
        self.menu2.append(self.create_menuitem("Add to Dict", self.addict, xstr))

        mi = self.create_menuitem("-------------", None)
        mi.set_sensitive(False)
        self.menu2.append(mi)

        strs = "Creating suggestion list for '{0:s}'".format(self.spellstr)
        self.mained.update_statusbar(strs)
        arr = pedspell.suggest(self, xstr)

        if len(arr) == 0:
            self.menu2.append(self.create_menuitem("No Matches", None))
        else:
            for aa, bb in arr:
                self.menu2.append(self.create_menuitem
                        (bb, self.menuitem_response))

        self.menu2.popup(None, None, None, None, event.button, event.time)
        #self.mained.update_statusbar("Done menu popup.")

    def set_sidetab(self, arg1, arg2, arg3):
        # reset all
        #print("set_sidetab", arg1, arg2, arg3)
        www = self.mained.get_width()
        if arg3 == 0:
            if self.mained.hpaned3.get_position() > www - 20:
                self.mained.hpaned3.set_position(www - www / 3)
            self.mained.update_statusbar("Sidetab buffer switched on.")
            self.mained.diffpane.area.loadbuff(self.text)
            self.mained.diffpane.area.fname = self.fname
            self.mained.diffpane.area.readonly = True

            usleep(100)
            self.gotoxy(self.xpos + self.caret[0], self.ypos + self.caret[1])
            self.mained.diffpane.area.xpos = self.xpos
            self.mained.diffpane.area.ypos = self.ypos
            self.mained.diffpane.area.gotoxy(
                         self.xpos + self.caret[0], self.ypos + self.caret[1])
            usleep(10)
            self.mained.diffpane.area.invalidate()
            pppp = self.notebook3.get_nth_page(0)
            lab = self.mained.make_label("ro " + os.path.basename(self.fname))
            lab.set_tooltip_text(self.fname)
            self.notebook3.set_tab_label(pppp, lab)
        else:
            self.mained.hpaned3.set_position(www - 10)
            self.mained.update_statusbar("Sidetab buffer switched off.")
            pass

    def set_diffs(self, arg1, arg2, arg3):
        # reset all
        if arg3 == 0:
            nn = self.notebook.get_n_pages(); cnt = 0
            while True:
                if cnt >= nn: break
                ppp = self.notebook.get_nth_page(cnt)
                ppp.area.diffmode = 0
                ppp.area.set_tablabel()
                cnt += 1
            www = self.mained.get_width()
            self.mained.hpaned3.set_position(www - 10)

        else:
            self.diffmode = arg3
            self.set_tablabel()

            got_src = 0; got_targ = 0; action_page = 0;
            src = ""; targ = ""
            srctxt = [] ;  targtxt = []
            action_tab = None

            # See if diff complete, put it in motion
            nn = self.notebook.get_n_pages(); cnt = 0
            while True:
                if cnt >= nn: break
                ppp = self.notebook.get_nth_page(cnt)
                #print("Area", ppp.area.fname, ppp.area.diffmode)
                if ppp.area.diffmode == 1:
                    got_src = True
                    src = os.path.basename(ppp.area.fname)
                    srctxt = ppp.area.text

                if ppp.area.diffmode == 2:
                    got_targ = True
                    targ = os.path.basename(ppp.area.fname)
                    targtxt = ppp.area.text
                    action_page = cnt
                    action_tab = ppp

                if ppp.area.diffmode == 1:
                    got_src = True
                cnt += 1

            if got_src and got_targ:
                www = self.mained.get_width()
                if self.mained.hpaned3.get_position() > www - 20:
                    self.mained.hpaned3.set_position(www - www / 3)

                self.mained.update_statusbar(    \
                            "Diff started.  Source: '%s' Target: '%s'" % (src, targ))

                pppp = self.notebook3.get_nth_page(0)
                self.notebook3.set_tab_label(pppp,
                            self.mained.make_label("'" + src + "' --vs-- '" + targ + "'"))
                self.notebook.set_current_page(action_page)
                action_tab.area.diffx(srctxt, targtxt)

    # --------------------------------------------------------------------

    def diffx(self, srctxt, targtxt):
        arrx = []; forw = 0; forw2 = 0
        diffscan = 500
        for aa in range(len(targtxt)):
            try:
                if srctxt[aa + forw2] == targtxt[aa + forw]:
                    arrx.append(targtxt[aa + forw])
                    continue
                fff = False
                # Resync forward
                try:
                    for bb in range(diffscan):
                        ttt = targtxt[aa + forw + bb]
                        if srctxt[aa + forw2] == ttt:
                            for cc in range(bb):
                                strx = " --ins-- [ " + targtxt[aa + forw + cc] + " ] "
                                arrx.append(strx)
                            arrx.append(ttt)
                            forw += bb
                            #print("forward set", forw, ttt)
                            fff = True
                            break
                except:
                    pass #print("EOB while fw", ttt)

                if fff:
                    continue

                # Resync on the other file
                try:
                    for bb in range(diffscan):
                        ttt = srctxt[aa  + forw2 + bb]
                        if ttt ==  targtxt[aa + forw]:
                            for cc in range(bb):
                                strx = " --del-- [ " + srctxt[aa + forw2 + cc] + " ] "
                                arrx.append(strx)
                            arrx.append(targtxt[aa + forw])
                            forw2 += bb
                            #print("backward set", forw, ttt)
                            fff = True
                            break
                except:
                    pass #print("EOB while other fw")

                if fff:
                    continue

                # See if diff is small
                lendiff = len(srctxt[aa + forw2]) - len(targtxt[aa + forw])
                #print ("lendiff", lendiff, srctxt[aa], targtxt[aa+forw])
                if abs(lendiff) < 3:
                    strx = " --chg-- [ " + srctxt[aa + forw2] + " ] "
                else:
                    strx = " --ins-- [ " + targtxt[aa + forw] + " ] "
                    forw2 -= 1   # Stand still on the other
                arrx.append(strx)
                #print("could not resync")

            except:
                #print("Buffers are different lengths", sys.exc_info())
                pass

        self.mained.diffpane.area.loadbuff(arrx)
        usleep(100)
        self.gotoxy(self.xpos + self.caret[0], self.ypos + self.caret[1])

        self.mained.diffpane.area.xpos = self.xpos
        self.mained.diffpane.area.ypos = self.ypos
        self.mained.diffpane.area.gotoxy(
                         self.xpos + self.caret[0], self.ypos + self.caret[1])
        usleep(10)
        self.mained.diffpane.area.invalidate()


    def iterdocs(self, callb, arg):
        nn = self.notebook.get_n_pages(); cnt = 0
        while True:
            if cnt >= nn: break
            ppp = self.notebook.get_nth_page(cnt)
            #print("Area", ppp.area.fname, ppp.area.diffmode)
            callb(ppp.area, arg)
            cnt += 1

    def builddoc(self, ppp):
        if ppp.area.diffmode == 1:
            got_src = True
        if ppp.area.diffmode == 2:
            got_targ = True

    def set_ro(self, arg1, arg2, arg3):
        print("set_ro")

    def re_diff(self, arg1, arg2, arg3):
        got_src = 0; got_targ = 0; action_page = 0;
        src = ""; targ = ""
        srctxt = [] ;  targtxt = []
        action_tab = None

        # See if diff complete, put it in motion
        nn = self.notebook.get_n_pages(); cnt = 0
        while True:
            if cnt >= nn: break
            ppp = self.notebook.get_nth_page(cnt)
            #print("Area", ppp.area.fname, ppp.area.diffmode)
            if ppp.area.diffmode == 1:
                got_src = True
                src = os.path.basename(ppp.area.fname)
                srctxt = ppp.area.text

            if ppp.area.diffmode == 2:
                got_targ = True
                targ = os.path.basename(ppp.area.fname)
                targtxt = ppp.area.text
                action_page = cnt
                action_tab = ppp

            if ppp.area.diffmode == 1:
                got_src = True
            cnt += 1

        if got_src and got_targ:
            www = self.mained.get_width()
            if self.mained.hpaned3.get_position() > www - 20:
                self.mained.hpaned3.set_position(www - www / 3)

            self.mained.update_statusbar(    \
                        "Diff re-started.  Source: '%s' Target: '%s'" % (src, targ))

            self.notebook.set_current_page(action_page)
            action_tab.area.diffx(srctxt, targtxt)


    def poprclick3(self, event):
        #print ("Making shift rclick3")
        if self.nomenu: return

        got_src = 0; got_targ = 0

        nn = self.notebook.get_n_pages(); cnt = 0
        while True:
            if cnt >= nn: break
            ppp = self.notebook.get_nth_page(cnt)
            #print("Area", ppp.area.fname, ppp.area.diffmode)
            if ppp.area.diffmode == 1:
                got_src = True
            if ppp.area.diffmode == 2:
                got_targ = True
            cnt += 1

        # Check if there is any:
        nn = self.notebook.get_n_pages(); cnt = 0
        while True:
            if cnt >= nn: break
            ppp = self.notebook.get_nth_page(cnt)
            #print("Area", ppp.area.fname, ppp.area.diffmode)
            if ppp.area.diffmode == 1:
                got_src = True
            if ppp.area.diffmode == 2:
                got_targ = True
            cnt += 1

        self.menu3 = Gtk.Menu()
        if not got_src:
            self.menu3.append(self.create_menuitem("Set as Diff Source", self.set_diffs, 1))
        if not got_targ:
            self.menu3.append(self.create_menuitem("Set as Diff Target", self.set_diffs, 2))
        else:
            self.menu3.append(self.create_menuitem("Re-Diff Buffers",  self.re_diff, 0))

        self.menu3.append(self.create_menuitem("Stop Diffing",  self.set_diffs, 0))
        self.menu3.append(self.create_menuitem("- - - - - - - - - - - - - - - ",  None, 0))
        self.menu3.append(self.create_menuitem("Show Buffer in Sidetab",  self.set_sidetab, 0))
        self.menu3.append(self.create_menuitem("Hide Sidetab",  self.set_sidetab, 1))

        #mi = self.create_menuitem("-------------", None)
        #mi.set_sensitive(False); self.menu3.append(mi)
        #self.menu3.append(self.create_menuitem("Toggle Read Only",  self.set_ro, 0))

        self.menu3.popup(None, None, None, None, event.button, event.time)

    def poprclick2(self, widget, event, strx):
        #print ("Making shift rclick2")
        if self.nomenu: return

        self.menu2 = Gtk.Menu()
        self.menu2.append(self.create_menuitem("Checking '%s'" % strx, None))
        mi = self.create_menuitem("-------------", None)
        mi.set_sensitive(False)
        self.menu2.append(mi)
        strs = "Creating class list for '{0:s}'".format(strx)
        self.mained.update_statusbar(strs)
        arr = pedstruct.suggest(self, strx)
        if len(arr) == 0:
            self.menu2.append(self.create_menuitem("No Matches", None))
        else:
            for bb in arr:
                self.menu2.append(self.create_menuitem(bb, self.menuitem_response2))

        self.menu2.popup(None, None, None, None, event.button, event.time)

    def poprclick(self, widget, event):

        if self.nomenu: return

        #print ("Making rclick")
        self.build_menu(self, pedmenu.rclick_menu)
        if event:
            self.menu.popup(None, None, None, None, event.button, event.time)
        else:
            event = Gdk.EventButton()
            self.menu.popup(None, None, None, None, event.button, event.time)

    def menuitem_response2(self, widget, stringx, arg):
        #print( "menuitem response2 '%s'" % stringx)
        #print( "Original str '%s'" % self.spellstr)
        disp2 = Gdk.Display()
        disp = disp2.get_default()
        clip = Gtk.Clipboard.get_default(disp)
        stringx = stringx.strip()
        clip.set_text(stringx, len(stringx))
        strs = "Copied to clipboard '{0:s}'".format(stringx)
        self.mained.update_statusbar(strs, True)

    def menuitem_response(self, widget, stringx, arg):
        #print( "menuitem response '%s'" % stringx)
        #print( "Original str '%s'" % self.spellstr)

        # See if Capitalized or UPPERCASE :
        if self.spellstr[0] in string.ascii_uppercase:
            stringx = stringx.capitalize()

        if self.spellstr.isupper():
            stringx = stringx.upper()

        pedconfig.conf.keyh.acth.clip_cb(None, stringx, self, False)

        self.fired += 1
        self.run_keytime()
        #self.mained.threads.submit_job(keytime, self, None)

    def activate_action(self, action):
        dialog = Gtk.MessageDialog(self, Gtk.DIALOG_DESTROY_WITH_PARENT,
            Gtk.ButtonsType.INFO, Gtk.ButtonsType.CLOSE,
            'You activated action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        dialog.connect ("response", lambda d, r: d.destroy())
        dialog.show()

    def rclick_action(self, action, sss, ttt):

        print( "rclick_action", sss, ttt)

        if ttt == 1:
            self.mained.newfile()
        elif ttt == 3:
            self.mained.open()
        elif ttt == 4:
            self.mained.save()
        elif ttt == 5:
            self.mained.save(True)
        elif ttt == 7:
            self.mained.copy()
        elif ttt == 8:
            self.mained.cut()
        elif ttt == 9:
            self.mained.paste()
        elif ttt == 11:
            self.toggle_ro()
        elif ttt == 13:
            print("menu exit")
            self.mained.activate_exit()
        elif ttt == 14:
             pedconfig.conf.pedwin.start_term()
        elif ttt == 15:
            self.start_edit(self.fname)
        elif ttt == 16:
            self.mained.tts()
        elif ttt == 17:
            pedmisc.exec_test(self, "rc")
        elif ttt == 18:
            self.start_external(["libreoffice", "--writer"],
                                        ["libreoffice", "--writer"])
        elif ttt == 19:
            self.start_m4filter()
        elif ttt == 20:
            self.start_mdfilter()
        elif ttt == 21:
            self.start_browser(self.fname)
        elif ttt == 22:
            self.start_htmlwin(self.fname)
        elif ttt == 23:
            self.start_htmlstr()
        elif ttt == 24:
            self.start_external(["thunar", "."], # Caja ?
                                        ["explorer", ""])
        elif ttt == 25:
            self.rescan()
        elif ttt == 26:
            self.find(self)
        elif ttt == 27:
            #print("Alt-Y")
            self.check_syntax()
        else:
            print("peddoc: Invalid menu item selected")

    def rescan(self):
        global last_scanned
        last_scanned = ""
        run_async_time(self, 0)
        self.mained.update_statusbar("Started rescan ...")

    def toggle_ro(self):
        self.readonly = not self.readonly
        self.set_tablabel()
        arrx = ["OFF", "ON"]
        self.mained.update_statusbar("Toggled read only to %s" % arrx[self.readonly])

    def create_menuitem(self, string, action, arg = None):
        rclick_menu = Gtk.MenuItem(string)
        if action:
            rclick_menu.connect("activate", action, string, arg)
        rclick_menu.show()
        return rclick_menu

        # Create the menubar and toolbar
        action_group = Gtk.ActionGroup("DocWindowActions")
        action_group.add_actions(entries)
        return action_group

    def build_menu(self, window, items):

        self.menu =  Gtk.Menu()
        for aa, bb, cc, dd, ee  in items:
            #print ("menu item", aa)
            if ee:
                menu_item = Gtk.MenuItem.new_with_mnemonic(
                            "----------------------------")
                menu_item.set_sensitive(False)
                menu_item.set_size_request(-1, 10)
                pass
            else:
                ttt = str(bb).replace("<control>", "CTRL+")
                ttt = str(ttt).replace("<alt>",     "ALT+")
                ttt = str(ttt).replace("<shift>",   "SHIFT+")
                fff = " " * (15 - len(aa))
                sss = aa + "%s\t%s" % (fff, ttt)
                menu_item = Gtk.MenuItem.new_with_mnemonic(sss)
                menu_item.connect("activate", self.rclick_action, aa, dd )

            self.menu.append(menu_item)
        self.menu.show_all()
        return self.menu

    def get_size(self):
        rect = self.get_allocation()
        return rect.width, rect.height

    def get_height(self):
        rect = self.get_allocation()
        return rect.height

    def get_width(self):
        rect = self.get_allocation()
        return rect.width

    def save(self):

        #print ("Saving", self.fname)
        # Always save params
        self.saveparms()
        strx = ""
        if not self.changed:
            strx = "File is not modified."
            self.mained.update_statusbar(strx)
            return

        # Is this file named 'untitled'?
        base, ext =  os.path.splitext(pedconfig.conf.UNTITLED)
        base1 = os.path.basename(self.fname)
        base2, ext2 =  os.path.splitext(base1)
        if base2[:len(base)] == base:
            self.file_dlg(Gtk.ResponseType.YES)
        else:
            bn = os.path.basename(self.fname)
            err = self.writeout()
            if  err[0]:
                strx = "Saved '{0:s}'".format(self.fname)
            else:
                #strx = "Not Saved '{0:s}' {1:s}".format(bn, err[1])
                strx = "Not Saved "

        if pedconfig.conf.verbose:
            print(strx)
        self.mained.update_statusbar(strx)

    def saveas(self):
        self.file_dlg(Gtk.ResponseType.YES)

    def coloring(self, flag):
        self.colflag = flag
        self.invalidate()

    def showcol(self, flag):
        self.scol = flag
        self.invalidate()

    def hexview(self, flag):
        self.hex = flag
        self.invalidate()

    def flash(self, flag):
        self.bigcaret = flag
        self.invalidate()

    def showtab(self, flag):
        self.stab = flag
        self.scol = flag
        self.invalidate()

    def closedoc(self, noprompt = False):
        #self.stopthread = True
        strx = "Closing '{0:s}'".format(self.fname)
        if pedconfig.conf.verbose:
            print("Closing doc:", strx)
        self.mained.update_statusbar(strx)
        self.saveparms()

        rrr = self.prompt_save(noprompt)
        if not rrr:
            # Clear treestore(s)
            self.mained.update_treestore([])
            self.mained.update_treestore2([])
            # Add to accounting:
            logentry("Closed File", self.start_time, self.fname)
            self.mained.oh.add(self.fname)
        return rrr

    # --------------------------------------------------------------------
    # Load file into this buffer, return False on failure

    def loadfile(self, filename, create = False, reload = True):

        if not self.second:
            if pedconfig.conf.verbose > 1:
                print("Loading file", filename)

        if not reload:
            # Is it already loaded? ... activate
            nn = self.notebook.get_n_pages()
            fname2 = os.path.realpath(filename)
            for aa in range(nn):
                vcurr = self.notebook.get_nth_page(aa)
                if vcurr.area.fname == fname2:
                    if pedconfig.conf.verbose:
                        print("Already open '"+ fname2 + "'")
                    self.mained.update_statusbar("Already open, activating '{0:s}'".format(fname2))
                    vcurr = self.notebook.set_current_page(aa)
                    vcurr = self.notebook.get_nth_page(aa)
                    self.mained.mywin.set_focus(vcurr.vbox.area)
                    return

        if not self.second:
            self.mained.oh.add(filename)

        self.fname = filename
        self.ext = os.path.splitext(self.fname)[1].lower()

        try:
            self.stat = os.stat(self.fname)
        except:
            pass

        #pedync.message("\n   open / read file:  \n\n"
        #                      "      %s" % self.fname)

        #print("stat", self.stat.st_mtime)
        self.start_time = time.time()
        if self.fname == "":
            strx = "Must specify file name."
            print(strx)
            self.mained.update_statusbar(strx)
            return False
        try:
            self.text = readfile(self.fname)
        except:
            errr = "Cannot read file '" + self.fname + "'" #, sys.exc_info()
            if pedconfig.conf.verbose:
                print(errr, sys.exc_info())

            #pedync.message("\n   Cannot open / read file:  \n\n"
            #                  "      %s" % self.fname)

            print(errr)
            self.mained.update_statusbar(errr)
            usleep(10)
            return False

        #self.ularr.append((10 ,10, 20))
        mlen = self.calc_maxline()

        # Set up scroll bars
        self.set_maxlinelen(mlen, False)
        self.set_maxlines(len(self.text), False)

        # Increment and wrap backup
        if not self.second:
            hhh = hash_name(self.fname)
            self.currback  =  pedconfig.conf.sql.get_int(hhh + "/bak")
            self.currback += 1
            if self.currback >= 9:
                self.currback = 1
            pedconfig.conf.sql.put(hhh + "/bak", self.currback)

        # File and backup related
        if not self.second:
            self.loadundo()
            self.loadparms()
            self.saveorg()
            self.savebackup()

            # Add to accounting:
            logentry("Opened File", self.start_time, self.fname)

        # Propagate main wndow ref
        pedmenu.mained = self.mained

        self.set_nocol()

        try:
            os.chdir(os.path.dirname(self.fname))
        except:
            print("Cannot change dir to file's cwd", sys.exc_info())

        # Let the system breed
        self.invalidate()
        usleep(10)

        # Color ON?
        self.set_nocol()

        # Are most of them read only?
        if not self.second:
            ro = 0
            nn = self.notebook.get_n_pages()
            for aa in range(nn):
                vcurr = self.notebook.get_nth_page(aa)
                #print("listing",  vcurr.area.fname, vcurr.area.readonly)
                if vcurr.area.readonly:
                    ro += 1
            #print("nn", nn, "ro count", ro)
            if ro > nn // 2:
                self.readonly = True

        return True

    def loadbuff(self, arrx):
        self.text = arrx
        usleep(1)
        # Set up scroll bars and other parameters
        mlen = self.calc_maxline()
        self.set_maxlinelen(mlen, False)
        self.set_maxlines(len(self.text), False)
        self.changed = True

    def calc_maxline(self):
        mlen = 0
        for aa in self.text:
            xlen = len(aa)
            if mlen < xlen:
                mlen = xlen
        #self.maxlinelen = mlen
        return mlen

    # Load per file parms (cursor etc)
    def loadparms(self):
        hhh = hash_name(self.fname)

        self.startxxx  =  pedconfig.conf.sql.get_int(hhh + "/xx")
        self.startyyy  =  pedconfig.conf.sql.get_int(hhh + "/yy")
        #print("got cursor pos:", self.fname, self.startxxx, self.startyyy)
        # Note: we set cursor on first focus

    # Save per file parms (cursor, fname, etc)
    def  saveparms(self):
        hhh = hash_name(self.fname)
        pedconfig.conf.sql.put(hhh + "/xx", self.xpos + self.caret[0])
        pedconfig.conf.sql.put(hhh + "/yy", self.ypos + self.caret[1])
        pedconfig.conf.sql.put(hhh + "/fname", self.fname)

        if self.tts:
            self.tts.haltspeak = True

        #print  "saveparm", time.clock() - got_clock

    # Create org backup
    def saveorg(self):
        hhh = hash_name(self.fname) + ".org"
        xfile = pedconfig.conf.data_dir + os.sep + hhh
        if not os.path.isfile(xfile):
            err =  writefile(xfile, self.text, "\n")
            if not err[0]:
                print("Cannot create (org) backup file", xfile, sys.exc_info())
            # Make a log entry
            logfile = pedconfig.conf.log_dir + os.sep + "backup.log"
            xentry = "Org " + time.ctime() + " " + \
                self.fname + " " + os.path.basename(xfile)
            writefile(logfile, (xentry, ""), "\n", "a+")

   # Create backup
    def savebackup(self):

        hhh = hash_name(self.fname)
        self.startxxx  =  pedconfig.conf.sql.get_int(hhh + "/xx")

        try:
            xfile = pedconfig.conf.data_dir + os.sep + hhh + "_" + str(self.currback) + ".bak"
            if pedconfig.conf.verbose > 2:
                print("Saving backup: ", xfile)

            try:
                writefile(xfile, self.text, "\n")
            except:
                print("Cannot create backup file " + xfile, sys.exc_info())
        except:
            print("Cannot back up ", sys.exc_info())


    def prompt_save(self, askname = True):

        # Always save params
        self.saveparms()

        if not self.changed:
            #print "not changed", self.fname
            return False

        msg = "\nWould you like to save:\n\n  \"%s\" \n" % self.fname
        rp = pedync.yes_no_cancel("pyedpro: Save File ?", msg)

        if rp == Gtk.ResponseType.YES:
            if askname:
                self.file_dlg(rp)
            else:
                self.save()
        elif rp == Gtk.ResponseType.NO:
            pass
        elif  rp == Gtk.ResponseType.CANCEL:
            return True
        else:
            print("warning: invalid response from dialog")

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

    # --------------------------------------------------------------------
    # The actual savefile routine

    def writeout(self):

        if pedconfig.conf.verbose:
            print("Saving '"+ self.fname + "'")

        if os.access(self.fname, os.F_OK):
            #wasread = os.access(self.fname, os.R_OK)
            #if not wasread:
            #    print("Cannot read '%s'" % self.fname,  sys.exc_info())
            #    self.mained.update_statusbar("Cannot read '%s'" % self.fname)
            #    return

            waswrite = os.access(self.fname, os.W_OK)
            if not waswrite:
                print("Cannot write '%s'" % self.fname,  sys.exc_info())
                self.mained.update_statusbar("Cannot write '%s'" % self.fname)
                self.savebackup()

                pedync.message("\n   Cannot Save file:  \n\n"
                                  "      '%s'" % self.fname)
                return (False, "Read only or Inaccessible file")

        err = writefile(self.fname, self.text, "\n")
        #print("err writefile", err)
        if not err[0]:
            print("Cannot write '%s'" % self.fname,  sys.exc_info())
            return

        self.set_changed(False)
        # Change access/ownership to group write
        try:
            ostat = os.stat(self.fname)
            os.chmod(self.fname, ostat.st_mode | stat.S_IWGRP)
        except:
            print("Cannot change group write on '%s'" % self.fname,  sys.exc_info())

        self.saveundo();  self.saveparms(); self.set_tablabel()

        # Add to accounting:
        logentry("Wrote File", self.start_time, self.fname)

        # Update stat info
        self.stat = os.stat(self.fname)

        return err

    def delundo(self):
        self.undoarr = []; self.redoarr = []
        # Remove file
        hhh = hash_name(self.fname) + ".udo"
        xfile = pedconfig.conf.data_dir + os.sep + hhh
        fh = open(xfile, "w")
        fh.close()
        hhh = hash_name(self.fname) + ".rdo"
        xfile = pedconfig.conf.data_dir + os.sep + hhh
        fh = open(xfile, "w")
        fh.close()

    def saveundo(self):
        hhh = hash_name(self.fname) + ".udo"
        xfile = pedconfig.conf.data_dir + os.sep + hhh
        try:
            fh = open(xfile, "wb")
            pickle.dump(self.undoarr, fh)
            fh.close()
        except:
            print("Cannot save undo file", sys.exc_info())
            put_exception("undo")


        hhh = hash_name(self.fname) + ".rdo"
        xfile = pedconfig.conf.data_dir + os.sep + hhh
        try:
            fh = open(xfile, "wb")
            pickle.dump(self.redoarr, fh)
            fh.close()
        except:
            print("Cannot save redo file", sys.exc_info())

    def loadundo(self):
        hhh = hash_name(self.fname) + ".udo"
        xfile = pedconfig.conf.data_dir + os.sep + hhh
        try:
            fh = open(xfile, "rb")
            try:
                self.undoarr = pickle.load(fh)
            except:
                pass
            fh.close()
        except:
            pass
            # Ignore it, not all files will have undo
            #print( "Cannot load undo file", xfile)
        self.initial_undo_size = len(self.undoarr)

        hhh = hash_name(self.fname) + ".rdo"
        xfile = pedconfig.conf.data_dir + os.sep + hhh
        try:
            fh = open(xfile, "rb")
            try:
                self.redoarr = pickle.load(fh)
            except:
                pass
            fh.close()
        except:
            pass
            # Ignore it, not all files will have redo
            #print( "Cannot load redo file", xfile)
        self.initial_redo_size = len(self.redoarr)

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
                        self.ext = os.path.splitext(self.fname)[1].lower()
                        self.writeout()
                        self.mained.update_statusbar("Saved under new filename '%s'" % fname)
                    else:
                        self.mained.update_statusbar("No new file name supplied, cancelled 'Save As'")
                else:
                    self.fname = fname
                    self.ext = os.path.splitext(self.fname)[1].lower()
                    self.writeout()

                pedconfig.conf.pedwin.mywin.set_title("pyedpro: " + self.fname)

        win.destroy()

    def overwrite_done(self, win, resp, fname, win2):
        #print( "overwrite done", resp)
        if resp == Gtk.ResponseType.YES:
            self.fname = fname
            self.ext = os.path.splitext(self.fname)[1].lower()
            self.writeout()
            self.set_nocol()
            win2.destroy()
        win.destroy()

    # --------------------------------------------------------------------
    # Turn off coloring if not python / c / sh / perl / header(s)

    def set_nocol(self):
        colflag = False
        ext = os.path.splitext(self.fname)[1].lower()
        for aa in pedconfig.conf.color_on:
            if ext == aa:
                colflag = True
                break
        self.colflag = colflag


    def do_chores(self):
        #print( "do_chores")
        if  not self.needscan:
            return
        self.needscan = False

        # Scan left pane
        pedconfig.conf.idle = pedconfig.conf.IDLE_TIMEOUT
        pedconfig.conf.syncidle = pedconfig.conf.SYNCIDLE_TIMEOUT

    def set_changed(self, flag):
        old = self.changed
        self.changed = flag
        # Exec actions:
        if old != self.changed:
            #print( "Setting changed on ", self.fname)
            self.set_tablabel()

    def set_tablabel(self):
        # Find me in tabs
        #print("Setting tablabels")
        nn = self.notebook.get_n_pages(); cnt = 0
        while True:
            if cnt >= nn: break
            ppp = self.notebook.get_nth_page(cnt)
            if ppp.area == self:
                self._setlabel(ppp)
                break
            cnt += 1
            #usleep(10)

    # Gdk.EventButton
    def doclabel_callb(self, widg, event):
        #print("doclabel_callb", event.button, event.type)
        if event.button == 3:
            #print("Right click", self.fname)
            self.poprclick3(event)

    def _setlabel(self, ppp):

        # Set label to tab
        ss = shortenstr(os.path.basename(self.fname), 24)
        if  self.changed:
            str2 = "* " + ss + "  "
        else:
            str2 = "  " + ss + "  "

        if  self.readonly:
            str3 = "ro " + str2
        else:
            str3 = "  " + str2

        if  self.diffmode == 1:
            str4 = "Diff/Source: " + str3
        elif  self.diffmode == 2:
            str4 = "Diff/Target: " + str3
        else:
            str4 = "" + str3

        label = Gtk.Label.new(str4)
        label.set_tooltip_text(self.fname)
        label.set_single_line_mode(True)

        eb = Gtk.EventBox(); eb.add(label)
        eb.connect_after("button-press-event", self.doclabel_callb)
        eb.set_above_child(True)

        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
        butt = Gtk.Button();  butt.add(image)
        butt.set_focus_on_click(False)
        butt.set_relief( Gtk.ReliefStyle.NONE)
        #rc = butt.get_modifier_style()
        #rc.xthickness = 1; rc.ythickness = 1
        #butt.modify_style(rc)

        butt.connect("clicked", self.close_button)
        butt.set_tooltip_text("Close '%s'" % os.path.basename(self.fname))
        hbox = Gtk.HBox()
        hbox.pack_start(eb, 0, 0, 0)
        hbox.pack_start(butt, 0, 0, 0)
        hbox.show_all()
        self.notebook.set_tab_label(ppp, hbox)
        hbox.queue_draw()

        #usleep(10)
        #print("Setting tablabel", str4)

    def close_button(self, arg1):
        #print( "close_button", arg1)
        # Select me first
        self.mained.close_document(self)

    # --------------------------------------------------------------------
    def savemacro(self):

        #print( "Savemacro")

        if not self.recarr:
            print("Cannot save, nothing recorded yet.")
            pedync.message("\n   Cannot save macro: nothing recorder yet.  \n\n")
            return

        fname = "untitled.mac"
        xdir = pedconfig.conf.config_dir + "/macros/"
        xfile = pedconfig.conf.config_dir + "/macros/" + fname
        old = os.getcwd()
        try:
            os.chdir(os.path.dirname(xfile))
        except:
            print("No macros directory", sys.exc_info())

        warnings.simplefilter("ignore")
        buts =   "Cancel", Gtk.ButtonsType.CANCEL, "Save Macro", Gtk.ButtonsType.OK
        fc = Gtk.FileChooserDialog("Save Macro", None, Gtk.FileChooserAction.SAVE, \
            buts)

        fc.set_current_folder(xdir)
        fc.set_current_name(os.path.basename(xfile))
        fc.set_default_response(Gtk.ButtonsType.OK)
        fc.connect("response", self.done_mac_fc, old)
        fc.run()
        warnings.simplefilter("default")

    def done_mac_fc(self, win, resp, old):
        #print(  "done_mac_fc", resp)
        # Back to original dir
        os.chdir(os.path.dirname(old))
        if resp == Gtk.ButtonsType.OK:

            #print("saveing", self.recarr)

            try:
                fname = win.get_filename()
                if not fname:
                    print("Must have filename")
                else:
                    fh = open(fname, "wb")
                    pickle.dump(self.recarr, fh)
                    fh.close()
            except:
                print("Cannot save macro file", sys.exc_info())
                self.mained.update_statusbar("Cannot save macro: '%s'" \
                                % os.path.basename(fname))

        win.destroy()

    def loadmacro(self):
        #print( "Loadmacro")

        xfile = pedconfig.conf.config_dir + "/macros/"
        old = os.getcwd()
        try:
            os.chdir(os.path.dirname(xfile))
        except:
            print("No macros directory", sys.exc_info())

        but =   "Cancel", Gtk.ButtonsType.CANCEL, "Load Macro", Gtk.ButtonsType.OK
        fc = Gtk.FileChooserDialog("Load Macro", None, Gtk.FileChooserAction.OPEN, \
            but)

        fc.set_current_folder(xfile)
        #fc.set_current_folder(old)
        fc.set_default_response(Gtk.ButtonsType.OK)
        fc.connect("response", self.done_mac_open_fc, old)
        fc.run()

    def done_mac_open_fc(self, win, resp, old):

        #print(  "done_mac_fc", resp)
        # Back to original dir
        os.chdir(os.path.dirname(old))

        if resp == Gtk.ButtonsType.OK:
            try:
                fname = win.get_filename()
                if not fname:
                    print("Must have filename")
                else:
                    fh = open(fname, "rb")
                    self.recarr = pickle.load(fh)
                    fh.close()
                    #print("macro", self.recarr)

            except:
                print("Cannot load macro file", sys.exc_info())
                self.mained.update_statusbar("Cannot load macro: '%s'" % os.path.basename(fname))

        win.destroy()

    def     find(self, dlg, flag = False):
        #print("find", dlg);
        pedfind.find(dlg, self, flag)

    # Refresh current search buffer
    def search_again(self):
        if len(self.accum) == 0:
            return

        if self.src_changed:
            self.search(self.srctxt, self.regex, self.boolcase, self.boolregex)

    # --------------------------------------------------------------------
    def search(self, srctxt, regex, boolcase, boolregex):

        # Remember old settings:
        self.srctxt = srctxt;       self.regex = regex
        self.boolcase = boolcase;   self.boolregex = boolregex
        self.src_changed = False

        self.accum = []

        curr  = self.caret[1] + self.ypos
        currx = self.caret[0] + self.xpos

        was = -1; cnt = 0; cnt2 = 0
        before = 0; after = 0
        marked = False

        for line in self.text:
            # Search one line for multiple matches
            mmm = src_line(line, cnt, srctxt, regex, boolcase, boolregex)

            # Add marker to current lin
            if cnt == curr:
                if not marked:
                    linex =  str(currx) + ":"  + str(cnt) +\
                         ":" + str(0) + " " +\
                             "---- current cursor position ----"
                    self.accum.append(linex)
                    marked = True

            # Mark the next match for the display
            if cnt > curr and was == -1:
                was = cnt2
            if  mmm:
                #print("mmm", mmm);

                # Multiple counts may be there
                for sss in mmm:
                    cnt2 += 1
                    # Mark the counters
                    if cnt <= curr:
                        before += 1
                    else:
                        after += 1
                    self.accum.append(sss)

            if cnt % 100 == 0:
                self.mained.update_statusbar(\
                            "Searching at %d" % cnt, True)
                usleep(1)
            cnt += 1

        #if not marked:
        #    self.accum.append(" ---- current cursor position ---- ")
        #    marked = True

        return was, cnt2, before, after

    def check_syntax(self):

        tempfile = "tmp"
        writefile(tempfile, self.text, "\n")

        #print("Checking file", self.ext)

        if self.ext == ".php" or  self.ext == ".inc":
            #print("Checking PHP file")
            try:
                comline = ["php", "-l", tempfile,]
                try:
                    ret = subprocess.Popen(comline, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                except:
                    print("Cannot check %s" % str(comline), sys.exc_info())
                    pedync.message("\n   Cannot check %s \n\n"  % str(comline) +
                               str(sys.exc_info()) )
                    return
                try:
                    outs, errs = ret.communicate()
                except:
                    print("Cannot communicate with %s" % str(comline), sys.exc_info())
                    return

            except:
                print("Cannot execute %s" % str(comline), sys.exc_info())
                pass

            #print("outs", outs, "errs", errs)

            if errs == b"":
                pedync.message("\n  PHP Syntax OK   \n")
                self.mained.update_statusbar("Syntax OK.")
            else:
                serr = str(errs)
                idx = serr.find("line ")
                if idx:
                    #print("idx", idx, "line no", "'" + serr[idx + 5:] + "'")
                    self.gotoxy(10, atoi(serr[idx + 5:]) - 1)

                print("Error on compile: '", serr, "'")
                pedync.message("    " + serr + "    ")


        elif self.ext == ".py":
            try:
               py_compile.compile('tmp', doraise = True)
            except py_compile.PyCompileError as msg:

                self.mained.update_statusbar("Syntax error.")

                if sys.version_info.major < 3:
                    try:
                        ln  = msg[2][1][1]; col = msg[2][1][2]
                        mmm = "\n" + msg[2][0] + "\n\n    Ln: " +  str(ln) + " Col: " + str(col)
                        self.gotoxy(col - 1, ln - 1)
                        pedync.message("    " + mmm + "    ", msg[1])
                    except:
                        pedync.message(" " + str(msg) + "  ", "Syntax Error")
                        #print("line", msg);
                        pass
                else:
                        print("Error on compile: '", msg.args, "'")
                        zzz = str(msg.args[2]).split("(")
                        sss = zzz[1].split()[2].replace(")", "")
                        #print ("sss", sss)
                        try:
                            self.gotoxy(10, int(sss) - 1)
                        except:
                            pass
                        pedync.message("    " + str(msg) + "    ")

            except:
                print(sys.exc_info())
            else:
                pedync.message("\n  PY Syntax OK   \n")
                self.mained.update_statusbar("Syntax OK.")
            finally:
                pass

        elif self.ext == ".js":

            tempfile2 = "tmp.js"
            os.rename(tempfile, tempfile2)
            tempfile = tempfile2

            print("Checking JS file")
            try:
                comline = ["node", "--check", tempfile2,]
                try:
                    ret = subprocess.Popen(comline, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                except:
                    print("Cannot check %s" % str(comline), sys.exc_info())
                    pedync.message("\n   Cannot check %s \n\n"  % str(comline) +
                               str(sys.exc_info()) )
                    return
                try:
                    outs, errs = ret.communicate()
                except:
                    print("Cannot communicate with %s" % str(comline), sys.exc_info())
                    return

            except:
                print("Cannot execute %s" % str(comline), sys.exc_info())
                pass

            #print("outs", outs, "errs", errs)

            if errs == b"":
                pedync.message("\n  JS Syntax OK   \n")
                self.mained.update_statusbar("Syntax OK.")
            else:
                serr = str(errs)
                idx = serr.find("line ")
                if idx:
                    #print("idx", idx, "line no", "'" + serr[idx + 5:] + "'")
                    self.gotoxy(10, atoi(serr[idx + 5:]) - 1)

                print("Error on compile: '", serr, "'")
                pedync.message("    " + serr + "    ")

        else:
            self.mained.update_statusbar("No Syntax check for this kind of file.")

        os.remove(tempfile)


# ------------------------------------------------------------------------
# Run this on an idle callback so the user can work while this is going

def run_async_time(win, arg):

    global last_scanned

    #print( "run_async_time enter", win.fname)

    if  last_scanned == win:
        #print("Not rescanning", win.fname)
        return

    last_scanned = win

    win.mained.start_tree()

    #print( "run_sync_time", time.time())

    if not win.text:
        return

    sumw = [] ; lname = win.fname.lower()

    #print("lname", lname[-2:])

    # Added flex and yacc
    if ".c" in lname[-2:] or ".h" in lname[-2:] or ".y" \
        in lname[-2:] or ".f" in lname[-2:] or ".php" in lname[:-4]:
        try:
            regex = re.compile(ckeywords)
            for line in win.text:
                res = regex.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append(line)
        except:
            print("Exception in c func handler", sys.exc_info())
            pass

    elif ".py" in lname[-3:]:
        try:
            regex = re.compile(pykeywords2)
            for line in win.text:
                res = regex.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append(line)

            regex3 = re.compile(pykeywords3)
            for line in win.text:
                res = regex3.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append("    " + line)
        except:
            print("Exception in py func handler", sys.exc_info())
            pass
    elif ".html" in lname[-5:]:
        #print("html file")
        try:
            regex = re.compile(htmlkeywords)
            for line in win.text:
                res = regex.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append(line)
        except:
            print("Exception in py func handler", sys.exc_info())
            pass
    elif ".bas" in lname[-4:]:
        try:
            regex = re.compile(basekeywords)
            for line in win.text:
                res = regex.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append(line)
        except:
            print("Exception in func extraction handler", sys.exc_info())
            pass
    elif ".s" in lname[-2:] or ".asm" in lname[-4:]:
        try:
            regex = re.compile(Skeywords)
            for line in win.text:
                res = regex.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append(line)
        except:
            print("Exception in func extraction handler", sys.exc_info())
            pass
    elif ".txt" in lname[-4:]:
        pass
    else:            # Default to 'C' like syntax
        try:
            for kw in sumkeywords:
                for line in win.text:
                    if line.find(kw) >= 0:
                        sumw.append(line)
        except:
            pass

        try:
            regex = re.compile(ckeywords)
            for line in win.text:
                res = regex.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append(line)
        except:
            print("Exception in c func handler", sys.exc_info())
            pass

    try:
        win.mained.update_treestore(sumw)
    except:
        # This is 'normal', ignore it
        print("run_async_time", sys.exc_info())
        pass

    #win.mained.update_statusbar("Rescan done.")

def keytime(self, arg):

    #print( "keytime raw", time.ctime(), self.fired)
    #return

    if self.fired ==  1:
        #print( "keytime", time.time(), self.fired)
        pedspell.spell(self, self.spellmode)
        self.walk_func()

    if self.fired:
        self.fired -= 1

    # Track this buffer
    #if self.diffmode == 2:
    #    self.mained.diffpane.area.xpos = self.xpos
    #    self.mained.diffpane.area.ypos = self.ypos
    #    self.mained.diffpane.area.set_caret(self.xpos + self.caret[0],
    #                                                self.ypos + self.caret[1], True)

    # Track pane buffer back to diff components
    if self.diffpane:
        got_src = 0; got_targ = 0
        src = ""; targ = ""
        srctxt = [] ;  targtxt = []
        dst_tab = None ; src_tab = None

        # See if diff complete, put it in motion
        nn = self.notebook.get_n_pages(); cnt = 0
        while True:
            if cnt >= nn: break
            ppp = self.notebook.get_nth_page(cnt)
            if ppp.area.diffmode == 1:
                got_src = True
                src = os.path.basename(ppp.area.fname)
                srctxt = ppp.area.text
                src_tab = ppp
            elif ppp.area.diffmode == 2:
                got_targ = True
                targ = os.path.basename(ppp.area.fname)
                targtxt = ppp.area.text
                dst_tab = ppp

            cnt += 1

        yyy = self.ypos +  self.caret[1]
        zzz = self.ypos +  self.caret[1]
        txt = ""
        for aa in range( self.ypos + self.caret[1]):
            try:
                txt = self.text[aa]
            except:
                pass
            if txt[:8] == " --del--":
                yyy -= 1

            if txt[:8] == " --ins--":
                zzz -= 1

        if got_targ:
            dst_tab.area.xpos = self.xpos
            dst_tab.area.ypos = self.ypos
            dst_tab.area.set_caret(self.xpos + self.caret[0], yyy, True)
        if got_src:
            src_tab.area.xpos = self.xpos
            src_tab.area.ypos = self.ypos
            src_tab.area.set_caret(self.xpos + self.caret[0], zzz, True)

# Do Tasks  when the system is idle
def idle_callback(self, arg):
    #print( "Idle callback", self.fname)
    GLib.source_remove(self.source_id)
    try:
        # Mon 06.Sep.2021 always save
        if self.changed:
            hhh = hash_name(self.fname) + "_" + str(self.currback) + ".sav"
            xfile = pedconfig.conf.data_dir + os.sep + hhh
            err = writefile(xfile, self.text, "\n")
            if err[0]:
                strx = "Backed up file '{0:s}'".format(xfile)
                # Make a log entry
                logfile = pedconfig.conf.log_dir + os.sep + "backup.log"
                xentry = "Sav " + time.ctime() + " " + \
                    self.fname + " " + os.path.basename(xfile) + "\n"
                writefile(logfile, (xentry, ""), "\n", "a+")
            else:
                strx = "Cannot back up file '{0:s}' {1:s}".format(xfile, err[1])

            self.mained.update_statusbar(strx)
    except:
        print("Exception in idle handler", sys.exc_info())

# Do Tasks2 when the system is idle

def idle_callback2(self, arg):
    #print( "Idle callback2", arg)
    GLib.source_remove(self.source_id2)
    try:
        run_async_time(self, None)
    except:
        print("Exception in async handler", sys.exc_info())

# EOF
