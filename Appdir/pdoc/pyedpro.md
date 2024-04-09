Module pyedpro
==============
! \mainpage

## Welcome to PyEdPro.

This is modern multi-platform editor. Simple, powerful,
configurable, extendable. Goodies like macro recording / playback, spell check,
column select, multiple clipboards, unlimited undo ... makes it an editor
that I use every day.

This is an open source text editor. Written in python. The motivation for
this project was to create a modern multi-platform editor. Simple,
powerful, configurable, extendable. To run this module without
installation put the supporting files in the 'pedlib'
subdirectory under the main file's direcory.

(like 'cp -a * to_target')

 This project is a successor of pyedit, after porting it to GTK3. PyEdPro
 will run anywhere PyGObject can run.

  Working and tested platforms currently are:

        Win 7 .. Win 10 ...
        Centos 6 .. 7 Ubuntu 14 ... 16 ...  20.x (should run on any linux )
        Windows (Native) plus MSYS2, Mingw,
        Raspberry PI 3, Raspberry PI 4, ...
        Mac ** Some functions are disabled - in particular async processing

  I mainly run it on Ubuntu, and in Win32 / MSYS2, some Fedora, Windows 10,
Windows 10 x64, and the Raspberry-Pi. It behaves consistently on all these
platforms.
  It is an absolute joy to edit in a different platform without the learning
curve of new keystrokes.  If you want an editor that works the same way in
all your workspaces, PyEdPro is the one.

Pyedpro functions near identical on Linux / Windows / Mac / Raspberry PI

 Pyedpro has:

            o  Macro recording/play,
            o  Search/replace,
            o  Functional navigation,
            o  Comment/string spell check,
            o  Full spell check, spell suggestion dialog
            o  Auto backup,
            o  Persistent undo/redo,  (undo beyond last save)
            o  Auto complete, auto correct,
            o
            o  ... and a lot more.

  PyeEdPro is fast, it is extendable. The editor has a table driven key mapping.
 One can easily edit the key map in keyhand.py, and the key actions
 in acthand.py The default key map resembles gedit / wed / etp / brief / Notepad

ASCII text editor, requires pyGtk. (PyGObject)

 See pygtk-dependencies for easy install of dependencies.
 See also the INSTALL file.

Functions
---------

    
`mainfunc()`
:   

    
`mainstart(name='', args='', oldpath='')`
:   Main Entry Point for the editor

    
`run_main(projname, strarr)`
:   

    
`terminate()`
:   Termination Handler

    
`tracer(frame, event, arg)`
:   

    
`xhelp()`
:   Offer Help

    
`xversion()`
:   Offer version number

Classes
-------

`MainPyed(projname, strarr)`
:   :Constructors:
    
    ::
    
        Application(**properties)
        new(application_id:str=None, flags:Gio.ApplicationFlags) -> Gtk.Application

    ### Ancestors (in MRO)

    * gi.repository.Gtk.Application
    * gi.overrides.Gio.Application
    * gi.repository.Gio.Application
    * gi.overrides.GObject.Object
    * gi.repository.GObject.Object
    * gi._gi.GObject
    * gi.repository.Gio.ActionGroup
    * gi.repository.Gio.ActionMap
    * gi.overrides.Gio.ActionMap
    * gi.repository.Gio.ActionMap
    * gobject.GInterface

    ### Methods

    `do_activate(self)`
    :   activate(self)

    `on_activate(self, instance)`
    :