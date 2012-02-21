#!/usr/bin/env python 

import sys
import subprocess

if len(sys.argv) > 1:
    fileName = sys.argv[1]
else:
    fileName = ""

if sys.platform == "win32":
    subprocess.Popen(["pythonw", "-O", "sconcho/sconcho_gui.py", fileName])
else:
    subprocess.Popen(["python", "-O", "sconcho/sconcho_gui.py", fileName])
