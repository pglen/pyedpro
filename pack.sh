#!/bin/sh

# Pack current project. Will back out from dir and create dirname.tgz
# and put it back to our dir.

CURR=`pwd | awk -F '/' {'print $NF'} |  sort -n | tail -1`
pushd `pwd` >/dev/null
mv -f $CURR.tgz /tmp>/dev/null  2>&1 
cd ..
echo "Packing / Archiving project $CURR"
tar cfz $CURR.tgz $CURR
mv $CURR.tgz $CURR
popd








