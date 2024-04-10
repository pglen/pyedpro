import os, sys, shutil
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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ]

includex = ["*", "pedlib/", "panglib", "pedlib/images",
            "image.png", "pyedpro_ubuntu.png"]

#shutil.copy("../README.md", "README.copy.md")
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
#os.remove("README.copy.md")

# Get version number  from the server support file:
fp = open("pyedpro.py", "rt")
vvv = fp.read(); fp.close()
loc_vers =  '1.0.0'     # Default
for aa in vvv.split("\n"):
    idx = aa.find("VERSION ")
    if idx == 0:        # At the beginning of line
        try:
            loc_vers = aa.split()[2].replace('"', "")
            break
        except:
            pass
#print("loc_vers:", loc_vers)
#sys.exit()

setuptools.setup(
    name="pyedpro",
    version=loc_vers,
    author="Peter Glen",
    author_email="peterglen99@gmail.com",
    description="High power editor in python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pglen/pyedpro",
    classifiers=classx,
    include_package_data=True,
    package_data={ "pedlib": ["docs/*"], },
    packages=setuptools.find_packages(include=includex),
    scripts = ['pyedpro.py', 'pangview.py'],

    package_dir = {
                    'pedlib': 'pedlib',
                    'pedlib/images': 'pedlib/images',
                    'pedlib/plugins': 'pedlib/plugins',
                    'pedlib/data' : 'pedlib/data',
                    'pycommon': 'pycommon',
                    'panglib': 'panglib',
                   },

    #package_py = {
    #                '':
    #                    ['pedlib/images/pyedpro.png',
    #                     'pedlib/images/pyedpro_sub.png',
    #                     'pedlib/images/pedicon.png', 'image.png',
    #                     'pyedpro_ubuntu.png'
    #                    ]
    #                },

    data_files =  [('/usr/share/icons/hicolor/96x96/apps/',
                        ['pedlib/images/pyedpro.png',
                            'pedlib/images/pedicon.png',
                            'pedlib/images/pyedpro_sub.png' ]),
                            ('/usr/share/applications', ['pyedpro.desktop']),
                   ],

    python_requires='>=3',
    install_requires=["pyvpacker", "pydbase" ],
    entry_points={
        'console_scripts': [ "pyedpro=pyedpro:mainfunc",
            "pangview=pangview:mainfunc",
            ],
    },
)

# EOF