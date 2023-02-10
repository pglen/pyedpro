#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings

#from pgutil import  *
#from pgui import  *

import pgutils

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import pgbox
import sutil

# Colors for editor selection. Use X11 color names.

font_colors =   \
        (
            # Color name; RGBA for display
            ("Black",       "#000000ff"),  ("White",       "#ffffffff"),
            ("Red",         "#ff0000ff"),  ("Green",       "#00ff00ff"),
            ("Blue",        "#0000ffff"),  ("Orange",      "#ff8800ff"),
            ("Yellow",      "#ffff00ff"),  ("Brown",       "#885500ff"),
            ("Cyan"   ,     "#00ffffff"),  ("Purple",      "#ff00ffff"),
            ("OrangeRed",    "#ff8888ff"), ("LightBlue",   "#8888ffff"),
            ("LightGreen",  "#88ff88ff"),  ("Gray",        "#888888ff"),
            ("LightGray",   "#aaaaaaff"),  ("Gold",        "#FFD700FF"),
            ("LightYellow", "#aaaaaa99ff"),  ("Gold",        "#FFD700FF"),
        )

font_sizes =      \
            (
            "7", "8", "9", "10", "12", "14", "18", "22", "24", "32", "36", "48", "64"
            )


class pgTextView(Gtk.VBox):

    def __init__(self, status = False):

        self.statstr = None
        Gtk.VBox.__init__(self)

        self.tagtablex = []
        self.callb = None
        self.grid = Gtk.Grid()
        self.add(self.grid)

        self._create_textview()
        self._create_toolbar()
        self._create_toolbar2()
        self._create_buttons()

        # Status bar
        self.statstr = Gtk.Label.new("Idle")
        self.statstr.set_halign(Gtk.Align.START)

        if  status:
            hstat = Gtk.HBox()
            hstat.pack_start(Gtk.Label.new("  Status:  "), 0, 0, 0)
            hstat.pack_start(Gtk.Label.new(" "), 0, 0, 0)
            hstat.pack_start(self.statstr, 1, 1, 0)

            self.grid.attach(hstat, 0, 4, 3, 1)

        self.textview.connect("key-press-event", self.area_key)
        self.textview.connect("move-cursor", self.area_curs)
        self.connect("button-press-event", self.area_button)
        #self.textview.connect("focus-out-event", self.focus_out)
        self.findcall = None;

    def  area_curs(self, ext_view, step, count, extend_selection):
        #print("step", step, "count", count)
        pass

    def _create_toolbar(self):

        nnn = 0
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 1, 3, 1)

        button_norm = Gtk.ToolButton()
        button_norm.set_icon_name("format-text-none-symbolic")
        button_norm.set_tooltip_text("Remove ALL Formatting")
        toolbar.insert(button_norm, nnn) ; nnn += 1

        button_bold = Gtk.ToolButton()
        button_bold.set_icon_name("format-text-bold-symbolic")
        button_bold.set_tooltip_text("Set Bold")
        toolbar.insert(button_bold, nnn)  ; nnn += 1

        button_italic = Gtk.ToolButton()
        button_italic.set_icon_name("format-text-italic-symbolic")
        button_italic.set_tooltip_text("Set Italic")
        toolbar.insert(button_italic, nnn)   ; nnn += 1

        button_underline = Gtk.ToolButton()
        button_underline.set_icon_name("format-text-underline-symbolic")
        button_underline.set_tooltip_text("Set Underline")
        toolbar.insert(button_underline, nnn)   ; nnn += 1

        button_sel = Gtk.ToolItem()

        combo = pgbox.ComboBox(font_sizes, self.combo_sel)
        #combo.sel_text("12")
        #print("str(self.mysize)", str(self.mysize))
        combo.sel_text(str(int(self.mysize)))
        combo.set_tooltip_text("Set Font Size")

        #hb = Gtk.HBox()
        #hb.pack_start(Gtk.Label.new("Font Size:"), 0, 0, 2)
        #hb.pack_start(combo, 0, 0, 0)
        button_sel.add(combo)
        toolbar.insert(button_sel, nnn)  ; nnn += 1

        button_sel2 = Gtk.ToolItem()

        #print("mmm", mmm)
        #hb2 = Gtk.HBox()
        combo2 = pgbox.ColorCombo(font_colors, self.combo_sel2)
        combo2.sel_text("Black")
        combo2.set_tooltip_text("Set Font Color")

        #hb2.pack_start(Gtk.Label.new("Font Color:"), 0, 0, 2)
        #hb2.pack_start(combo2, 0, 0, 0)
        button_sel2.add(combo2)
        toolbar.insert(button_sel2, nnn)  ; nnn += 1

        # ----------------------------------------------------------------

        button_sel3 = Gtk.ToolItem()
        #hb3 = Gtk.HBox()
        combo3 = pgbox.ColorCombo(font_colors, self.combo_sel3)
        combo3.sel_text("White")
        combo3.set_tooltip_text("Set Background Color")
        #hb3.pack_start(Gtk.Label.new("Font Back:"), 0, 0, 2)
        #hb3.pack_start(combo3, 0, 0, 0)
        button_sel3.add(combo3)
        toolbar.insert(button_sel3, nnn)  ; nnn += 1

        button_color = Gtk.ToolButton()
        button_color.set_icon_name("preferences-desktop-theme")
        button_color.set_tooltip_text("Remove Color Attributes")
        button_color.connect("clicked", self.on_rm_color)
        toolbar.insert(button_color, nnn)  ; nnn += 1

        button_norm.connect("clicked", self.on_rm_clicked, self.tag_norm)
        button_bold.connect("clicked", self.on_button_clicked, self.tag_bold)
        button_italic.connect("clicked", self.on_button_clicked, self.tag_italic)
        button_underline.connect("clicked", self.on_button_clicked, self.tag_underline)

        #toolbar.insert(Gtk.SeparatorToolItem(), nnn)  ; nnn += 1

    def _create_toolbar2(self):

        nnn = 0
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 0, 3, 1)

        radio_justifyleft = Gtk.RadioToolButton()
        radio_justifyleft.set_icon_name("format-justify-left-symbolic")
        toolbar.insert(radio_justifyleft, nnn)   ; nnn += 1

        radio_justifycenter = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifycenter.set_icon_name("format-justify-center-symbolic")
        toolbar.insert(radio_justifycenter, nnn)   ; nnn += 1

        radio_justifyright = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifyright.set_icon_name("format-justify-right-symbolic")
        toolbar.insert(radio_justifyright, nnn)   ; nnn += 1

        radio_justifyfill = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifyfill.set_icon_name("format-justify-fill-symbolic")
        toolbar.insert(radio_justifyfill, nnn)   ; nnn += 1

        radio_justifyleft.connect(
            #"toggled", self.on_justify_toggled, Gtk.Justification.LEFT
            "toggled", self.on_justify_toggled, self.tag_left
        )
        radio_justifycenter.connect(
            #"toggled", self.on_justify_toggled, Gtk.Justification.CENTER
            "toggled", self.on_justify_toggled, self.tag_center
        )
        radio_justifyright.connect(
            "toggled", self.on_justify_toggled, self.tag_right
        )

        radio_justifyfill.connect(
            "toggled", self.on_justify_toggled, self.tag_fill
        )

        button_big = Gtk.ToolButton()
        button_big.set_icon_name("format-text-larger-symbolic")
        button_big.set_tooltip_text("Set Superscript")
        button_big.connect("clicked", self.on_super_button, self.tag_super)
        toolbar.insert(button_big, nnn)  ; nnn += 1

        button_big = Gtk.ToolButton()
        button_big.set_icon_name("format-text-smaller-symbolic")
        button_big.set_tooltip_text("Set Subscript")
        button_big.connect("clicked", self.on_super_button, self.tag_sub)
        toolbar.insert(button_big, nnn)  ; nnn += 1

        button_big = Gtk.ToolButton()
        button_big.set_icon_name("tools-check-spelling")
        button_big.set_tooltip_text("Set XX Large font")
        button_big.connect("clicked", self.on_button_clicked, self.tag_xbig)
        toolbar.insert(button_big, nnn)   ; nnn += 1

        button_color = Gtk.ToolButton()
        button_color.set_icon_name("font-x-generic")
        button_color.set_tooltip_text("Set Font")
        #button_color.connect("clicked", self.on_color_clicked, 0)
        toolbar.insert(button_color, nnn)  ; nnn += 1

        toolbar.insert(Gtk.SeparatorToolItem(), nnn)   ; nnn += 1

        button_clear = Gtk.ToolButton()
        button_clear.set_icon_name("edit-clear-symbolic")
        button_clear.set_tooltip_text("Remove ALL formatting")
        button_clear.connect("clicked", self.on_clear_clicked)
        toolbar.insert(button_clear, nnn)    ; nnn += 1

        toolbar.insert(Gtk.SeparatorToolItem(), nnn)   ; nnn += 1

        button_search = Gtk.ToolButton()
        button_search.set_icon_name("system-search-symbolic")
        button_search.set_tooltip_text("Search current text")
        button_search.connect("clicked", self.on_search_clicked)
        toolbar.insert(button_search, nnn)   ; nnn += 1

        button_mag = Gtk.ToolButton()
        button_mag.set_icon_name("zoom-fit-best")
        button_mag.set_tooltip_text("Magnify Font")
        button_mag.connect("clicked", self.on_zoom_clicked)
        toolbar.insert(button_mag, nnn)  ; nnn += 1

        button_mag = Gtk.ToolButton()
        button_mag.set_icon_name("zoom-in-symbolic")
        button_mag.set_tooltip_text("Set larger font")
        button_mag.connect("clicked", self.on_zoom_clicked)
        toolbar.insert(button_mag, nnn)   ; nnn += 1

        button_mag2 = Gtk.ToolButton()
        button_mag2.set_icon_name("zoom-out-symbolic")
        button_mag2.set_tooltip_text("Set smaller Font")
        button_mag2.connect("clicked", self.on_unzoom_clicked)
        toolbar.insert(button_mag2, nnn)   ; nnn += 1

    def area_key(self, widget, event):
        #print("TextViewWin keypress", event.string, event.keyval)
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            print("TextViewWin control keypress", event.string, event.keyval)

            if event.keyval == 102:
                #print("control find")
                if self.findcall:
                    # Call with object argument
                    self.findcall[0](self.findcall[1])


    def area_button(self, but, event):
        #print("click", event.x, event.y)
        # textview
        endd = self.textbuffer.get_end_iter()
        isx, iter = self.textview.get_iter_at_location(event.x, event.y)
        if isx:
            txt =  self.textbuffer.get_text(iter, endd, False)
            #print("[", txt[:4], "]")

            #defvals = self.textview.get_default_attributes()
            #print(defvals.appearance.rise)

            #ixy, attr = iter.get_attributes()
            #if ixy:
            #    #attr.ref()
            #    #print(attr.refcount)
            #    print(dir(attr))
            #    #print(attr.refcount)
            #    #print(attr.appearance.rise)
            #    attr.unref()
            #else:
            #    print("no artt")

            #attr.unref()


    def on_rm_color(self, arg1):
        print(  "on_rm_color", arg1)

        bounds = self.textbuffer.get_selection_bounds()

        if not len(bounds):
            if self.statstr:
                self.statstr.set_text("No selection")
            #print("No selection")
            return
        else:
            start, end = bounds

            # Clear out old colors
            for cc in range(len(font_colors)):
                rrr = "backgr%d" % cc
                self.textbuffer.remove_tag(getattr(self, rrr), start, end)

            for cc in range(len(font_colors)):
                rrr = "color%d" % cc
                self.textbuffer.remove_tag(getattr(self, rrr), start, end)

            self.textbuffer.set_modified(1)

    def on_combo_clicked(self, arg1, arg2):
        #print("on_combo_clicked")
        #cont = ("12", "32", "64")
        #combo_box = pgbox.ComboBox(cont)
        #combo_box.show()
        pass

    def combo_sel(self, sel):
        #print("combo_sel", sel)
        bounds = self.textbuffer.get_selection_bounds()
        if not len(bounds):
            if self.statstr:
                self.statstr.set_text("No selection")
            #print("No selection")
            return
        else:
            nnn = "size%d" % int(sel);
            start, end = bounds

            # Femove size tags from here
            for aa in font_sizes:
                rrr = "size%d" % int(aa);
                self.textbuffer.remove_tag(getattr(self, rrr), start, end)
            try:
                self.textbuffer.apply_tag(getattr(self, nnn), start, end)
                self.textbuffer.set_modified(1)
            except:
                print("Cannot apply size tag ", nnn, sys.exc_info())

    def combo_sel2(self, sel):
        #print("combo_sel2", sel)
        bounds = self.textbuffer.get_selection_bounds()

        if not len(bounds):
            if self.statstr:
                self.statstr.set_text("No selection")
            #print("No selection")
            return
        else:
            # Clear out old colors
            start, end = bounds
            for cc in range(len(font_colors)):
                rrr = "color%d" % cc
                self.textbuffer.remove_tag(getattr(self, rrr), start, end)

            # Find out the offset:
            cnt = 0
            for aa, bb in font_colors:
                if aa == sel:
                    break
                cnt += 1
            nnn = "color%d" % cnt
            #print("nnn", nnn)
            start, end = bounds
            try:
                self.textbuffer.apply_tag(getattr(self, nnn), start, end)
                self.textbuffer.set_modified(1)
            except:
                print("Cannot apply size tag ", nnn, sys.exc_info())

    def combo_sel3(self, sel):
        #print("combo_sel3", sel)
        bounds = self.textbuffer.get_selection_bounds()

        if not len(bounds):
            if self.statstr:
                self.statstr.set_text("No selection")
            #print("No selection")
            return
        else:
            start, end = bounds

            # Clear out old colors
            for cc in range(len(font_colors)):
                rrr = "backgr%d" % cc
                self.textbuffer.remove_tag(getattr(self, rrr), start, end)

            # Find out the offset:
            cnt = 0
            for aa, bb in font_colors:
                if aa == sel:
                    break
                cnt += 1

            nnn = "backgr%d" % cnt
            #print("nnn", nnn)

            try:
                self.textbuffer.apply_tag(getattr(self, nnn), start, end)
                self.textbuffer.set_modified(1)
            except:
                print("Cannot apply size tag ", nnn, sys.exc_info())


    def on_zoom_clicked(self, arg1):

        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        mysize = myfd.get_size() / Pango.SCALE

        fd = Pango.FontDescription()
        fd.set_size((mysize + 1) * Pango.SCALE)
        self.textview.modify_font(fd)

    def on_unzoom_clicked(self, arg1):

        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        mysize = myfd.get_size() / Pango.SCALE

        fd = Pango.FontDescription()
        fd.set_size((mysize - 1) * Pango.SCALE)
        self.textview.modify_font(fd)

    def _create_textview(self):

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 2, 3, 1)

        scrolledwindow.add(self.textview)

        self.fd = Pango.FontDescription()
        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        self.mysize = myfd.get_size() / Pango.SCALE
        self.myfam = myfd.get_family()
        #print(self.mysize)

        #self.textview.set_has_window(True)

        #self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        self.tag_regular = self.textbuffer.create_tag("regular", size=self.mysize * Pango.SCALE)
        self.tag_super   = self.textbuffer.create_tag("super", rise=5 * Pango.SCALE)
        self.tag_sub     = self.textbuffer.create_tag("sub",   rise=-5 * Pango.SCALE)
        self.tag_norm    = self.textbuffer.create_tag("norm", weight=14*Pango.SCALE)
        self.tag_xbig    = self.textbuffer.create_tag("xbig", size=30*Pango.SCALE)
        self.tag_big     = self.textbuffer.create_tag("big", size=20*Pango.SCALE)
        #self.tag_red     = self.textbuffer.create_tag("red", foreground="red")
        #self.tag_redbg   = self.textbuffer.create_tag("redbg", background="red")
        self.tag_norm    = self.textbuffer.create_tag("normal", style=Pango.Style.NORMAL)
        self.tag_bold    = self.textbuffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tag_italic     = self.textbuffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tag_underline  = self.textbuffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.tag_found      = self.textbuffer.create_tag("found", background="yellow")
        self.tag_left       = self.textbuffer.create_tag("justleft", justification=Gtk.Justification.LEFT)
        self.tag_center     = self.textbuffer.create_tag("justcent", justification=Gtk.Justification.CENTER)
        self.tag_right      = self.textbuffer.create_tag("justright", justification=Gtk.Justification.RIGHT)
        self.tag_fill       = self.textbuffer.create_tag("justfill",  justification=Gtk.Justification.FILL)

        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)

        # We create the attributes for all possible size tags
        for aa in font_sizes:
            nnn = "size%d" % int(aa);
            ttt = self.textbuffer.create_tag(nnn, size=int(aa) * Pango.SCALE)
            setattr(self, nnn, ttt)

        # We create the attributes for all possible color tags
        cnt = 0
        for aa, bb in font_colors:
            print
            nnn = "color%d" % cnt;
            ttt = self.textbuffer.create_tag(nnn, foreground=aa)
            setattr(self, nnn, ttt)
            cnt += 1

        cnt = 0
        for aa, bb in font_colors:
            nnn = "backgr%d" % int(cnt);
            ttt = self.textbuffer.create_tag(nnn, background=aa)
            setattr(self, nnn, ttt)
            cnt += 1

        #print(dir(self))

    def _create_buttons(self):

        #check_editable = Gtk.CheckButton(label="Editable")
        #check_editable.set_active(True)
        #check_editable.connect("toggled", self.on_editable_toggled)
        #self.grid.attach(check_editable, 0, 2, 1, 1)
        ##
        #check_cursor = Gtk.CheckButton(label="Cursor Visible")
        #check_cursor.set_active(True)
        #check_editable.connect("toggled", self.on_cursor_toggled)
        #self.grid.attach_next_to(
        #    check_cursor, check_editable, Gtk.PositionType.RIGHT, 1, 1)

        # ---------------------------------------------------------------------------------

        radio_wrapword =  Gtk.RadioButton.new_with_label_from_widget(None, "Word")
        self.grid.attach(radio_wrapword, 0, 3, 1, 1)

        radio_wrapchar =  Gtk.RadioButton.new_with_label_from_widget(radio_wrapword, "Character")
        self.grid.attach_next_to(
            radio_wrapchar, radio_wrapword, Gtk.PositionType.RIGHT, 1, 1)

        radio_wrapnone = Gtk.RadioButton.new_with_label_from_widget(radio_wrapword, "None")
        self.grid.attach_next_to(
                radio_wrapnone, radio_wrapchar, Gtk.PositionType.RIGHT, 1, 1)

        radio_wrapnone.connect("toggled", self.on_wrap_toggled, Gtk.WrapMode.NONE)
        radio_wrapchar.connect("toggled", self.on_wrap_toggled, Gtk.WrapMode.CHAR)
        radio_wrapword.connect("toggled", self.on_wrap_toggled, Gtk.WrapMode.WORD)

    def get_text(self):
        startt = self.textbuffer.get_start_iter()
        endd = self.textbuffer.get_end_iter()
        txt = self.textbuffer.get_text(startt, endd, False)
        return txt

    #def get_all(self):
    #    print("Get_all called")
    #    startt = self.buffer.get_start_iter()
    #    endd = self.buffer.get_end_iter()
    #    return self.buffer.get_text(startt, endd, True)

    def  get_modified(self):
        return self.textbuffer.get_modified()

    def  set_modified(self, valx):
        return self.textbuffer.set_modified(valx)

    def set_text(self, txt):
        if self.textbuffer.get_modified():
            startt = self.textbuffer.get_start_iter()
            endd = self.textbuffer.get_end_iter()
            old = self.textbuffer.get_text(startt, endd, False)
            if self.callb:
                self.callb(old)
            #print("old_content", old)
        self.textbuffer.set_text(txt)

    def on_rm_clicked(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.remove_all_tags(start, end)
            self.textbuffer.set_modified(1)

            # This was the old clear -- now clearing ALL
            #self.textbuffer.remove_tag(self.tag_bold, start, end)
            #self.textbuffer.remove_tag(self.tag_italic, start, end)
            #self.textbuffer.remove_tag(self.tag_underline, start, end)
            #self.textbuffer.remove_tag(self.tag_red, start, end)
            #self.textbuffer.remove_tag(self.tag_redbg, start, end)
            #self.textbuffer.remove_tag(self.tag_big, start, end)
            #self.textbuffer.remove_tag(self.tag_xbig, start, end)
            #self.textbuffer.remove_tag(self.tag_regular, start, end)

    def on_button_clicked(self, widget, tag):

        bounds = self.textbuffer.get_selection_bounds()
        if not len(bounds):
            if self.statstr:
                self.statstr.set_text("No style selection.")
        else:
            start, end = bounds
            #print("Apply Tag", tag, start, end)
            self.textbuffer.apply_tag(tag, start, end)
            self.textbuffer.set_modified(1)

    def on_super_button(self, widget, tag):

        bounds = self.textbuffer.get_selection_bounds()
        if not len(bounds):
            if self.statstr:
                self.statstr.set_text("No style selection.")
        else:
            start, end = bounds

            self.textbuffer.remove_tag(self.tag_super, start, end)
            self.textbuffer.remove_tag(self.tag_sub, start, end)

            #print("Apply Tag", tag, start, end)
            self.textbuffer.apply_tag(tag, start, end)
            self.textbuffer.set_modified(1)

    def on_size_button(self, widget, tag):

        bounds = self.textbuffer.get_selection_bounds()
        if not len(bounds):
            if self.statstr:
                self.statstr.set_text("No style selection.")
        else:
            start, end = bounds

            self.textbuffer.remove_tag(self.tag_super, start, end)
            self.textbuffer.remove_tag(self.tag_sub, start, end)

            #print("Apply Tag", tag, start, end)
            self.textbuffer.apply_tag(tag, start, end)
            self.textbuffer.set_modified(1)

    def on_clear_clicked(self, widget):
        start = self.textbuffer.get_start_iter()
        end = self.textbuffer.get_end_iter()
        self.textbuffer.remove_all_tags(start, end)
        self.textbuffer.set_modified(1)

    def on_editable_toggled(self, widget):
        self.textview.set_editable(widget.get_active())
        self.textbuffer.set_modified(1)

    def on_cursor_toggled(self, widget):
        self.textview.set_cursor_visible(widget.get_active())

    def on_wrap_toggled(self, widget, mode):
        self.textview.set_wrap_mode(mode)

    def on_justify_toggled(self, widget, justification):
        #print("on_justify_toggled", justification)
        #self.textview.set_justification(justification)
        #start = self.textbuffer.get_start_iter()
        #end = self.textbuffer.get_end_iter()

        bounds = self.textbuffer.get_selection_bounds()
        if not len(bounds):
            if self.statstr:
                self.statstr.set_text("No selection.")
        else:
            start, end = bounds
            #print("Apply Just Tag", justification, start, end)

            # Remove old justification
            self.textbuffer.remove_tag(self.tag_left, start, end)
            self.textbuffer.remove_tag(self.tag_center, start, end)
            self.textbuffer.remove_tag(self.tag_right, start, end)
            self.textbuffer.remove_tag(self.tag_fill, start, end)

            self.textbuffer.apply_tag(justification, start, end)
            self.textbuffer.set_modified(1)

    def on_search_clicked(self, widget):

        if self.findcall:
            # Call with object argument
            self.findcall[0](self.findcall[1])

        dialog.destroy()

    def search_and_mark(self, text, start):
        end = self.textbuffer.get_end_iter()
        match = start.forward_search(text, 0, end)

        if match is not None:
            match_start, match_end = match
            self.textbuffer.apply_tag(self.tag_found, match_start, match_end)
            self.search_and_mark(text, match_end)

    # --------------------------------------------------------------------
    # Load it here

    def deser_buff(self, buffx):

        if not buffx:
            return

        #print("UnSer buff")

        fmt = self.textbuffer.register_deserialize_tagset()
        self.textbuffer.deserialize_set_can_create_tags(fmt, True)
        self.textbuffer.deserialize(self.textbuffer, fmt,
                                self.textbuffer.get_start_iter(), buffx)
        self.textbuffer.set_modified(0)

    # --------------------------------------------------------------------
    # Save it here

    def ser_buff(self):

        #print("Ser buff")

        startt = self.textbuffer.get_start_iter()
        endd = self.textbuffer.get_end_iter()

        fmt = self.textbuffer.register_serialize_tagset()
        sss = self.textbuffer.serialize(self.textbuffer, fmt, startt, endd)
        if not sss: sss = b""
        return sss

    # Print TextTag  (testing)
    def ptag(self, ttt, tt):

        global cnt              # Print only one
        if cnt: return
        cnt += 1

        print(ttt)
        #print(dir(ttt))
        ll = ttt.list_properties()
        for aa in ll:
            #print(nnnn, end= " ")
            try:
                nn = tt.lookup(aa.name)
                if nn:
                    #nnn = nn.get_property("size")
                    #print("size", nnn)

                    lll = nn.list_properties()
                    for bb in lll:
                        nnn = bb.name   #get_property("name")
                        try:
                            pp = nn.get_property(nnn)
                        except:
                            pass
                        print(aa.name, "prop", "'" + nnn + "'" , "val =", pp)
                    print()

            except:
                print(sys.exc_info())
                pass
            #print()

        return

    # --------------------------------------------------------------------

    def print_tags(self):

        #startt = self.textbuffer.get_start_iter()
        #endd = self.textbuffer.get_end_iter()

        # TagTable
        #tt = self.textbuffer.get_property("tag-table")
        #print("table", tt)

        tt = self.textbuffer.get_tag_table()
        print("table", tt)
        tt.foreach(self.ptag, tt)
        print()

        return

        txt = self.textbuffer.get_text(startt, endd, False)
        lc =  self.textbuffer.get_char_count()
        for aa in range(lc):
            iii = self.textbuffer.get_iter_at_offset(aa)
            eee = self.textbuffer.get_iter_at_offset(aa+1)
            ccc = self.textbuffer.get_text(iii, eee, False)
            #print("aa", ccc)

        return txt


        #all = self.edview.get_all()
        #print("serialize", self.edview.textbuffer.get_deserialize_formats())
        #print("str", self.edview.serial_str())
        #print("serialize", self.edview.textbuffer.get_deserialize_formats())

        #vv = self.edview.textbuffer
        #startt = vv.get_start_iter(); endd = vv.get_end_iter()
        #while True:
        #    prev = startt.copy()
        #    nextok = startt.forward_line()
        #    ttt = vv.get_text(prev, startt, False)
        #    prevc = prev.copy()
        #    while True:
        #        sss = prevc.get_toggled_tags(True)
        #        if sss:
        #            print("tags on toggle", sss)
        #            for cc in sss:
        #                print("cc", cc.get_property("name"))
        #            print("pos", prevc.get_line(), prevc.get_line_offset())
        #        beg = prevc.copy()
        #        nextokc = prevc.forward_char()
        #        if not nextokc:
        #            break
        #        if startt == prevc:
        #            break
        #        chh = vv.get_text(beg, prevc, False)
        #        print(chh, end="")
        #
        #    #print("tags", prev.get_tags())
        #    #print("line:", ttt, end="")
        #    if not nextok:
        #        break
        #
        ##print("tags:", self.edview.textbuffer.get_tags())


