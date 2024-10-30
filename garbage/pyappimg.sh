#!/bin/bash

mkdir -p Appdir
rm -r Appdir/*
cp -a pyedpro/* Appdir

python-appimage build app Appdir

