#!/usr/bin/env python

#from __future__ import absolute_import
#from __future__ import print_function

import signal, os, time, sys, pickle, subprocess, random, warnings
import math, copy

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

realinc = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pycommon")
if realinc not in sys.path:
    sys.path.append(realinc)

#print("import", __file__)
import pgutils
import pgsimp

IDXERR = "Index is larger than the available number of controls."

gui_testmode = 0

def randcol():
    return random.randint(0, 255)

def randcolstr(start = 0, endd = 255):
    rr =  random.randint(start, endd)
    gg =  random.randint(start, endd)
    bb =  random.randint(start, endd)
    strx = "#%02x%02x%02x" % (rr, gg, bb)
    return strx

'''
for a in (style.base, style.fg, style.bg,
      style.light, style.dark, style.mid,
      style.text, style.base, style.text_aa):
for st in (gtk.STATE_NORMAL, gtk.STATE_INSENSITIVE,
           gtk.STATE_PRELIGHT, gtk.STATE_SELECTED,
           gtk.STATE_ACTIVE):
    a[st] = gtk.gdk.Color(0, 34251, 0)
'''


# ------------------------------------------------------------------------
# Bemd some of the parameters for us

class CairoHelper():

    def __init__(self, cr):
        self.cr = cr

    def set_source_rgb(self, col):
        self.cr.set_source_rgb(col[0], col[1], col[2])

    def rectangle(self, rect):
        self.cr.rectangle(rect[0], rect[1], rect[2], rect[3])

    # --------------------------------------------------------------------
    #   0 1           0+2
    #   x,y     -      rr
    #         -   -
    #  midy -       -
    #         -   -
    #           -      bb
    #          midx    1+3

    def romb(self, rect):

        #print("romb", rect[0], rect[1], rect[2], rect[3])
        midx =  rect[0] + rect[2] // 2
        midy =  rect[1] + rect[3] // 2

        self.cr.move_to(rect[0], midy)
        self.cr.line_to(midx, rect[1])
        self.cr.line_to(rect[0]+rect[2], midy)
        self.cr.line_to(midx, rect[1]+rect[3])
        self.cr.line_to(rect[0], midy)

    def circle(self, xx, yy, size):
        self.cr.arc(xx, yy, size, 0,  2 * math.pi)

    # --------------------------------------------------------------------
    #   0 1+2    midx    1+2
    #   x,y       -
    #           -   -
    #  x+hh   -       -  y+ww

    def tri(self, rect):
        #                xx       yy       ww       hh
        #print("tri", rect[0], rect[1], rect[2], rect[3])
        midx =  rect[0] + rect[2] // 2
        self.cr.move_to(rect[0], rect[1] + rect[3])
        self.cr.line_to(midx, rect[1])
        self.cr.line_to(rect[0] + rect[2], rect[1] + rect[3])
        self.cr.line_to(rect[0], rect[1] + rect[3])

    # Inverse, down
    # --------------------------------------------------------------------
    #   0 1+2    midx    1+2
    #   x,y   -   -   -
    #           -   -
    #  x+hh       -      y+ww

    def tri2(self, rect):
        #                xx       yy       ww       hh
        #print("tri2", rect[0], rect[1], rect[2], rect[3])
        midx =  rect[0] + rect[2] // 2
        self.cr.move_to(rect[0], rect[1])
        self.cr.line_to(midx, rect[1] + rect[3])
        self.cr.line_to(rect[0] + rect[2], rect[1])
        self.cr.line_to(rect[0], rect[1])

class   TextTable(Gtk.Table):

    def __init__(self, confarr, main = None, textwidth = 24):
        GObject.GObject.__init__(self)
        self.texts = []
        #self.set_homogeneous(False)
        self.main = main
        row = 0
        for aa, bb in confarr:
            #print("aa", aa, "bb", bb)
            label = Gtk.Label()
            label.set_text_with_mnemonic(aa)
            tbox = Gtk.Entry()
            label.set_mnemonic_widget(tbox)
            tbox.set_width_chars (textwidth)
            self.texts.append(tbox)
            self.attach_defaults(label, 0, 1, row, row + 1)
            self.attach_defaults(tbox,  1, 2, row, row + 1)
            row += 1

class   TextRow(Gtk.HBox):

    def __init__(self, labelx, initval, main, align=20):

        GObject.GObject.__init__(self)
        #super().__init__(self)

        self.set_homogeneous(False)
        self.main = main
        self.label = Gtk.Label()
        self.label.set_text_with_mnemonic(labelx)
        #self.label.set_xalign(1)

        # Adjust for false character
        lenx = len(labelx);
        if "_" in labelx: lenx -= 1
        #spp = int((align - lenx) * 1.8) # Space is smaller than avarage char
        #self.pack_start(Spacer(spp), False, False, 0)

        self.pack_start(Spacer(), False, False, 0)
        self.pack_start(self.label, False, False, 0)
        self.pack_start(Spacer(4), False, False, 0)
        self.tbox = Gtk.Entry()
        self.tbox.set_width_chars (8)
        self.tbox.set_text(initval)
        self.pack_start(self.tbox, False, False, 0)

        self.label.set_mnemonic_widget(self.tbox)

        self.tbox.connect("focus_out_event", self.edit_done)
        self.tbox.connect("key-press-event", self.edit_key)
        self.tbox.connect("key-release-event", self.edit_key_rel)

    def edit_done(self, textbox, event):
        #print(textbox.get_text())
        pass

    def edit_key_rel(self, textbox, event):
        #print(textbox, event.string, event.keyval)
        if event.string == "\t":
            #print("Tab")
            return None

        if event.string == "\r":
            #print("Newline", event.string)
            # Switch to next control
            '''
            #ee = event.copy() #Gdk.Event(Gdk.EventType.KEY_PRESS)
            #ee.keyval = Gdk.KEY_Tab
            #ee.string = "\t"
            #e.state = event.state
            #super().emit("key-release-event", ee)
            #super().foreach(self.callb)
            '''
            pass


    def callb(self, arg1):
        #print ("callb arg1", arg1)
        pass

    def edit_key(self, textbox, event):
        #print(textbox, event.string, event.keyval)
        if event.string == "\t":
            #print("Tab")
            pass
        if event.string == "\r":
            #print("Newline")
            # Switch to next control (any way you can)
            arrx = (Gtk.DirectionType.TAB_FORWARD,  Gtk.DirectionType.RIGHT,
            Gtk.DirectionType.LEFT, Gtk.DirectionType.UP)
            for aa in arrx:
                ret = self.main.child_focus(aa)
                if ret:
                    break

    def get_text(self):
        return self.tbox.get_text()

    def set_text(self, txt):
        return self.tbox.set_text(txt)


class LabelButt(Gtk.EventBox):

    ''' Imitate button '''
    def __init__(self, front, callb, toolt=""):

        GObject.GObject.__init__(self)

        self.set_can_focus(True)
        self.label = Gtk.Label.new_with_mnemonic(front)
        self.label.set_mnemonic_widget(self)
        #self.curve =  Gdk.Cursor(Gdk.CursorType.CROSSHAIR)
        self.arrow =  Gdk.Cursor(Gdk.CursorType.ARROW)
        self.hand =  Gdk.Cursor(Gdk.CursorType.HAND1)

        #gdk_window = self.get_root_window()
        #self.arrow = gdk_window.get_cursor()

        if toolt:
            self.label.set_tooltip_text(toolt)
        self.label.set_single_line_mode(True)
        self.add(self.label)

        self.label.connect("event-after", self.eventx, front)
        self.connect("mnemonic-activate", self.mnemonic, front)

        if callb:
            self.connect("button-press-event", callb, front)

        self.set_above_child(True)
        self.add_mnemonic_label(self.label)

        #self.label.connect("motion-notify-event", self.area_motion)
        self.connect("motion-notify-event", self.area_motion)
        self.connect("enter-notify-event", self.area_enter)
        self.connect("leave-notify-event", self.area_leave)

    def eventx(self, *args):
        print("eventx", *args)

    def mnemonic(self, *arg):
        print("Mnemonic", *arg)

    def area_motion(self, arg1, arg2):
        #print("LabelButt Motion")
        pass

    def area_enter(self, arg1, arg2):
        #print("LabelButt enter")
        gdk_window = self.get_root_window()
        gdk_window.set_cursor(self.hand)

    def area_leave(self, arg1, arg2):
        #print("LabelButt leave")
        gdk_window = self.get_root_window()
        gdk_window.set_cursor(self.arrow)

class Led(Gtk.DrawingArea):

    def __init__(self, color, size = 20, border = 2):
        GObject.GObject.__init__(self)
        #self.size_allocate();
        #self.size_request()
        self.border = border
        self.set_size_request(size + border, size + border)
        self.connect("draw", self.draw)
        self.color =  color

    def set_color(self, col):
        self.color = col
        self.queue_draw()

    def draw(self, area, cr):
        rect = self.get_allocation()
        #print ("draw", rect)

        #cr.rectangle(0, 0, rect.width, rect.height);
        #x = 0; y = 0; width = 10; height = 10
        #cr.save()
        #cr.translate(x + width / 2., y + height / 2.)
        #cr.scale(width / 2., height / 2.)
        #cr.restore()

        ccc = pgutils.str2float(self.color)
        cr.set_source_rgba(ccc[0] * 0.7, ccc[1] * 0.7, ccc[2] * 0.7)
        cr.arc(rect.width/2, rect.height/2., rect.width/2., 0., 2 * math.pi)
        cr.fill()

        cr.set_source_rgba(ccc[0], ccc[1], ccc[2])
        cr.arc(rect.width/2, rect.height/2, rect.width / 2. * .8, 0., 2 * math.pi)
        cr.fill()

        # Reflection on the r
        cr.set_source_rgba(ccc[0], ccc[1] + 0.51, ccc[2])
        cr.arc(rect.width/2+1, rect.height/2, rect.width / 2. * .2, 0., 2 * math.pi)
        cr.fill()

# ------------------------------------------------------------------------

class MenuButt(Gtk.DrawingArea):

    def __init__(self, menarr, callb, tooltip = "Menu", size = 20, border = 2):
        GObject.GObject.__init__(self)

        warnings.simplefilter("ignore")

        self.border = border
        self.callb = callb
        self.menarr = menarr
        self.set_size_request(size + border, size + border)
        self.connect("draw", self.draw)
        self.connect("button-press-event", self.area_button)
        self.connect("key-press-event", self.area_key)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.set_tooltip_text(tooltip)
        self.set_can_focus(True)
        self.pointer = self.get_pointer()

    def _create_menuitem(self, string, action, arg = None):
        rclick_menu = Gtk.MenuItem(string)
        rclick_menu.connect("activate", action, string, arg);
        rclick_menu.show()
        return rclick_menu

        # Create the menubar and toolbar
        #action_group = Gtk.ActionGroup("DocWindowActions")
        #action_group.add_actions(entries)
        #return action_group

    def area_key(self, area, event):
        pass
        #print("keypress mb", event.type, event.string);

    def _make_menu(self):
        self.grab_focus()
        self.menu3 = Gtk.Menu()
        cnt = 0
        for aa in self.menarr:
            self.menu3.append(self._create_menuitem(aa, self.menu_fired, cnt))
            cnt = cnt + 1

    def area_rbutton(self, area, event):
        #print("rmenu butt ", event.type, event.button);
        if  event.type == Gdk.EventType.BUTTON_RELEASE:
            if event.button == 3:
                #print( "Left Click at x=", event.x, "y=", event.y)
                self._make_menu()
                self.menu3.popup(None, None, None, None, event.button, event.time)

    def area_button(self, area, event):
        #print("menu butt ", event.type, event.button);
        if  event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:
                #print( "Left Click at x=", event.x, "y=", event.y)
                self._make_menu()
                self.menu3.popup(None, None, None, None, event.button, event.time)

    def menu_fired(self, menu, menutext, arg):
        #print ("menu item fired:", menutext, arg)
        if self.callb:
            self.callb(self, menutext, arg)

    def _draw_line(self, cr, xx, yy, xx2, yy2):
        cr.move_to(xx, yy)
        cr.line_to(xx2, yy2)
        cr.stroke()

    def draw(self, area, cr):
        rect = self.get_allocation()
        #print ("draw", rect)

        if self.is_focus():
            cr.set_line_width(3)
        else:
            cr.set_line_width(2)

        self._draw_line(cr, self.border, rect.height/4,
                                rect.width - self.border, rect.height/4);
        self._draw_line(cr, self.border, 2*rect.height/4,
                                rect.width - self.border, 2*rect.height/4);
        self._draw_line(cr, self.border, 3*rect.height/4,
                                rect.width - self.border, 3*rect.height/4);


# ------------------------------------------------------------------------

class WideButt(Gtk.Button):

    def __init__(self, labelx, callme = None, space = 2):
        #super().__init__(self)
        GObject.GObject.__init__(self)
        self.set_label(" " * space + labelx + " " * space)
        self.set_use_underline (True)
        if callme:
            self.connect("clicked", callme)

class FrameTextView(Gtk.TextView):

    def __init__(self, callme = None):

        GObject.GObject.__init__(self)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_size_request(100, 100)
        self.scroll.add_with_viewport(self)
        self.frame = Gtk.Frame()
        self.frame.add(self.scroll)

        self.set_buffer(Gtk.TextBuffer())
        self.set_size_request(150, 150)
        ls = self.get_style_context()
        fd = ls.get_font(Gtk.StateFlags.NORMAL)
        #newfd = fd.to_string() + " " + str(fd.get_size() / Pango.SCALE + 4)
        #print("newfd", newfd)
        self.modify_font(Pango.FontDescription("Sans 13"))

    def append(self, strx):
        buff = self.get_buffer()
        old = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), False)
        buff.set_text(old + "\n" +  strx)
        pgutils.usleep(20)
        #mainwin.statb2.scroll_to_iter(buff.get_end_iter(), 1.0, True, 0.1, 0.1)
        sb = self.scroll.get_vscrollbar()
        sb.set_value(2000000)

class Label(Gtk.Label):
    def __init__(self, textm = "", widget = None, tooltip=None, font = None):
        GObject.GObject.__init__(self)
        self.set_text_with_mnemonic(textm)
        if widget:
            self.set_mnemonic_widget(widget)
        if tooltip:
            self.set_tooltip_text(tooltip)
        if font:
            self.override_font(Pango.FontDescription(font))

class Logo(Gtk.VBox):

    def __init__(self, labelx, tooltip = None, callme = None):

        GObject.GObject.__init__(self)

        self.logolab = Gtk.Label(labelx)
        self.logolab.set_has_window(True)
        if tooltip:
            self.logolab.set_tooltip_text(tooltip)

        self.logolab.set_events( Gdk.EventMask.BUTTON_PRESS_MASK |
                             Gdk.EventMask.BUTTON_RELEASE_MASK )

        if callme:
            self.logolab.connect("button-press-event", callme)

        self.logolab.modify_font(Pango.FontDescription('Times 45'))

        #self.pack_start(Spacer(), 0, 0, False)
        self.pack_start(self.logolab, 0, 0, False)
        #self.pack_start(Spacer(), 0, 0, False)

    def forallcallb(self, arg1):
        #print ("arg1", arg1)
        arg1.hide();

    def hide(self):
        self.forall(self.forallcallb)


# ------------------------------------------------------------------------
# This override covers / hides the complexity of the treeview and the
# textlisbox did not have the needed detail

class ListBox(Gtk.TreeView):

    def __init__(self, limit = -1, colname = ''):

        self.limit = limit
        self.treestore = Gtk.TreeStore(str)
        Gtk.TreeView.__init__(self, self.treestore)

        cell = Gtk.CellRendererText()
        # create the TreeViewColumn to display the data
        tvcolumn = Gtk.TreeViewColumn(colname)
        # add the cell to the tvcolumn and allow it to expand
        tvcolumn.pack_start(cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        tvcolumn.add_attribute(cell, 'text', 0)

        # add tvcolumn to treeview
        self.append_column(tvcolumn)
        self.set_activate_on_single_click (True)

        self.callb = None
        self.connect("row-activated",  self.tree_sel)

    def tree_sel(self, xtree, xiter, xpath):
        #print("tree_sel", xtree, xiter, xpath)
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            xstr = xmodel.get_value(xiter, 0)
            #print("Selected", xstr)
            if self.callb:
                self.callb(xstr)
        pass

    def set_callback(self, funcx):
        self.callb = funcx

    # Delete previous contents
    def clear(self):
        try:
            while True:
                root = self.treestore.get_iter_first()
                if not root:
                    break
                try:
                    self.treestore.remove(root)
                except:
                    print("except: treestore remove")

        except:
            print("update_tree", sys.exc_info())
            pass

    # Select Item. -1 for select none; Rase Valuerror for wrong index.
    def select(self, idx):
        ts = self.get_selection()
        if idx == -1:
            ts.unselect_all()
            return
        iter = self.treestore.get_iter_first()
        for aa in range(idx):
            iter = self.treestore.iter_next(iter)
            if not iter:
                break
        if not iter:
            pass
            #raise ValueError("Invalid selection index.")
        ts.select_iter(iter)

    # Return the number of list items
    def get_size(self):
        cnt = 0
        iter = self.treestore.get_iter_first()
        if not iter:
            return cnt
        cnt = 1
        while True:
            iter = self.treestore.iter_next(iter)
            if not iter:
                break
            cnt += 1
        return cnt

    def get_item(self, idx):
        cnt = 0; res = ""
        iter = self.treestore.get_iter_first()
        if not iter:
            return ""
        cnt = 1
        while True:
            iter = self.treestore.iter_next(iter)
            if not iter:
                break
            if cnt == idx:
                res = self.treestore.get_value(iter, 0)
                break
            cnt += 1
        return res

    def append(self, strx):
        if self.limit != -1:
            # count them
            cnt = self.get_size()
            #print("limiting cnt=", cnt, "limit=", self.limit)
            for aa in range(cnt - self.limit):
                iter = self.treestore.get_iter_first()
                if not iter:
                    break
                try:
                    self.treestore.remove(iter)
                except:
                    print("except: treestore remove lim")

        last = self.treestore.append(None, [strx])
        self.set_cursor_on_cell(self.treestore.get_path(last), None, None, False)

    def get_text(self):
        sel = self.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            return xmodel.get_value(xiter, 0)

    # Get current IDX -1 for none
    def get_curridx(self):
        sel = self.get_selection()
        xmodel, xiter = sel.get_selected()
        if not xiter:
            return -1

        # Count back from match
        cnt = 0
        while True:
            xiter = self.treestore.iter_previous(xiter)
            if not xiter:
                break
            #print ("xiter:", xiter)
            cnt += 1
        return cnt

class Spinner(Gtk.SpinButton):

    def __init__(self, startx = 0, endx = 100, defx = 0, cb=None):

        GObject.GObject.__init__(self)
        self.cb_func = cb

        adj2 = Gtk.Adjustment(startx, startx, endx, 1.0, 5.0, 0.0)
        self.set_adjustment(adj2)
        self.set_value(defx)
        self.set_wrap(True)
        self.connect("value_changed", self.spinned)

    def spinned(self, spin):
        #print("spinned", spin)
        if self.cb_func:
            self.cb_func(self.get_value())

# ------------------------------------------------------------------------
# Highlite test items

def set_testmode(flag):
    global gui_testmode
    gui_testmode = flag

# ------------------------------------------------------------------------
# An N pixel horizontal spacer. Defaults to X pix  get_center

def vspacer(sp = 8):
    lab = Gtk.VBox()
    lab.set_size_request(sp, sp)

    if gui_testmode:
        lab.override_background_color(
                    Gtk.StateFlags.NORMAL, Gdk.RGBA(1, .5, .5) )
    return lab

# ------------------------------------------------------------------------
# An N pixel horizontal spacer. Defaults to X pix  get_center

class xSpacer(Gtk.HBox):

    def __init__(self, sp = None):
        GObject.GObject.__init__(self)
        #self.pack_start()
        if gui_testmode:
            col = randcolstr(100, 200)
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))
        if sp == None:
            sp = 6
        self.set_size_request(sp, sp)

# ------------------------------------------------------------------------
# An N pixel spacer. Defaults to 1 char height / width

class Spacer(Gtk.Label):

    global gui_testmode

    def __init__(self, sp = 1, title=None, left=False, bottom=False, test=False):

        GObject.GObject.__init__(self)

        #sp *= 1000
        #self.set_markup("<span  size=\"" + str(sp) + "\"> </span>")
        #self.set_text(" " * sp)

        if title:
            self.set_text(title)
        else:
            self.set_text(" " * sp)

        if left:
            self.set_xalign(0)

        if bottom:
            self.set_yalign(1)

        if test or gui_testmode:
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#888888"))

        #self.set_property("angle", 15)
        #attr = self.get_property("attributes")
        #attr2 = Pango.AttrList()
        #print ("attr", dir(attr))
        #attr.
        #self.set_property("attributes", attr)
        #self.set_property("label", "wtf")
        #self.set_property("background-set", True)

# ------------------------------------------------------------------------
# Added convenience methods

class   xVBox(Gtk.VBox):

    def __init__(self, col = None):
        GObject.GObject.__init__(self)
        self.pad = 0
        if gui_testmode:
            if not col:
                col = randcolstr(100, 200)
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))

    def set_padding(self, pad):
        self.pad = pad

    def pack(self, obj, expand = False, pad = 0):
        if pad == 0:
            pad = self.pad
        self.pack_start(obj, expand, expand, pad)

class   xHBox(Gtk.HBox):

    def __init__(self, col = None):
        GObject.GObject.__init__(self)
        self.pad = 0
        if gui_testmode:
            if not col:
                col = randcolstr(100, 200)
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))

    def set_padding(self, pad):
        self.pad = pad

    def pack(self, obj, expand = False, pad = 0):
        if pad == 0:
            pad = self.pad
        self.pack_start(obj, expand, expand, pad)

# ------------------------------------------------------------------------

class   RadioGroup(Gtk.Frame):

    def __init__(self, rad_arr, call_me):

        GObject.GObject.__init__(self)
        self.buttons = []
        self.callme = call_me
        vbox6 = Gtk.VBox(); vbox6.set_spacing(4);
        vbox6.set_border_width(6)

        if gui_testmode:
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#778888"))

        self.radio = Gtk.RadioButton.new_with_mnemonic(None, "None")

        for aa in range(len(rad_arr)):
            #rad2 = Gtk.RadioButton.new_from_widget(self.radio)
            #rad2.set_label(rad_arr[aa])
            rad2 = Gtk.RadioButton.new_with_mnemonic_from_widget(self.radio, rad_arr[aa])
            self.buttons.append(rad2)
            rad2.connect("toggled", self.radio_toggle, aa)
            vbox6.pack_start(rad2, False, False, False)

        self.add(vbox6)

    def radio_toggle(self, button, idx):
        #print("RadioGroup", button.get_active(), "'" + str(idx) + "'")
        if  button.get_active():
            self.callme(button, self.buttons[idx].get_label())

    def set_tooltip(self, idx, strx):
        if idx >= len(self.buttons):
            raise ValueError(IDXERR)
        self.buttons[idx].set_tooltip_text(strx)

    def set_entry(self, idx, strx):
        if idx >= len(self.buttons):
            raise ValueError(IDXERR)
        self.buttons[idx].set_label(strx)

    def set_sensitive(self, idx, valx):
        if idx >= len(self.buttons):
            raise ValueError(IDXERR)
        self.buttons[idx].set_sensitive(valx)

    def get_size(self):
        return len (self.buttons)

    def set_check(self, idx, valx):
        if idx >= len(self.buttons):
            raise ValueError(IDXERR)
        self.buttons[idx].set_active(valx)
        self.buttons[idx].toggled()

    def get_check(self):
        cnt = 0
        for aa in (self.buttons):
            if aa.get_active():
                return cnt
            cnt += 1
        # Nothing selected ...
        return -1

    def get_text(self):
        for aa in (self.buttons):
            if aa.get_active():
                return aa.get_label()
        # Nothing selected ... empty str
        return ""


# Bug fix in Gtk

class   SeparatorMenuItem(Gtk.SeparatorMenuItem):

    def __init__(self):
        Gtk.SeparatorMenuItem.__init__(self);
        self.show()

# ------------------------------------------------------------------------

class coords():
    pass

class Menu():

    def __init__(self, menarr, callb, event, submenu = False):

        #GObject.GObject.__init__(self)

        warnings.simplefilter("ignore")

        self.callb   = callb
        self.menarr  = menarr
        self.title   = menarr[0]
        self.gtkmenu = Gtk.Menu()

        # Remember initial location
        self.event   = coords();
        self.event.x = event.x;  self.event.y = event.y
        #print("popup Menu at:", self.event.x, self.event.y)

        cnt = 0
        for aa in self.menarr:
            #print("type aa", type(aa))
            if type(aa) == str:
                if aa == "-":
                    mmm = SeparatorMenuItem()
                else:
                    mmm = self._create_menuitem(aa, self.menu_fired, cnt)

                if not submenu:
                    self.gtkmenu.append(mmm)
                    if cnt == 0:
                        mmm.set_sensitive(False)
                        self.gtkmenu.append(SeparatorMenuItem())
                else:
                    if cnt != 0:
                        self.gtkmenu.append(mmm)

            elif type(aa) == Menu:
                mmm = self._create_menuitem(aa.title, self.dummy, cnt)
                mmm.set_submenu(aa.gtkmenu)
                self.gtkmenu.append(mmm)
            else:
                raise ValueError("Menu needs text or submenu")
            cnt = cnt + 1

        if not submenu:
            self.gtkmenu.popup(None, None, None, None, event.button, event.time)

    def dummy(self, menu, menutext, arg):
        pass

    def _create_menuitem(self, string, action, arg = None):
        rclick_menu = Gtk.MenuItem(label=string)
        rclick_menu.connect("activate", action, string, arg);
        rclick_menu.show()
        return rclick_menu

    def menu_fired(self, menu, menutext, arg):
        #print ("menu item fired:", menutext, arg)
        if self.callb:
            self.callb(menutext, arg)
        self.gtkmenu = None

# ------------------------------------------------------------------------

class Lights(Gtk.Frame):

    def __init__(self, col_arr, size = 6, call_me = None):

        GObject.GObject.__init__(self)
        self.box_arr = []
        vboxs = Gtk.VBox()
        vboxs.set_spacing(4);
        vboxs.set_border_width(4)

        for aa in col_arr:
            box = self.colbox(pgutils.str2float(aa), size)
            vboxs.pack_start(box, False, False, False)
            self.box_arr.append(box)

        self.add(vboxs)

    def set_color(self, idx, col):
        if idx >= len(self.box_arr):
            raise ValueError(IDXERR)
        self.box_arr[idx].modify_bg(Gtk.StateFlags.NORMAL, pgutils.str2col(col))

    def set_colors(self, colarr):
        for idx in range(len(self.box_arr)):
            self.box_arr[idx].modify_bg(
                        Gtk.StateFlags.NORMAL, pgutils.str2col(colarr[idx]))

    def set_tooltip(self, idx, strx):
        if idx >= len(self.box_arr):
            raise ValueError(IDXERR)
        self.box_arr[idx].set_tooltip_text(strx)

    def set_tooltips(self, strarr):
        for idx in range(len(self.box_arr)):
            self.box_arr[idx].set_tooltip_text(strarr[idx])

    def get_size(self):
        return len (self.box_arr)

    def colbox(self, col, size):

        lab1 = Gtk.Label("  " * size + "\n" * (size // 3))
        lab1.set_lines(size)
        eventbox = Gtk.EventBox()
        frame = Gtk.Frame()
        frame.add(lab1)
        eventbox.add(frame)
        eventbox.color =  col  # Gtk.gdk.Color(col)
        eventbox.modify_bg(Gtk.StateFlags.NORMAL, pgutils.float2col(eventbox.color))
        return eventbox

class ScrollListBox(Gtk.Frame):

    def __init__(self, limit = -1, colname = '', callme = None):
        Gtk.Frame.__init__(self)
        self.listbox = ListBox(limit, colname)
        if callme:
            self.listbox.set_callback(callme)
        self.listbox.scroll = Gtk.ScrolledWindow()
        self.listbox.scroll.add_with_viewport(self.listbox)
        self.add(self.listbox.scroll)
        self.autoscroll = True

    # Propagate needed ops to list control

    def append_end(self, strx):
        #print("ser str append", strx)
        self.listbox.append(strx)

        if self.autoscroll:
            pgutils.usleep(10)              # Wait for it to go to screen
            sb = self.listbox.scroll.get_vscrollbar()
            sb.set_value(2000000)
        self.listbox.select(-1)

    def clear(self):
        self.listbox.clear()

    def select(self, num):
        self.listbox.select(num)

# ------------------------------------------------------------------------

class   ComboBox(Gtk.ComboBox):

    def __init__(self, init_cont = [], callme = None):

        self.store = Gtk.ListStore(str)
        Gtk.ComboBox.__init__(self)

        self.set_model(self.store)
        cell = Gtk.CellRendererText()

        cell.set_property("text", "hello")
        #cell.set_property("background", "#ffff00")
        #cell.set_property("background-set", True)
        cell.set_padding(10, 0)

        if callme:
            self.connect("changed", callme)

        #cell.set_property("foreground", "#ffff00")
        #cell.set_property("foreground-set", True)
        #print("background-set", cell.get_property("background-set"))
        #print("foreground-set", cell.get_property("foreground-set"))
        #print(" list_properties", cell.list_properties())

        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.set_entry_text_column(0)

        for bb in init_cont:
            self.store.append([bb])

        self.connect("changed", self.combo_changed)

    def combo_changed(self, combo):
        name = ""
        tree_iter = combo.get_active_iter()
        try:
            if tree_iter is not None:
                model = combo.get_model()
                name = model[tree_iter][0]
                #print("Selected: name=%s" % (name))
            else:
                entry = combo.get_child()
                name = entry.get_text()
                #print("Entered: %s" % name)
        except:
            pass

        #print("Combo new selection / entry: '%s'" % name)

    def delall(self):
         # Delete previous contents
        try:
            while True:
                root = self.store.get_iter_first()
                if not root:
                    break
                try:
                    self.store.remove(root)
                except:
                    print("except: self.store remove")
        except:
            print("combo delall", sys.exc_info())
            pass

    # --------------------------------------------------------------------
    def  sel_text(self, txt):

        #print("Sel combo text")

        model = self.get_model()
        iter = model.get_iter_first()
        if iter:
            cnt = 0
            while True:

                #print("entry %d" % cnt, model[iter][0], txt)
                if  model[iter][0] == txt:
                    #print("Found %d" % cnt, model[iter][0])
                    self.set_active_iter(iter)
                    break

                iter = model.iter_next(iter)
                if not iter:
                    break
                cnt += 1

    def     sel_first(self):
        model = self.get_model()
        iter = model.get_iter_first()
        self.set_active_iter(iter)

class Rectangle():

    # Accept rect, array, integers
    def __init__(self, *rrr):
        #Gdk.Rectangle.__init__(self)
        if len(rrr) == 4:
            idx = 0
            for aa in rrr:
                bb = int(aa)
                if idx == 0:
                    self.x = bb
                elif idx == 1:
                    self.y = bb
                elif idx == 2:
                    #self.width = bb
                    self.w = bb
                elif idx == 3:
                    #self.height = bb
                    self.h = bb
                else:
                    raise ValueError
                idx += 1
        else:
            for aaa in rrr:
                self.x = aaa[0]; self.y =  aaa[1]
                self.w =  aaa[2];
                #self.width =  aaa[2];
                self.h =  aaa[3]
                #self.height =  aaa[3]
                break
            pass

    # Make it smaller
    def resize(self, ww, hh = 0):
        if hh == 0:
            hh = ww

        #if ww + self.w <= 0 or hh + self.h <= 0:
        #    raise (ValuError, "Cannot have negative rect size")

        self.x -= ww/2; self.w += ww
        self.y -= hh/2; self.h += hh

    def copy(self):
        #print("rect to copy", str(self))
        #print("rect to copy", dir(self))
        nnn = Rectangle()                   # New Instance
        '''
        # Self
        for aa in dir(self):
            try:
                #nnn.__setattr__(aa, self.__getattribute__(aa))
                nnn.aa = self.__getattribute__(aa)
                #print("cp:", aa, end = "")
                #if type(self.__getattribute__(aa)) == int:
                #    print(" -> ", self.__getattribute__(aa), end= " ")
                #print(" --- ", end = "")
            except:
                #print(sys.exc_info())
                print("no", aa)
                pass
        '''

        # Assign explictly
        nnn.x = self.x + 0
        nnn.y = self.y + 0
        nnn.w = self.w + 0
        nnn.h = self.h + 0

        #nnn.width = self.width + 1
        #nnn.height = self.height + 1

        #print("rect out", str(nnn))
        #print("rect out", dir(nnn))
        return nnn

    # Normalize; Put the rect in positive space

    def norm(self, rect):
        rect3 = rect.copy()
        if rect3.h < 0:
            rect3.y -= abs(rect3.h)
            rect3.h = abs(rect3.h)
        if rect3.w < 0:
            rect3.x -= abs(rect3.w)
            rect3.w = abs(rect3.w)
        return rect3

    # I was too lazy to write it; Crappy Gdk rect kicked me to it

    # ==========    self
    # =        =
    # =    ----=----
    # ====|======   |  rect2
    #     |         |
    #      ---------

    def intersect(self, rect2):

        rect3 = self.norm(rect2);   rect4 = self.norm(self)

        urx = rect4.x + rect4.w;    lry = rect4.y + rect4.h
        urx2 = rect3.x + rect3.w;   lry2 = rect3.y + rect3.h
        inter = 0

        # X intersect
        if rect3.x >= rect4.x and rect3.x <= urx:
            inter += 1;
        # Y intersect
        if rect3.y >= rect4.y and rect3.y <= lry:
            inter += 1;

        # X intersect rev
        if rect4.x >= rect3.x and rect4.x <= urx2:
            inter += 1;
        # Y intersect rev
        if rect4.y >= rect3.y and rect4.y <= lry2:
            inter += 1;

        #print("inter", inter, str(self), "->", str(rect2))
        return (inter >= 2, self.x)

    # I was too lazy to write it; Crappy Gdt rect kicked me to it
    def contain(self, rect2):
        #self.dump()
        #rect2.dump()
        inter = 0
        # X intersect
        if rect2.x >= self.x and rect2.x + rect2.w <= self.x + self.w:
            inter += 1;
        # Y intersect
        if rect2.y >= self.y and rect2.y + rect2.h <= self.y + self.h:
            inter += 1;
        #print("inter", inter)
        return (inter == 2, self.x)

    # Convert index to values
    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.w
        elif key == 3:
            return self.h
        else:
            raise IndexError;

    def dump(self):
        return (self.x, self.y, self.w, self.h)

    '''
    # This was killed in favour of self implemented Rectangle class
    def __getattr__(self, attr):
        if attr == "w":
            return self.width
        elif attr == "h":
            return self.height
        else:
            return super(Gdk.Rectangle, self).__getattr__(attr)

    def __setattr__(self, attr, val):
        if attr == "w":
            self.width = val
        elif attr == "h":
            self.height = val
        else:
            super(Gdk.Rectangle, self).__setattr__(attr, val)
    '''

    def __str__(self):
        return "R: x=%d y=%d w=%d h=%d" % (self.x, self.y, self.w, self.h)

# Right click button

class RCLButt(Gtk.Button):

    def __init__(self, labelx, callme = None, rcallme = None, space = 2, ttip = None):
        #super().__init__(self)
        GObject.GObject.__init__(self)
        self.rcallme = rcallme
        self.callme  = callme
        self.set_label(" " * space + labelx + " " * space)
        self.set_use_underline (True)

        if ttip:
            self.set_tooltip_text(ttip)

        #col = Gdk.RGBA(); col.parse("#ccffcc")
        #self.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color(1000, 10000, 1))
        #style = self.get_style_context())

        self.connect("clicked", self.clicked)
        self.connect("button-press-event", self.pressed)
        self.connect("button-release-event", self.pressed)
        self.connect("draw", self.draw)

    def draw(self, area, cr):
        #print("button", area, cr)
        rect = self.get_allocation()
        col = (.2, .7, .7)
        cr.set_source_rgb(col[0], col[1], col[2])
        cr.rectangle(0, 0, rect.width, rect.height)
        cr.fill()
        layout = self.create_pango_layout("Button Here ... LONG")
        xxx, yyy = layout.get_pixel_size()
        xx = rect.width / 2 - xxx/2
        yy = rect.height / 2 - yyy/2
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(xx, yy)
        PangoCairo.show_layout(cr, layout)
        #return True

    def  pressed(self, arg1, event):
        #print("pressed", arg1, event)
        if  event.type == Gdk.EventType.BUTTON_RELEASE:
            if event.button == 1:
                if self.callme:
                    self.callme(self, arg1, event)

            if event.button == 3:
                if self.rcallme:
                    self.rcallme(self, arg1, event)

        else:
            # Unknown button action
            pass

    def clicked(self, arg1):
        pass
        #print("clicked", arg1)
        #if self.callme:
        #    self.callme(arg1)

# ------------------------------------------------------------------------
# Highlite test items

def set_gui_testmode(flag):
    global gui_testmode
    gui_testmode = flag

if __name__ == '__main__':
    print("This file was not meant to run as the main module")

# EOF






