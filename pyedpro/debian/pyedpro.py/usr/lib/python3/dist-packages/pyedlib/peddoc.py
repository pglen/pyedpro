#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import signal, os, time, string, pickle, re, platform, subprocess

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from . import keyhand, pedconfig, pedync
from . import pedcolor, pedspell, pedmenu, utils
from . import peddraw

from .pedutil import *

VSCROLLGAP  = 2             # Gap between the page boundary and ver. scroll
HSCROLLGAP  = 4             # Gap between the page boundary and hor. scroll
PAGEUP      = 20            # One page worth of scroll

# Do not redefine this here, as it is determined by the gtk (pango) lib
#TABSTOP = 8                 # One tab stop worth of spaces

# On version 0.21 (and after) we force GTK to assume our idea of tabstop.
# Even though we do not draw the tabs with GTK it is cleaner (simpler)
# this way. (See mess on tabs before V21)
TABSTOP = 4                 # One tab stop worth of spaces

# Profile line, use it on bottlenecks
#got_clock = time.clock()
# profiled code here
#print(  "Str", time.clock() - got_clock)

from .keywords import *

# Globals

last_scanned = None

# Colors for the text, configure the defaults here

FGCOLOR  = "#000000"
BGCOLOR  = "#fefefe"
RBGCOLOR = "#aaaaff"
CBGCOLOR = "#ff8888"
KWCOLOR  = "#88aaff"
CLCOLOR  = "#880000"
COCOLOR  = "#4444ff"
STCOLOR  = "#ee44ee"

# UI specific values:

DRAGTRESH = 3                   # This many pixels for drag highlight

# ------------------------------------------------------------------------
# We create a custom class for display, as we want a text editor that
# can take thousands of lines.

class pedDoc(Gtk.DrawingArea, peddraw.peddraw):

    def __init__(self, buff, appwin, readonly = False):

        # Save params
        self.appwin = appwin;
        self.readonly = readonly

        # Gather globals
        self.keyh = pedconfig.conf.keyh

        # Init vars
        self.xpos = 0; self.ypos = 0
        self.changed = False;
        self.src_changed = False
        self.needscan = True;
        self.record = False;
        self.recarr = []                # Macros
        self.undoarr = []               # Undo
        self.redoarr = []               # Redo
        self.queue = []                 # Idle tasks
        self.colsel = False
        self.oldsearch = ""
        self.oldgoto = ""
        self.oldrep = ""
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
        self.accum = [];
        self.tokens = [];
        self.ularr = []
        self.bigcaret = False
        self.stab = False
        self.honeshot = False
        self.initial_undo_size = 0
        self.initial_redo_size = 0
        self.spell = False
        self.spellmode = False
        self.start_time = time.time();
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
        self.sep = "\n";
        self.tts = None

        # Parent widget
        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        peddraw.peddraw.__init__(self)

        # Our font
        fsize  =  pedconfig.conf.sql.get_int("fsize")
        fname  =  pedconfig.conf.sql.get_str("fname")
        if fsize == 0: fsize = 14
        if fname == "": fname = "Monospace"

        self.setfont(fname, fsize)

        if self.readonly:
            self.set_tooltip_text("Read only buffer")

        # Create scroll items
        sm = len(self.text) + self.get_height() / self.cyy + 10
        self.hadj = Gtk.Adjustment(value=0, lower=0, upper=self.maxlinelen,
                            step_increment = 1, page_increment = 15, page_size = 25);
        self.vadj = Gtk.Adjustment(value=0, lower=0, upper=sm,
                            step_increment = 1, page_increment = 15, page_size = 25);

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
        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)
        self.connect("focus", self.area_focus)
        self.connect("configure_event", self.configure_event)
        #self.connect("size-request", self.)
        self.connect("size-allocate", self.size_alloc)
        self.connect("scroll-event", self.scroll_event)
        self.connect("focus-in-event", self.focus_in_cb)
        self.connect("focus-out-event", self.focus_out_cb)

    # Customize your colors here
    def setcol(self):
        ccc = pedconfig.conf.sql.get_str("fgcolor")
        if ccc == "":
            self.fgcolor  = pedcolor.str2float(FGCOLOR)
        else:
            self.fgcolor  = pedcolor.str2float(ccc)
        #print( "fgcol", self.fgcolor, ccc)

        ccc = pedconfig.conf.sql.get_str("rbgcolor")
        if ccc == "":
            self.rbgcolor = pedcolor.str2float(RBGCOLOR)
        else:
            self.rbgcolor = pedcolor.str2float(ccc)
        #print( "rgbcolor", self.rbgcolor, ccc)

        ccc = pedconfig.conf.sql.get_str("cbgcolor")
        if ccc == "":
            self.cbgcolor = pedcolor.str2float(CBGCOLOR)
        else:
            self.cbgcolor = pedcolor.str2float(ccc)
        #print( "cbgcolor", self.cbgcolor, ccc)

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


    def setfont(self, fam, size):

        self.fd = Pango.FontDescription()
        self.fd.set_family(fam)
        self.fd.set_size(size * Pango.SCALE);

        self.pangolayout = self.create_pango_layout("a")
        self.pangolayout.set_font_description(self.fd)

        # Get Pango steps
        self.cxx, self.cyy = self.pangolayout.get_pixel_size()

        # Get Pango tabs
        self.tabarr = Pango.TabArray(80, False)
        #for aa in range(self.tabarr.get_size()):
        #    self.tabarr.set_tab(aa, Pango.TAB_LEFT, aa * TABSTOP * self.cxx * Pango.SCALE)

        self.pangolayout.set_tabs(self.tabarr)
        ts = self.pangolayout.get_tabs()

        '''if ts != None:
            al, self.tabstop = ts.get_tab(1)
        self.tabstop /= self.cxx * Pango.SCALE'''

    def  set_maxlinelen(self, mlen = -1, ignore = True):
        if mlen == -1: self.calc_maxline()
        self.maxlinelen = mlen
        self.oneshot = ignore
        #value, lower, upper, step_increment, page_increment, page_size)
        #self.hadj.set_all(0, 0, self.maxlinelen * 2, 1, 15, 25);
        self.hadj.set_value(0)
        self.hadj.set_lower(0)
        self.hadj.set_upper(self.maxlinelen * 2)
        self.hadj.set_step_increment(1)
        self.hadj.set_page_increment(15)
        self.hadj.set_page_size(25)

    def  set_maxlines(self, lines = 0, ignore = True):
        self.maxlines = len(self.text) + self.get_height() / self.cyy + 25
        self.oneshot = ignore
        #self.vadj.set_all(0, 0, self.maxlines, 1, 15, 25);
        self.vadj.set_value(0)
        self.vadj.set_lower(0)
        self.vadj.set_upper(self.maxlines)
        self.vadj.set_step_increment(1)
        self.vadj.set_page_increment(15)
        self.vadj.set_page_size(25)

    # Do Tasks  when the system is idle
    def idle_callback(self):
        #print( "Idle callback")
        GLib.source_remove(self.source_id)
        try:
            if self.changed:
                hhh = hash_name(self.fname) + ".sav"
                xfile = pedconfig.conf.data_dir + "/" + hhh
                err = writefile(xfile, self.text, "\n")
                if err[0]:
                    strx = "Backed up file '{0:s}'".format(xfile)
                else:
                    strx = "Cannot back up file '{0:s}' {1:s}".format(xfile, err[1])

                self.mained.update_statusbar(strx)
        except:
            print("Exception in idle handler", sys.exc_info())

    # Do Tasks2 when the system is idle
    def idle_callback2(self):
        #print( "Idle callback2")
        GLib.source_remove(self.source_id2)
        try:
            run_async_time(self)
        except:
            print("Exception in async handler", sys.exc_info())

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
        #print ("focus_in_cb")
        self.focus = True

        try:
            os.chdir(os.path.dirname(self.fname))
            xstat = os.stat(self.fname)
            #print(self.fname, "stat", self.stat.st_mtime, "xstat", xstat.st_mtime)
            if self.stat.st_mtime !=  xstat.st_mtime:
                rrr = pedync.yes_no_cancel("File changed outside PyEdPro",
                    "'%s'\n" \
                    "changed outside PyEdPro." \
                    "Reload?" % self.fname, False);
                if rrr == Gtk.ResponseType.YES:
                    print("Reloading")
                    self.savebackup()
                    self.loadfile(self.fname)

            # Update stat info
            self.stat = xstat
        except:
            utils.put_exception("cmp mtime")
            pass

        self.update_bar2()
        self.needscan = True
        self.do_chores()

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
        cr.set_source_rgba(255, 255, 255)
        cr.rectangle( 0, 0, self.www, self.hhh);
        cr.fill()

        # Pre set for drawing
        cr.set_source_rgba(*list(fg_color));
        cr.move_to(0, 0)
        self.layout = PangoCairo.create_layout(cr)
        self.layout.set_font_description(self.fd)

        self.draw_maintext(cr)

        if not self.hex:
            # Do the text drawing in stages ...
            self.draw_selection(cr)
            self.draw_syntax(cr)
            self.draw_comments(cr)
            self.draw_spellerr(cr)

        if self.startxxx != -1:
            self.gotoxy(self.startxxx, self.startyyy)
            self.startxxx = -1; self.startyyy = -1

        self.draw_caret(cr)

    def idle_queue(func):
        self.queue.append(func)
        #print( queue)

    def area_button(self, area, event):

        if pedconfig.conf.pgdebug > 5:
            print( "Button press  ", event.type, " x=", event.x, " y=", event.y)

        event.x = int(event.x)
        event.y = int(event.y)

        if  event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:
                #print( "Left Click at x=", event.x, "y=", event.y)
                self.mx = int(event.x); self.my = int(event.y)
                xxx = int(event.x / self.cxx)
                yyy = int(event.y / self.cyy)

                # Find current pos, gather tabs, adjust back
                try:
                    line = self.text[self.ypos + yyy]
                except:
                    line = "";

                offs = calc_tabs2(line, xxx)

                #print( "offs, xxx", offs, xxx)
                self.set_caret(self.xpos + xxx - (offs - xxx),
                                     self.ypos + yyy )
                #rp = xxx + self.xpos
                #print( "xpos", self.xpos, "xxx", xxx, "rp", rp)
                #print( line)
                #print( "line part", "'" + line[rp:rp+8] + "'")

                # Erase selection
                if self.xsel != -1:
                    self.clearsel()

                self.fired += 1
                GLib.timeout_add(300, self.keytime)

            if event.button == 3:
                #print( "Right Click at x=", event.x, "y=", event.y)
                flag = False; xx = 0; yy = 0; zz = 0
                if self.spell:
                    yyy = int(self.ypos + self.get_height() / self.cyy)
                    for xaa, ybb, lcc in self.ularr:
                        # Look within visible range
                        if ybb >= self.ypos and ybb < yyy:
                            ybb -= self.ypos;
                            xaa -= self.xpos; lcc -= self.xpos;
                            xaa *= self.cxx ; ybb *= self.cyy
                            lcc *= self.cxx
                            yy2 = ybb + self.cyy

                            if self.intersect(xaa, ybb, lcc, yy2, event):
                                xx = int(xaa / self.cxx + self.xpos)
                                yy = int(ybb / self.cyy + self.ypos)
                                zz = int(lcc / self.cxx + self.xpos)
                                flag = True
                if flag:
                    line = self.text[yy];
                    #print( "'" + line[xx:zz] + "'")
                    self.xsel = xx; self.xsel2 = zz
                    self.ysel = self.ysel2 = yy
                    self.spellstr = line[int(xx):int(zz)]
                    self.popspell(area, event, self.spellstr)
                else:
                    self.poprclick(area, event)

        elif  event.type == Gdk.EventType.BUTTON_RELEASE:
            #print( "button release", event.button)
            self.mx = -1; self.my = -1
            self.scrtab = False
            ttt = "Release"
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
                line = "";

            # Find current pos on tabbed line
            offs = calc_tabs2(line, xxx)
            self.set_caret(self.xpos + xxx - (offs - xxx), self.ypos + yyy )
            #self.set_caret(len(xxx2), yyy)

            # Erase selection
            if self.xsel != -1:
                self.clearsel()

            # Select word
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                pedconfig.conf.keyh.act.ctrl_b(self)
            else:
                pedconfig.conf.keyh.act.alt_v(self)
            # Copy to clip

            if event.state & Gdk.ModifierType.SHIFT_MASK:
                pedconfig.conf.keyh.act.ctrl_c(self)

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

        self.xsel  = xssel;  self.ysel  = yssel;
        self.xsel2 = xesel;  self.ysel2 = yesel

    def pix2xpos(self, xx):
        return int(self.xpos + xx / self.cxx)

    def pix2ypos(self, yy):
        return int(self.ypos + yy / self.cyy)

    def pix2pos(self, xx, yy):
        return int(self.xpos + xx / self.cxx), int(self.ypos + yy / self.cyy)

    def area_motion(self, area, event):
        #print ("motion event", event.state, event.x, event.y)
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            #print( "motion event butt 1", event.state, event.x, event.y)
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

        # Contain
        ylen = len(self.text)
        xx2 = max(xx, 0);  yy2 = max(yy, 0)
        xx2 = min(xx, self.maxlinelen);  yy2 = min(yy, ylen)

        if sel:
            self.xsel = xx2; self.xsel2 = xx2 + sel
            self.ysel = yy2; self.ysel2 = yy2
            self.invalidate()

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
        return self.get_height()  / self.cyy;

    def get_width_char(self):
        return self.get_width() / self.cxx;

    # --------------------------------------------------------------------
    # Goto position, put caret (cursor) back to view, [vh]scrap
    # distance from ends. This function was a difficult to write. :-{
    # Note the trick with comparing old cursor pos for a hint on scroll
    # direction.
    # xx, yy - absolute position in the text buffer

    def set_caret(self, xx, yy):

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
                #goject.timeout_add(
                GLib.timeout_add(300, self.keytime)

        if yy - self.ypos < self.vscgap and self.ypos:
            #print( "Scroll from caret up")
            if yy < self.ypos + self.caret[1]:
                #print( "move u", "ypos", self.ypos, "yy", yy)
                self.ypos = int(yy - self.vscgap)
                self.ypos = int(max(self.ypos, 0))
                need_inval = True
                # Force new spell check
                self.fired += 1
                GLib.timeout_add(300, self.keytime)

        yy -= self.ypos
        if self.ypos < 0: self.ypos = 0

        # ----------------------------------------------------------------
        # Put it back in view xxx:

        xoff = cww - self.hscgap
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

        oldx = self.caret[0] * self.cxx;
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
        self.invalidate(None)

        # Update scroll bars, prevent them from sending scroll message:
        self.oneshot = True; self.vscroll.set_value(self.ypos)
        self.honeshot = True; self.hscroll.set_value(self.xpos)

        self.update_bar2()

        if  need_inval or self.bigcaret:
            self.invalidate()

    def update_bar2(self):
        clip = pedconfig.conf.keyh.act.currclip;
        self.mained.update_statusbar2(self.caret[0] + self.xpos, \
                self.caret[1] + self.ypos, self.insert, len(self.text), clip)

    def clearsel(self):
        old = self.xsel
        self.xsel  =  self.ysel = -1
        self.xsel2 =  self.ysel2 = -1
        if old != -1:
            self.invalidate()

    def keytime(self):
        #print( "keytime raw", time.time(), self.fired)
        if self.fired ==  1:
            #print( "keytime", time.time(), self.fired)
            pedspell.spell(self, self.spellmode)
            self.walk_func()
        self.fired -= 1

    def walk_func(self):
        #print( "walk func")
        # ts2 ---------------------------------------------------
        sumw2 = []
        if self.text:
            sline = self.caret[1] + int(self.ypos)
            sline = max(sline, 0); sline = min(sline, len(self.text))
            #print( "Start point", sline, self.text[sline])
            # Walk back to last function
            if ".c" in self.fname:
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

        try:
            self.appwin.update_treestore2(sumw2)
        except:
            # This is normal, ignore it
            print("walk2", sys.exc_info())
            pass

    # Call key handler
    def area_key(self, area, event):

        #print ("area_key", event)
        # Restart timer ticks
        pedconfig.conf.idle = pedconfig.conf.IDLE_TIMEOUT
        pedconfig.conf.syncidle = pedconfig.conf.SYNCIDLE_TIMEOUT

        # Maintain a count of events, only fire only fire on the last one
        self.fired += 1
        GLib.timeout_add(300, self.keytime)
        # The actual key handler
        self.keyh.handle_key(self, area, event)

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
        xx = 0;
        self.queue_draw_area(xx, yy, ww, hh)

    def invalidate(self, rect = None):
        #print( "Invalidate:", rect)
        if rect == None:
            self.queue_draw()
        else:
             self.queue_draw_area(rect.x, rect.y, \
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
        GLib.timeout_add(300, self.keytime)

    def popspell(self, widget, event, xstr):
        # Create a new menu-item with a name...
        self.menu2 = Gtk.Menu()
        self.menu2.append(self.create_menuitem("Checking '%s'" % xstr, None))
        self.menu2.append(self.create_menuitem("Add to Dict", self.addict, xstr))

        mi = self.create_menuitem("-------------", None)
        mi.set_sensitive(False)
        self.menu2.append(mi)

        strs = "Creating suggestion list for '{0:s}'".format(xstr)
        self.mained.update_statusbar(strs)
        arr = pedspell.suggest(self, xstr)

        if len(arr) == 0:
            self.menu2.append(self.create_menuitem("No Matches", None))
        else:
            for aa, bb in arr:
                self.menu2.append(self.create_menuitem(bb, self.menuitem_response))

        self.menu2.popup(None, None, None, None, event.button, event.time)
        #self.mained.update_statusbar("Done menu popup.")

    def poprclick(self, widget, event):
        #print ("Making rclick")
        self.build_menu(self, pedmenu.rclick_menu)
        self.menu.popup(None, None, None, None, event.button, event.time)

    def menuitem_response(self, widget, stringx, arg):
        #print( "menuitem response '%s'" % stringx)
        #print( "Original str '%s'" % self.spellstr)

        # See if Capitalized or UPPERCASE :
        if self.spellstr[0] in string.ascii_uppercase:
            stringx = stringx.capitalize()

        if self.spellstr.isupper():
            stringx = stringx.upper()

        pedconfig.conf.keyh.act.clip_cb(None, stringx, self, False)

        self.fired += 1
        GLib.timeout_add(300, self.keytime)

    def activate_action(self, action):
        dialog = Gtk.MessageDialog(self, Gtk.DIALOG_DESTROY_WITH_PARENT,
            Gtk.ButtonsType.INFO, Gtk.ButtonsType.CLOSE,
            'You activated action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        dialog.connect ("response", lambda d, r: d.destroy())
        dialog.show()

    def rclick_action(self, action, sss, ttt):
        #print( "rclck_action", sss, ttt)
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
            #self.mained.activate_exit()
            #print("Toggle read only");
            self.readonly = not self.readonly
            arrx = ["OFF", "ON"]
            self.mained.update_statusbar("Toggled read only to %s" % arrx[self.readonly])

        elif ttt == 13:
            self.mained.activate_exit()
        elif ttt == 14:
            self.start_term()
        elif ttt == 15:
            self.start_edit()
        elif ttt == 16:
            self.mained.tts()
        else:
            print("peddoc: Invalid menu item selected")

    def start_term(self):
        #print("Terminal Here")
        try:
            if platform.system().find("Win") >= 0:
                print("No terminal on windows. (TODO)")
            else:
                # Stumble until terminal found
                ret = subprocess.Popen(["gnome-terminal"])
                if ret.returncode:
                    ret = subprocess.Popen(["xfce4-terminal"])
        except:
            print("Cannot launch terminal", sys.exc_info())
            pedync.message("\n   Cannot launch terminal executable \n\n"
                       "              (Please install)")


    def start_edit(self):
        #print("Editor Here")

        myscript = os.path.join(os.path.dirname(__file__), '../pyedpro.py')
        myscript = os.path.realpath(myscript)
        print("myscript: python", myscript);

        try:
            if platform.system().find("Win") >= 0:
                print("No exe on windows. (TODO)")
            else:
                # Stumble until editor found
                ret = subprocess.Popen(["python", myscript])
                if ret.returncode:
                    ret = subprocess.Popen(["xfce4-terminal"])
        except:
            print("Cannot launch terminal", sys.exc_info())
            pedync.message("\n   Cannot launch editor script \n\n"
                       "              (Please install)")


    def create_menuitem(self, string, action, arg = None):
        rclick_menu = Gtk.MenuItem(string)
        if action:
            rclick_menu.connect("activate", action, string, arg);
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
                menu_item.set_size_request(-1, 10);
                pass
            else:
                ttt = str(bb).replace("<control>", "CTRL+")
                ttt = str(ttt).replace("<alt>",     "ALT+")
                ttt = str(ttt).replace("<shift>",   "SHIFT+")
                fff = " " * (15 - len(aa))
                sss = aa + "%s\t%s" % (fff, ttt)
                menu_item = Gtk.MenuItem.new_with_mnemonic(sss)
                menu_item.connect("activate", self.rclick_action, aa, dd );

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
                strx = "Not Saved '{0:s}' {1:s}".format(bn, err[1])

        if(pedconfig.conf.verbose):
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
        strx = "Closing '{0:s}'".format(self.fname)
        if(pedconfig.conf.verbose):
            print("Closing doc:", strx)
        self.mained.update_statusbar(strx)
        self.saveparms()

        # Clear treestore(s)
        self.appwin.update_treestore([])
        self.appwin.update_treestore2([])

        # Add to accounting:
        utils.logentry("Closed File", self.start_time, self.fname)

        return self.prompt_save(noprompt)

    # --------------------------------------------------------------------
    # Load file into this buffer, return False on failure

    def loadfile(self, filename, create = False):
        self.fname = filename
        try:
            self.stat = os.stat(self.fname)
        except:
            pass

        #pedync.message("\n   open / read file:  \n\n"
        #                      "      %s" % self.fname)

        #print("stat", self.stat.st_mtime)
        self.start_time = time.time();
        if self.fname == "":
            strx = "Must specify file name."
            print(strx)
            self.mained.update_statusbar(strx)
            return False
        try:
            self.text = readfile(self.fname)
        except:
            errr = "Cannot read file '" + self.fname + "'" #, sys.exc_info()
            if(pedconfig.conf.verbose):
                print(errr, sys.exc_info())

            #pedync.message("\n   Cannot open / read file:  \n\n"
            #                  "      %s" % self.fname)

            self.mained.update_statusbar(errr)
            usleep(10)
            return False

        #self.ularr.append((10 ,10, 20))
        mlen = self.calc_maxline()

        # Set up scroll bars
        self.set_maxlinelen(mlen, False)
        self.set_maxlines(len(self.text), False)

        self.loadundo()
        self.saveorg()
        self.savebackup()
        self.loadparms()

        # Add to accounting:
        utils.logentry("Opened File", self.start_time, self.fname)

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

        return True

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
        xfile = pedconfig.conf.data_dir + "/" + hhh
        if not os.path.isfile(xfile):
            err =  writefile(xfile, self.text, "\n")
            if not err[0]:
                print("Cannot create (org) backup file", xfile, sys.exc_info())

   # Create backup
    def savebackup(self):
        hhh = hash_name(self.fname) + ".bak"
        xfile = pedconfig.conf.data_dir + "/" + hhh
        try:
            writefile(xfile, self.text, "\n")
        except:
            sss = "Cannot create backup file" + xfile + sys.exc_info()
            print(sss)

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

    def writeout(self):
        if(pedconfig.conf.verbose):
            print("Saving '"+ self.fname + "'")
        err = writefile(self.fname, self.text, "\n")
        if err[0]:
            self.set_changed(False)

        self.saveundo()
        self.saveparms()
        self.set_tablabel()

        # Add to accounting:
        utils.logentry("Wrote File", self.start_time, self.fname)

        # Update stat info
        self.stat = os.stat(self.fname)

        return err

    def delundo(self):
        self.undoarr = []; self.redoarr = []
        # Remove file
        hhh = hash_name(self.fname) + ".udo"
        xfile = pedconfig.conf.data_dir + "/" + hhh
        fh = open(xfile, "w")
        fh.close()
        hhh = hash_name(self.fname) + ".rdo"
        xfile = pedconfig.conf.data_dir + "/" + hhh
        fh = open(xfile, "w")
        fh.close()

    def saveundo(self):
        hhh = hash_name(self.fname) + ".udo"
        xfile = pedconfig.conf.data_dir + "/" + hhh
        try:
            fh = open(xfile, "wb")
            pickle.dump(self.undoarr, fh)
            fh.close()
        except:
            print("Cannot save undo file", sys.exc_info())
            utils.put_exception("undo")


        hhh = hash_name(self.fname) + ".rdo"
        xfile = pedconfig.conf.data_dir + "/" + hhh
        try:
            fh = open(xfile, "wb")
            pickle.dump(self.redoarr, fh)
            fh.close()
        except:
            print("Cannot save redo file", sys.exc_info())

    def loadundo(self):
        hhh = hash_name(self.fname) + ".udo"
        xfile = pedconfig.conf.data_dir + "/" + hhh
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
        xfile = pedconfig.conf.data_dir + "/" + hhh
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
                    dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
                    Gtk.MESSAGE_QUESTION, Gtk.ButtonsType.YES_NO,
                    "\nWould you like overwrite file:\n\n  \"%s\" \n" % fname)
                    dialog.set_title("Overwrite file ?")
                    dialog.set_default_response(Gtk.ResponseType.YES)
                    dialog.connect("response", self.overwrite_done, fname, win)
                    dialog.run()
                else:
                    win.destroy()
                    self.fname = fname
                    self.writeout()

    def overwrite_done(self, win, resp, fname, win2):
        #print( "overwrite done", resp)
        if resp == Gtk.ResponseType.YES:
            self.fname = fname
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
        nn = self.notebook.get_n_pages(); cnt = 0
        while True:
            if cnt >= nn: break
            ppp = self.notebook.get_nth_page(cnt)
            if ppp.area == self:
                self._setlabel(ppp)
                break
            cnt += 1

    def _setlabel(self, ppp):
        # Set label to tab
        ss = shortenstr(os.path.basename(self.fname), 24)
        if  self.changed:
            str2 = "  *" + ss + "  "
        else:
            str2 = "  " + ss + "  "
        label = Gtk.Label.new(str2)
        label.set_tooltip_text(self.fname)
        label.set_single_line_mode(True)

        image = Gtk.Image();
        image.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
        butt = Gtk.Button();  butt.add(image)
        butt.set_focus_on_click(False)
        butt.set_relief( Gtk.ReliefStyle.NONE)
        rc = butt.get_modifier_style()
        #rc.xthickness = 1; rc.ythickness = 1
        #butt.modify_style(rc)

        butt.connect("clicked", self.close_button)
        butt.set_tooltip_text("Close '%s'" % os.path.basename(self.fname))
        hbox = Gtk.HBox()

        hbox.pack_start(label, 0, 0, 0)
        hbox.pack_start(butt, 0, 0, 0)
        hbox.show_all()
        self.notebook.set_tab_label(ppp, hbox)

    def close_button(self, arg1):
        #print( "close_button", arg1)
        # Select me first
        self.mained.closedoc(self)

    # --------------------------------------------------------------------
    def savemacro(self):
        #print( "Savemacro")

        fname = "untitled.mac"
        xfile = pedconfig.conf.config_dir + "/macros/" + fname
        old = os.getcwd()
        try:
            os.chdir(os.path.dirname(xfile))
        except:
            print("No macros directory", sys.exc_info())

        but =   "Cancel", Gtk.ButtonsType.CANCEL, "Save Macro", Gtk.ButtonsType.OK
        fc = Gtk.FileChooserDialog("Save Macro", None, Gtk.FileChooserAction.SAVE, \
            but)

        fc.set_current_folder(xfile)
        fc.set_current_name(os.path.basename(xfile))
        fc.set_default_response(Gtk.ButtonsType.OK)
        fc.connect("response", self.done_mac_fc, old)
        fc.run()

    def done_mac_fc(self, win, resp, old):
        #print(  "done_mac_fc", resp)
        # Back to original dir
        os.chdir(os.path.dirname(old))
        if resp == Gtk.ButtonsType.OK:
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
            except:
                print("Cannot load macro file", sys.exc_info())

        win.destroy()

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

        self.accum = [];

        curr = self.caret[1] + self.ypos
        was = -1; cnt = 0; cnt2 = 0

        for line in self.text:
            # Search one line for multiple matches
            mmm = src_line(line, cnt, srctxt, regex, boolcase, boolregex)

            if cnt > curr and was == -1:
                was = cnt2
            if  mmm:
                cnt2 += 1;
                for sss in mmm:
                    self.accum.append(sss)
            if cnt % 100 == 0:
                self.mained.update_statusbar("Searching at %d" % cnt)
                usleep(1)
            cnt += 1
        return was, cnt2

# Run this on an idle callback so the user can work while this is going

def run_async_time(win):

    global last_scanned

    #print( "run_async_time enter")

    if  last_scanned == win:
        return

    last_scanned = win
    win.appwin.start_tree()

    #print( "run_sync_time", time.time())

    sumw = [] ; lname = win.fname.lower()
    if not win.text:
        return

    # Added flex and yacc
    if ".c" in lname or ".h" in lname or ".y" in lname or ".f" in lname:
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

    elif ".py" in lname:
        try:
            regex = re.compile(pykeywords2)
            for line in win.text:
                res = regex.search(line)
                if res:
                    #print( res, res.start(), res.end())
                    sumw.append(line)
        except:
            print("Exception in py func handler", sys.exc_info())
            pass
    elif ".bas" in lname:
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
    elif ".s" in lname:
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
    elif ".txt" in lname:
        pass
    else:
        try:
            for kw in sumkeywords:
                for line in win.text:
                    if line.find(kw) >= 0:
                        sumw.append(line)
        except:
            pass

    try:
        win.appwin.update_treestore(sumw)
    except:
        # This is 'normal', ignore it
        print("run_async_time", sys.exc_info())
        pass

# EOF

















































































