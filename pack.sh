#!/bin/sh

# Pack current project. Will back out from dir and create dirname.tgz
# and put it back to our dir.

if [ ! -f pyedpro.png ] ; then
    echo "Please start from pyedpro directory"
    exit
fi

#CURR=`pwd | awk -F '/' {'print $NF'} |  sort -n | tail -1`
VAR=$(grep "VERSION.*=" pyedpro/pyedpro.py | awk '{print $3}' | sed "s/\"//g")
CURR=pyedpro-$VAR.tar.gz
#echo "Packing: " $CURR ; exit
if [ -f ../$CURR ] ; then
    echo "File \"$CURR\" exist. Please delete to recreate."
    exit
fi

cd ..
echo "Packing / Archiving project into \"../$CURR\" "
tar cfz $CURR pyedpro
#echo Created $CURR in parent directory
