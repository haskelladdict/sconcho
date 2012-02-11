#!/usr/bin/env python

import sys
import subprocess

if len(sys.argv) > 1:
    fileName = sys.argv[1]
else:
    fileName = ""

subprocess.Popen(["python", "-O", "sconcho/sconcho_gui.py", fileName])
