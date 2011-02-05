# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2010 Markus Dittrich
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

import os, sys

from PyQt4.QtCore import (QString, QSettings)
from PyQt4.QtGui import QApplication
from sconcho.gui.mainWindow import MainWindow
import sconcho.util.symbolParser as parser
import sconcho.util.messages as msg
import sconcho.util.settings as settings


ORGANIZATION        = "Sconcho"
ORGANIZATION_DOMAIN = "sconcho.sourceforge.net"
APPLICATION         = "sconcho"


def sconcho_gui_launcher(fileName = None):
    """ Main routine starting up the sconcho framework. """

    defaultSettings = settings.DefaultSettings(ORGANIZATION, APPLICATION)
    currPath = os.path.dirname(__file__)
    symbolPaths = set_up_symbol_paths(currPath, defaultSettings)

    # We attempt to read all available knitting symbols 
    # before firing up the MainWindow. At the very least we
    # require to find a symbol for a "knit" stitch. If not, 
    # we terminate right away.
    knittingSymbols = parser.parse_all_symbols(symbolPaths)
    try:
        knittingSymbols[QString("knit")]
    except KeyError:
        sys.exit(msg.errorOpeningKnittingSymbols % symbolPaths)
    
    # fire up the MainWindow
    app = QApplication(sys.argv)
    app.setOrganizationName(ORGANIZATION)
    app.setOrganizationDomain(ORGANIZATION_DOMAIN)
    app.setApplicationName(APPLICATION)
    window = MainWindow(currPath, defaultSettings, knittingSymbols, fileName)
    window.show()
    app.exec_()



def set_up_symbol_paths(path, settings):
    """ Creates the list with paths where symbols should
    be loaded from. """

    symbolPaths = [os.path.join(path, "symbols")]
    customSymbolPath = settings.personal_symbol_path
    symbolPaths.append(customSymbolPath)

    return symbolPaths

