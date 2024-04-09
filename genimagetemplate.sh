#!/bin/bash

APPDIR=Appdir
mkdir -p $APPDIR
rm -rf $APPDIR/*
rm -rf appimage-build
cp -a pyedpro/* $APPDIR
find $TARG -name "*.pyc" -exec rm {} \;
appimage-builder --generate
# EOF
