#!/bin/bash

mkdir -p AppImage
rm -rf AppImage/*
cp -a pyedpro/* AppImage
find AppImage -name "*.pyc" -exec rm {} \;
ARCH=x86_64 appimagetool AppImage
rm -rf AppImage
rm -rf AppDir
rm -rf appimage-build
mv pyedpro.py-x86_64.AppImage ../largefiles

# EOF
