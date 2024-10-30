#!/bin/sh

# Pack current project. Will back out from dir and create dirname.tgz
# and put it back to our dir.

CURR=`pwd | awk -F '/' {'print $NF'} |  sort -n | tail -1`
cd ..
echo "Packing / Archiving project \"$CURR\" "
tar cfz $CURR.tgz $CURR
echo Created $CURR.tgz in parent directory
