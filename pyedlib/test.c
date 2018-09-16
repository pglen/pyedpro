                            PyEdit Key Assignments

This is a list of default key assignments for PyEdit. The keys are assigned
in keyhand.py and the actions are implemented in acthand.py.
Regular keys are added to the buffer. To implement a new feature follow a
particular key's execution path, and replicate functionality.

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
    Shift-Tab                   -- Insert a real tab up to % 8
    Ctrl-A                      -- Select All in buffer
    Ctrl-B                      -- Select word (till spaces)
    Ctrl-C                      -- Copy selection to Clipboard
    Ctrl-D                      -- Delete (trim) spaces from end of line
    Ctrl-E                      -- Capitalize (Emphasize) word
    Ctrl-F                      -- Find in file or all buffers
    Ctrl-G                      -- Goto next match
    Shift-Ctrl-G                -- Goto previous match
    Ctrl-H                      -- Find / Replace
    Ctrl-I                      -- Insert count-up number
    Shift-Ctrl-I                -- Reset and insert count-up number
    Ctrl-J                      -- Toggle coloring
    Ctrl-K                      -- Toggle Hex View
    Ctrl-L                      -- Lowercase word
    Ctrl-M                      -- Toggle auto correct
    Ctrl-N                      -- New File
    Ctrl-O                      -- Open file
    Ctrl-P                      -- Print (not implemented)
    Ctrl-Q                      -- Quit program**
    Ctrl-R                      -- Reverse three words***
    Ctrl-S                      -- Save current file
    Ctrl-T                      -- Transpose two words
    Ctrl-U                      -- Uppercase word
    Ctrl-V                      -- Paste from Clipboard
    Ctrl-W                      -- Close current file
    Ctrl-X                      -- Cut to Clipboard
    Ctrl-Y                      -- Redo last undo
    Ctrl-Z                      -- Undo last change
                                
    Ctrl Left                   -- Go left one word
    Ctrl Right                  -- Go right one word
    Ctrl PgUp                   -- Go up one large page (2x)
    Ctrl PgDn                   -- Go down one large page (2x)
    Ctrl Home                   -- Go to beginning of file
    Ctrl End                    -- Go end of file
    Ctrl Space                  -- Enable / disable keyboard
                                
    Altl Left                    -- Go to begin of current word*
    Alt Right                    -- Go to end of current word
    Alt Up                       -- Go to next buffer
    Alt Down                     -- Go to previous buffer
    Alt PgUp                     -- Go to next buffer
    Alt PgDn                     -- Go to previous buffer
    Alt Home                     -- Go to first buffer
    Alt End                      -- Go to last buffer
                                
    Home Home                    -- Go to begin of page (PgUp)
    3x Home                      -- Go to begin of file
                                
    Alt-A                        -- Save All buffers
    Alt-B                        -- Show Buffers
    Alt-C                        -- Start column select
    Alt-D                        -- Delete current line
    Alt-E                        -- Show edit Menu
    Alt-F                        -- Show File Menu
    Alt-G                        -- Goto line dialog
    Alt-H                        -- Help Menu
    Alt-I                        -- Ignore (convert) tabs to spaces
    Alt-J                        -- Jump to next long line (80+)
    Alt-K                        -- Delete (kill) till end of line
    Alt-M                        -- Macros menu
    Alt-N                        -- Next search result
    Alt-O                        -- Open file (Simplified Dialog)
    Alt-P                        -- Previous search result
    Alt-Q                        -- Hide top Pane
    Alt-R                        -- Redo
    Alt-S                        -- Search for text
    Alt-T                        -- Find / Replace (taush)
    Alt-U                        -- Undo
    Alt-V                        -- Select Current Word (till delimiters)
    Alt-W                        -- Write (Save) Current buffer
    Alt-X                        -- Exit program
    Alt-Y                        -- Check Python syntax (compile buffer)
    Alt-Z                        --
                                
    Alt-0                        -- Switch to Function pane (left)
                                
    Alt-1                        -- Switch to buffer 1
    Alt-2                        -- Switch to buffer 2
    ....                         -- ....
    ....                         -- ....
    Alt-9                        -- Switch to buffer 9
                                
    Alt-F1                       --  Gnome - Menu
    Alt-F2                       --  Cnome - Run App
    Alt-F4                       --  Exit program (Use Alt-X)
    Alt-F7                       --  Gnome - Move window
    Alt-F8                       --  Gnome - Resize window
    Alt-F9                       --  Gnome - Minimize window
    Alt-F10                      --  Gnome - Fumm Screen window
                                
    F1                            -- Help
    F2                            -- Dev Help
    F3                            -- Key assignments Help
    F4                            -- Animate macro
    F5                            -- Previous Match
    F6                            -- Next Match
    F7                            -- Start / Stop Record
    F8                            -- Play Macro
    F9                            -- Toggle code spell check****
    Shift-F9                      -- Toggle full file (text) spell check
    F10                           -- System - Menu
    shift F10                     -- Notebook tab menu (if enabled)
    F11                           -- Toggle full Screen
    F12                           -- Cursor Locator
    Shift-F12                     -- Reveal tabs and spaces and 80 column marker
    Ctrl-F12                      -- Reveal Hex view

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
    Alt-O                       -- Change One
    Alt-A                       -- Change All
    Alt-Tab                     -- Navigate between search / main windows
    Arrow Up/Down               -- Next / prev match
    ENTER                       -- Change selection

  Mouse actions:

    Left Click                  -- Positon caret (text cursor)
    Right Click                 -- Call up right click menu
    Right Click (on spell)      -- Call up spell correction list
    Click - Hold - Drag (L-R)   -- Select
    Click - Hold - Drag  (U-D)  -- Column Select
    Double Click                -- Select Word

Notes:

    *       Alt-Arrow   Goto begin / end of current word. Word delimited with
                        alpha_num + punctuation
    **      Ctrl-Q      Quit program, no save, but files are backed up in
                        (~/pyedit/data) '*.sav'
    ***     Ctrl-R      Reverse words around the middle.(a = b becomes b = a)
    ****    F9          Only Comments and strings are checked

Unrecognized key is inserted verbatim into the buffer, and a message is printed on the
controlling terminal. If no action is listed, that key is unassigned. Most dialogs
can be dismissed with the Esc key or the Alt-X key combination.






