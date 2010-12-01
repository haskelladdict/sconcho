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

# set up path to symbols and docs
currPath = os.path.dirname(__file__)
sys.path.append(currPath)

from PyQt4.QtGui import QApplication
from gui.mainWindow import MainWindow
import util.symbolParser as parser


def sconcho_gui_launcher(fileName = None):
    """
    Main routine starting up the sconcho framework.
    """
   
    app = QApplication(sys.argv)
    app.setOrganizationName("Markus Dittrich")
    app.setOrganizationDomain("sconcho.sourceforge.net")
    app.setApplicationName("sconcho")
    window = MainWindow(currPath, fileName)
    window.show()
    app.exec_()
