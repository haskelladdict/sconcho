#!/usr/bin/python

import sys, os


def main():
    """ This is a simple wrapper for starting the main
    sconcho gui. 

    For now we check if any command line arguments were
    passed. If yes, we assume the first one was meant to
    be a sconcho spf file and then pass it on to 
    sconcho_gui_launcher().
    """

    fileName = None
    if len(sys.argv) > 1:
        fileName = sys.argv[1]

    try:
        from sconcho.sconcho_gui import sconcho_gui_launcher
        sconcho_gui_launcher(fileName)
    except ImportError as error:
        print("Failed to start sconcho - %s" % error)



if __name__ == "__main__":

    main()
