# py Common

## Common GUI routines (and classes) for python PyGobject (Gtk) development.

 Just a sampler of what is in there (pasted from code, in no particular order):

  * class CairoHelper():
  * class TextTable(Gtk.Table):
  * class TextRow(Gtk.HBox):
  * class RadioGroup(Gtk.Frame):
  * class Led(Gtk.DrawingArea):
  * class SeparatorMenuItem(Gtk.SeparatorMenuItem):
  * class Menu():
  * class MenuButt(Gtk.DrawingArea):
  * class Lights(Gtk.Frame):
  * class WideButt(Gtk.Button):
  * class ScrollListBox(Gtk.Frame):
  * class TextRow(Gtk.HBox):
  * class RadioGroup(Gtk.Frame):
  * class Led(Gtk.DrawingArea):
  * class Lights(Gtk.Frame):
  * class FrameTextView(Gtk.TextView):
  * class Label(Gtk.Label):
  * class Logo(Gtk.VBox):
  * class xSpacer(Gtk.HBox):
  * class ScrollListBox(Gtk.Frame):
  * class ListBox(Gtk.TreeView):

 ... and a lot more ...

 These classes act as a simplification of the PyGtk (PyGobject) classes.

 For instance the Label takes a constructor, and feeds the arguments as
 one would expect. Like this:

        def __init__(self, textm = "", widget = None, tooltip=None, font = None):

 The defaults are set to a reasonable value, and the named argument can be
set on one line. This makes the code look compact and maintainable.

 See descendent projects for examples. (pyedpro; pycal; pggui; ...)

 This code will be merged / moved to the pyvguicom python module.

Peter Glen

# EOF
