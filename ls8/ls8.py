"""Main."""

import os
import sys
from cpu import *
'''
Usage:
python(3) ls8.py call -> loads ../examples/call.ls8 into cpu
To load new programs, add program file to /examples folder
'''

current_dir = os.getcwd() + '\examples\\'


if sys.argv[1][-4] == '.':
    command = current_dir + sys.argv[1]
else:
    command = current_dir + sys.argv[1] + '.ls8'

cpu = CPU()

cpu.load(command)
cpu.run()