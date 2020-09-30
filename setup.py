#!/usr/bin/env python3

# Here we imported the 'setup' module which allows us to install Python
# scripts to the local system beside performing some other tasks, you can find the
# documentation here: https://docs.python.org/2/distutils/apiref.html

import os, sys, fnmatch

from setuptools import setup

descx = '''PyEdPro is modern multi-platform editor. Simple, powerful,
configurable, extendable. Goodies like macro recording / playback, spell check,
column select, multiple clipboards, unlimited undo ...
   PyEdPro.py has macro recording/play, search/replace, one click function navigation,
auto backup, undo/redo, auto complete, auto correct, syntax check, spell suggestion
 ... and a lot more.
   The recorded macros, the undo / redo information the editing session details persist
 after the editor is closed.
    The spell checker can check code comments. The parsing of the code is
rudimentary, comments and strings are spell checked. (Press F9) The code is filtered
out for Python and  'C'. The spell checker is executed on live text. (while typing)
'''

classx = [
          'Development Status :: Mature',
          'Environment :: GUI',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Editors',
          'Topic :: Software Development :: Editor',
        ]

setup(name = "pyedpro.py",      # Name of the program.
      version = "1.7",          # Version of the program.
      description = "Easy-to-use advanced editor in python",
      long_description = descx,
      classifiers = classx,
      author = "Peter Glen",
      author_email = "peterglen@gmail.com",
      license='GPLv3',            # The license of the program.
      url="https://github.com/pglen/pyedpro.git",
      scripts = ['pyedpro.py', 'pangview.py'],
      packages=['pedlib', 'panglib', 'pycommon'],
      package_dir = {'pedlib': 'pedlib', 'panglib': 'panglib', 'pycommon': '../pycommon'},
      package_data = {'pedlib': ['data/*', 'images/*']},
      data_files =  [('/usr/share/icons/hicolor/96x96/apps/', ['pedlib/images/pyedpro.png',
                           'pedlib/images/pedicon.png' ]),
                        ('/usr/share/applications', ['pyedpro.desktop'])],
      #include_package_data=True
      )

# EOF