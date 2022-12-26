#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings

#from pgutil import  *
#from pgui import  *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import pgbox

deftext = "It puzzles me when I see a person lacking fundamentals is \
  able to amass a fortune to the tune of billions. What is even more \
puzziling is that they beleive their 'BS' and open flout all."

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self):

        self.cnt = 0
        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL)

        self.set_title("Test pgTextView")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(800, 600)
        #self.set_default_size(1024, 768)
        self.connect("destroy", self.OnExit)

        #self.connect("key-press-event", self.key_press_event)
        #self.connect("button-press-event", self.button_press_event)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        #vbox = Gtk.VBox();

        self.tview = pgTextView()
        self.tview.set_text(deftext)

        self.add(self.tview)

        self.show_all()

    def OnExit(self, win):
        #print("OnExit", win)
        Gtk.main_quit()


class pgTextView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.callb = None
        self.grid = Gtk.Grid()
        self.add(self.grid)

        self._create_textview()
        self._create_toolbar()
        self._create_buttons()

        self.textview.connect("key-press-event", self.area_key)
        #self.connect("button-press-event", self.area_button)
        #self.textview.connect("focus-out-event", self.focus_out)
        self.findcall = None;

    def area_key(self, widget, event):
        #print("TextViewWin keypress", event.string, event.keyval)
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == 102:
                #print("control find")
                if self.findcall:
                    # Call with object argument
                    self.findcall[0](self.findcall[1])

    '''
    def area_button(self, but, event):
        print("TextViewWin click", event.x, event.y)
        pass
    '''

    '''
    def focus_out(self, arg1, arg2):
        print("Focus out")
    '''

    def on_color_clicked(self, arg1, arg2):
        print(  "on_color_clicked", arg1, arg2)
        pass

    def on_combo_clicked(self, arg1, arg2):
        print("on_combo_clicked")
        cont = ("12", "32", "64")
        combo_box = pgbox.ComboBox(cont)
        combo_box.show()

    def combo_sel(self, sel):
        print("sel", sel)

    def combo_sel2(self, sel):
        print("sel2", sel)

    def _create_toolbar(self):

        nnn = 0
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 0, 3, 1)

        button_norm = Gtk.ToolButton()
        button_norm.set_icon_name("format-text-none-symbolic")
        button_norm.set_tooltip_text("Remove formatting")
        toolbar.insert(button_norm, nnn) ; nnn += 1

        button_bold = Gtk.ToolButton()
        button_bold.set_icon_name("format-text-bold-symbolic")
        button_bold.set_tooltip_text("Set Bold")
        toolbar.insert(button_bold, nnn)  ; nnn += 1

        button_italic = Gtk.ToolButton()
        button_italic.set_icon_name("format-text-italic-symbolic")
        toolbar.insert(button_italic, nnn)   ; nnn += 1

        button_underline = Gtk.ToolButton()
        button_underline.set_icon_name("format-text-underline-symbolic")
        toolbar.insert(button_underline, nnn)   ; nnn += 1

        button_sel = Gtk.ToolItem()
        mmm = ("8", "9", "10", "12", "14")
        combo = pgbox.ComboBox(mmm, self.combo_sel)
        #combo.sel_text("12")
        print("str(self.mysize)", str(self.mysize))
        combo.sel_text(str(int(self.mysize)))

        button_sel.add(combo)
        toolbar.insert(button_sel, nnn)  ; nnn += 1

        button_sel2 = Gtk.ToolItem()
        mmm = ("Black",  "Red", "Green", "Blue", "Gray", "White")
        combo2 = pgbox.ColorCombo(mmm, self.combo_sel2)
        combo2.sel_text("Black")
        button_sel2.add(combo2)
        toolbar.insert(button_sel2, nnn)  ; nnn += 1

        button_color = Gtk.ToolButton()
        button_color.set_icon_name("preferences-desktop")
        button_color.set_tooltip_text("Set Background Color")
        button_color.connect("clicked", self.on_button_clicked, self.tag_redbg)
        toolbar.insert(button_color, nnn)  ; nnn += 1

        button_big = Gtk.ToolButton()
        button_big.set_icon_name("format-text-larger-symbolic")
        button_big.set_tooltip_text("Set Large Font")
        button_big.connect("clicked", self.on_button_clicked, self.tag_big)
        toolbar.insert(button_big, nnn)  ; nnn += 1

        button_big = Gtk.ToolButton()
        button_big.set_icon_name("format-text-smaller-symbolic")
        button_big.set_tooltip_text("Set Smaller Font")
        button_big.connect("clicked", self.on_button_clicked, self.tag_regular)
        toolbar.insert(button_big, nnn)  ; nnn += 1

        button_big = Gtk.ToolButton()
        button_big.set_icon_name("tools-check-spelling")
        button_big.set_tooltip_text("Set XX Large font")
        button_big.connect("clicked", self.on_button_clicked, self.tag_xbig)
        toolbar.insert(button_big, nnn)   ; nnn += 1

        button_color = Gtk.ToolButton()
        button_color.set_icon_name("font-x-generic")
        button_color.set_tooltip_text("Set Font")
        button_color.connect("clicked", self.on_color_clicked, 0)
        toolbar.insert(button_color, nnn)  ; nnn += 1

        button_norm.connect("clicked", self.on_rm_clicked, self.tag_norm)
        button_bold.connect("clicked", self.on_button_clicked, self.tag_bold)
        button_italic.connect("clicked", self.on_button_clicked, self.tag_italic)
        button_underline.connect("clicked", self.on_button_clicked, self.tag_underline)

        toolbar.insert(Gtk.SeparatorToolItem(), nnn)  ; nnn += 1

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
            "toggled", self.on_justify_toggled, Gtk.Justification.LEFT
        )
        radio_justifycenter.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.CENTER
        )
        radio_justifyright.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.RIGHT
        )
        radio_justifyfill.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.FILL
        )

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
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 1, 3, 1)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()

        self.fd = Pango.FontDescription()
        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        self.mysize = myfd.get_size() / Pango.SCALE
        self.myfam = myfd.get_family()
        print(self.mysize)

        #self.textview.set_has_window(True)

        #self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        scrolledwindow.add(self.textview)

        self.tag_regular = self.textbuffer.create_tag("regular", size=self.mysize * Pango.SCALE)
        #self.tag_norm = self.textbuffer.create_tag("norm", weight=20*Pango.SCALE)
        self.tag_xbig = self.textbuffer.create_tag("xbig", size=30*Pango.SCALE)
        self.tag_big = self.textbuffer.create_tag("big", size=20*Pango.SCALE)
        self.tag_red = self.textbuffer.create_tag("red", foreground="red")
        self.tag_redbg = self.textbuffer.create_tag("redbg", background="red")
        self.tag_norm = self.textbuffer.create_tag("normal", style=Pango.Style.NORMAL)
        self.tag_bold = self.textbuffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tag_italic = self.textbuffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tag_underline = self.textbuffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.tag_found = self.textbuffer.create_tag("found", background="yellow")
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)

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

    def get_all(self):
        print("Get_all called")
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        return self.buffer.get_text(startt, endd, True)

    def  get_modified(self):
        return self.textbuffer.get_modified()

    def set_text(self, txt):
        if self.textbuffer.get_modified():
            startt = self.textbuffer.get_start_iter()
            endd = self.textbuffer.get_end_iter()
            old = self.textbuffer.get_text(startt, endd, False)
            if self.callb:
                self.callb(old)
            #print("old_content", old)
        self.textbuffer.set_text(txt)
        self.textbuffer.set_modified(False)

    def on_rm_clicked(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.remove_tag(self.tag_bold, start, end)
            self.textbuffer.remove_tag(self.tag_italic, start, end)
            self.textbuffer.remove_tag(self.tag_underline, start, end)
            self.textbuffer.remove_tag(self.tag_red, start, end)
            self.textbuffer.remove_tag(self.tag_redbg, start, end)
            self.textbuffer.remove_tag(self.tag_big, start, end)
            self.textbuffer.remove_tag(self.tag_xbig, start, end)
            self.textbuffer.remove_tag(self.tag_regular, start, end)

    def on_button_clicked(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            #print("Apply Tag", tag, start, end)
            self.textbuffer.apply_tag(tag, start, end)

    def on_clear_clicked(self, widget):
        start = self.textbuffer.get_start_iter()
        end = self.textbuffer.get_end_iter()
        self.textbuffer.remove_all_tags(start, end)

    def on_editable_toggled(self, widget):
        self.textview.set_editable(widget.get_active())

    def on_cursor_toggled(self, widget):
        self.textview.set_cursor_visible(widget.get_active())

    def on_wrap_toggled(self, widget, mode):
        self.textview.set_wrap_mode(mode)

    def on_justify_toggled(self, widget, justification):
        self.textview.set_justification(justification)

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


class pgTextView2(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.callb = None
        self.grid = Gtk.Grid()
        self.add(self.grid)
        self._create_textview();
        self._create_toolbar()
        self._create_buttons()

        self.fd = Pango.FontDescription()
        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        self.mysize = myfd.get_size() / Pango.SCALE
        self.myfam = myfd.get_family()
        self.textview.connect("key-press-event", self.area_key)
        #self.connect("button-press-event", self.area_button)
        #self.textview.connect("focus-out-event", self.focus_out)
        self.findcall = None;

    def area_key(self, widget, event):
        #print("TextViewWin keypress", event.string, event.keyval)
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == 102:
                #print("control find")
                if self.findcall:
                    # Call with object argument
                    self.findcall[0](self.findcall[1])

    '''
    def area_button(self, but, event):
        print("TextViewWin click", event.x, event.y)
        pass
    '''

    '''
    def focus_out(self, arg1, arg2):
        print("Focus out")
    '''

    def _create_toolbar(self):
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 0, 3, 1)

        button_norm = Gtk.ToolButton()
        button_norm.set_icon_name("format-text-none-symbolic")
        button_norm.set_tooltip_text("Remove formatting")
        toolbar.insert(button_norm, 0)

        button_bold = Gtk.ToolButton()
        button_bold.set_icon_name("format-text-bold-symbolic")
        toolbar.insert(button_bold, 1)

        button_italic = Gtk.ToolButton()
        button_italic.set_icon_name("format-text-italic-symbolic")
        toolbar.insert(button_italic, 2)

        button_underline = Gtk.ToolButton()
        button_underline.set_icon_name("format-text-underline-symbolic")
        toolbar.insert(button_underline, 3)

        button_norm.connect("clicked", self.on_rm_clicked, self.tag_norm)
        button_bold.connect("clicked", self.on_button_clicked, self.tag_bold)
        button_italic.connect("clicked", self.on_button_clicked, self.tag_italic)
        button_underline.connect("clicked", self.on_button_clicked, self.tag_underline)

        toolbar.insert(Gtk.SeparatorToolItem(), 4)

        radio_justifyleft = Gtk.RadioToolButton()
        radio_justifyleft.set_icon_name("format-justify-left-symbolic")
        toolbar.insert(radio_justifyleft, 5)

        radio_justifycenter = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifycenter.set_icon_name("format-justify-center-symbolic")
        toolbar.insert(radio_justifycenter, 6)

        radio_justifyright = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifyright.set_icon_name("format-justify-right-symbolic")
        toolbar.insert(radio_justifyright, 7)

        radio_justifyfill = Gtk.RadioToolButton.new_from_widget(radio_justifyleft)
        radio_justifyfill.set_icon_name("format-justify-fill-symbolic")
        toolbar.insert(radio_justifyfill, 8)

        radio_justifyleft.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.LEFT
        )
        radio_justifycenter.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.CENTER
        )
        radio_justifyright.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.RIGHT
        )
        radio_justifyfill.connect(
            "toggled", self.on_justify_toggled, Gtk.Justification.FILL
        )

        toolbar.insert(Gtk.SeparatorToolItem(), 9)

        button_clear = Gtk.ToolButton()
        button_clear.set_icon_name("edit-clear-symbolic")
        button_clear.set_tooltip_text("Remove ALL formatting")
        button_clear.connect("clicked", self.on_clear_clicked)
        toolbar.insert(button_clear, 10)

        toolbar.insert(Gtk.SeparatorToolItem(), 11)

        button_search = Gtk.ToolButton()
        button_search.set_icon_name("system-search-symbolic")
        button_search.set_tooltip_text("Search current text")
        button_search.connect("clicked", self.on_search_clicked)
        toolbar.insert(button_search, 12)

        button_mag = Gtk.ToolButton()
        button_mag.set_icon_name("zoom-in-symbolic")
        button_mag.set_tooltip_text("Magnify Font")
        button_mag.connect("clicked", self.on_zoom_clicked)
        toolbar.insert(button_mag, 13)

        button_mag2 = Gtk.ToolButton()
        button_mag2.set_icon_name("zoom-out-symbolic")
        button_mag2.set_tooltip_text("Set smaller Font")
        button_mag2.connect("clicked", self.on_unzoom_clicked)
        toolbar.insert(button_mag2, 14)

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

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 1, 3, 1)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()

        #self.textview.set_has_window(True)


        #self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        scrolledwindow.add(self.textview)

        #self.tag_norm = self.textbuffer.create_tag("norm", weight=Pango.Weight.NORMAL)
        self.tag_norm = self.textbuffer.create_tag("normal", style=Pango.Style.NORMAL)
        self.tag_bold = self.textbuffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tag_italic = self.textbuffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tag_underline = self.textbuffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.tag_found = self.textbuffer.create_tag("found", background="yellow")
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)

        pg = Gtk.Widget.create_pango_context(self.textview)
        myfd = pg.get_font_description()
        self.myfontsize = myfd.get_size() / Pango.SCALE
        print("myfontsize", self.myfontsize)


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

    def get_all(self):
        print("Get_all called")
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        return self.buffer.get_text(startt, endd, True)

    def  get_modified(self):
        return self.textbuffer.get_modified()

    def set_text(self, txt):
        if self.textbuffer.get_modified():
            startt = self.textbuffer.get_start_iter()
            endd = self.textbuffer.get_end_iter()
            old = self.textbuffer.get_text(startt, endd, False)
            if self.callb:
                self.callb(old)
            #print("old_content", old)
        self.textbuffer.set_text(txt)
        self.textbuffer.set_modified(False)

    def on_rm_clicked(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.remove_tag(self.tag_bold, start, end)
            self.textbuffer.remove_tag(self.tag_italic, start, end)
            self.textbuffer.remove_tag(self.tag_underline, start, end)

    def on_button_clicked(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            #print("Apply Tag", tag, start, end)
            self.textbuffer.apply_tag(tag, start, end)

    def on_clear_clicked(self, widget):
        start = self.textbuffer.get_start_iter()
        end = self.textbuffer.get_end_iter()
        self.textbuffer.remove_all_tags(start, end)

    def on_editable_toggled(self, widget):
        self.textview.set_editable(widget.get_active())

    def on_cursor_toggled(self, widget):
        self.textview.set_cursor_visible(widget.get_active())

    def on_wrap_toggled(self, widget, mode):
        self.textview.set_wrap_mode(mode)

    def on_justify_toggled(self, widget, justification):
        self.textview.set_justification(justification)

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

if __name__ == '__main__':

    print("Start pytextview")
    mainwin = MainWin()
    Gtk.main()

