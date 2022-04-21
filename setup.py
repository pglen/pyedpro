import setuptools

descx = '''PyEdPro is modern multi-platform editor. Simple, powerful,
configurable, extendable. Goodies like macro recording / playback, spell check,
column select, multiple clipboards, unlimited undo ...
   PyEdPro.py has macro recording/play, search/replace, one click function navigation,
auto backup, undo/redo, auto complete, auto correct, syntax check, spell suggestion
 ... and a lot more.
   The recorded macros, the undo / redo information the editing session details persist
 after the editor is closed.
    The spell checker can check code comments. The parsing of the code is
rudimentary, comments and strings are spell checked. (Press F9 or Shit-F9) The code is filtered
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

inclu = ["*", "pedlib/", "panglib", "pyedpro.py", "pangview.py",
            "image.png", "pyedpro_ubuntu.png"]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyedpro",
    version="2.9.0",
    author="Peter Glen",
    author_email="peterglen99@gmail.com",
    description="High power editor in python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pglen/pyedpro",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,

    packages=setuptools.find_packages(include=inclu),
    #packages=['pedlib', 'panglib', 'pycommon'],
    #scripts = ['pyedpro.py', 'pangview.py'],

    package_dir = {'pedlib': 'pyedpro/pedlib', 'panglib': 'pyedpro/panglib', 'pycommon': '../pycommon',
                    'pedlib/data' : 'pyedpro/pedlib/data', },

    package_data = {'':
                        ['pyedpro/pedlib/data/KEYS',    'pyedpro/pedlib/images/pyedpro.png',
                        'pyedpro/pedlib/data/KEYS.TXT', 'pyedpro/pedlib/images/pyedpro_sub.png',
                         'pyedpro/pedlib/images/pedicon.png', 'image.png',
                         'pyedpro_ubuntu.png'
                        ]
                    },

    data_files =  [('/usr/share/icons/hicolor/96x96/apps/', ['pyedpro/pedlib/images/pyedpro.png',
                       'pyedpro/pedlib/images/pedicon.png', 'pyedpro/pedlib/images/pyedpro_sub.png' ]),
                            ('/usr/share/applications', ['pyedpro/pyedpro.desktop']),

                    #("pedlib/data",  ["pyedpro/pedlib/data/KEYS", "pyedpro/pedlib/data/KEYS.TXT",
                    #          "pyedpro/pedlib/data/QHELP", "pyedpro/pedlib/data/spell.txt"]),
                   ],

    python_requires='>=3',
    entry_points='''
        [console_scripts]
        pyedpro=pyedpro.pyedpro:mainstart
    ''',
)
