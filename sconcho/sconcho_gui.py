#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2009-2011 Markus Dittrich
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License Version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License Version 3 for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
#######################################################################

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import logging
from time import gmtime, strftime
from functools import partial
import os, sys, traceback, tempfile

try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str

from PyQt4.QtCore import (QSettings, QVariant)
from PyQt4.QtGui import QApplication
from sconcho.gui.main_window import MainWindow
import sconcho.util.symbol_parser as parser
import sconcho.util.messages as msg
import sconcho.util.settings as settings
import sconcho.util.misc as misc

# module level logger:
logger = logging.getLogger(__name__)


ORGANIZATION        = "Sconcho"
ORGANIZATION_DOMAIN = "sconcho.sourceforge.net"
APPLICATION         = "sconcho"


def sconcho_gui_launcher(currPath, defaultSettings, knittingSymbols, fileName):
    """ Main routine starting up the sconcho framework. """


    # fire up the MainWindow
    app = QApplication(sys.argv)
    app.setOrganizationName(ORGANIZATION)
    app.setOrganizationDomain(ORGANIZATION_DOMAIN)
    app.setApplicationName(APPLICATION)
    window = MainWindow(currPath, defaultSettings, knittingSymbols, fileName)

    window.show()
    if sys.platform == "darwin":
        window.raise_()
    app.exec_()



def create_log_file(logPath):
    """ Initialize the log file """

    timeStamp = strftime("%m%d%Y%H%M%S", gmtime())

    # open a log file for this session
    if not os.path.exists(logPath):
        os.mkdir(logPath)
    logHandle = tempfile.NamedTemporaryFile(prefix="sconcho_" + timeStamp, 
                                            delete=False,
                                            dir=logPath)
    logHandle.write("sconcho started on " + timeStamp + "\n\n")
    logHandle.flush()

    return logHandle



def install_exception_handler(logHandle):
    """ Install our custom exception hook and make sure that any
    exceptions are written to a log file.

    NOTE: For now we only do this on Windows, on Linux and
    Mac OSX we can retrieve console output anyways.

    """

    sys.excepthook = partial(sconcho_excepthook, logHandle)



def sconcho_excepthook(logHandle, exceptType, value, tback):
    """ This hook allows us to log any uncaught exceptions.

    NOTE: I use this to be able to be able to better trace user errors.

    """

    # log the exception here
    if logHandle:
        traceback.print_exception(exceptType, value, tback, file=logHandle)
        logHandle.flush()

    # then call the default handler
    sys.__excepthook__(exceptType, value, tback) 



def initialize_logger(logHandle):
    """ Initialize the logfile.

    If logHandle is None loging goes to stdout.

    """

    if logHandle:
        logging.basicConfig(filename=logHandle.name,
                            filemode="a",
                            level=logging.DEBUG, 
                            format=("%(asctime)s - %(name)s -  %(levelname)s "
                                    "=> %(message)s"),
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        logging.basicConfig(level=logging.DEBUG, 
                            format=("%(asctime)s - %(name)s -  %(levelname)s "
                                    "=> %(message)s"),
                            datefmt='%m/%d/%Y %I:%M:%S %p')

    # optimizations
    logging.logThreads=0
    logging.logProcesses=0



def main(fileName=None):
    """ This is a simple wrapper for starting the main
    sconcho sconcho.gui. 

    For now we check if any command line arguments were
    passed. If yes, we assume the first one was meant to
    be a sconcho spf file and then pass it on to 
    sconcho_gui_launcher().
    """

    # load settings
    defaultSettings = settings.DefaultSettings(ORGANIZATION, APPLICATION)
    currPath = os.path.dirname(__file__)
    symbolPaths = misc.set_up_symbol_paths(currPath, defaultSettings)

    # set up logging if requested
    doLogging = defaultSettings.doLogging.value
    loggingPath = unicode(defaultSettings.loggingPath.value)
    if doLogging and loggingPath:
        logHandle = create_log_file(loggingPath)
    else:
        logHandle = None

    install_exception_handler(logHandle)
    initialize_logger(logHandle)

    # check that file exists; this is required since Sconcho.app
    # on OS X seems to pass some bogus string that then causes
    # issues
    if len(sys.argv) > 1:
        fileNameTmp = sys.argv[1]
        if os.path.isfile(fileNameTmp):
            fileName = fileNameTmp

    # We attempt to read all available knitting symbols 
    # before firing up the MainWindow. At the very least we
    # require to find a symbol for a "knit" stitch. If not, 
    # we terminate right away.
    knittingSymbols = parser.parse_all_symbols(symbolPaths)
    try:
        knittingSymbols[QString("knit")]
    except KeyError:
        sys.exit(msg.errorOpeningKnittingSymbols % symbolPaths)
    
    sconcho_gui_launcher(currPath, defaultSettings, knittingSymbols, fileName)
    logging.shutdown()


if __name__ == "__main__":

    main()
