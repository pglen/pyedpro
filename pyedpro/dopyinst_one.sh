#!/bin/bash

# Build new installation, one file

rm -rf build dist pyedpro.spec

#for aa in ../pycommon/*.py; do
#    COMM+="--hidden-import=$aa "
#done
#for aa in pedlib/*.py; do
#    LIB+="--hidden-import=$aa "
#done

pyinstaller pyedpro.py -p pyedlib -p ../pycommon    \
    --hidden-import=cairo                           \
    --hidden-import=sqlite3                         \
    --hidden-import=webkit2                         \
    --add-data="pedlib/data:pedlib/data"            \
    --add-data="pedlib/images:pedlib/images"        \
    --add-data=".:."                                \
    --onefile                                       \

# eof









