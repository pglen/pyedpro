#!/bin/bash

TARG=/tmp/AppImage_$$_pyedpro
#echo $TARG ; exit
VER=$(grep "VERSION.*=" pyedpro/pyedpro.py | awk '{print $3}' | sed "s/\"//g")
OUTFILE=pyedpro-$VER-x86_64.appimage
#echo $OUTFILE ; exit
mkdir -p $TARG
rm -rf $TARG/*
cp -a pyedpro/* $TARG
cp -a ~/.local/lib/python3.10/site-packages/pyvpacker.py $TARG
cp -a ~/.local/lib/python3.10/site-packages/pydbase/ $TARG
cp -a ~/.local/lib/python3.10/site-packages/pyvguicom/ $TARG
find $TARG -name "*.pyc" -exec rm {} \;
ARCH=x86_64 appimagetool $TARG  $OUTFILE
#LARGFILES=../largefiles
#mv $OUTFILE $LARGFILES
#echo Results in $LARGFILES/$OUTFILE
echo Results in $OUTFILE
rm -rf $TARG

# EOF
