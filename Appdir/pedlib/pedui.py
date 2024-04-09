#!/usr/bin/env python

# Menu items for the pyedit project

'''
    <menuitem action='Stop'/>
      <menu action='ColorMenu'>
        <menuitem action='Red'/>
        <menuitem action='Green'/>
        <menuitem action='Blue'/>
    </menu>
      <menu action='ShapeMenu'>
        <menuitem action='Square'/>
        <menuitem action='Rectangle'/>
        <menuitem action='Oval'/>
        <menuitem action='Bold'/>
      </menu>
'''

ui_info = \
'''<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='New'/>
      <menuitem action='Open'/>
      <menuitem action='Close'/>
      <menuitem action='Close All'/>
      <menuitem action='Save'/>
      <menuitem action='SaveAs'/>
      <menuitem action='SaveAll'/>
      <separator/>
      <menuitem action='Load Session'/>
      <menuitem action='Save Session'/>
      <separator/>
      <menuitem action='Start Terminal'/>
      <menu action='Recent'>
          <placeholder action='Recent Files'/>
          <separator/>
      </menu>
      <menu action='Sessions'>
          <placeholder action='Recent Sessions'/>
          <separator/>
      </menu>
      <separator/>
      <menuitem action='Quit'/>
      <menuitem action='Exit'/>
    </menu>

    <menu action='EditMenu'>
      <menuitem action='Cut'/>
      <menuitem action='Copy'/>
      <separator/>
      <menuitem action='Paste'/>
      <menuitem action='Find'/>
      <separator/>
      <menuitem action='Undo'/>
      <menuitem action='Redo'/>
      <separator/>
      <menuitem action='Discard Undo'/>
      <separator/>
      <menuitem action='Spell'/>
      <menuitem action='Spell2'/>
      <separator/>
      <menuitem action='MakeRO'/>
      <menuitem action='MakeRW'/>
      <separator/>
      <menuitem action='ColorBar'/>
      <menuitem action='RedBar'/>
      <menuitem action='unColorBar'/>
      <separator/>
      <menuitem action='StopDiff'/>
      <menuitem action='TogStrip'/>
    </menu>

    <menu action='NavMenu'>
      <menuitem action='Goto'/>
      <menuitem action='Find'/>
      <separator/>
      <menuitem action='Next'/>
      <menuitem action='Prev'/>
      <separator/>
      <menuitem action='Begin'/>
      <menuitem action='End'/>
    </menu>

    <menu action='MacrosMenu'>
      <menuitem action='Record'/>
      <menuitem action='Play'/>
      <menuitem action='Animate'/>
      <separator/>
      <menuitem action='Savemacro'/>
      <menuitem action='Loadmacro'/>
    </menu>

    <menu action='PreferencesMenu'>
        <menuitem action='Colors'/>
        <menuitem action='Fonts'/>
      <menuitem action='Settings'/>
    </menu>

    <menu action='WinMenu'>
      <menuitem action='PrevWin'/>
      <menuitem action='NextWin'/>
    <separator/>
      <menuitem action='SaveAll'/>
    <separator/>
      <menuitem action='ShowLog'/>
    </menu>

    <menu action='HelpMenu'>
      <menuitem action='Help'/>
      <menuitem action='DevHelp'/>
      <menuitem action='KeyHelp'/>
      <menuitem action='KeyDoc'/>
      <menuitem action='About'/>
    </menu>

  </menubar>

  <toolbar  name='ToolBar'>
    <toolitem action='New'/>
    <toolitem action='Open'/>
    <toolitem action='Save'/>
    <toolitem action='Close'/>
    <toolitem action='Exit'/>
    <toolitem action='Quit'/>
    <separator/>
    <toolitem action='Copy'/>
    <toolitem action='Cut'/>
    <toolitem action='Paste'/>

   <toolitem action='Undo'/>
    <toolitem action='Redo'/>
    <separator/>
    <toolitem action='Find'/>
    <toolitem action='Goto'/>

     </toolbar>
</ui>'''

'''    <toolitem action='Record'/>
    <toolitem action='Play'/>
    <separator/>

    <toolitem action='About'/>
    <toolitem action='QuickHelp'/>
    <toolitem action='Help'/>   '''


























