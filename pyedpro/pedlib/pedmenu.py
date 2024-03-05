#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import sys
import gi

import gettext
gettext.bindtextdomain('pyedpro', './locale/')
gettext.textdomain('pyedpro')

_ = gettext.gettext

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject

(
  COLOR_RED,
  COLOR_GREEN,
  COLOR_BLUE
) = list(range(3))

(
  SHAPE_SQUARE,
  SHAPE_RECTANGLE,
  SHAPE_OVAL,
) = list(range(3))

mained = None

# ------------------------------------------------------------------------
# Callback for rigth click menu

def rclick_action(self, arg):

    print ("rclick_action local", "'" + arg.name + "'")

    if arg.name == "<pydoc>/New":
        mained. newfile()

    if arg.name == "<pydoc>/Open":
        mained.open()

    if arg.name == "<pydoc>/Save":
        mained.save()

    if arg.name == "<pydoc>/SaveAs":
        mained.save(True )

    if arg.name == "<pydoc>/Copy":
        mained.copy( )

    if arg.name == "<pydoc>/Cut":
        mained.cut()

    if arg.name == "<pydoc>/Paste":
        mained.paste()

    if arg.name == "<pydoc>/Read":
        mained.tts()

def rclick_quit(self, arg):
    print(__name__, arg.name)
    mained.activate_exit()

rclick_menu = (
	        ( _("_New \t"),           "<control>N",    rclick_action, 1, None ),
            ( "",               None,               None, 2, "<Separator>" ),
            ( _("_Rescan\t\t"),       "Right CTRL+R",          rclick_action, 25, None ),
            ( _("_Find\t"),       "CTRL+F",          rclick_action, 26, None ),
            ( _("Check Syntax"),     "Alt-Y",        rclick_action, 27, None ),
            ( "",               None,               None, 2, "<Separator>" ),
            ( _("_Open  \t\t"),          "<control>O",    rclick_action, 3, None ),
            ( _("_Save   \t\t"),          "<control>S",    rclick_action, 4, None ),
            ( _("Save_As \t\t"),        None,            rclick_action, 5, None ),
            ( _("Toggle _RO"),     None,            rclick_action, 11, None ),
            ( "",               None,               None, 6, "<Separator>" ),
            ( _("_Copy \t"),          "<control>C",    rclick_action, 7, None ),
            ( _("C_ut  \t"),           "<control>X",    rclick_action, 8, None ),
            ( _("_Paste \t\t"),         "<control>V",    rclick_action, 9, None ),
            ( "",               None,               None, 10, "<Separator>" ),
            ( _("Terminal Here"), "Right CTRL+T",   rclick_action, 14, None ),
            ( "",               None,               None, 10, "<Separator>" ),
            ( _("File Manager"), "Right CTRL+F",        rclick_action, 24, None ),
            ( _("Exec current"),  None,             rclick_action, 17, None ),
            ( _("Libre Office"), "Right CTRL+L", rclick_action, 18, None ),
            ( _("NEW pyedpro"),   None,     rclick_action, 15, None ),
            ( _("Filter to M4"), "<control><shift>R", rclick_action, 19, None ),
            ( _("To Markdown"), None,        rclick_action, 20, None ),
            ( _("In Browser"), None,           rclick_action, 21, None ),
            ( _("As HTML String"), None,       rclick_action, 23, None ),
            ( _("As HTML File"), None,         rclick_action, 22, None ),
            ( "",               None,               None, 12, "<Separator>" ),
            ( _("Read Selection"), None,            rclick_action, 16, None ),
            ( "",               None,               None, 12, "<Separator>" ),
            ( _("E_xit\t\t"),          "<alt>X",        rclick_quit, 13, None ),
            )

rclick_menu2 = (
            ( _("Terminal Here"),  None,            rclick_action, 14, None ),
            ( _("Exec current"),  None,             rclick_action, 17, None ),
            )

def create_action_group(self):
    # GtkActionEntry
    if sys.version_info[0] < 3:
        verx = "_Help"
    else:
        verx = "_Help"

    entries = (
      ( "FileMenu", None, "_File" ),                # name, stock id, label
      ( "EditMenu", None, "_Edit" ),
      ( "PreferencesMenu", None, "Settings" ),
      ( "NavMenu", None, "Navigation" ),
      ( "MacrosMenu", None, "_Macros" ),
      ( "ColorMenu", None, "_Color"  ),
      ( "ShapeMenu", None, "Shape" ),
      ( "WinMenu", None, "Windows" ),
      ( "HelpMenu", None, verx ),

      # -------------------------------------------------------------------

      ( "New", Gtk.STOCK_NEW,                       # name, stock id
        "_New", "<control>N",                       # label, accelerator
        "Create a new file",                        # tooltip
        self.activate_action ),

      ( "Open", Gtk.STOCK_OPEN,
        "_Open", "<control>O",
        "Open a file",
        self.activate_action ),

      ( "Close", Gtk.STOCK_CLEAR,
        "_Close","<control>W",
        "Close current buffer",
        self.activate_action ),

      ( "Close All", Gtk.STOCK_CLEAR,
        "Close All","<control><shift>W",
        "Close all buffers",
        self.activate_action ),

      ( "Save", Gtk.STOCK_SAVE,
        "_Save","<control>S",
        "Save current file",
        self.activate_action ),

      ( "SaveAs", Gtk.STOCK_SAVE_AS,
        "Save _As...", "<control><shift>S",
        "Save to a file",
        self.activate_action ),

      ( "Save Session", Gtk.STOCK_SAVE,
        "Save _Session ...", "",
        "Save session to a file",
        self.activate_action ),

      ( "Load Session", Gtk.STOCK_OPEN,
        "Load _Session ...", "<control><shift>O",
        "Load session from a file",
        self.activate_action ),

      ( "Start Terminal", Gtk.STOCK_FILE,
        "Start _Terminal ...", "",
        "Star terminal in current dir",
        self.activate_action ),

      ( "Recent", Gtk.STOCK_OPEN,
        "_Recent  ", "",
        "Load recent file list",
         self.activate_action ),

      ( "Recent Files", Gtk.STOCK_OPEN,
        "Recent Files ", "",
        "Load recent file",
         self.open_recent ),

      ( "Sessions", Gtk.STOCK_OPEN,
        "_Recent Session ", "",
        "Load recent session list",
         self.activate_action ),

      ( "Recent Sessions", Gtk.STOCK_OPEN,
        "Recent _Sessions", "",
        "Load recent sessions ",
         self.open_recent_sess ),

     ( "Quit", Gtk.STOCK_QUIT,
        "_Quit  (No Save)", "<control>Q",
        "Quit program, abandon files",
         self.activate_quit ),

      ( "Exit", Gtk.STOCK_CLOSE,
        "_Exit", "<alt>X",
        "Exit program, save files",
         self.activate_exit ),

      ( "Cut", Gtk.STOCK_CUT,
        "Cu_t   \t\tCtrl-X", "",
        "Cut selection to clipboard",
         self.activate_action ),

       ( "Copy", Gtk.STOCK_COPY,
        "_Copy   \t\tCtrl-C", "",
        "Copy selection to clipboard",
         self.activate_action ),

      ( "Paste", Gtk.STOCK_PASTE,
        "_Paste  \t\tCtrl-V", "",
        "Paste clipboard into text",
         self.activate_action ),

      ( "Findit", Gtk.STOCK_PASTE,
        "_Find  \tCtrl-F", "",
        "Find text",
         self.activate_action ),

      ( "Undo", Gtk.STOCK_UNDO,
        "_Undo  \t\tCtrl-Z", "",
        "Undo last Edit",
         self.activate_action ),

       ( "TogStrip", Gtk.STOCK_UNDO,
        "_Toggle Line No. Strip  ", "",
        "Toggle line number stip",
         self.activate_action ),

      ( "Redo", Gtk.STOCK_REDO,
        "_Redo  \t\tCtrl-Y", "",
        "Redo last Undo",
         self.activate_action ),

      ( "Discard Undo", Gtk.STOCK_QUIT,
        "Discard Undo / Redo", "",
        "Discard all undo / redo information",
         self.activate_action ),

      ( "Spell", Gtk.STOCK_SPELL_CHECK,
        "_Spell (code) \tF9", "",
        "Spell Buffer (code mode)",
         self.activate_action ),

      ( "Spell2", Gtk.STOCK_SPELL_CHECK,
        "S_pell (text) \tShift-F9", "",
        "Spell Buffer (text mode)",
         self.activate_action ),

      ( "MakeRO", Gtk.STOCK_NO,
        "Make _Buffs Read Only \t", "",
        "Make All ReadOnly",
         self.activate_action ),

       ( "MakeRW", Gtk.STOCK_YES,
        "Make Buffs Read _Write \t", "",
        "Make All Read_Write",
         self.activate_action ),

       ( "ColorBar", Gtk.STOCK_CLEAR,
        "Set TEAL on tab Window \t", "",
        "Color for visual distinction",
         self.activate_action ),

       ( "RedBar", Gtk.STOCK_CLEAR,
        "Set RED on tab Window \t", "",
        "Color for visual distinction",
         self.activate_action ),

       ( "unColorBar", Gtk.STOCK_YES,
        "Reset Color on tab Window \t", "",
        "Color for visual distinction",
         self.activate_action ),

       ( "StopDiff", Gtk.STOCK_HOME,
        "Stop diffing \t", "",
        "Stop all diffs",
         self.activate_action ),

      ( "Settings", Gtk.STOCK_REDO,
        "Settings", "",
        "Change program settings",
         self.activate_action ),

      ( "Goto", Gtk.STOCK_INDEX,
        "Goto Line\t\tAlt-G", "",
        "Goto line in file",
         self.activate_action ),

      ( "Find", Gtk.STOCK_FIND,
        "Find in File\tCtrl-F", "",
        "Find line in file",
         self.activate_action ),

      ( "Next", Gtk.STOCK_MEDIA_NEXT,
        "Next Match\tAlt-N F6", "",
        "Goto Next match in file",
         self.activate_action ),

        ( "Prev", Gtk.STOCK_MEDIA_PREVIOUS,
        "Prev Match\t\tAlt-P F5", "",
        "Goto previous match in file",
         self.activate_action ),

        ( "Begin", Gtk.STOCK_MEDIA_PLAY,
        "Begin of doc\tCtrl-Home", "",
        "Goto the beginning of document",
         self.activate_action ),

        ( "End", Gtk.STOCK_MEDIA_PAUSE,
        "End of doc\t\tCtrl-End", "",
        "Goto the end of document",
         self.activate_action ),

      ( "Record", Gtk.STOCK_MEDIA_RECORD,
        "Start / Stop Record\t\tF7", "",
        "Start / Stop Recording macro",
         self.activate_action ),

      ( "Play", Gtk.STOCK_MEDIA_PLAY,
        "Play Macro       \t\t\tF8", "",
        "Play macro",
         self.activate_action ),

      ( "Animate", Gtk.STOCK_ADD,
        "_Animate macro\t\tShift-F8", None,
        "Play macro with animation effect",
         self.activate_action ),

      ( "Savemacro", Gtk.STOCK_SAVE,
        "Save macro", None,
        "Save macro to file",
         self.activate_action ),

      ( "Loadmacro", Gtk.STOCK_APPLY,
        "Load macro", None,
        "Load macro from file",
         self.activate_action ),

      ( "Colors", Gtk.STOCK_COLOR_PICKER,
        "Set Colors", None,
        "Set Editor window colors",
         self.activate_action ),

      ( "Fonts", Gtk.STOCK_SELECT_FONT,
        "Set Font", None,
        "Set Editor Window Font",
         self.activate_action ),

      ( "NextWin", Gtk.STOCK_GO_FORWARD,
        "Next Window\t\tAlt-PgUp", None,
        "Switch to next window",
         self.activate_action ),

      ( "PrevWin", Gtk.STOCK_GO_BACK,
        "Prev. Window\t\tAlt-PgDn", None,
        "Switch to next window",
         self.activate_action ),

      ( "SaveAll", Gtk.STOCK_SAVE_AS,
        "Save All\t(Alt-A)", None,
        "Save all Buffers",
         self.activate_action ),

      ( "ShowLog", Gtk.STOCK_DIALOG_INFO,
        "Show Log Window", None,
        "Show log window",
         self.activate_action ),

      ( "About", "demo-gtk-logo",
        "_About", "",
        "About",
        self.activate_about ),

      ( "KeyHelp", Gtk.STOCK_INFO,
        "_Sys Help          \tShift-F2", "",
        "Show keyboard help",
        self.activate_khelp ),

      ( "KeyDoc", Gtk.STOCK_INFO,
        "_Keyhelp in Doc", "",
        "Show keyboard help in a new doc",
        self.activate_action ),

      ( "DevHelp", Gtk.STOCK_INFO,
        "_Developer Help\tF2", "",
        "Show developer help",
        self.activate_dhelp ),

        ( "Help", Gtk.STOCK_HELP,
         "_Help          \t\t\tF1", "",
        "Show Help",
        self.activate_action ),

      ( "Logo", "demo-gtk-logo",
         None, None,
        "GTK+",
        self.activate_action ),
    );

    # GtkToggleActionEntry
    toggle_entries = (
      ( "Bold", Gtk.STOCK_BOLD,                    # name, stock id
         "_Bold", "<control>B",                    # label, accelerator
        "Bold",                                    # tooltip
        self.activate_action,
        True ),                                    # is_active
    )

    # GtkRadioActionEntry
    color_entries = (
      ( "Red", None,                               # name, stock id
        "_Red", "<control><shift>R",               # label, accelerator
        "Blood", COLOR_RED ),                      # tooltip, value
      ( "Green", None,                             # name, stock id
        "_Green", "<control><shift>G",             # label, accelerator
        "Grass", COLOR_GREEN ),                    # tooltip, value
      ( "Blue", None,                              # name, stock id
        "_Blue", "<control><shift>B",              # label, accelerator
        "Sky", COLOR_BLUE ),                       # tooltip, value
    )

    # GtkRadioActionEntry
    shape_entries = (
      ( "Square", None,                            # name, stock id
        "_Square", "<control><shift>S",            # label, accelerator
        "Square",  SHAPE_SQUARE ),                 # tooltip, value
      ( "Rectangle", None,                         # name, stock id
        "_Rectangle", "<control><shift>R",         # label, accelerator
        "Rectangle", SHAPE_RECTANGLE ),            # tooltip, value
      ( "Oval", None,                              # name, stock id
        "_Oval", "<control><shift>O",              # label, accelerator
        "Egg", SHAPE_OVAL ),                       # tooltip, value
    )

    # Create the menubar and toolbar
    action_group = Gtk.ActionGroup("AppWindowActions")
    action_group.add_actions(entries)
    #action_group.add_toggle_actions(toggle_entries)
    #action_group.add_radio_actions(color_entries, COLOR_RED, self.activate_radio_action)
    #action_group.add_radio_actions(shape_entries, SHAPE_OVAL, self.activate_radio_action)

    return action_group


# EOF