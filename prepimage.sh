#!/bin/bash

TARG=/tmp/AppImage_pyedpro

mkdir -p $TARG
rm -rf $TARG/*
cp -a pyedpro/* $TARG
find $TARG -name "*.pyc" -exec rm {} \;
ARCH=x86_64 appimagetool $TARG
mv pyedpro.py-x86_64.AppImage ../largefiles
rm -rf $TARG

# EOF
