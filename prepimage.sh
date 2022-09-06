#!/bin/bash

mkdir -p AppImage
rm -rf AppImage/*
cp -a pyedpro/* AppImage
find AppImage -name "*.pyc" -exec rm {} \;
ARCH=x86_64 appimagetool AppImage

# EOF
