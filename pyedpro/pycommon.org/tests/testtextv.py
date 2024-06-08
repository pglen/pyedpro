#!/usr/bin/env python

'''

  This is a test application for driving the pgTextView control;
  It has load / save functionality.

'''

import os, sys, getopt, signal, random, time, warnings

#from pgutil import  *
#from pgui import  *

import pgutils
import pgtextview

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import pgbox
import sutil

#deftext = "It puzzles me when I see a person lacking fundamentals is \
#  able to amass a fortune to the tune of billions. What is even more \
#puzziling is that they beleive their 'BS' and open flout all."

# The pango example text

deftext = \
'''
Text sizes: <span size="xx-small">tiny</span> <span size="x-small">very small</span> <span size="small">small</span> <span size="medium">normal</span> <span size="large">large</span> <span size="x-large">very large</span> <span size="xx-large">huge</span>
Text <span color="gray">c<span color="green">o</span>l<span color="tomato">o</span>rs</span> and <span background="pink">backgrounds</span>
Colorful <span underline="low" underline-color="blue"><span underline="double" underline-color="red">under</span>lines</span> and <span background="pink"><span underline="error">mo</span><span underline="error" underline-color="green">re</span></span>
Colorful <span strikethrough="true" strikethrough-color="magenta">strikethroughs</span>
Superscripts and subscripts: 𝜀<span rise="-6000" size="x-small" font_desc="italic">0</span> = 𝜔<span rise="8000" size="smaller">𝜔<span rise="14000" size="smaller">𝜔<span rise="20000">.<span rise="23000">.<span rise="26000">.</span></span></span></span></span>
<span letter_spacing="3000">Letterspacing</span>
OpenType font features: <span font_desc="sans regular" font_features="dlig=0">feast</span> versus <span font_desc="sans regular" font_features="dlig=1">feast</span>
Shortcuts: <tt>Monospace</tt> – <b>Bold</b> – <i>Italic</i> – <big>Big</big> – <small>Small</small> – <u>Underlined</u> – <s>Strikethrough</s> – Super<sup>script</sup> – Sub<sub>script</sub>

#'''

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self):

        self.cnt = 0
        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL)

        self.fname = "Unnamed.mup"
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

        self.fd = Pango.FontDescription()
        pg = Gtk.Widget.create_pango_context(self)
        myfd = pg.get_font_description()
        mysize = myfd.get_size() / Pango.SCALE
        #print("mysize", mysize)

        vbox = Gtk.VBox();

        self.tview = pgtextview.pgTextView()
        #self.tview.set_text(deftext)

        buff = self.tview.textbuffer
        buff.insert_markup(buff.get_start_iter(), deftext, len(deftext))
        buff.set_modified(0)

        vbox.pack_start(self.tview,1,1,2)
        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label.new(" "), 1, 1, 0)

        testbutt = Gtk.Button.new_with_mnemonic("   _Import   ")
        testbutt.connect("activate", self.oninp)
        testbutt.connect("pressed", self.oninp)
        hbox.pack_start(testbutt, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        testbutt = Gtk.Button.new_with_mnemonic("   _Export   ")
        testbutt.connect("activate", self.onexp)
        testbutt.connect("pressed", self.onexp)
        hbox.pack_start(testbutt, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        testbutt = Gtk.Button.new_with_mnemonic("   _Test   ")
        testbutt.connect("activate", self.ontest)
        testbutt.connect("pressed", self.ontest)
        hbox.pack_start(testbutt, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        loadbutt = Gtk.Button.new_with_mnemonic("   _Load   ")
        loadbutt.connect("activate", self.onload)
        loadbutt.connect("pressed", self.onload)
        hbox.pack_start(loadbutt, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        savebutt = Gtk.Button.new_with_mnemonic("   _Save   ")
        savebutt.connect("activate", self.onsave)
        savebutt.connect("pressed", self.onsave)
        hbox.pack_start(savebutt, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        butt = Gtk.Button.new_with_mnemonic("   E_xit   ")
        butt.connect("activate", self.OnExit)
        butt.connect("pressed", self.OnExit)
        hbox.pack_start(butt, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        vbox.pack_start(hbox, 0, 0, 4)

        self.add(vbox)
        self.show_all()

    def oninp(self, butt):
        sss = \
        b'GTKTEXTBUFFERCONTENTS-0001\x00\x00\x00\xcc <text_view_markup>\n <tags>\n  ' \
        b'<tag name="bold" priority="7">\n   <attr name="weight" type="gint" value="700" />\n ' \
        b'</tag>\n </tags>\n<text><apply_tag ' \
        b'name="bold">Hello</apply_tag>\n</text>\n</text_view_markup>\n '

        self.tview.deser_buff(sss)

    def onexp(self, butt):
        sss = self.tview.ser_buff()
        print(sss)

    # Use it to print stuff
    def ontest(self, butt):
        self.tview.print_tags()

    def onload(self, butt):
        #print("onload", butt)
        self.fname = sutil.opendialog()
        fp = open(self.fname, "rb")
        ddd = fp.read()  #.decode("cp437")
        fp.close()

        self.tview.deser_buff(ddd)

    def onsave(self, butt):
        #print("Save", butt)
        if not self.tview.textbuffer.get_modified():
            sutil.message("\nFile is not modified.", title="File Save")
            return
        fname = sutil.savedialog(0)
        #print("got fname", fname)
        if not fname:
            return
        if os.path.isfile(fname):
            resp = pgutils.yes_no_cancel("Overwrite File Prompt",
                        "Overwrite existing file?\n '%s'" % fname, False)
            if resp == Gtk.ResponseType.NO:
                print("not saved")
                return
        buff  =  self.tview.textbuffer
        serx = self.tview.ser_buff()
        #print(serx)
        fp = open(fname, "wb")
        fp.write(serx)
        fp.close()
        self.tview.textbuffer.set_modified(0)

    def OnExit(self, win, arg2 = None):
        if self.tview.textbuffer.get_modified():
            resp = pgutils.yes_no_cancel("File modified",
            "Save file? \n\n '%s' \n" % self.fname, False)
            if resp == Gtk.ResponseType.YES:
                #print("saving")
                self.onsave(None)

        #print("OnExit", win)
        Gtk.main_quit()

if __name__ == '__main__':

    #print("Starting pytextview")
    mainwin = MainWin()

    Gtk.main()


