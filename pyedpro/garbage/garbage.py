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

