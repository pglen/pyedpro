#!/bin/bash

# Find string in whole project

#find . -name "*.py" -type f -exec grep -H $1 {} \;

find . -name "*.py" | grep -v pycommon.org/ | grep -v study/ | grep -v debian/ | \
    grep -v garbage/ | xargs -i grep -H $1 {}

# EOF
