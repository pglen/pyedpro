
from __future__ import absolute_import

import signal, os, time, sys, codecs

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GObject

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

import cairo


# ------------------------------------------------------------------------

class HtmlEditor(Gtk.Widget):

    #def __init__(self, args = None, kwds = None):
    #    super().__init__(*args, **kwds)

    def __init__(self):
        super().__init__()

        self.state = 0; self.stat2 = 0

        #self.set_title("Html Editor")
        #self.connect("destroy", Gtk.main_quit)
        #self.resize(500, 500)
        #self.filename = None

        self.set_can_focus(True)
        self.set_can_default(True)
        self.set_sensitive(True)

        self.editor = WebKit2.WebView()
        self.editor.set_editable(True)
        self.editor.load_html("", "file:///")
        #self.present()


        #overlay

        #self.editor.set_size_request(300, 300)
        #self.editor.set_can_focus(True)
        #self.editor.set_can_default(True)
        #self.editor.set_sensitive(True)

        #self.scroll = Gtk.ScrolledWindow()
        #self.scroll.add(self.editor)
        #self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.ui = self.generate_ui()
        #self.add_accel_group(self.ui.get_accel_group())
        self.toolbar1 = self.ui.get_widget("/toolbar_main")
        self.toolbar2 = self.ui.get_widget("/toolbar_format")
        self.menubar = self.ui.get_widget("/menubar_main")

        #self.layout = Gtk.VBox()
        #self.layout.pack_start(self.menubar, False, False, 0)
        #self.layout.pack_start(self.toolbar1, False, False, 0)
        #self.layout.pack_start(self.toolbar2, False, False, 0)
        #self.layout.pack_start(self.scroll, True, True, 0)
        ##self.add(self.layout)
        #
        ##self.layout.pack_start(self.editor.get_inspector(), True, True, 0)
        ##self.inspect = WebKit2.WebInspector()
        ##self.inspect.attach()
        ##self.editor.get_inspector().attach()
        #
        #self.editor.get_settings().set_property("enable_developer_extras", True)
        #self.editor.get_inspector().set_property("height", 200)
        #self.editor.get_inspector().show()
        #print("hhh", self.editor.get_inspector().get_attached_height())
        #self.editor.show_all()

    def do_draw(self, cr):

        # paint background
        if 1: #self.stat2:
            bg_color2 = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
            #print(bg_color2)
            #bg_color = Gdk.RGBA(bg_color2.red-0.1, bg_color2.green-0.1, bg_color2.blue -0.1)
            #bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)

            bg_color = Gdk.RGBA(.9, .9, .9)
            #print(bg_color)
        else:
            bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)

        cr.rectangle(10, 10, 64, 64)
        cr.set_source_rgba(1., 0., 0.)
        cr.fill()

        cr.set_source_rgba(*list(bg_color))
        #cr.paint()

        #sss = self.get_state()
        #if sss ==  Gtk.StateFlags.SELECTED:

        if 0: #self.stat2:
            fg_color = self.get_style_context().get_color(Gtk.StateFlags.SELECTED)
        else:
            fg_color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)

        #print(fg_color)

        # draw a diagonal line
        allocation = self.get_allocation()
        cr.set_source_rgba(*list(fg_color));
        cr.move_to(10, 10)
        #cr.line_to(100, 100)
        cr.line_to(allocation.width-10, allocation.height-10)

        #PangoCairo.show_layout(cr, self.layout)

        #if self.state:
        #    cr.move_to(1, 1)
        #    PangoCairo.show_layout(cr, self.layout)
        cr.stroke()

        #self.queue_draw()

        #self.editor.do_draw(self.editor, cr)

        #super().do_draw.invoke(Gtk.VBox, self, *args, **kwargs)
        #self.editor.do_draw(self.editor, cr)
        WebKit2.WebView.do_draw(self, cr)

        #self.layout.do_draw(self.layout, cr)
        #return True

    def do_realize(self):
        allocation = self.get_allocation()
        attr = Gdk.WindowAttr()
        attr.window_type = Gdk.WindowType.CHILD
        attr.x = allocation.x
        attr.y = allocation.y
        attr.width = allocation.width
        attr.height = allocation.height
        attr.visual = self.get_visual()
        attr.event_mask = self.get_events() | Gdk.EventMask.EXPOSURE_MASK
        WAT = Gdk.WindowAttributesType
        mask = WAT.X | WAT.Y | WAT.VISUAL
        window = Gdk.Window(self.get_parent_window(), attr, mask);
        self.set_window(window)
        self.register_window(window)
        self.set_realized(True)
        window.set_background_pattern(None)


    def  event_release(self, arg1, arg2):
        #print("widget release", arg1, arg2)
        #self.set_state(Gtk.StateFlags.NORMAL)
        self.state = 0
        self.queue_draw()
        xx, yy =  self.get_pointer()
        rrr = self.get_allocation()
        #print(xx, yy, "vvv", rrr.x, rrr.y, rrr.width, rrr.height)

        # If release was outside, cancel action
        if xx < 0 or xx > rrr.width:
            #print("xx over")
            return
        if yy < 0 or yy > rrr.height:
            #print("yy over")
            return
        self.eventx(arg1, arg2)

    def generate_ui(self):
        ui_def = """
        <ui>
        <menubar name="menubar_main">
            <menu action="menuFile">
            <menuitem action="new" />
            <menuitem action="open" />
            <menuitem action="save" />
            </menu>
            <menu action="menuEdit">
            <menuitem action="cut" />
            <menuitem action="copy" />
            <menuitem action="paste" />
            </menu>
            <menu action="menuInsert">
            <menuitem action="insertimage" />
            </menu>
            <menu action="menuFormat">
            <menuitem action="bold" />
            <menuitem action="italic" />
            <menuitem action="underline" />
            <menuitem action="strikethrough" />
            <separator />
            <menuitem action="font" />
            <menuitem action="color" />
            <separator />
            <menuitem action="justifyleft" />
            <menuitem action="justifyright" />
            <menuitem action="justifycenter" />
            <menuitem action="justifyfull" />
            </menu>
        </menubar>
        <toolbar name="toolbar_main">
            <toolitem action="new" />
            <toolitem action="open" />
            <toolitem action="save" />
            <separator />
            <toolitem action="undo" />
            <toolitem action="redo" />
            <separator />
            <toolitem action="cut" />
            <toolitem action="copy" />
            <toolitem action="paste" />
        </toolbar>
        <toolbar name="toolbar_format">
            <toolitem action="bold" />
            <toolitem action="italic" />
            <toolitem action="underline" />
            <toolitem action="strikethrough" />
            <separator />
            <toolitem action="font" />
            <toolitem action="color" />
            <separator />
            <toolitem action="justifyleft" />
            <toolitem action="justifyright" />
            <toolitem action="justifycenter" />
            <toolitem action="justifyfull" />
            <separator />
            <toolitem action="insertimage" />
            <toolitem action="insertlink" />
        </toolbar>
        </ui>
        """

        actions = Gtk.ActionGroup("Actions")
        actions.add_actions([
        ("menuFile", None, "_File"),
        ("menuEdit", None, "_Edit"),
        ("menuInsert", None, "_Insert"),
        ("menuFormat", None, "_Format"),

        ("new", Gtk.STOCK_NEW, "_New", None, None, self.on_new),
        ("open", Gtk.STOCK_OPEN, "_Open", None, None, self.on_open),
        ("save", Gtk.STOCK_SAVE, "_Save", None, None, self.on_save),

        ("undo", Gtk.STOCK_UNDO, "_Undo", None, None, self.on_action),
        ("redo", Gtk.STOCK_REDO, "_Redo", None, None, self.on_action),

        ("cut", Gtk.STOCK_CUT, "_Cut", None, None, self.on_action),
        ("copy", Gtk.STOCK_COPY, "_Copy", None, None, self.on_action),
        ("paste", Gtk.STOCK_PASTE, "_Paste", None, None, self.on_paste),

        ("bold", Gtk.STOCK_BOLD, "_Bold", "<ctrl>B", None, self.on_action),
        ("italic", Gtk.STOCK_ITALIC, "_Italic", "<ctrl>I", None, self.on_action),
        ("underline", Gtk.STOCK_UNDERLINE, "_Underline", "<ctrl>U", None, self.on_action),
        ("strikethrough", Gtk.STOCK_STRIKETHROUGH, "_Strike", "<ctrl>T", None, self.on_action),
        ("font", Gtk.STOCK_SELECT_FONT, "Select _Font", "<ctrl>F", None, self.on_select_font),
        ("color", Gtk.STOCK_SELECT_COLOR, "Select _Color", None, None, self.on_select_color),

        ("justifyleft", Gtk.STOCK_JUSTIFY_LEFT, "Justify _Left", None, None, self.on_action),
        ("justifyright", Gtk.STOCK_JUSTIFY_RIGHT, "Justify _Right", None, None, self.on_action),
        ("justifycenter", Gtk.STOCK_JUSTIFY_CENTER, "Justify _Center", None, None, self.on_action),
        ("justifyfull", Gtk.STOCK_JUSTIFY_FILL, "Justify _Full", None, None, self.on_action),

        ("insertimage", "insert-image", "Insert _Image", None, None, self.on_insert_image),
        ("insertlink", "insert-link", "Insert _Link", None, None, self.on_insert_link),
        ])

        actions.get_action("insertimage").set_property("icon-name", "insert-image")
        actions.get_action("insertlink").set_property("icon-name", "insert-link")

        ui = Gtk.UIManager()
        ui.insert_action_group(actions)
        ui.add_ui_from_string(ui_def)
        return ui

    def on_action(self, action):
        self.editor.run_javascript("document.execCommand('%s', false, false);" % action.get_name())

    def on_paste(self, action):
        self.editor.execute_editing_command(WebKit2.EDITING_COMMAND_PASTE)

    def on_new(self, action):
        self.editor.load_html("", "file:///")

    def on_select_font(self, action):
        dialog = Gtk.FontChooserDialog("Select a font")
        if dialog.run() == Gtk.ResponseType.OK:
            fname = dialog.get_font_desc().get_family()
            fsize = dialog.get_font_desc().get_size()
            self.editor.run_javascript("document.execCommand('fontname', null, '%s');" % fname)
            self.editor.run_javascript("document.execCommand('fontsize', null, '%s');" % fsize)
        dialog.destroy()

    def on_select_color(self, action):
        dialog = Gtk.ColorChooserDialog("Select Color")
        if dialog.run() == Gtk.ResponseType.OK:
            (r, g, b, a) = dialog.get_rgba()
            color = "#%0.2x%0.2x%0.2x%0.2x" % (
                int(r * 255),
                int(g * 255),
                int(b * 255),
                int(a * 255))
            self.editor.run_javascript("document.execCommand('forecolor', null, '%s');" % color)
        dialog.destroy()

    def on_insert_link(self, action):
        dialog = Gtk.Dialog("Enter a URL:", self, 0,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        entry = Gtk.Entry()
        dialog.vbox.pack_start(entry, False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            self.editor.run_javascript(
                "document.execCommand('createLink', true, '%s');" % entry.get_text())
        dialog.destroy()

    def on_insert_image(self, action):
        dialog = Gtk.FileChooserDialog("Select an image file", self, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            if os.path.exists(fn):
                self.editor.run_javascript(
                "document.execCommand('insertImage', null, '%s');" % fn)
        dialog.destroy()

    def on_open(self, action):
        dialog = Gtk.FileChooserDialog("Select an HTML file", self, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            if os.path.exists(fn):
                self.filename = fn
                with open(fn) as fd:
                    self.editor.load_html(fd.read(), "file:///")
        dialog.destroy()

    def on_save(self, action):
        def completion(html, user_data):
            open_mode = user_data
            with open(self.filename, open_mode) as fd:
                fd.write(html)

        if self.filename:
            self.get_html(completion, 'w')
        else:
            dialog = Gtk.FileChooserDialog("Select an HTML file", self, Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            if dialog.run() == Gtk.ResponseType.OK:
                self.filename = dialog.get_filename()
                self.get_html(completion, "w+")
            dialog.destroy()

    def get_html(self, completion_function, user_data):
        def javascript_completion(obj, result, user_data):
            html = self.editor.get_title()
            completion_function(html, user_data)
        self.editor.run_javascript("document.title=document.documentElement.innerHTML;",
                                   None,
                                   javascript_completion,
                                   user_data)

#e = HtmlEditor()
#e.show_all()
#e.scroll.grab_focus()
#Gtk.main()

class   HtmlEdit(Gtk.VBox):

    def __init__(self, editable = False, statsetter = None):

        self.statsetter = statsetter
        self.editable = editable

        self._htmlx = pgwebw(editable)
        self.ui = generate_ui(self._htmlx)
        self.urlbar  = self.create_urlbar()
        self.toolbar = self.ui.get_widget("/toolbar_format")
        browse_scroll = Gtk.ScrolledWindow()
        browse_scroll.add(self._htmlx)
        self.pack_start(self.urlbar, False, False, 0)
        self.pack_start(self.toolbar, False, False, 0)
        self.pack_start(browse_scroll, 1, 1, 2)

    def get_view(self):
        return self._htmlx

    def url_callb(self):
        pass

    def backurl(self, url, parm, buff):
        self.webview.go_back()

    def baseurl(self, url, parm, buff):
        self.webview.load_uri("file://" + self.fname)

    def forwurl(self, url, parm, buff):
        self.webview.go_forward()

    def go(self, xstr):
        print("go", xstr)

        if not len(xstr):
            return

        #  Leave known URL scemes alone
        if xstr[:7] == "file://":
            sss = os.path.realpath(xstr[7:])
            xstr = "file://" + sss
            pass
        elif xstr[:7] == "http://":
            pass
        elif xstr[:8] == "https://":
            pass
        elif xstr[:6] == "ftp://":
            pass
        elif str.isdecimal(xstr[0]):
            #print("Possible IP")
            pass
        else:
            # Yeah, padd it
            xstr = "https://" + xstr

        self.webview.load_uri(xstr)

    def url_callb(self, xtxt):
        self.go(xtxt)


    def gourl(self, url, parm, buff):
        self.go(self.edit.get_text())

    def create_urlbar(self):

        self.edit = SimpleEdit();
        self.edit.setsavecb(self.url_callb)
        self.edit.single_line = True

        hbox3 = Gtk.HBox()
        uuu  = Gtk.Label("  URL:  ")
        uuu.set_tooltip_text("Current / New URL; press Enter to go")
        hbox3.pack_start(uuu, 0, 0, 0)
        hbox3.pack_start(self.edit, True, True, 2)
        bbb = LabelButt(" Go ", self.gourl, "Go to speified URL")
        ccc = LabelButt(" <-Back  ", self.backurl, "Go Back")
        ddd = LabelButt("  Forw-> ", self.forwurl, "Go Forw")
        eee = LabelButt("   Base  ", self.baseurl, "Go to base URL")
        hbox3.pack_start(Gtk.Label("  "), 0, 0, 0)
        hbox3.pack_start(bbb, 0, 0, 0)
        hbox3.pack_start(ccc, 0, 0, 0)
        hbox3.pack_start(ddd, 0, 0, 0)
        hbox3.pack_start(eee, 0, 0, 0)

        hbox3.pack_start(Gtk.Label("  ^  "), 0, 0, 0)
        hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)

        return hbox3




# EOF