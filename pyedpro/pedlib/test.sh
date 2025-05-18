#!/bin/bash
##########################################################################
##                                                                      ##
##       this script searches for the necessary binaries and            ##
##       aborts if something isn't found                                ##
##                                                                      ##
##                                                                      ##
## This program is free software; you can redistribute it and/or modify ##
## it under the terms of the GNU General Public License as published by ##
## the Free Software Foundation; either version 2 of the License, or    ##
## (at your option) any later version.                                  ##
##                                                                      ##
##########################################################################

. config_build nocheck
. $SCRIPTS/misc/lib/lib_fail

FILES="tune2fs cp mv gunzip gzip umount mount cat mkisofs dd mke2fs rmdir tar"
FAILED="false"

# if we use a compressed ISO9660 we need that too
if [ "$COMPRESSEDFS" = "yes" ]; then
    FILES="$FILES mkzftree"
fi


exit 0
