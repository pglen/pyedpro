#!/usr/bin/env python

import sys, os, re
import pygtk, gobject, gtk, pango
        
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

class PangoView(gtk.Window):

    hovering_over_link = False
    waiting = False

    hand_cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
    regular_cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)
    wait_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
    callback = None
    bscallback = None

    # Create the toplevel window
    def __init__(self, pvg, parent=None):
    
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())

        self.set_title(self.__class__.__name__)
        #self.set_border_width(0)
        
        try:
            self.set_icon_from_file("/usr/share/pangview/pang.png")
        except:
            print "Cannot load app icon."

        www = gtk.gdk.screen_width();
        hhh = gtk.gdk.screen_height();
        
        #self.set_default_size(7*www/8, 7*hhh/8)
        if pvg.full_screen:
            self.set_default_size(www, hhh)
        else:
            self.set_default_size(3*www/4, 3*hhh/4)

        self.set_position(gtk.WIN_POS_CENTER)
        #self.set_title("Pango test display");

        hpaned = gtk.HPaned()
        hpaned.set_border_width(5)
        
        self.add(hpaned)
                 
        view1 = gtk.TextView();
        view1.set_border_width(8)

        view1.connect("key-press-event", self.key_press_event)
        view1.connect("event-after", self.event_after)
        view1.connect("motion-notify-event", self.motion_notify_event)
        view1.connect("visibility-notify-event", self.visibility_notify_event)

        view1.set_editable(False)
        view1.set_cursor_visible(False)
        self.view = view1

        self.buffer_1 = view1.get_buffer()
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(view1)
       
        view2 = gtk.TextView();
        view2.set_border_width(8)
        view2.set_editable(False)
        self.buffer_2 = view2.get_buffer()
        sw2 = gtk.ScrolledWindow()
        sw2.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
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
        www = gtk.gdk.screen_width();
        hhh = gtk.gdk.screen_height();
        self.resize(www, hhh)
        
    def showcur(self, flag):
        #return
        self.waiting = flag
        wx, wy, modx = self.view.window.get_pointer()
        bx, by = self.view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, wx, wy)
        self.set_cursor_if_appropriate (self.view, bx, by)
        self.view.window.get_pointer()

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
        pixbuf = gtk.gdk.pixbuf_new_from_xpm_data(xpm_data)
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
        if (event.keyval == gtk.keysyms.Return or
            event.keyval == gtk.keysyms.KP_Enter):
            buffer = text_view.get_buffer()
            iter = buffer.get_iter_at_mark(buffer.get_insert())
            self.follow_if_link(text_view, iter)
        elif event.keyval == gtk.keysyms.Tab: 
            #print "Tab"
            pass
        elif event.keyval == gtk.keysyms.space: 
            #print "Space"
            pass
        elif event.keyval == gtk.keysyms.BackSpace: 
            if self.bscallback:
                self.bscallback()
        if event.keyval == gtk.keysyms.Escape or event.keyval == gtk.keysyms.q:
            sys.exit(0)
           
        if event.state & gtk.gdk.MOD1_MASK:       
            if event.keyval == gtk.keysyms.x or event.keyval == gtk.keysyms.X:
                sys.exit(0)            
        return False

    # Links can also be activated by clicking.
    def event_after(self, text_view, event):
        if event.type != gtk.gdk.BUTTON_RELEASE:
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

        x, y = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
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
                #print "Calling link ", page
                # Paint a new cursor
                self.waiting = True
                wx, wy, mod = text_view.window.get_pointer()
                bx, by = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, wx, wy)
                self.set_cursor_if_appropriate (text_view, bx, by)
                text_view.window.get_pointer()

                if self.callback:
                    self.callback(page)
                break

    # Looks at all tags covering the position (x, y) in the text view,
    # and if one of them is a link, change the cursor to the "hands" cursor
    # typically used by web browsers.

    def set_cursor_if_appropriate(self, text_view, x, y):

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
            text_view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.wait_cursor)
        elif self.hovering_over_link:
            text_view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.hand_cursor)
        else:
            text_view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.regular_cursor)

    # Update the cursor image if the pointer moved.

    def motion_notify_event(self, text_view, event):
        x, y = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
            int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)
        text_view.window.get_pointer()
        return False

    # Also update the cursor image if the window becomes visible
    # (e.g. when a window covering it got iconified).
    
    def visibility_notify_event(self, text_view, event):
        wx, wy, mod = text_view.window.get_pointer()
        bx, by = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, wx, wy)

        self.set_cursor_if_appropriate (text_view, bx, by)
        return False

    def key_press_event2(self, text_view, event):
        if (event.keyval == gtk.keysyms.Return or
            event.keyval == gtk.keysyms.KP_Enter):
            buffer = text_view.get_buffer()
            iter = buffer.get_iter_at_mark(buffer.get_insert())
            self.follow_if_link(text_view, iter)
        elif event.keyval == gtk.keysyms.Tab: 
            #print "Tab"
            pass
        elif event.keyval == gtk.keysyms.space: 
            #print "Space"
            pass
        elif event.keyval == gtk.keysyms.BackSpace: 
            if self.bscallback:
                self.bscallback()
        if event.keyval == gtk.keysyms.Escape or event.keyval == gtk.keysyms.q:
            sys.exit(0)
           
        if event.state & gtk.gdk.MOD1_MASK:       
            if event.keyval == gtk.keysyms.x or event.keyval == gtk.keysyms.X:
                sys.exit(0)
            
        return False

    def event_after2(self, text_view, event):
        if event.type != gtk.gdk.BUTTON_RELEASE:
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

        x, y = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
            int(event.x), int(event.y))
        iter = text_view.get_iter_at_location(x, y)

        self.follow_if_link(text_view, iter)
        return False

    def visibility_notify_event2(self, text_view, event):
        wx, wy, mod = text_view.window.get_pointer()
        bx, by = text_view.window_to_buffer_coords\
            (gtk.TEXT_WINDOW_WIDGET, wx, wy)

        self.set_cursor_if_appropriate (text_view, bx, by)
        return False

    def motion_notify_event2(self, text_view, event):
        x, y = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
            int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)
        text_view.window.get_pointer()
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
            text_view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.wait_cursor)
        elif self.hovering_over_link:
            text_view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.hand_cursor)
        else:
            text_view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.regular_cursor)

def main():
    PangoView()
    gtk.main()

if __name__ == '__main__':
    main()


