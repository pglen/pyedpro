
from __future__ import absolute_import
from __future__ import print_function

import sys, os

base = os.path.realpath(__file__)
print("file", os.path.dirname(base))
os.chdir(os.path.dirname(base))

#sys.path.append(os.path.dirname(base))

sys.exit(0)


