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

from PyQt4.QtGui import QDialog 

from sconcho.gui.ui_new_pattern_dialog import Ui_NewPatternDialog



##########################################################################
#
# This widget allows initiates the start of a new project/patter
# grid. Users can adjust the grid dimensions of the new pattern grid.
#
##########################################################################
class NewPatternDialog(QDialog, Ui_NewPatternDialog):


    def __init__(self, parent = None):
        """
        Initialize the dialog.
        """

        super(NewPatternDialog, self).__init__(parent)
        self.setupUi(self)



    @property
    def num_rows(self):
        """ Return the number of rows selected. """

        return self.rowSpinner.value()
      

    @property
    def num_columns(self):
        """ Return the number of columns selected. """

        return self.columnSpinner.value()
