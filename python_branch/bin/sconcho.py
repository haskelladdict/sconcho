#!/usr/bin/python
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

import os, sys
sys.path.append("../")

from PyQt4.QtGui import QApplication
from gui.mainWindow import MainWindow
import sconchoIO.symbolParser as parser

# for now hardcode the path; this has to become a bit
# more spiffy lateron
SYMBOL_PATHS = ["./symbols"]


# main startup routine
if __name__ == "__main__":
    """
    Main routine starting up the sconcho framework.
    """

    symbols = parser.parse_all_symbols(SYMBOL_PATHS)

    app = QApplication(sys.argv)
    window = MainWindow(symbols)
    window.show()
    sys.exit(app.exec_())
    
