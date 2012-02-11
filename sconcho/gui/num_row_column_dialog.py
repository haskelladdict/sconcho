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

from functools import partial

try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str
                          
from PyQt4.QtCore import (SIGNAL, QDir)
from PyQt4.QtGui import (QDialog)

from gui.ui_num_row_column_dialog import Ui_NumRowColumnDialog



##########################################################################
#
# This widget allows users to select the number of rows to insert 
# into the canvas
#
##########################################################################
class NumRowColumnDialog(QDialog, Ui_NumRowColumnDialog):


    def __init__(self, requestType, parent = None):
        """ Initialize the dialog. """

        super(NumRowColumnDialog, self).__init__(parent)
        self.setupUi(self)

        message = ("please select the number of\n" + requestType
                   + " to add")
        self.requestLabel.setText(message)
        self.setWindowTitle("insert " + requestType)
                                  


    @property
    def num(self):
        
        return self.numSpinner.value()
