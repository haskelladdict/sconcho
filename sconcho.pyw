#!/usr/bin/python

import sys, os

try:
    from sconcho.sconcho_gui import sconcho_launcher
    sconcho_launcher()
except ImportError as error:
    print("Failed to start sconcho - %s" % error)

