#!/usr/bin/env python

#import pygtk, gobject, gtk, pango

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

import copy
import panglib.stack as stack
import panglib.parser as parser

from    panglib.utils import *

old_stresc = ""
accum = ""
old_xtag = None

# ------------------------------------------------------------------------
# Hack for caching interaction with the pango subsystem.
# If the text formatting parameters have not changed, we accumulate the strings
# and dump it out when needed

# Check for state change by comparing object vars

def chkstate(obj_1, obj_2):

    ret = True
    if not obj_1: return ret
    if not obj_2: return ret

    # See if dictionaries match
    if len(obj_1.__dict__) != len(obj_2.__dict__):
        return ret
    ret = False
    # See if variables match
    for aa in obj_1.__dict__:
        if obj_1.__dict__[aa] !=  obj_2.__dict__[aa]:
            ret = True
            break
    return ret

# Callback class, extraction of callback functions from the pangview parser.
# The class TextState is the format controlling class, Mainview is the target
# window, and the Emit() function is to aid debug. These funtions may also
# manipulate the parser stack. Note the naming convention like Bold() for
# bold start, eBold() for bold end.

class CallBack():

    def __init__(self, TextState, Mainview, Emit, Pvg):
        self.TextState = TextState
        self.Mainview = Mainview
        self.emit = Emit
        self.pvg = Pvg
        self.oldstate = None

    def Span(self, vparser, token, tentry):
        self.emit("<span ")

    def Tab(self, vparser, token, tentry):
        #print ("textstate tab", vparser.strx)
        # Erase current token str
        #vparser.strx = ""
        self.TextState.tab += 1
        #self.Mainview.add_text("\t")
        self.emit( "<tab>")

    def Strike(self, vparser, token, tentry):
        self.TextState.strike = True
        self.emit( "<strike>")

    def eStrike(self, vparser, token, tentry):
        self.TextState.strike = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<estrike>")

    def Bold(self, vparser, token, tentry):
        #print ("got bold")
        self.TextState.bold = True
        self.emit( "<bold>")

    def eBold(self, vparser, token, tentry):
        #print ("got ebold")
        self.TextState.bold = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<ebold>")

    def Italic(self, vparser, token, tentry):
        #print ("Got Italic")
        self.TextState.italic = True
        self.emit("<italic>")

    def eItalic(self, vparser, token, tentry):
        self.TextState.italic = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit ( "<eitalic>")

    def flush(self):
        global oldstate, accum
        if accum != "":
            if self.oldstate:
                TextState2 = self.oldstate
            else:
                TextState2 =  self.TextState

            xtag2 =  self.parseTextState(TextState2)
            self.Mainview.add_text_xtag(accum, xtag2, self.pvg.flag)
            accum = ""

    # --------------------------------------------------------------------
    def Text(self, vparser, token, tentry):

        global oldstate, accum, old_stresc

        self.emit(vparser.strx)
        stresc = unescape(vparser.strx)
        # If wrapping, output one space only
        if self.TextState.wrap:
            if stresc == " ":
                if old_stresc == " ":
                    return
                old_stresc = " "
            else:
                old_stresc = ""

        # Enable / Disable caching
        enable_cache = True
        if enable_cache:
            if not chkstate(self.oldstate, self.TextState) and len(accum) < 1000:
                #print ("caching: '" + accum + "'")
                accum += stresc
                return
                pass
            else:
                #print ("printing: '" +  accum + "'")
                pass
        else:
            accum += stresc

        # Materialize text
        if not self.TextState.hidden:
            #print   ("func", self.pvg.flag)
            #self.Mainview.add_text_xtag(stresc, xtag, self.pvg.flag)
            if enable_cache:
                if self.oldstate:
                    xtag2 = self.parseTextState(self.oldstate, vparser)
                else:
                    xtag2 = self.parseTextState(self.TextState, vparser)
            else:
                xtag2 = self.parseTextState(self.TextState, vparser)
            self.Mainview.add_text_xtag(accum, xtag2, self.pvg.flag)
            accum = ""
        else:
            if self.pvg.verbose:
                print ("Hidden:", accum)

        # Save tag state
        #self.oldstate = dupstate(self.TextState)
        accum += stresc
        self.oldstate = copy.deepcopy(self.TextState)

    # --------------------------------------------------------------------
    def parseTextState(self, TextState, vparser = None):

        xtag = Gtk.TextTag()

        if TextState.font != "":
            xtag.set_property("font", TextState.font)

        # This is one shot per count, reset tab
        if vparser:
            while  TextState.tab:
                vparser.strx = "\t" + vparser.strx
                #self.Mainview.add_text("\t")
                TextState.tab -=1

        SCALE_LARGE = 1.2
        SCALE_X_LARGE = 1.4
        SCALE_XX_LARGE = 1.8
        SCALE_SMALL = 0.8
        SCALE_X_SMALL = 0.6

        # Decorate textag according to machine state
        if TextState.fixed:    xtag.set_property("family", "Monospace")
        if TextState.bold:     xtag.set_property("weight", Pango.Weight.BOLD)
        if TextState.italic:   xtag.set_property("style", Pango.Style.ITALIC)
        #if TextState.itbold:   xtag.set_property("foreground", "red")
        if TextState.large:    xtag.set_property("scale", SCALE_LARGE)
        if TextState.xlarge:   xtag.set_property("scale", SCALE_X_LARGE)
        if TextState.xxlarge:  xtag.set_property("scale", SCALE_XX_LARGE)
        if TextState.small:    xtag.set_property("scale", SCALE_SMALL)
        if TextState.xsmall:    xtag.set_property("scale", SCALE_X_SMALL)
        if TextState.ul:       xtag.set_property("underline", Pango.Underline.SINGLE)
        if TextState.dul:      xtag.set_property("underline", Pango.Underline.DOUBLE)

        if TextState.red:      xtag.set_property("foreground", "red")
        if TextState.green:    xtag.set_property("foreground", "green")
        if TextState.blue:     xtag.set_property("foreground", "blue")

        if TextState.bgred:    xtag.set_property("background", "red")
        if TextState.bggreen:  xtag.set_property("background", "green")
        if TextState.bgblue:   xtag.set_property("background", "blue")

        if TextState.strike:   xtag.set_property("strikethrough", True)
        if TextState.wrap:     xtag.set_property("wrap_mode", Gtk.WrapMode.WORD)

        if TextState.center:   xtag.set_property("justification", Gtk.Justification.CENTER)
        if TextState.right:    xtag.set_property("justification", Gtk.Justification.RIGHT)
        if TextState.fill:     xtag.set_property("justification", Gtk.Justification.FILL)

        #print ("bgcolor:",  TextState.bgcolor )
        if TextState.bgcolor != "":
            xtag.set_property("background", TextState.bgcolor)

        #print ("color:",  TextState.color )
        if TextState.color != "":
            xtag.set_property("foreground", TextState.color)

        if TextState.size != 0:
            xtag.set_property("size", TextState.size * Pango.SCALE)

        if TextState.link != "":
            xtag.set_data("link", TextState.link)
            if TextState.color == "":
                xtag.set_property("foreground", "blue")

        # Sub / Super sets the size again ...
        if TextState.sub:
            rr = -4; ss = 8
            if TextState.size != 0:
                rr = - TextState.size / 6
                ss  = TextState.size / 2
            xtag.set_property("rise", rr * Pango.SCALE)
            xtag.set_property("size", ss * Pango.SCALE)

        if TextState.sup:
            rr = 6; ss = 8
            if TextState.size != 0:
                rr =  TextState.size / 2
                ss  = TextState.size /2
            xtag.set_property("rise", rr * Pango.SCALE)
            xtag.set_property("size", ss * Pango.SCALE)

        # Calculate current indent
        ind = TextState.indent * 32;
        #if TextState.indent > 0:
        xtag.set_property("indent", ind)

        # Calculate current margin
        ind = TextState.margin * 32;
        if TextState.margin > 0:
            xtag.set_property("left_margin", ind)
            xtag.set_property("right_margin", ind)

        # Calculate current Left margin
        ind = TextState.lmargin * 32;
        if TextState.lmargin > 0:
            xtag.set_property("left_margin", ind)

        return xtag

    def Bgred(self, vparser, token, tentry):
        self.TextState.bgred = True
        self.emit( "<bgred>")

    def eBgred(self, vparser, token, tentry):
        self.TextState.bgred = False
        #    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        vparser.popstate()
        self.emit( "<ebgred>")

    def Bggreen(self, vparser, token, tentry):
        self.TextState.bggreen = True
        self.emit( "<bggreen>")

    def eBggreen(self, vparser, token, tentry):
        self.TextState.bggreen = False
        #    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        vparser.popstate()
        self.emit( "<ebggreen>")

    def Bgblue(self, vparser, token, tentry):
        self.TextState.bgblue = True
        self.emit( "<bgblue>")

    def eBgblue(self, vparser, token, tentry):
        self.TextState.bgblue = False
        #    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        vparser.popstate()
        self.emit( "<ebgblue>")

    def Xlarge(self, vparser, token, tentry):
        self.TextState.xlarge = True
        self.emit( "<xlarge>")

    def eXlarge(self, vparser, token, tentry):
        self.TextState.xlarge = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<exlarge>")

    def Large(self, vparser, token, tentry):
        self.TextState.large = True
        self.emit( "<large>")

    def eLarge(self, vparser, token, tentry):
        self.TextState.large = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<elarge>")

    def Dunderline(self, vparser, token, tentry):
        self.TextState.dul = True
        self.emit( "<dunderline>")

    def eDunderline(self, vparser, token, tentry):
        self.TextState.dul = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<edunderline>")

    def Underline(self, vparser, token, tentry):
        self.TextState.ul = True
        self.emit( "<underline>")

    def eUnderline(self, vparser, token, tentry):
        self.TextState.ul = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<eunderline>")

    def ItBold(self, vparser, token, tentry):
        self.TextState.itbold = True
        self.emit( "<itbold>")

    def eItBold(self, vparser, token, tentry):
        self.TextState.itbold = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<eitbold>")

    def Green(self, vparser, token, tentry):
        self.TextState.green = True
        self.emit( "<green>")

    def eGreen(self, vparser, token, tentry):
        self.TextState.green = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<egreen>")

    def Blue(self, vparser, token, tentry):
        self.TextState.blue = True
        self.emit( "<blue>")

    def eBlue(self, vparser, token, tentry):
        self.TextState.blue = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<eblue>")

    def Red(self, vparser, token, tentry):
        self.TextState.red = True
        self.emit( "<red>")

    def eRed(self, vparser, token, tentry):
        self.TextState.red = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<ered>")

    def Center(self, vparser, token, tentry):
        self.TextState.center = True
        self.emit( "<center>")

    def eCenter(self, vparser, token, tentry):
        self.TextState.center = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<ecenter>")

    def Right(self, vparser, token, tentry):
        self.TextState.right = True
        self.emit( "<right>")

    def eRight(self, vparser, token, tentry):
        self.TextState.right = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<eright>")

    def Xsmall(self, vparser, token, tentry):
        self.TextState.xsmall = True
        self.emit( "<xsmall>")

    def eXsmall(self, vparser, token, tentry):
        self.TextState.xsmall = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<exsmall>")

    def Small(self, vparser, token, tentry):
        self.TextState.small = True
        self.emit( "<small>")

    def eSmall(self, vparser, token, tentry):
        self.TextState.small = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<esmall>")

    def Xxlarge(self, vparser, token, tentry):
        self.TextState.xxlarge = True
        self.emit( "<xxlarge>")

    def eXxlarge(self, vparser, token, tentry):
        self.TextState.xxlarge = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<exxlarge>")

    def Margin(self, vparser, token, tentry):
        self.TextState.margin += 1
        self.emit( "<margin>")

    def eMargin(self, vparser, token, tentry):
        if self.TextState.margin > 0:
            self.TextState.margin -= 1
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<emargin>")

    def Lmargin(self, vparser, token, tentry):
        self.TextState.lmargin += 1
        self.emit( "<margin>")

    def eLmargin(self, vparser, token, tentry):
        if self.TextState.lmargin > 0:
            self.TextState.lmargin -= 1
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<emargin>")

    def Fixed(self, vparser, token, tentry):
        self.TextState.fixed = True
        self.emit( "<fixed>")

    def eFixed(self, vparser, token, tentry):
        self.TextState.fixed = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<efixed>")

    def Sup(self, vparser, token, tentry):
        self.TextState.sup = True
        self.emit( "<sup>")

    def eSup(self, vparser, token, tentry):
        self.TextState.sup = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<esup>")

    def Sub(self, vparser, token, tentry):
        self.TextState.sub = True
        self.emit( "<sub>")

    def eSub(self, vparser, token, tentry):
        self.TextState.sub = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<esub>")

    def Hid(self, vparser, token, tentry):
        self.TextState.hidden = True
        self.emit( "<hid>")

    def eHid(self, vparser, token, tentry):
        self.TextState.hidden = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<ehid>")

    def Indent(self, vparser, token, tentry):
        self.TextState.indent += 1
        self.emit( "<indent>")

    def eIndent(self, vparser, token, tentry):
        if self.TextState.indent > 0:
            self.TextState.indent -= 1
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<eindent>")

    def Wrap(self, vparser, token, tentry):
        self.TextState.wrap = True
        self.emit( "<wrap>")

    def eWrap(self, vparser, token, tentry):
        self.TextState.wrap = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<ewrap>")

    def Fill(self, vparser, token, tentry):
        self.TextState.fill = True
        self.emit( "<fill>")

    def eFill(self, vparser, token, tentry):
        self.TextState.fill = False
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<efill>")

    def Nbgcol(self, vparser, token, tentry):
        self.emit( "<nbgcol> " + vparser.strx[3:len(vparser.strx)-1])
        self.TextState.bgcolor = vparser.strx[3:len(vparser.strx)-1]

    def eNbgcol(self, vparser, token, tentry):
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.TextState.bgcolor = ""
        self.emit( "<enbgcol> ")

    def Ncol(self, vparser, token, tentry):
        self.emit( "<ncol> " + vparser.strx)
        self.TextState.color = vparser.strx[1:len(vparser.strx)-1]

    def Ncol2(self, vparser, token, tentry):
        self.emit( "<ncol2> " + vparser.strx)
        self.TextState.color = vparser.strx[3:len(vparser.strx)-1]

    def eNcol(self, vparser, token, tentry):
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.TextState.color = ""
        self.emit( "<encol> ")

    def Link(self, vparser, token, tentry):
        self.emit( "<link>")

    def Link2(self, vparser, token, tentry):
        xstack = stack.Stack()
        # Walk optionals:
        while True:
            vparser.popstate()
            if vparser.fsm == parser.KEYVAL:
                #print (" Reducing keyval", fsm, "'"+ttt+"'", "\"" + stry + "\""            )
                xstack.push([vparser.ttt, "=", vparser.stry])
            if vparser.contflag == 0:
                break

        while True:
            xkey = xstack.pop()
            if not xkey:
                break
            kk, ee, vv = xkey;
            vv = vv.replace("\"",""); vv = vv.replace("\'","")

            #print ("link key: '" + kk + "' val: '" + vv + "'")
            if kk == "file" or kk == "name":
                # Try docroot - current dir - home dir
                fname = self.pvg.docroot + "/" + vv
                if not isfile(fname):
                    fname = vv
                    if not isfile(fname):
                        fname = "~/" + vv
                        if not isfile(fname):
                            fname = vv

                self.TextState.link = fname
            if kk == "color" or kk == "fg":
                #print ("setting color in link")
                self.TextState.color = vv

        self.emit( "<link2>")

    def eLink(self, vparser, token, tentry):
        self.TextState.link = ""
        self.TextState.color = ""
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<elink>")

    def Image(self, vparser, token, tentry):
        self.emit( "<image>")

    def Image2(self, vparser, token, tentry):
        xstack = stack.Stack()
        # Walk optionals:
        while True:
            vparser.popstate()
            if vparser.fsm == parser.KEYVAL:
                #print (" Reducing keyval", fsm, "'"+ttt+"'", "\"" + stry + "\""            )
                xstack.push([vparser.ttt, "=", vparser.stry])
            if vparser.contflag == 0:
                break

        xtag = Gtk.TextTag();  fname = ""; www = 0; hhh = 0

        while True:
            xkey = xstack.pop()
            if not xkey:
                break
            kk, ee, vv = xkey;
            vv = vv.replace("\"",""); vv = vv.replace("\'","")

            #print ("key: '" + kk + "' val: '" + vv + "'")

            if kk == "align":
                if vv == "left":
                    xtag.set_property("justification", Gtk.JUSTIFY_LEFT)
                elif vv == "center":
                    xtag.set_property("justification", Gtk.JUSTIFY_CENTER)
                elif vv == "right":
                    xtag.set_property("justification", Gtk.JUSTIFY_RIGHT)

            if kk == "width":
                www = int(vv)

            if kk == "height":
                hhh = int(vv)

            if kk == "name" or kk == "file":
                # Try docroot - curr dir - home/Pictures - home
                fname = self.pvg.docroot + "/" + vv
                if not isfile(fname):
                    fname = vv
                    if not isfile(fname):
                        fname = "~/Pictures" + vv
                        if not isfile(fname):
                            fname = "~/" + vv

        # Exec collected stuff
        self.Mainview.add_text_xtag(" ", xtag, self.pvg.flag)
        try:
            pixbuf = Gtk.gdk.pixbuf_new_from_file(fname)
            if www and hhh:
                #print ("scaling to", www, hhh)
                pixbuf2 = Gtk.gdk.Pixbuf(Gtk.gdk.COLORSPACE_RGB, True, 8, www, hhh)
                pixbuf.scale(pixbuf2, 0, 0, www, hhh,
                    0, 0, float(www)/pixbuf.get_width(), float(hhh)/pixbuf.get_height(),
                Gtk.gdk.INTERP_BILINEAR)
                self.Mainview.add_pixbuf(pixbuf2, self.pvg.flag)
            else:
                self.Mainview.add_pixbuf(pixbuf, self.pvg.flag)

        except gobject.GError as error:
            #print ("Failed to load image file '" + vv + "'")
            self.Mainview.add_broken(self.pvg.flag)

        #vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<image2>")

    def eImage(self, vparser, token, tentry):
        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit( "<eimage>")

    def Span2(self, vparser, token, tentry):
        xstack = stack.Stack()
        # Walk optionals:
        while True:
            fsm, contflag, ttt, stry = vparser.fstack.pop()
            if fsm == parser.KEYVAL:
                #print (" Reducing keyval", fsm, "'"+ttt+"'", "\"" + stry + "\""            )
                xstack.push([ttt, "=", stry])
            if contflag == 0:
                break

        # Set font parameters:
        while True:
            xkey = xstack.pop()
            if not xkey:
                break
            kk, ee, vv = xkey;
            vv = vv.replace("\"",""); vv = vv.replace("\'","")

            #print ("key ",kk, vv)
            if kk == "background" or kk == "bg" or kk == "bgcolor":
                self.TextState.bgcolor = vv
            if kk == "foreground" or kk == "fg" or kk == "color":
                self.TextState.color = vv
            elif kk == "size":
                self.TextState.size = int(vv)
            elif kk == "font":
                self.TextState.font = vv
            elif kk == "bold":
                if isTrue(vv):
                    self.TextState.bold = True
                else:
                    self.TextState.bold = False

            elif kk == "italic":
                if isTrue(vv):
                    self.TextState.italic = True
                else:
                    self.TextState.italic = False

            elif kk == "under" or kk == "underline":
                if isTrue(vv):
                    self.TextState.ul = True
                else:
                    self.TextState.ul = False

            elif kk == "align" or kk == "alignment":
                vvv = vv.lower()
                if vvv == "left":
                    self.TextState.left = True
                elif vvv == "right":
                    self.TextState.right = True
                elif vvv == "center":
                    #print (" centering")
                    self.TextState.center = True

        self.emit(" spantxt >");


    def eSpan(self, vparser, token, tentry):
        #print ("called span", parser.strx)
        self.TextState.color = ""
        self.TextState.bgcolor = ""
        self.TextState.size = 0
        self.TextState.font = ""
        self.TextState.left = False
        self.TextState.center = False
        self.TextState.right = False
        self.TextState.ul = False

        vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
        self.emit ("<espan>" )

    def Keyval(self, vparser, token, tentry):

        #print ("called keyval", vparser.fsm, token, vparser.strx)

        # Pop two items, create keyval
        fsm, contflag, ttt, stry = vparser.fstack.pop()      # EQ
        fsm2, contflag2, ttt2, stry2 = vparser.fstack.pop()  # Key

        # Push back summed item (reduce)
        vparser.fstack.push([parser.KEYVAL, 1, stry2, vparser.strx])
        vparser.fsm = fsm2















