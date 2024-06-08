#!/usr/bin/env python

''' This encapsulates the webkit import and failure thereof '''

import os, sys, getopt, signal, random, time, warnings
import inspect

#realinc = os.path.realpath(os.path.dirname(__file__) + os.sep + "../pycommon")
#sys.path.append(realinc)

from pgutils import  *
from pggui import  *
from pgsimp import  *
from pgtextview import  *

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

WebKit2 = None

class dummywebview(Gtk.VBox):

    def __int__(self):
        super().__init__(self)
        #self.pack_start(Gtk.Label(label="No WebView"), 1, 1, 0)
    def set_editable(self, flag):
        self.pack_start(Gtk.Label(label="No WebView Available"), 1, 1, 0)
        pass
    def load_html(self, ff, kk = None):
        pass
    def connect(self, aa, bb):
        pass

class dummywebkit():
    WebView = dummywebview

try:
    gi.require_version("WebKit2", '4.1')
    from gi.repository import WebKit2
    #present = 1
except:
    try:
        #print("Trying V 4.0:", sys.exc_info())
        gi.require_version("WebKit2", '4.0')
        from gi.repository import WebKit2
    except:
        try:
            #print("Trying with jno qualifier")
            #gi.require_version("WebKit2", '4.0')
            from gi.repository import WebKit2
        except:
            # Giving up, patch fake one
            print("Cannot import:", sys.exc_info())
            print("WebWiew is not available.")
            try:
                WebKit2 = dummywebkit
            except:
                print("Fake kit Exc:", sys.exc_info())
            #print("Fake kit:", WebKit2)
            #raise

ui_def = """
        <ui>
            <toolbar name="toolbar_format">
                <toolitem action="cut" />
                <toolitem action="copy" />
                <toolitem action="paste" />
                <separator />
                <toolitem action="removeformat" />
                <toolitem action="bold" />
                <toolitem action="italic" />
                <toolitem action="underline" />
                <toolitem action="strikethrough" />
                <separator />
                <toolitem action="justifyleft" />
                <toolitem action="justifyright" />
                <toolitem action="justifycenter" />
                <toolitem action="justifyfull" />
                <separator />
                <toolitem action="undo" />
                <toolitem action="redo" />
                <separator />
                <toolitem action="font" />
                <toolitem action="fontsize" />
                <toolitem action="color" />
                <toolitem action="backgroundcolor" />
                <separator />
                <toolitem action="insertimage" />
                <toolitem action="insertlink" />
                <toolitem action="inserttable" />
                <toolitem action="editmarker" />
                <toolitem action="H1" />
                <toolitem action="H2" />
                <toolitem action="H3" />
                <toolitem action="H4" />
            </toolbar>
        </ui>
        """

#unmask_reserved =   Gdk.ModifierType.GDK_MODIFIER_RESERVED_13_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_14_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_15_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_16_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_17_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_18_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_19_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_20_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_21_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_22_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_23_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_24_MASK | \
#                    Gdk.ModifierType.GDK_MODIFIER_RESERVED_25_MASK

# These are not setting the modified flag

navkeys = [   \
                Gdk.KEY_Up,         Gdk.KEY_KP_Up,
                Gdk.KEY_Down,       Gdk.KEY_KP_Down ,
                Gdk.KEY_Left,       Gdk.KEY_KP_Left,
                Gdk.KEY_Right,      Gdk.KEY_KP_Right,
                Gdk.KEY_Page_Up,    Gdk.KEY_KP_Page_Up,
                Gdk.KEY_Page_Down,  Gdk.KEY_KP_Page_Down,
                Gdk.KEY_Home,       Gdk.KEY_KP_Home,
                Gdk.KEY_End,        Gdk.KEY_KP_End,

                # Also the modifier keys themselves
                Gdk.KEY_Alt_L,      Gdk.KEY_Alt_R,
                Gdk.KEY_Control_L,  Gdk.KEY_Control_R,
                Gdk.KEY_Super_L,    Gdk.KEY_Super_R,
                Gdk.KEY_Shift_L,    Gdk.KEY_Shift_R,

          ]

# ------------------------------------------------------------------------

class pgwebw(WebKit2.WebView):

    ''' Define our override of the webkit class '''

    def __init__(self, xlink=None):
        try:
            GObject.GObject.__init__(self)
        except:
            print("Cannot ??? in parent object", sys.exc_info())
            pass
        self.xlink = xlink
        self.set_editable(True)

        #if editable:
        #    self.set_editable(True)

        self.fname = ""
        self.load_html("", "file:///")
        self.ui = self.generate_ui()
        self.connect("key-release-event",  self.keypress)
        self.modified = False

    def  _get_response_data_finish(self, resource, result, user_data=None):
        self.old_html = resource.get_data_finish(result)
        #print((self.old_html))

    def keypress(self, arg, arg2):

        ''' Here we imitate the way the accelerator works '''

        state = arg2.get_state() & Gdk.ModifierType.MODIFIER_MASK
        key = arg2.get_keyval()[1]
        #print("key",  key, "state", state)

        #GDK_MODIFIER_RESERVED_25_MASK

        # Feeding off the accelarator's definitions
        ag = self.ui.get_action_groups()[0]
        acts = ag.list_actions()

        # Scan - Fire
        for aa in acts:
            if aa.accel:
                #print(nnn, aa.accel, aa.accel_parsed)
                if state == aa.accel_parsed[1]:
                    #print("state match")
                    if key == aa.accel_parsed[0]:
                        #print("Fire ", aa.get_name(), aa.get_label())
                        #lab = aa.get_label()
                        aa.activate()
                        break   # Only one accel the other is a mistake

        # See if nav key
        navkey = False
        for aa in navkeys:
            if key == aa:
                #print("Navkey", aa)
                navkey = True
        if not navkey:
            # Exclude Ctrl-s
            if state == Gdk.ModifierType.CONTROL_MASK and key == 115:
                #print("Control s")
                pass
            else:
                #print("set on key", key)
                self.modified =  True

    def do_ready_to_show(self):
        print("do_ready_to_show() was called")
        pass

    def do_load_changed(self, status):

        #print("do_load_changed()", status)
        if status == WebKit2.LoadEvent.FINISHED:
            ''' Create a shadow of content '''

            # This gets it without spaces
            #resource = self.get_main_resource()
            #resource.get_data(None, self._get_response_data_finish, None)

            # Get it by JS
            def completion(html, user_data):
                self.old_html = html
            self.get_html(completion, '')


        if self.get_uri():
            if self.xlink:
                self.xlink.set_status("Loading ... " + self.get_uri()[:64])

        if status == 3: #WebKit2.LoadEvent.WEBKIT_LOAD_FINISHED:
            #print("got WEBKIT_LOAD_FINISHED")
            if self.get_uri():
                if self.xlink:
                    self.xlink.edit.set_text(self.get_uri()[:64])
                    self.xlink.set_status("Finished: " + self.get_uri()[:64])
            self.grab_focus()

    def do_load_failed(self, load_event, failing_uri, error):
        print("do_load_failed() was called", failing_uri)
        if self.xlink:
            self.xlink.set_status("Failed: " + failing_uri[:64])

    def on_header(self, action):
        #print("on_aheader", action.get_name())
        ddd = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        ccc = None
        while True:
            #target = Gdk.Atom.intern ("text/html", True);
            #ccc = ddd.wait_for_contents(target)
            #if ccc:
            #    break
            target2 = Gdk.Atom.intern ("text/plain", True);
            ccc = ddd.wait_for_contents(target2)
            if ccc:
                break
            break

        if not ccc:
            return

        dddd = ccc.get_data().decode()
        if not dddd:
            return
        #print("dddd", dddd)
        htmlx = "<%s>%s</%s>" % (action.get_name(), dddd, action.get_name())
        self.run_javascript("document.execCommand \
                            ('insertHTML', null, '%s');" % htmlx)
        Gtk.Clipboard.clear(ddd)
        self.modified = True

    def on_action(self, action):
        #print("on_action", action.get_name())
        # Make it caller neutral
        if type(action) == str:
            nnn = action
        else:
            nnn = action.get_name()
        self.run_javascript("document.execCommand('%s', false, false);" % nnn)
        self.modified = True

    def on_paste(self, action = ""):
        print("Paste")
        self.execute_editing_command(WebKit2.EDITING_COMMAND_PASTE)

    def on_new(self, action):
        self.load_html("", "file:///")
        self.modified = False

    def on_fontsize(self, action):
        #print("on_fontsize")
        sizex = sizedialog()
        #print("sizex", sizex)
        if not sizex:
            return

        c = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        sel = c.wait_for_targets()
        #print("sel", sel)
        target = Gdk.Atom.intern ("text/plain", True);
        ccc = c.wait_for_contents(target)
        if not ccc:
            htmlx = "<span style=\"font-size: %dpx;\">%s</span>" % (int(sizex), "")
            self.run_javascript("document.execCommand('insertHTML', null, '%s');" % htmlx)
            return

        ddd = ccc.get_data().decode()
        if not ddd:
            return

        #print("ddd", ddd)
        htmlx = "<span style=\"font-size: %dpx;\">%s</span>" % (int(sizex), ddd)
        self.run_javascript("document.execCommand('insertHTML', null, '%s');" % htmlx)
        Gtk.Clipboard.clear(c)
        self.modified = True

    def on_select_font(self, action):
        dialog = Gtk.FontChooserDialog("Select a font")
        if dialog.run() == Gtk.ResponseType.OK:
            fname = dialog.get_font_desc().get_family()
            fsize = dialog.get_font_desc().get_size() / Pango.SCALE
            ttt = int(1 + round(fsize / 10)) % 9
            print("Setting font", fname, fsize, ttt)
            self.run_javascript("document.execCommand('fontname', null, '%s');" % fname)
            self.run_javascript("document.execCommand('fontsize', null, '%s');" % ttt)
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
            self.run_javascript("document.execCommand('forecolor', null, '%s');" % color)
        dialog.destroy()

    def on_select_bgcolor(self, action):
        dialog = Gtk.ColorChooserDialog("Select Background Color")
        if dialog.run() == Gtk.ResponseType.OK:
            (r, g, b, a) = dialog.get_rgba()
            color = "#%0.2x%0.2x%0.2x%0.2x" % (
                int(r * 255),
                int(g * 255),
                int(b * 255),
                int(a * 255))
            self.run_javascript("document.execCommand('backcolor', null, '%s');" % color)
        dialog.destroy()

    def on_edit_marker(self, action):
        print("on_edit_marker", action.get_name())

        c = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        sel = c.wait_for_targets()
        target = Gdk.Atom.intern ("text/html", True);
        ccc = c.wait_for_contents(target)
        #print("sel", ccc.get_data())
        #ccc.free()
        htmlx = markdialog(ccc.get_data().decode())
        if htmlx:
            print("markdialog result:\n", htmlx)
            self.run_javascript("document.execCommand('insertHTML', null, '%s');" % htmlx)

    def on_insert_table(self, action):
        htmlx = "<table align=center border=0 contentEditable=true>" + \
                "<tr><td>TR1 C1 <td>| TR1 C2 <tr><td>TR2 C1<td>| TR2 C1</table><br>"

        #print("table", htmlx)
        self.run_javascript("document.execCommand('insertHTML', null, '%s');" % htmlx)
        self.modified = True

    def on_insert_link(self, action):
        dialog = Gtk.Dialog("   Enter a URL:   ", None, 0,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        entry = Gtk.Entry()
        dialog.vbox.pack_start(Gtk.Label("  "), False, False, 0)
        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label("  "), False, False, 0)
        hbox.pack_start(entry, False, False, 0)
        hbox.pack_start(Gtk.Label("  "), False, False, 0)
        dialog.vbox.pack_start(hbox, False, False, 0)

        dialog.vbox.pack_start(Gtk.Label("  "), False, False, 0)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            self.run_javascript(
                "document.execCommand('createLink', True, '%s');" % entry.get_text())
        dialog.destroy()
        self.modified = True

    def on_insert_image(self, action):
        dialog = Gtk.FileChooserDialog("Select an image file", None, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            if os.path.exists(fn):
                self.run_javascript(
                "document.execCommand('insertImage', null, '%s');" % fn)
        dialog.destroy()
        self.modified = True

    def on_open(self, action):
        dialog = Gtk.FileChooserDialog("Select an HTML file", self, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            if os.path.exists(fn):
                self.fname = fn
                with open(fn) as fd:
                    self.load_html(fd.read(), "file:///")
        dialog.destroy()

    def on_save(self, action):
        def completion(html, user_data):
            open_mode = user_data
            with open(self.fname, open_mode) as fd:
                fd.write(html)

        if self.fname:
            self.get_html(completion, 'w')
        else:
            dialog = Gtk.FileChooserDialog("Select an HTML file", None,
                    Gtk.FileChooserAction.SAVE,
                        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            if dialog.run() == Gtk.ResponseType.OK:
                self.fname = dialog.get_filename()
                print("Saving", self.fname)
                self.get_html(completion, "w+")
            dialog.destroy()

    def get_html(self, completion_function, user_data):

        #print("get_html")
        def javascript_completion(obj, result, user_data):
            #print("javascript_completion", result)
            fin = self.run_javascript_finish(result)
            #print("fin", fin)
            html = fin.get_js_value().to_string()
            #print("len html", len(html), "\n")
            completion_function(html, user_data)
        self.run_javascript("document.documentElement.innerHTML;",
                                   None,
                                   javascript_completion,
                                   user_data)

    def get_lastmod(self, completion_function, user_data):

        print("get_lastmod")
        def javascript_completion(obj, result, user_data):
            print("javascript_completion", result)
            fin = self.run_javascript_finish(result)
            #print("fin", fin)
            html = fin.get_js_value().to_string()
            print("lastmod", html, "\n")
            #completion_function(html, user_data)
        self.run_javascript("document.lastModified",
                                   None,
                                   javascript_completion,
                                   user_data)


    def generate_ui(self):

        ''' define toolbar items and actions here '''

        actions = Gtk.ActionGroup("Actions")
    # ----------------------------------------------------------------
    # Name,     Stock Icon,   Accelerator,  ToolTip,   Action

    # Some already has app accels

        accel_arr = [ \

    #("menuFile",    None, "_File"),
    #("menuEdit",    None, "_Edit"),
    #("menuInsert",  None, "_Insert"),
    #("menuFormat",  None, "_Format"),
    #("new",         Gtk.STOCK_NEW, "_New", None, None, self.on_new),
    #("open",        Gtk.STOCK_OPEN, "_Open", None, None, self.on_open),
    #("save",        Gtk.STOCK_SAVE, "_Save", None, None, self.on_save),

    ("cut",         Gtk.STOCK_CUT, "_Cut", None, None, self.on_action),
    ("copy",        Gtk.STOCK_COPY, "_Copy", None, None, self.on_action),
    ("paste",       Gtk.STOCK_PASTE, "_Paste", None, None, self.on_paste),

    ("undo",        Gtk.STOCK_UNDO, "_Undo", "<Control>z", "Undo Last Edit", self.on_action),
    ("redo",        Gtk.STOCK_REDO, "_Redo", "<Control>y", "Redo Last Undo", self.on_action),

    ("removeformat", Gtk.STOCK_PROPERTIES, "_removeFormat", "<Control>M", "Remove Formatting", self.on_action),
    ("bold",        Gtk.STOCK_BOLD, "_Bold", "", "Bold / UnBold Selection", self.on_action),
    ("italic",      Gtk.STOCK_ITALIC, "_Italic", "", None, self.on_action),
    ("underline",       Gtk.STOCK_UNDERLINE, "_Underline", "", None, self.on_action),
    ("strikethrough", Gtk.STOCK_STRIKETHROUGH, "_Strike", "", None, self.on_action),
    ("font",        Gtk.STOCK_SELECT_FONT, "Select _Font", "", None, self.on_select_font),
    ("fontsize",    None, "Select Font _Size", "<Control>f", "Set Absolute Size (removes color)", self.on_fontsize),
    ("color",       Gtk.STOCK_SELECT_COLOR, "Select _Color", None, None, self.on_select_color),
    ("backgroundcolor", Gtk.STOCK_COLOR_PICKER, "Select Back Color", None, None, self.on_select_bgcolor),

    ("justifyleft",  Gtk.STOCK_JUSTIFY_LEFT, "Justify _Left", None, None, self.on_action),
    ("justifyright", Gtk.STOCK_JUSTIFY_RIGHT, "Justify _Right", None, None, self.on_action),
    ("justifycenter", Gtk.STOCK_JUSTIFY_CENTER, "Justify _Center", None, None, self.on_action),
    ("justifyfull",   Gtk.STOCK_JUSTIFY_FILL, "Justify _Full", None, None, self.on_action),

    # Pad Images by name (may not be present in all styles)
    ("insertimage", "insert-image", "Insert _Image", None, None, self.on_insert_image),
    ("insertlink", "insert-link", "Insert _Link", None, None, self.on_insert_link),
    ("inserttable", "insert-table", "Insert _Table", None, None, self.on_insert_table),
    ("editmarker", "edit-marker", "edit _Marker", None, None, self.on_edit_marker),

    ("H1",   Gtk.STOCK_EXECUTE, "Header 1", None, "Insert Header 1", self.on_header),
    ("H2",   Gtk.STOCK_EXECUTE, "Header 2", None, "Insert Header 2", self.on_header),
    ("H3",   Gtk.STOCK_EXECUTE, "Header 3", None, "Insert Header 3", self.on_header),
    ("H4",   Gtk.STOCK_EXECUTE, "Header 4", None, "Insert Header 4", self.on_header),

    ]

        actions.add_actions(accel_arr)

        #print(dir(actions))
        for aa in accel_arr:
        #    print("acc arr", dir(aa))
        #    break
        #    act = actions.get_action(aa[0])
        #    print("act", act.get_name(), act.get_tooltip())
            pass
        #    try:
        #        act = Gtk.Action.new(aa[0], aa[2], aa[4], aa[1])
        #        actions.add_action_with_accel(act, aa[3])
        #    except:
        #        #print("Exc on", aa)
        #        pass

        actions.get_action("insertimage").set_property("icon-name", "insert-image")
        actions.get_action("insertlink").set_property("icon-name", "insert-link")
        actions.get_action("inserttable").set_property("icon-name", "appointment-new")
        actions.get_action("editmarker").set_property("icon-name", "text-editor")
        actions.get_action("fontsize").set_property("icon-name", "preferences-desktop-font")
        actions.get_action("removeformat").set_property("icon-name", "text-direction")

        ui = Gtk.UIManager()
        ui.insert_action_group(actions)
        ui.add_ui_from_string(ui_def)

        # Fill in defaults
        xxx = ui.get_action_groups()[0].list_actions()
        for aa in xxx:
            nnn = aa.get_name()
            # Find the original, patth missing info
            for bb in accel_arr:
                # Convert tuple
                bbb = list(bb)
                if bb[0] == nnn:
                    # Pad for this round
                    for cc in range(5 - len(bbb)):
                        bbb.append("")

                    #print("lab", bb[2], aa.get_label())
                    #print("found", nnn, bbb[3])

                    setattr(aa, "accel", bbb[3])
                    if bbb[3]:
                        try:
                            nn, ss = Gtk.accelerator_parse(bbb[3])
                            setattr(aa, "accel_parsed", (nn, ss))
                        except:
                            pass

            # Pad it with capitalize name if not there
            if  not aa.get_tooltip():
                aa.set_tooltip(nnn[0].upper() + nnn[1:])

        return ui

# This is kicked in if there is no library  (is it used?)

class pgwebw_fake(Gtk.VBox):

    def __init__(self):
        super(pgwebw_fake, self).__init__();
        pass

    def load_uri(self, url):
        pass

def markdialog(sss):

    spaceneed = 64
    # Wrap tesxt if long
    ssss = ""
    cnt = 0; fff = 0
    for aa in sss:
        if cnt > spaceneed:
            fff = 1
        if fff and aa.isspace():
            cnt = 0; fff = 0
            ssss += "\n"
        ssss += aa
        cnt += 1

    dialog = Gtk.Dialog("   Edit markup   ", None, 0,
    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

    textview = Gtk.TextView()
    textview.set_editable(True)

    textbuffer = textview.get_buffer()
    textbuffer.set_text(ssss)

    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    scrolledwindow.add(textview)
    scrolledwindow.set_size_request(640, 480)

    hhh = "\n          " \
            "In general, any valid html can go here. Keep it simple.\n" \
            "The editor already decorated this sufficiently, "\
              "try to edit existing items in place.\n"

    lll = Gtk.Label(hhh)
    fd = Pango.FontDescription("Sans 9")
    lll.override_font(fd)
    thbox = Gtk.HBox()
    thbox.pack_start(lll, 1, 1, 1)
    dialog.vbox.pack_start(thbox, False, False, 0)
    hbox = Gtk.HBox()
    hbox.pack_start(Gtk.Label(" "), False, False, 0)
    hbox.pack_start(scrolledwindow, 1, 1, 0)
    hbox.pack_start(Gtk.Label(" "), False, False, 0)
    dialog.vbox.pack_start(hbox, 1, 1, 0)
    #dialog.vbox.pack_start(Gtk.Label(" "), False, False, 0)
    dialog.show_all()

    htmlx = ""
    if dialog.run() == Gtk.ResponseType.OK:
        bi = textbuffer.get_start_iter()
        ei = textbuffer.get_end_iter()
        htmlx = textbuffer.get_text(bi, ei, False)

    dialog.destroy()

    # Unwrap it
    usss = ""
    cnt = 0; fff = 0
    for aa in htmlx:
        if aa == '\n':
            pass
        else:
            usss += aa
    return usss

def treecallb(ddd):
    global sizex
    #print("tree cb", ddd[0])
    sizex = ddd[0]

def sizedialog():

    ''' Present a selection Dialog for font sizes '''

    dialog = Gtk.Dialog("  Font Size   ", None, 0, () )

    #(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

    global sizex
    sizex = ""
    treedat = ["8", "9", "10", "12", "14", "20", "24", "32", "48", "56", "64",
                    "72", "96", "128"]

    tree = SimpleTree(["Font Sizes"])
    for aa in treedat:
        tree.append((aa,))

    def actcallb(ddd):
        #print("Activate cb", ddd, dialog)
        dialog.response(Gtk.ResponseType.OK)
        #print("Activate cb2", ddd, dialog)

    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    scrolledwindow.add(tree)
    scrolledwindow.set_size_request(120, 300)

    tree.setcallb(treecallb)
    tree.setActcallb(actcallb)

    hhh = "\n          " \
            "In general, any valid html can go here. Keep it simple.\n" \
            "The editor already decorated this sufficiently, "\
              "try to edit existing items in place.\n"

    lll = Gtk.Label(hhh)
    fd = Pango.FontDescription("Sans 9")
    lll.override_font(fd)
    thbox = Gtk.HBox()
    thbox.pack_start(lll, 1, 1, 1)
    #dialog.vbox.pack_start(thbox, False, False, 0)

    hbox = Gtk.HBox()
    hbox.pack_start(Gtk.Label(" "), False, False, 0)
    hbox.pack_start(scrolledwindow, 1, 1, 0)
    hbox.pack_start(Gtk.Label(" "), False, False, 0)
    dialog.vbox.pack_start(hbox, 1, 1, 0)
    #dialog.vbox.pack_start(Gtk.Label(" "), False, False, 0)
    dialog.show_all()

    if dialog.run() == Gtk.ResponseType.OK:
        #print("ok", sizex)
        pass
    else:
        sizex = 0

    dialog.destroy()
    return sizex

# EOF
