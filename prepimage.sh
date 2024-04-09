#!/bin/bash

TARG=/tmp/AppImage_$$_pyedpro
#echo $TARG
#exit
mkdir -p $TARG
rm -rf $TARG/*
cp -a pyedpro/* $TARG
cp -a ~/.local/lib/python3.10/site-packages/webkit/ $TARG
cp -a ~/.local/lib/python3.10/site-packages/pyvpacker/ $TARG
cp -a ~/.local/lib/python3.10/site-packages/pydbase/ $TARG
cp -a ~/.local/lib/python3.10/site-packages/pydbase/dbutils.py $TARG
find $TARG -name "*.pyc" -exec rm {} \;
ARCH=x86_64  appimagetool  $TARG
mv pyedpro.py-x86_64.AppImage ../largefiles
rm -rf $TARG

# EOF
