#!/usr/bin/env python3

#from __future__ import absolute_import
from __future__ import print_function

import sys, os, re, time
import signal, pickle

#import pygtk, gobject, gtk, pango

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

# Our modules

import  panglib.parser as parser
import  panglib.stack as stack
import  panglib.lexer as lexer
import  panglib.pangdisp as pangdisp
import  panglib.pangfunc as pangfunc

import inspect
if inspect.isbuiltin(time.process_time):
    time.clock = time.process_time

# This parser digests formatted text similar to pango in Gtk.
# Was created to quickly display formatted messages.
# See SYNTAX for details on text formats

'''
# We initialize parser variables in the context of the parser module.
#
# a.) Token definitions, b.) Lexer tokens,
# c.) Parser functions,  d.) Parser state, e.) Parse table
#
# To create a custom parser, just add new tokens / states
#

# Quick into: The lexer creates a stack of tokens. The parser scans
# the tokens, and walks the state machine for matches. If match
# is encountered, the parser calls the function in the state table,
# and / or changes state. Reduce is called after the state has been
# successfully digested. For more info see lex / yacc literature.
'''

# Connect parser token to lexer item. This way the definitions are synced
# without the need for double definition

def parse_lookup(strx):
    ret = None
    for aa in parser.tokdef:
        if strx == aa[1]:
            #print "found", aa
            ret = aa
            break
    if ret == None:
        print ("Token '" + strx + "' not found, please correct it.")
        sys.exit(1)
    return aa

# The short verion, returning the num only
def pl(strx):
    aa = parse_lookup(strx)
    return aa[0]

# Some globals read: (Pang View Globals):

class pvg():

    buf = None; xstack = None; verbose = False
    pgdebug = False; show_lexer = False; full_screen = False
    lstack = None;  fullpath = None; docroot = None
    got_clock = 0; show_timing = False; second = ""
    xfull_screen = False; flag = False; show_parse = False
    emit = False; show_state = False; pane_pos = -1

# ------------------------------------------------------------------------
# Token definitions:
# Use textual context nn[idx][1] for development, numeric nn[idx][0]
# for production use.
#
# The order of the definitions do not matter.
#
# To add a new syntactic element, search for an existing feature (like 'wrap')
# Add the new element into the a.) definition, b.) regex defintion,
# c.) state definition, d.) state table, e.) action function.
#
# The script is self checking, will report on missing defintions. However,
# it can not (will not) report on syntactic anomalies.
#

parser.tokdef = \
         [parser.unique(), "span"   ],      \
         [parser.unique(), "espan" ],       \
         [parser.unique(), "it"     ],      \
         [parser.unique(), "eit"    ],      \
         [parser.unique(), "bold"   ],      \
         [parser.unique(), "ebold"  ],      \
         [parser.unique(), "itbold" ],      \
         [parser.unique(), "eitbold"],      \
         [parser.unique(), "ul"   ],        \
         [parser.unique(), "eul"  ],        \
         [parser.unique(), "dul"   ],       \
         [parser.unique(), "edul"  ],       \
         [parser.unique(), "ncol"   ],      \
         [parser.unique(), "ncol2"   ],     \
         [parser.unique(), "encol"  ],      \
         [parser.unique(), "nbgcol"   ],    \
         [parser.unique(), "enbgcol"  ],    \
         [parser.unique(), "hid"   ],       \
         [parser.unique(), "ehid"  ],       \
         [parser.unique(), "indent"   ],    \
         [parser.unique(), "eindent"  ],    \
         [parser.unique(), "margin"   ],    \
         [parser.unique(), "emargin"  ],    \
         [parser.unique(), "lmargin"   ],   \
         [parser.unique(), "elmargin"  ],   \
         [parser.unique(), "wrap"   ],      \
         [parser.unique(), "ewrap"  ],      \
         [parser.unique(), "link"   ],      \
         [parser.unique(), "elink"  ],      \
         [parser.unique(), "image"   ],     \
         [parser.unique(), "eimage"  ],     \
         [parser.unique(), "sub"   ],       \
         [parser.unique(), "esub"  ],       \
         [parser.unique(), "sup"   ],       \
         [parser.unique(), "esup"  ],       \
         [parser.unique(), "fill"   ],      \
         [parser.unique(), "efill"  ],      \
         [parser.unique(), "fixed"   ],     \
         [parser.unique(), "efixed"  ],     \
         [parser.unique(), "cent"   ],      \
         [parser.unique(), "ecent"  ],      \
         [parser.unique(), "right"   ],     \
         [parser.unique(), "eright"  ],     \
         [parser.unique(), "red"   ],       \
         [parser.unique(), "ered"  ],       \
         [parser.unique(), "bgred"   ],     \
         [parser.unique(), "ebgred"  ],     \
         [parser.unique(), "green"   ],     \
         [parser.unique(), "egreen"  ],     \
         [parser.unique(), "bggreen"   ],   \
         [parser.unique(), "ebggreen"  ],   \
         [parser.unique(), "blue"   ],      \
         [parser.unique(), "eblue"  ],      \
         [parser.unique(), "bgblue"   ],    \
         [parser.unique(), "ebgblue"  ],    \
         [parser.unique(), "large"   ],     \
         [parser.unique(), "elarge"  ],     \
         [parser.unique(), "xlarge"   ],    \
         [parser.unique(), "exlarge"  ],    \
         [parser.unique(), "xxlarge"   ],   \
         [parser.unique(), "exxlarge"  ],   \
         [parser.unique(), "small"   ],     \
         [parser.unique(), "esmall"  ],     \
         [parser.unique(), "xsmall"   ],    \
         [parser.unique(), "exsmall"  ],    \
         [parser.unique(), "strike"   ],    \
         [parser.unique(), "estrike"  ],    \
         [parser.unique(), "escquo" ],      \
         [parser.unique(), "dblbs"  ],      \
         [parser.unique(), "ident"  ],      \
         [parser.unique(), "str"    ],      \
         [parser.unique(), "str2"   ],      \
         [parser.unique(), "str3"   ],      \
         [parser.unique(), "str4"   ],      \
         [parser.unique(), "eq"     ],      \
         [parser.unique(), "comm"   ],      \
         [parser.unique(), "bsnl"   ],      \
         [parser.unique(), "lt"     ],      \
         [parser.unique(), "gt"     ],      \
         [parser.unique(), "sp"     ],      \
         [parser.unique(), "tab"    ],      \
         [parser.unique(), "nl"     ],      \
         [parser.unique(), "tab2"   ],      \
         [parser.unique(), "any"    ],      \

# ------------------------------------------------------------------------
# Lexer tokens. The lexer will search for the next token.
# When editing, update tokdef and tokens together.
#
# The order of the definitions matter. First token match is returned.
#
# Please note for simplicity we defined a stateless lexer. For example,
# the str is delimited by "" and str2 is delimited by '' to allow
# quotes in the str. For more complex string with quotes in it, escape
# the quotes. (\48)
#
# Elements:
#      --- enum tokdef -- token regex -- placeholder (compiled regex) --

parser.tokens =  [
    [parse_lookup("span"),      "<span "        , None  ],
    [parse_lookup("espan"),     "</span>"       , None, ],
    [parse_lookup("it"),        "<i>"           , None, ],
    [parse_lookup("eit"),       "</i>"          , None, ],
    [parse_lookup("hid"),       "<hid>"         , None, ],
    [parse_lookup("ehid"),      "</hid>"        , None, ],
    [parse_lookup("bold"),      "<b>"           , None, ],
    [parse_lookup("tab"),       "<tab>"         , None, ],
    [parse_lookup("ebold"),     "</b>"          , None, ],
    [parse_lookup("itbold"),    "<ib>"          , None, ],
    [parse_lookup("eitbold"),   "</ib>"         , None, ],
    [parse_lookup("red"),       "<r>"           , None, ],
    [parse_lookup("ered"),      "</r>"          , None, ],
    [parse_lookup("bgred"),     "<rb>"           , None, ],
    [parse_lookup("ebgred"),    "</rb>"          , None, ],
    [parse_lookup("indent"),    "<in>"          , None, ],
    [parse_lookup("eindent"),   "</in>"         , None, ],
    [parse_lookup("margin"),    "<m>"          , None, ],
    [parse_lookup("emargin"),   "</m>"         , None, ],
    [parse_lookup("lmargin"),    "<lm>"          , None, ],
    [parse_lookup("elmargin"),   "</lm>"         , None, ],
    [parse_lookup("blue"),      "<e>"           , None, ],
    [parse_lookup("eblue"),     "</e>"          , None, ],
    [parse_lookup("bgblue"),    "<eb>"           , None, ],
    [parse_lookup("ebgblue"),   "</eb>"          , None, ],
    [parse_lookup("green"),     "<g>"           , None, ],
    [parse_lookup("egreen"),    "</g>"          , None, ],
    [parse_lookup("bggreen"),   "<gb>"           , None, ],
    [parse_lookup("ebggreen"),  "</gb>"          , None, ],
    [parse_lookup("large"),     "<l>"           , None, ],
    [parse_lookup("elarge"),    "</l>"          , None, ],
    [parse_lookup("xlarge"),    "<xl>"          , None, ],
    [parse_lookup("exlarge"),   "</xl>"         , None, ],
    [parse_lookup("xxlarge"),   "<xxl>"         , None, ],
    [parse_lookup("exxlarge"),  "</xxl>"        , None, ],
    [parse_lookup("small"),     "<sm>"          , None, ],
    [parse_lookup("esmall"),    "</sm>"         , None, ],
    [parse_lookup("xsmall"),    "<xs>"          , None, ],
    [parse_lookup("exsmall"),   "</xs>"          , None, ],
    [parse_lookup("cent"),      "<c>"           , None, ],
    [parse_lookup("ecent"),     "</c>"          , None, ],
    [parse_lookup("right"),     "<t>"           , None, ],
    [parse_lookup("eright"),    "</t>"          , None, ],
    [parse_lookup("strike"),    "<s>"           , None, ],
    [parse_lookup("estrike"),   "</s>"          , None, ],
    [parse_lookup("ul"),        "<u>"           , None, ],
    [parse_lookup("eul"),       "</u>"          , None, ],
    [parse_lookup("dul"),       "<uu>"          , None, ],
    [parse_lookup("edul"),      "</uu>"         , None, ],
    [parse_lookup("wrap"),      "<w>"           , None, ],
    [parse_lookup("ewrap"),     "</w>"          , None, ],
    [parse_lookup("link"),      "<link "        , None, ],
    [parse_lookup("elink"),     "</link>"       , None, ],
    [parse_lookup("image"),      "<image "      , None, ],
    [parse_lookup("eimage"),     "</image>"     , None, ],
    [parse_lookup("sub"),       "<sub>"         , None, ],
    [parse_lookup("esub"),      "</sub>"        , None, ],
    [parse_lookup("sup"),       "<sup>"         , None, ],
    [parse_lookup("esup"),      "</sup>"        , None, ],
    [parse_lookup("fill"),      "<j>"           , None, ],
    [parse_lookup("efill"),      "</j>"         , None, ],
    [parse_lookup("fixed"),      "<f>"          , None, ],
    [parse_lookup("efixed"),     "</f>"         , None, ],
    [parse_lookup("nbgcol"),    "<bg#[0-9a-fA-F]+ *>"  , None, ],
    [parse_lookup("enbgcol"),   "</bg#>"          , None, ],
    [parse_lookup("ncol2"),      "<fg#[0-9a-fA-F]+ *>"  , None, ],
    [parse_lookup("ncol"),      "<#[0-9a-fA-F]+ *>"  , None, ],
    [parse_lookup("encol"),     "</#>"          , None, ],
    [parse_lookup("tab2"),      r"\\t"            , None, ],
    [parse_lookup("escquo"),    r"\\\""         , None, ],
    [parse_lookup("dblbs"),     r"\\\\"         , None, ],
    [parse_lookup("ident"),     "[A-Za-z0-9_\-\./]+" , None, ],
    [parse_lookup("str4"),      "\#[0-9a-zA-Z]+", None, ],
    [parse_lookup("str3"),      "(\\\\[0-7]+)+"    , None, ],
    [parse_lookup("str"),       "\".*?\""       , None, ],
    [parse_lookup("str2"),      "\'.*?\'"       , None, ],
    [parse_lookup("comm"),      "\n##.*"          , None, ],
    [parse_lookup("eq"),        "="             , None, ],
    [parse_lookup("lt"),        "<"             , None, ],
    [parse_lookup("gt"),        ">"             , None, ],
    [parse_lookup("sp"),        " "             , None, ],
    [parse_lookup("bsnl"),      "\\\\\n"        , None, ],
    [parse_lookup("nl"),        r"\n"            , None, ],
    [parse_lookup("any"),       "."             , None, ],
    ]

# Just to make sure no one is left out: (for debug only)

#if len(parser.tokens) != len(parser.tokdef):
#    print ("Number of token definitions and tokens do not match.")
#    sys.exit(1)

# ------------------------------------------------------------------------
# Parser state machine states. The state machine runs through the whole
# file stepping the rules. The functions may do anything, including reduce.
# Blank reduce may be executed with the state transition set to 'REDUCE'
#
# The number is the state, the string is for debugging / analyzing
# Once ready, operate on the numbers for speed.
# The E-states are not used, kept it for extensibility.

parser.IGNORE  = [parser.unique(),      "ignore"]
parser.INIT    = [parser.unique(),      "init"]
parser.SPAN    = [parser.unique(),      "span"]
parser.SPANTXT = [parser.unique(),      "spantxt"]
parser.IDENT   = [parser.unique(),      "ident"]
parser.KEY     = [parser.unique(),      "key"]
parser.VAL     = [parser.unique(),      "val"]
parser.EQ      = [parser.unique(),      "eq"]
parser.KEYVAL  = [parser.unique(),      "keyval"]
parser.ITALIC  = [parser.unique(),      "italic"]
parser.EITALIC = [parser.unique(),      "eitalic"]
parser.BOLD    = [parser.unique(),      "bold"]
parser.EBOLD   = [parser.unique(),      "ebold"]
parser.ITBOLD  = [parser.unique(),      "itbold"]
parser.EITBOLD = [parser.unique(),      "eitbold"]
parser.UL      = [parser.unique(),      "ul"]
parser.EUL     = [parser.unique(),      "eul"]
parser.DUL     = [parser.unique(),      "dul"]
parser.EDUL    = [parser.unique(),      "edul"]
parser.RED     = [parser.unique(),      "red"]
parser.ERED    = [parser.unique(),      "ered"]
parser.BGRED     = [parser.unique(),     "bgred"]
parser.EBGRED    = [parser.unique(),    "ebgred"]
parser.GREEN   = [parser.unique(),      "green"]
parser.EGREEN  = [parser.unique(),      "egreen"]
parser.BGGREEN   = [parser.unique(),    "bggreen"]
parser.EBGGREEN  = [parser.unique(),    "ebggreen"]
parser.BLUE    = [parser.unique(),      "blue"]
parser.EBLUE   = [parser.unique(),      "eblue"]
parser.BGBLUE    = [parser.unique(),    "bgblue"]
parser.EBGBLUE   = [parser.unique(),    "ebgblue"]
parser.STRIKE  = [parser.unique(),      "strike"]
parser.ESTRIKE = [parser.unique(),      "estrike"]
parser.LARGE  = [parser.unique(),       "large"]
parser.ELARGE = [parser.unique(),       "elarge"]
parser.XLARGE  = [parser.unique(),      "xlarge"]
parser.EXLARGE = [parser.unique(),      "exlarge"]
parser.XXLARGE  = [parser.unique(),     "xlarge"]
parser.EXXLARGE = [parser.unique(),     "exlarge"]
parser.SMALL  = [parser.unique(),       "small"]
parser.ESMALL = [parser.unique(),       "esmall"]
parser.XSMALL  = [parser.unique(),      "xsmall"]
parser.EXSMALL = [parser.unique(),      "exsmall"]
parser.CENT  = [parser.unique(),        "cent"]
parser.ECENT = [parser.unique(),        "ecent"]
parser.RIGHT  = [parser.unique(),       "right"]
parser.ERIGHT = [parser.unique(),       "eright"]
parser.WRAP  = [parser.unique(),        "wrap"]
parser.EWRAP = [parser.unique(),        "ewrap"]
parser.LINK  = [parser.unique(),        "link"]
parser.ELINK = [parser.unique(),        "elink"]
parser.IMAGE  = [parser.unique(),       "image"]
parser.EIMAGE = [parser.unique(),       "eimage"]
parser.SUB  = [parser.unique(),         "sup"]
parser.ESUB = [parser.unique(),         "esup"]
parser.SUP  = [parser.unique(),         "sub"]
parser.ESUP = [parser.unique(),         "esub"]
parser.FILL  = [parser.unique(),        "fill"]
parser.EFILL = [parser.unique(),        "efill"]
parser.FIXED  = [parser.unique(),       "fixed"]
parser.EFIXED = [parser.unique(),       "efixed"]
parser.INDENT  = [parser.unique(),      "indent"]
parser.EINDENT = [parser.unique(),      "eindent"]
parser.MARGIN  = [parser.unique(),      "margin"]
parser.EMARGIN = [parser.unique(),      "emargin"]
parser.LMARGIN  = [parser.unique(),     "lmargin"]
parser.ELMARGIN = [parser.unique(),     "elmargin"]
parser.HID  = [parser.unique(),         "hid"]
parser.EIHID = [parser.unique(),        "ehid"]
parser.NCOL  = [parser.unique(),        "ncol"]
parser.ENCOL = [parser.unique(),        "encol"]
parser.NBGCOL  = [parser.unique(),      "nbgcol"]
parser.ENBNCOL = [parser.unique(),      "enbgcol"]

# ------------------------------------------------------------------------
# State groups for recursion:

# Color instructions: (not used)

STATECOL = [parser.RED, parser.GREEN, parser.BLUE]

# These are states that have recursive actions:
# (like bold in italic or size in color etc ...) Note specifically, that
# the SPAN state is not in this list, as inside span definitions formatting
# does not make sence. This parser ignores such occurances.

STATEFMT = [parser.INIT,  parser.BOLD, parser.ITALIC, parser.RED,
            parser.GREEN, parser.BLUE, parser.BGRED, parser.BGGREEN,
            parser.BGBLUE, parser.UL, parser.DUL, parser.STRIKE,
            parser.SMALL, parser.NCOL, parser.NBGCOL, parser.XSMALL,
            parser.LARGE, parser.XLARGE, parser.XXLARGE,
            parser.SUB, parser.SUP, parser.LINK, parser.CENT,
            parser.RIGHT, parser.WRAP, parser.FILL, parser.INDENT,
            parser.SPANTXT, parser.FIXED, parser.MARGIN, parser.LMARGIN ]

# Our display object
mainview = pangdisp.PangoView(pvg)

# ------------------------------------------------------------------------
# Accumulate output: (mostly for testing)
_cummulate = ""

def emit(strx):
    global _cummulate;
    _cummulate += " '" + strx + "' "

def show_emit():
    global _cummulate;
    print (_cummulate)

# ------------------------------------------------------------------------
# Parser functions that are called on parser events. Note the 'e' prefix
# for the 'end' function -> bold() -> ebold()  (end bold)
# The trivial functions are extracted to pungfunc.py

from    panglib.utils import *

# ------------------------------------------------------------------------
# Text display state:

class TextState():

    def __init__(self):

        self.font = ""
        self.bold = False;  self.itbold = False;   self.italic = False
        self.ul = False; self.dul = False
        self.red = False;  self.blue = False; self.green = False
        self.bgred = False;  self.bgblue = False; self.bggreen = False
        self.strike = False; self.large = False; self.small = False; self.xsmall = False
        self.xlarge = False; self.xxlarge = False; self.center = False
        self.wrap = False; self.hidden = False; self.color =  ""; self.right = False
        self.indent = 0; self.margin = 0; self.size = 0; self.font = "";
        self.fixed = False; self.bgcolor = ""
        self.sub = False; self.sup = False; self.image = ""; self.link = ""; self.lmargin = 0
        self.fill = False; self.tab = 0

    def clear(self):
        for aa in self.__dict__:
            if aa[:2] == "__":
                continue
            if isinstance(self.__dict__[aa], bool):
                   self.__dict__[aa] = False
            elif isinstance(self.__dict__[aa], int):
                   self.__dict__[aa] = 0
            elif isinstance(self.__dict__[aa], str):
                   self.__dict__[aa] = ""
            else:
                print ("  Other", aa, type(self.__dict__[aa]))
                pass

# ------------------------------------------------------------------------
# Class of tokens for simple alternates:

# This token class is for generic text.
TXTCLASS = pl("ident"), pl("eq"), pl("lt"), pl("str"), pl("str2"), \
             pl("str3"), pl("gt"), pl("nl"), pl("sp"), pl("any"),


ts = TextState()
cb = pangfunc.CallBack(ts, mainview, emit, pvg)

#cb.Text("d", "dd", "ddd")

# ------------------------------------------------------------------------
# Parse table.
#
# Specify state machine state, token to see for action or class to see for
# action, function to execute when match encountered, the new parser
# state when match encountered, continuation flag for reduce. (will
# reduce until cont flag == 0) See reduce example for key->val.
#
# Alternatives can be specified with multiple lines for the same state.
# New parser state field overrides state set by function. (set to IGNORE)
#
# Parser ignores unmatched entries.
#    (Bad for languages, good for error free parsing like text parsing)
#
# Parser starts in INIT. Parser skips IGNORE. (in those cases, usually
# the function sets the new state)
#
# Use textual context for development, numeric for production
#
# This table specifies a grammar for text processing, similar to Pango
#
#     -- State -- StateClass -- Token -- TokenClass -- Function -- newState -- cont. flag

parser.parsetable = [
    [ None,    STATEFMT,     pl("span"),     None,   cb.Span,       parser.SPAN, 0 ],
    [ None,    STATEFMT,     pl("bold"),     None,   cb.Bold,    parser.BOLD, 0 ],
    [ None,    STATEFMT,     pl("it"),       None,   cb.Italic,  parser.ITALIC, 0 ],
    [ None,    STATEFMT,     pl("itbold"),   None,   cb.ItBold,     parser.ITBOLD, 0 ],
    [ None,    STATEFMT,     pl("ul"),       None,   cb.Underline,  parser.UL, 0 ],
    [ None,    STATEFMT,     pl("dul"),      None,   cb.Dunderline, parser.DUL, 0 ],
    [ None,    STATEFMT,     pl("red"),      None,   cb.Red,        parser.RED, 0 ],
    [ None,    STATEFMT,     pl("bgred"),    None,   cb.Bgred,      parser.BGRED, 0 ],
    [ None,    STATEFMT,     pl("blue"),     None,   cb.Blue,       parser.BLUE, 0 ],
    [ None,    STATEFMT,     pl("bgblue"),   None,   cb.Bgblue,     parser.BGBLUE, 0 ],
    [ None,    STATEFMT,     pl("green"),    None,   cb.Green,      parser.GREEN, 0 ],
    [ None,    STATEFMT,     pl("bggreen"), None,    cb.Bggreen,    parser.BGGREEN, 0 ],
    [ None,    STATEFMT,     pl("strike"),   None,   cb.Strike,     parser.STRIKE, 0 ],
    [ None,    STATEFMT,     pl("large"),    None,   cb.Large,      parser.LARGE, 0 ],
    [ None,    STATEFMT,     pl("xlarge"),   None,   cb.Xlarge,     parser.XLARGE, 0 ],
    [ None,    STATEFMT,     pl("xxlarge"), None,    cb.Xxlarge,    parser.XXLARGE, 0 ],
    [ None,    STATEFMT,     pl("small"),    None,   cb.Small,      parser.SMALL, 0 ],
    [ None,    STATEFMT,     pl("xsmall"),    None,  cb.Xsmall,     parser.XSMALL, 0 ],
    [ None,    STATEFMT,     pl("cent"),     None,   cb.Center,     parser.CENT, 0 ],
    [ None,    STATEFMT,     pl("right"),    None,   cb.Right,      parser.RIGHT, 0 ],
    [ None,    STATEFMT,     pl("wrap"),     None,   cb.Wrap,       parser.WRAP, 0 ],
    [ None,    STATEFMT,     pl("link"),     None,   cb.Link,       parser.LINK, 0 ],
    [ None,    STATEFMT,     pl("image"),     None,  cb.Image,      parser.IMAGE, 0 ],
    [ None,    STATEFMT,     pl("sub"),     None,    cb.Sub,        parser.SUB, 0 ],
    [ None,    STATEFMT,     pl("sup"),     None,    cb.Sup,        parser.SUP, 0 ],
    [ None,    STATEFMT,     pl("fill"),     None,   cb.Fill,       parser.FILL, 0 ],
    [ None,    STATEFMT,     pl("fixed"),    None,   cb.Fixed,      parser.FIXED, 0 ],
    [ None,    STATEFMT,     pl("indent"),   None,   cb.Indent,     parser.INDENT, 0 ],
    [ None,    STATEFMT,     pl("margin"),   None,   cb.Margin,     parser.MARGIN, 0 ],
    [ None,    STATEFMT,     pl("lmargin"),   None,  cb.Lmargin,    parser.LMARGIN, 0 ],
    [ None,    STATEFMT,     pl("hid"),      None,   cb.Hid,        parser.HID, 0 ],
    [ None,    STATEFMT,     pl("ncol"),     None,   cb.Ncol,       parser.NCOL, 0 ],
    [ None,    STATEFMT,     pl("ncol2"),     None,  cb.Ncol2,       parser.NCOL, 0 ],
    [ None,    STATEFMT,     pl("nbgcol"),   None,   cb.Nbgcol,     parser.NBGCOL, 0 ],

    [ parser.INIT,   None,   None,           TXTCLASS, cb.Text,       parser.IGNORE, 0 ],

    [ None,   STATEFMT,   pl("tab"),      None,   cb.Tab,      parser.IGNORE, 0 ],
    [ None,   STATEFMT,   pl("tab2"),     None,   cb.Tab,      parser.IGNORE, 0 ],
    [ None,   STATEFMT,   pl("bsnl"),     None,   None,      parser.IGNORE, 0 ],

    [ parser.SPAN,   None,   pl("ident"),    None,     None,     parser.KEY, 1 ],
    [ parser.KEYVAL, None,   pl("ident"),    None,     cb.Keyval,   parser.KEY, 1 ],
    [ parser.KEY,    None,   pl("eq"),       None,     None,     parser.VAL, 1 ],
    [ parser.VAL,    None,   pl("ident"),    None,     cb.Keyval,   parser.IGNORE, 0 ],
    [ parser.VAL,    None,   pl("str"),      None,     cb.Keyval,   parser.IGNORE, 0 ],
    [ parser.VAL,    None,   pl("str2"),     None,     cb.Keyval,   parser.IGNORE, 0 ],
    [ parser.VAL,    None,   pl("str4"),     None,     cb.Keyval,   parser.IGNORE, 0 ],
    [ parser.SPAN,   None,   pl("gt"),       None,     cb.Span2,    parser.SPANTXT, 0 ],
    [ parser.SPAN,   None,   pl("sp"),       None,     None,     parser.IGNORE, 0 ],

    [ parser.IMAGE,   None,   pl("ident"),    None,     None,     parser.KEY, 1 ],
    [ parser.IMAGE,   None,   pl("gt"),       None,     cb.Image2,   parser.IGNORE, 0 ],
    [ parser.IMAGE,   None,   pl("sp"),       None,     None,     parser.IGNORE, 0 ],

    [ parser.LINK,   None,   pl("ident"),    None,     None,     parser.KEY, 1 ],
    [ parser.LINK,   None,   pl("gt"),       None,     cb.Link2,    parser.SPANTXT, 0 ],
    [ parser.LINK,   None,   pl("sp"),       None,     None,     parser.IGNORE, 0 ],

    [ parser.SPANTXT, None,  pl("espan"),    None,     cb.eSpan,      parser.INIT, 0 ],
    [ parser.SPANTXT, None,  pl("elink"),    None,     cb.eLink,      parser.IGNORE, 0 ],

    [ parser.SPANTXT, None,  pl("bold"),     None,     cb.Bold,   parser.BOLD, 0 ],
    [ parser.SPANTXT, None,  pl("it"),       None,     cb.Italic, parser.ITALIC, 0 ],
    [ parser.SPANTXT, None, None,       TXTCLASS,      cb.Text,   parser.IGNORE, 0 ],

    [ parser.ITALIC,   None, None,       TXTCLASS,     cb.Text,       parser.IGNORE, 0 ],
    [ parser.ITALIC,   None,  pl("eit"),      None,    cb.eItalic,    parser.IGNORE, 0 ],

    [ parser.BOLD,     None, None,       TXTCLASS,     cb.Text,   parser.IGNORE, 0 ],
    [ parser.BOLD,     None,  pl("ebold"),    None,    cb.eBold,  parser.IGNORE, 0 ],

    [ parser.ITBOLD,   None,   None,       TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.ITBOLD,   None,   pl("eitbold"), None,    cb.eItBold,    parser.IGNORE, 0 ],

    [ parser.UL,       None,   None,       TXTCLASS,   cb.Text,         parser.IGNORE, 0 ],
    [ parser.UL,       None,  pl("eul"),       None,   cb.eUnderline,   parser.IGNORE, 0 ],

    [ parser.DUL,       None,   None,       TXTCLASS,   cb.Text,   parser.IGNORE, 0 ],
    [ parser.DUL,       None,  pl("edul"),       None,  cb.eDunderline,   parser.IGNORE, 0 ],

    [ parser.RED,      None,   None,       TXTCLASS,    cb.Text,        parser.IGNORE, 0 ],
    [ parser.RED,      None,   pl("ered"),     None,    cb.eRed,        parser.IGNORE, 0 ],

    [ parser.BGRED,    None,   None,       TXTCLASS,    cb.Text,        parser.IGNORE, 0 ],
    [ parser.BGRED,    None,   pl("ebgred"),     None,  cb.eBgred,      parser.IGNORE, 0 ],

    [ parser.BLUE,     None,    None,       TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.BLUE,     None,   pl("eblue"),     None,   cb.eBlue,       parser.IGNORE, 0 ],

    [ parser.BGBLUE,     None,    None,       TXTCLASS,  cb.Text,       parser.IGNORE, 0 ],
    [ parser.BGBLUE,     None,  pl("ebgblue"),    None,  cb.eBgblue,       parser.IGNORE, 0 ],

    [ parser.GREEN,    None,    None,       TXTCLASS,   cb.Text,      parser.IGNORE, 0 ],
    [ parser.GREEN,    None,   pl("egreen"),     None,  cb.eGreen,    parser.IGNORE, 0 ],

    [ parser.BGGREEN,    None,    None,       TXTCLASS,  cb.Text,      parser.IGNORE, 0 ],
    [ parser.BGGREEN,    None,   pl("ebggreen"),     None,    cb.eBggreen,    parser.IGNORE, 0 ],

    [ parser.STRIKE,   None,   None,       TXTCLASS,   cb.Text,      parser.IGNORE, 0 ],
    [ parser.STRIKE,   None,   pl("estrike"), None,       cb.eStrike,   parser.IGNORE, 0 ],

    [ parser.LARGE,    None,   None,       TXTCLASS,   cb.Text,      parser.IGNORE, 0 ],
    [ parser.LARGE,    None,   pl("elarge"),    None,      cb.eLarge,    parser.IGNORE, 0 ],

    [ parser.XLARGE,    None,   None,       TXTCLASS,  cb.Text,      parser.IGNORE, 0 ],
    [ parser.XLARGE,    None,   pl("exlarge"),    None,    cb.eXlarge,    parser.IGNORE, 0 ],

    [ parser.XXLARGE,    None,   None,       TXTCLASS, cb.Text,      parser.IGNORE, 0 ],
    [ parser.XXLARGE,    None,   pl("exxlarge"),    None,  cb.eXxlarge,    parser.IGNORE, 0 ],

    [ parser.SMALL,     None,   None,       TXTCLASS,  cb.Text,      parser.IGNORE, 0 ],
    [ parser.SMALL,     None,  pl("esmall"),    None,     cb.eSmall,    parser.IGNORE, 0 ],

    [ parser.XSMALL,     None,   None,       TXTCLASS,  cb.Text,      parser.IGNORE, 0 ],
    [ parser.XSMALL,     None,  pl("exsmall"),    None,     cb.eXsmall,    parser.IGNORE, 0 ],

    [ parser.CENT,     None,   None,       TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.CENT,     None,  pl("ecent"),    None,        cb.eCenter,     parser.IGNORE, 0 ],

    [ parser.RIGHT,     None,   None,      TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.RIGHT,     None,  pl("eright"),    None,      cb.eRight,     parser.IGNORE, 0 ],

    [ parser.WRAP,     None,   None,       TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.WRAP,     None,  pl("ewrap"),    None,        cb.eWrap,      parser.IGNORE, 0 ],

    [ parser.SUB,     None,   None,       TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.SUB,     None,  pl("esub"),      None,        cb.eSub,      parser.IGNORE, 0 ],

    [ parser.SUP,     None,   None,       TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.SUP,     None,  pl("esup"),      None,        cb.eSup,      parser.IGNORE, 0 ],

    [ parser.FILL,     None,   None,       TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.FILL,     None,  pl("efill"),    None,        cb.eFill,      parser.IGNORE, 0 ],

    [ parser.FIXED,     None,   None,       TXTCLASS,   cb.Text,       parser.IGNORE, 0 ],
    [ parser.FIXED,     None,  pl("efixed"),    None,     cb.eFixed,      parser.IGNORE, 0 ],

    [ parser.INDENT,     None,   None,       TXTCLASS, cb.Text,       parser.IGNORE, 0 ],
    [ parser.INDENT,     None,  pl("eindent"),    None,    cb.eIndent,  parser.IGNORE, 0 ],

    [ parser.MARGIN,     None,   None,       TXTCLASS, cb.Text,       parser.IGNORE, 0 ],
    [ parser.MARGIN,     None,  pl("emargin"),    None,    cb.eMargin,  parser.IGNORE, 0 ],

    [ parser.LMARGIN,     None,   None,       TXTCLASS, cb.Text,       parser.IGNORE, 0 ],
    [ parser.LMARGIN,     None,  pl("elmargin"),    None,   cb.eLmargin,  parser.IGNORE, 0 ],

    [ parser.HID,     None,   None,       TXTCLASS,    None,     parser.IGNORE, 0 ],
    [ parser.HID,     None,  pl("ehid"),    None,          cb.eHid,     parser.IGNORE, 0 ],

    [ parser.NCOL,     None,   None,     TXTCLASS,     cb.Text,      parser.IGNORE, 0 ],
    [ parser.NCOL,     None,  pl("encol"),    None,        cb.eNcol,    parser.IGNORE, 0 ],

    [ parser.NBGCOL,     None,   None,     TXTCLASS,     cb.Text,      parser.IGNORE, 0 ],
    [ parser.NBGCOL,     None,  pl("enbgcol"),    None,      cb.eNbgcol,    parser.IGNORE, 0 ],
    ]

# Check parse table: (obsolete: now it is self checking)
'''
for aa in parser.parsetable:
    if aa[2]:
        found = 0
        for bb in parser.tokdef:
            if aa[2] == bb[1]:
                found = True
        if not found :
            print ("Parse table contains unkown definition '" + aa[2] + "'")
            sys.exit(1)

'''
def main():

    Gtk.main()
    return 0

# ------------------------------------------------------------------------

def bslink():

    if lstack.stacklen() == 1:
        return

    lstack.pop()
    strx = lstack.last()

    #print ("backspace linking to:", strx)

    if strx == None or strx == "":
        return

    mainview.showcur(True)
    showfile(strx)

def link(strx):

    if strx == None or strx == "":
        return

    if not isfile(strx):
        mainview.showcur(False)
        message_dialog("Missing or broken link",
            "Cannot find file '%s'" % strx );
        return
    #print ("linking to:", strx)
    showfile(strx)

# ------------------------------------------------------------------------

def     message_dialog(title, strx):

    dialog = Gtk.MessageDialog(mainview,
            Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT,
            Gtk.MESSAGE_INFO, Gtk.BUTTONS_OK, strx)
    dialog.set_title(title);
    dialog.run()
    dialog.destroy()

# ------------------------------------------------------------------------

def showfile(strx):

    global buf, xstack, mainview, pvg, ts

    got_clock =  time.clock()

    if pvg.verbose:
        print ("Showing file:", strx)

    try:
        fh = open(strx)
    except:
        strerr = "File:  '" + strx + "'  must be an existing and readble file. "
        print (strerr)
        mainview.add_text(strerr)
        return
    try:
        buf = fh.read();
    except:
        strerr2 =  "Cannot read file '" + strx + "'"
        print (strerr2)
        mainview.add_text(strerr2)
        fh.close()
        return
    fh.close()

    if pvg.show_timing:
        print  ("loader:", time.clock() - got_clock)

    if pvg.pgdebug > 5: print (buf)

    lstack.push(strx)

    mainview.clear(pvg.flag)
    ts.clear()

    xstack = stack.Stack()
    lexer.Lexer(buf, xstack, parser.tokens)

    if pvg.show_timing:
        print  ("lexer:", time.clock() - got_clock)

    if pvg.show_lexer:  # To show what the lexer did
        xstack.dump()

    parser.Parse(buf, xstack, pvg)
    cb.flush()
    mainview.showcur(False)

    if pvg.show_timing:
        print  ("parser:", time.clock() - got_clock)

    # Output results
    if pvg.emit:
        show_emit()

def help():
    myname = os.path.basename(sys.argv[0])
    print()
    print (myname + ":", "Version 0.95 - Utility for displaying a pango file.")
    print ()
    print ("Usage: " + myname + " [options] filename")
    print ()
    print ("Options are:")
    print ("            -d level  - Debug level (1-10)")
    print ("            -c file   - Contents file for left pane")
    print ("            -a pos    - Set pane position (pixels)")
    print ("            -e        - Emit parse string")
    print ("            -v        - Verbose")
    print ("            -f        - Full screen")
    print ("            -s        - Show parser states"    )
    print ("            -o        - Cover all windows (Full screen)")
    print ("            -t        - Show timing")
    print ("            -x        - Show lexer output")
    print ("            -p        - Show parser messages")
    print ("            -h        - Help")
    print ()

# ------------------------------------------------------------------------

def mainfunc():

    import getopt

    opts = []; args = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:c:a:hvxftopes")
    except getopt.GetoptError as err:
        print ("Invalid option(s) on command line:", err)
        sys.exit(1)

    #print ("opts", opts, "args", args)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pvg.pgdebug = int(aa[1])
            except:
                pvg.pgdebug = 0

        if aa[0] == "-c":
            pvg.second = aa[1]
            #print (pvg.second)

        if aa[0] == "-a":
            try:
                pvg.pane_pos = int(aa[1])
            except:
                print ("Pane position must be a number")

            print (pvg.pane_pos)

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-v": pvg.verbose = True
        if aa[0] == "-x": pvg.show_lexer = True
        if aa[0] == "-f": pvg.full_screen = True
        if aa[0] == "-o": pvg.xfull_screen = True
        if aa[0] == "-t": pvg.show_timing = True
        if aa[0] == "-e": pvg.emit = True
        if aa[0] == "-p": pvg.show_parse  = True
        if aa[0] == "-s": pvg.show_state  = True

    try:
        strx = args[0]
    except:
        help(); exit(1)

    global lstack
    lstack = stack.Stack()

    fullpath = os.path.abspath(strx);
    pvg.docroot = os.path.dirname(fullpath)

    if pvg.xfull_screen:
        mainview.fullscreen()
    elif pvg.full_screen:
        mainview.set_fullscreen()

    mainview.callback = link
    mainview.bscallback = bslink

    if pvg.second != "":
        if pvg.pane_pos >= 0:
            mainview.set_pane_position(pvg.pane_pos)
        else:
            mainview.set_pane_position(250)
        pvg.flag = True
        showfile(pvg.second)

    pvg.flag = False
    showfile(strx)

    main()

if __name__ == "__main__":
    mainfunc()

# EOF
