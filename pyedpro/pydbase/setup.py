import setuptools

descx = '''
        It is an insanely simple database. Fast. If all you need is a key / value
        pair, this is the perfect solution.
        (Yes, all you need is a key / value pair, as any and every structure
        can be built out of it)
'''

classx = [
          'Development Status :: Mature',
          'Environment :: GUI',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Databases',
        ]

includex = ["*", ]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydbase",
    version="1.0",
    author="Peter Glen",
    author_email="peterglen99@gmail.com",
    description="High speed database with key / data in python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pglen/pydbase",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    packages=setuptools.find_packages(include=includex),

    scripts = ['pydbase.py'],
    py_modules = ["twincore", "pypacker" ],
    #package_dir = {'': '.'},

    python_requires='>=3',
    entry_points={
        'console_scripts': [ "pydbase=pydbase:mainfunc", ],
    },
)

# EOF
