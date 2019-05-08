#   PyEdPro README

## Python editor.

   Welcome to PyEdPro. This is modern multi-platform editor. Simple, powerful,
configurable, extendable. Goodies like macro recording / playback, spell check,
column select, multiple clipboards, unlimited undo ... makes it an editor
that I use every day.

 This project is a successor of pyedit, after porting it to GTK3. PyEdPro
 will run anywhere PyGTK (GObject) can run.

  Working and tested platforms currently are:

        Win 7 .. Win 10 ...
        Centos 6 .. 7 Ubuntu 14 ... 16
        Msys, Msys2, Mingw, Raspberry PI ...

  I mainly run it in MSYS2, Ubuntu, Fedora, Windows 10, and the Raspberry-Pi.
It behaves consistently on all these platforms. If you want an editor
that works the same way in all your workspaces, PyEdPro is the one.

   PyEdPro.py has macro recording/play, search/replace, one click function navigation,
comment/string spell check, auto backup, persistent undo/redo, auto complete,
auto correct, syntax check, spell suggestion ... and a lot more.

   PyEdPro is fast, it is extendable, as python lends itself to easy extending. The
editor has a table driven key mapping. One can easily edit the key map in
keyhand.py, and the key actions in acthand.py

  If you encounter blank screen after start, cairo is not installed. The terminal interface
will complain, but if you start from the GUI, you can see the message in the
log window. (Menu->Windows->Show_Log) To install cairo type 'sudo apt install cairo'.

 The default key map resembles gedit / wed / etp / brief. Full ASCII;
 Any fixed font can be configured.

  See KEYS file for the list of keyboard shortcuts or press F3 in the
editor or look at the file in pyedlib/KEYS.

  On initial start, PyEdPro shows a left pane and a top pane. The left pane
is for function summary and the top pane is for double view of the same file.
(to see the caller and the callee) These panes can be hidden with the mouse by
dragging on their handle, or by the key combination Alt-Q (Shift-Alt-Q for
the left pane)

  PyEdPro remembers a lot about the editing session. Loaded files, cursor positions,
fonts, font size, colors, search strings, goto numbers, undo / redo info,
window positions ... and more.
 This is all stored in the directory ~/.PyEdPro. You may safely delete that
directory to start PyEdPro with no memory of what has been done.

  Starting PyEdPro with no command line arguments will put you back to the
previous session, exactly where you left off.

 The editor will work on all PyGobject platforms, and can open UNIX and Windows files
transparently. It will save the file as the current platform's native CRLF
convention dictates.

  Developer's note: in order to make PyEdPro multi platform, we save
the configuration info into a SQLite database in the ~/.PyEdPro directory.

     (~/ stands for the user's home directory)

 Contributors are welcome.

 ### PyEdPro Key Assignments

   This is a list of default key assignments for PyEdPro. The keys are assigned
in keyhand.py and the actions are implemented in acthand.py. Regular keys are
added to the buffer. To implement a new feature follow a particular key's
execution path, and replicate functionality. It is eazy to follow, as it is
table driven. (For the latest vestion of the table see: KEYS.TXT)

    Left Arrow                  -- Go left one char
    Right Arrow                 -- Go right one char
    Up Arrow                    -- Go up one line
    Down Arrow                  -- Go down one line
    PgUp                        -- Go up one page
    PgDn                        -- Go down one page
    Home                        -- Go to beginning of line
    End                         -- Go end of line

    [a-z]|[A-Z]|[0-9]           -- Insert character (key)
    !@#$%^&*()_ ...             -- Insert punctuation (key)

    Tab                         -- Insert 4 spaces up to % 4
    Shift-Tab                   -- Insert a real tab up to % 4
    Ctrl-A                      -- Select All text in buffer
    Ctrl-B                      -- Select word (till spaces)
    Ctrl-C                      -- Copy selection to Clipboard
    Ctrl-D                      -- Delete (trim) spaces from end of line
    Ctrl-E                      -- Capitalize (emphasize) word
    Ctrl-F                      -- Find in file or all buffers
    Ctrl-G                      -- Goto next match
    Shift-Ctrl-G                -- Goto previous match
    Ctrl-H                      -- Cursor left  (like in Emacs)
    Ctrl-I                      -- Insert count-up number
    Shift-Ctrl-I                -- Reset and insert count-up number
    Ctrl-J                      -- Down Arrow
    Ctrl-K                      -- Up Arrow
    Ctrl-L                      -- Right Arrow
    Ctrl-M                      -- Toggle auto correct
    Ctrl-N                      -- New File
    Ctrl-O                      -- Open file
    Ctrl-P                      -- Print (not implemented on all platforms)
    Ctrl-Q                      -- Quit program **
    Ctrl-R                      -- Reverse three words ***
    Ctrl-S                      -- Save current file
    Ctrl-T                      -- Transpose two words
    Ctrl-U                      -- Uppercase word
    Ctrl-V                      -- Paste from Clipboard
    Ctrl-W                      -- Close current file
    Ctrl-X                      -- Cut to Clipboard
    Ctrl-Y                      -- Redo last undo
    Ctrl-Z                      -- Undo last change

    Ctrl Up                     -- Go up 10 lines
    Ctrl Down                   -- Go down 10 lines
    Ctrl Left                   -- Go left one word
    Ctrl Right                  -- Go right one word
    Ctrl PgUp                   -- Go up one large page (2x)
    Ctrl PgDn                   -- Go down one large page (2x)
    Ctrl Home                   -- Go to beginning of file
    Ctrl End                    -- Go end of file
    Ctrl Space                  -- Enable / disable keyboard

    Ctrl 0                      -- Switch to clipboard 0 (OS Clipboard)
    Ctrl 1                      -- Switch to clipboard 1
      .
      .
    Ctrl 8                      -- Switch to clipboard 8
    Ctrl 9                      -- Switch to sum of all clipboards

    Alt Left                    -- Go to begin of the current word*
    Alt Right                   -- Go to end of the current word
    Alt Up                      -- Go to next buffer
    Alt Down                    -- Go to previous buffer
    Alt PgUp                    -- Go to next buffer
    Alt PgDn                    -- Go to previous buffer
    Alt Home                    -- Go to first buffer
    Alt End                     -- Go to last buffer

    Home Home                   -- Go to beginning of page (PgUp)
    3x Home                     -- Go to begin of file (Ctrl-Home)

    Alt-A                       -- Save All buffers
    Alt-B                       -- Show Buffers
    Alt-C                       -- Start column select
    Alt-D                       -- Delete current line
    Alt-E                       -- Show edit Menu
    Alt-F                       -- Show File Menu
    Alt-G                       -- Goto line dialog
    Alt-H                       -- Help Menu
    Alt-I                       -- Ignore (convert) tabs to spaces
    Alt-J                       -- Jump to next long line (80+)
    Alt-K                       -- Delete (kill) till end of line
    Alt-L                       -- Select current line
    Alt-M                       -- Macros menu
    Alt-N                       -- Next search result
    Alt-O                       -- Open file (Simplified Dialog)
    Alt-P                       -- Previous search result
    Alt-Q                       -- Hide top Pane
    Alt-R                       -- Redo
    Alt-S                       -- Search for text
    Alt-T                       -- Find / Replace (Taush)
    Alt-U                       -- Undo
    Alt-V                       -- Select Current Word (till delimiters)
    Alt-W                       -- Write (Save) Current buffer
    Alt-X                       -- Exit program
    Alt-Y                       -- Check Python syntax (compile buffer)
    Alt-Z                       -- Wrap long lines

    Alt-0                       -- Switch to Function pane (left)****

    Alt-1                       -- Switch to buffer 1
    Alt-2                       -- Switch to buffer 2
    Alt-3                       -- Switch to buffer 3
    Alt-4                       -- Switch to buffer 4
    Alt-5                       -- Switch to buffer 5
    Alt-6                       -- Switch to buffer 6
    Alt-7                       -- Switch to buffer 7
    Alt-8                       -- Switch to buffer 8
    Alt-9                       -- Switch to buffer 9

    Alt-F1                      --  Gnome - Menu
    Alt-F2                      --  Gnome - Run App
    Alt-F4                      --  Gnome - Exit program (Use Alt-X)
    Alt-F7                      --  Gnome - Move window
    Alt-F8                      --  Gnome - Re-size window
    Alt-F9                      --  Gnome - Minimize window
    Alt-F10                     --  Gnome - Full Screen window

    Ctrl-Alt-H                  --  Left Arrow
    Ctrl-Alt-J                  --  Toggle coloring
    Ctrl-Alt-K                  --  Toggle Hex View
    Ctrl-Alt-L                  --  Lowercase word

    F1                           -- Help
    F2                           -- Dev Help
    F3                           -- Key assignments Help
    F4                           -- Animate macro
    F5                           -- Previous Match
    F6                           -- Next Match
    F7                           -- Start / Stop Record
    F8                           -- Play Macro
    F9                           -- Toggle code spell check****
    Shift-F9                     -- Toggle full file (text) spell check
    F10                          -- Application's main - Menu
    shift F10                    -- Notebook tab menu (if enabled)
    F11                          -- Toggle full Screen
    F12                          -- Cursor Locator
    Shift-F12                    -- Reveal tabs and spaces and 80 column marker
    Ctrl-F12                     -- Reveal Hex view

Context dependent key assignments:

    Alt-X                       -- Exit dialog
    ESC                         -- Exit dialog (cancel)
    ENTER                       -- Exit dialog (accept)

 Find / Replace context:

    Alt-S                       -- Case Insensitive search
    Alt-R                       -- Regular expression search
    Alt-A                       -- All buffer search

 Find / Replace results context:

    Alt-S                       -- Change currently Selected
    Alt-O                       -- Change One (rescans buffer)
    Alt-A                       -- Change All
    Alt-Tab                     -- Navigate between search / main windows
    Arrow Up/Down               -- Next / Prev match
    ENTER                       -- Change selection

  Mouse actions:

    Left Click                  -- position caret (text cursor)
    Right Click                 -- Call up right click menu
    Right Click (on spell)      -- Call up spell correction list
    Click - Hold - Drag (L-R)   -- Select
    Click - Hold - Drag  (U-D)  -- Column Select
    Double Click                -- Select Word

Notes:

    *       Alt-Arrow   Goto begin / end of current word. Word delimited with
                        alpha_num + punctuation
    **      Ctrl-Q      Quit program, no save, but files are backed up in
                        (~/.pyedpro/data) '*.sav'
    ***     Ctrl-R      Reverse words around the middle. (a = b becomes b = a)
                        Useful for turining assignments.
    ****    F9          Only Comments and strings are checked, otherwise all
                        text is checked
    *****   Alt-0       Alt - 1 .. 9 brings back the focus to current buffer

  Any unrecognized key is inserted verbatim into the buffer, and a message is printed
on the controlling terminal. If no action is listed, that key is unassigned.

  As a matter of consistency, most dialogs can be dismissed with the Esc key or
the Alt-X key combination. The main window can be exited by Alt-X or standard exit
keys like Alt-F4;

The author,

      Peter Glen

Screen from a regular session, note the function list on the left:

![Screen Shot](image.png)

Screen from Ubuntu:

![Screen Shot](pyedpro_ubuntu.png)

License:    Open Source, FreeWare





