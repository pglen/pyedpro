#!/usr/bin/env python

import sys, os, re

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import GdkPixbuf

# XPM data for missing image

xpm_data = [
"16 16 3 1",
"       c None",
".      c #000000000000",
"X      c #FFFFFFFFFFFF",
"                ",
"   ......       ",
"   .XXX.X.      ",
"   .XXX.XX.     ",
"   .XXX.XXX.    ",
"   .XXX.....    ",
"   ..XXXXX..    ",
"   .X.XXX.X.    ",
"   .XX.X.XX.    ",
"   .XXX.XXX.    ",
"   .XX.X.XX.    ",
"   .X.XXX.X.    ",
"   ..XXXXX..    ",
"   .........    ",
"                ",
"                "
]

class PangoView(Gtk.Window):

    hovering_over_link = False
    waiting = False

    hand_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
    regular_cursor = Gdk.Cursor(Gdk.CursorType.XTERM)
    wait_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
    callback = None
    bscallback = None

    # Create the toplevel window
    def __init__(self, pvg, parent=None):

        Gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: Gtk.main_quit())

        self.set_title(self.__class__.__name__)
        #self.set_border_width(0)

        img_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(img_dir, "pangview.png")

        try:
            self.set_icon_from_file(img_path)
        except:
            #print ("Cannot load app icon.")
            pass

        #rect = self.get_allocation()

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print (disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        #www = rect.width;
        #hhh = rect.height;

        #self.set_default_size(7*www/8, 7*hhh/8)
        if pvg.full_screen:
            self.set_default_size(www, hhh)
        else:
            #self.set_default_size(3*www/4, 3*hhh/4)
            self.set_default_size(hhh, 3*hhh/4)

        self.set_position(Gtk.WindowPosition.CENTER)
        #self.set_title("Pango test display");

        hpaned = Gtk.HPaned()
        hpaned.set_border_width(5)

        self.add(hpaned)

        view1 = Gtk.TextView();
        view1.set_border_width(8)

        view1.connect("key-press-event", self.key_press_event)
        view1.connect("event-after", self.event_after)
        view1.connect("motion-notify-event", self.motion_notify_event)
        view1.connect("visibility-notify-event", self.visibility_notify_event)

        view1.set_editable(False)
        view1.set_cursor_visible(False)
        self.view = view1

        self.buffer_1 = view1.get_buffer()
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(view1)

        view2 = Gtk.TextView();
        view2.set_border_width(8)
        view2.set_editable(False)
        self.buffer_2 = view2.get_buffer()
        sw2 = Gtk.ScrolledWindow()
        sw2.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw2.add(view2)

        view2.connect("key-press-event", self.key_press_event2)
        view2.connect("event-after", self.event_after2)
        view2.connect("motion-notify-event", self.motion_notify_event2)
        view2.connect("visibility-notify-event", self.visibility_notify_event2)

        hpaned.add1(sw2)
        hpaned.add2(sw)

        self.hpaned = hpaned
        self.set_pane_position(1)

        self.iter = self.buffer_1.get_iter_at_offset(0)
        self.iter2 = self.buffer_1.get_iter_at_offset(0)

        self.set_focus(view1)

        self.show_all()

    def set_pane_position(self, pos):
        self.hpaned.set_position(pos);

    def set_fullscreen(self):
        www = Gdk.screen_width();
        hhh = Gdk.screen_height();
        self.resize(www, hhh)

    def showcur(self, flag):
        #return
        self.waiting = flag
        #wx, wy, modx = self.view.window.get_pointer()
        wx, wy = self.view.get_pointer()

        bx, by = self.view.window_to_buffer_coords(Gtk.TextWindowType.TEXT, wx, wy)
        self.set_cursor_if_appropriate (self.view, bx, by)
        #self.view.window.get_pointer()

    # We manipulate the buffers through these functions:

    def clear(self, flag=False):
        if flag:
            self.buffer_2.set_text("", 0)
            self.iter2 = self.buffer_2.get_iter_at_offset(0)
        else:
            self.buffer_1.set_text("", 0)
            self.iter = self.buffer_1.get_iter_at_offset(0)

    def add_pixbuf(self, pixbuf, flag=False):
        if flag:
            self.buffer_2.insert_pixbuf(self.iter2, pixbuf)
        else:
            self.buffer_1.insert_pixbuf(self.iter, pixbuf)
        self.waiting = False

    def add_broken(self, flag=False):
        pixbuf = Gdk.pixbuf_new_from_xpm_data(xpm_data)
        if flag:
            self.buffer_2.insert_pixbuf(self.iter2, pixbuf)
        else:
            self.buffer_1.insert_pixbuf(self.iter, pixbuf)
        self.waiting = False

    def add_text(self, text, flag=False):
        if flag:
            self.buffer_2.insert(self.iter2, text)
        else:
            self.buffer_1.insert(self.iter, text)
        self.waiting = False

    def add_text_tag(self, text, tags, flag=False):
        if flag:
            self.buffer_2.insert_with_tags_by_name(self.iter2, text, tags)
        else:
            self.buffer_1.insert_with_tags_by_name(self.iter, text, tags)
        self.waiting = False

    def add_text_xtag(self, text, tags, flag=False):
        if flag:
            try: self.buffer_2.get_tag_table().add(tags)
            except: pass
            self.buffer_2.insert_with_tags(self.iter2, text, tags)
        else:
            try: self.buffer_1.get_tag_table().add(tags)
            except: pass

            self.buffer_1.insert_with_tags(self.iter, text, tags)
        self.waiting = False

    # --------------------------------------------------------------------
    # Links can be activated by pressing Enter.

    def key_press_event(self, text_view, event):
        if (event.keyval == Gdk.KEY_Return or
            event.keyval == Gdk.KEY_KP_Enter):
            buffer = text_view.get_buffer()
            iter = buffer.get_iter_at_mark(buffer.get_insert())
            self.follow_if_link(text_view, iter)
        elif event.keyval == Gdk.KEY_Tab:
            #print ("Tab")
            pass
        elif event.keyval == Gdk.KEY_space:
            #print ("Space")
            pass
        elif event.keyval == Gdk.KEY_BackSpace:
            if self.bscallback:
                self.bscallback()
        if event.keyval == Gdk.KEY_Escape or event.keyval == Gdk.KEY_q:
            sys.exit(0)

        if event.state & Gdk.ModifierType.MOD1_MASK:
            if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
                sys.exit(0)
        return False

    # Links can also be activated by clicking.
    def event_after(self, text_view, event):
        if event.type != Gdk.EventType.BUTTON_RELEASE:
            return False
        if event.button != 1:
            return False
        buffer = text_view.get_buffer()

        # We should not follow a link if the user has selected something
        try:
            start, end = buffer.get_selection_bounds()
        except ValueError:
            # If there is nothing selected, None is return
            pass
        else:
            if start.get_offset() != end.get_offset():
                return False

        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        iter = text_view.get_iter_at_location(x, y)

        self.follow_if_link(text_view, iter)
        return False

    def follow_if_link(self, text_view, iter):
        ''' Looks at all tags covering the position of iter in the text view,
            and if one of them is a link, follow it by showing the page identified
            by the data attached to it.
        '''
        tags = iter.get_tags()
        for tag in tags:
            page = tag.get_data("link")
            if page != None:
                #print ("Calling link ", page)
                # Paint a new cursor
                self.waiting = True
                wx, wy = text_view.get_pointer()
                bx, by = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, wx, wy)
                self.set_cursor_if_appropriate (text_view, bx, by)
                #text_view.window.get_pointer()

                if self.callback:
                    self.callback(page)
                break

    # Looks at all tags covering the position (x, y) in the text view,
    # and if one of them is a link, change the cursor to the "hands" cursor
    # typically used by web browsers.

    def set_cursor_if_appropriate(self, text_view, x, y):

        '''hovering = False
        buffer = text_view.get_buffer()
        #iter = text_view.get_iter_at_location(x, y)
        iter = text_view.get_iter_at_position(x, y)
        tags = iter.get_tags()
        for tag in tags:
            page = tag.get_data("link")
            #if page != 0:
            if page != None:
                hovering = True
                break

        if hovering != self.hovering_over_link:
            self.hovering_over_link = hovering
        '''

        if self.waiting:
            cur = self.wait_cursor
        elif self.hovering_over_link:
            cur = self.hand_cursor
        else:
            cur = self.regular_cursor

        try:
            text_view.get_window(Gtk.TextWindowType.TEXT).set_cursor()
        except:
            print (sys.exc_info())

    # Update the cursor image if the pointer moved.

    def motion_notify_event(self, text_view, event):
        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)
        #text_view.window.get_pointer()
        return False

    # Also update the cursor image if the window becomes visible
    # (e.g. when a window covering it got iconified).

    def visibility_notify_event(self, text_view, event):
        wx, wy = text_view.get_pointer()
        bx, by = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, wx, wy)

        self.set_cursor_if_appropriate (text_view, bx, by)
        return False

    def key_press_event2(self, text_view, event):
        if (event.keyval == Gdk.KEY_Return or
            event.keyval == Gdk.KEY_KP_Enter):
            buffer = text_view.get_buffer()
            iter = buffer.get_iter_at_mark(buffer.get_insert())
            self.follow_if_link(text_view, iter)
        elif event.keyval == Gdk.KEY_Tab:
            #print ("Tab")
            pass
        elif event.keyval == Gdk.KEY_space:
            #print ("Space")
            pass
        elif event.keyval == Gdk.KEY_BackSpace:
            if self.bscallback:
                self.bscallback()
        if event.keyval == Gdk.KEY_Escape or event.keyval == Gdk.KEY_q:
            sys.exit(0)

        if event.state & Gdk.ModifierType.MOD1_MASK:
            if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
                sys.exit(0)

        return False

    def event_after2(self, text_view, event):
        if event.type != Gdk.EventType.BUTTON_RELEASE:
            return False
        if event.button != 1:
            return False
        buffer = text_view.get_buffer()

        # we should not follow a link if the user has selected something
        try:
            start, end = buffer.get_selection_bounds()
        except ValueError:
            # If there is nothing selected, None is return
            pass
        else:
            if start.get_offset() != end.get_offset():
                return False

        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        iter = text_view.get_iter_at_location(x, y)

        self.follow_if_link(text_view, iter)
        return False

    def visibility_notify_event2(self, text_view, event):
        wx, wy = text_view.get_pointer()
        bx, by = text_view.window_to_buffer_coords\
            (Gtk.TextWindowType.WIDGET, wx, wy)

        self.set_cursor_if_appropriate (text_view, bx, by)
        return False

    def motion_notify_event2(self, text_view, event):
        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)
        #text_view.window.get_pointer()
        return False

    def set_cursor_if_appropriate2(self, text_view, x, y):

        hovering = False
        buffer = text_view.get_buffer()
        iter = text_view.get_iter_at_location(x, y)
        tags = iter.get_tags()
        for tag in tags:
            page = tag.get_data("link")
            #if page != 0:
            if page != None:
                hovering = True
                break

        if hovering != self.hovering_over_link:
            self.hovering_over_link = hovering

        if self.waiting:
            text_view.get_window(Gtk.TEXT_WINDOW_TEXT).set_cursor(self.wait_cursor)
        elif self.hovering_over_link:
            text_view.get_window(Gtk.TEXT_WINDOW_TEXT).set_cursor(self.hand_cursor)
        else:
            text_view.get_window(Gtk.TEXT_WINDOW_TEXT).set_cursor(self.regular_cursor)

# Some globals read: (Pang View Globals):

class pvg():

    buf = None; xstack = None; verbose = False
    pgdebug = False; show_lexer = False; full_screen = False
    lstack = None;  fullpath = None; docroot = None
    got_clock = 0; show_timing = False; second = ""
    xfull_screen = False; flag = False; show_parse = False
    emit = False; show_state = False; pane_pos = -1

def main():
    PangoView(pvg)
    Gtk.main()

if __name__ == '__main__':
    main()

