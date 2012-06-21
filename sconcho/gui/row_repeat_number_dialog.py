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

from PyQt4.QtCore import (SIGNAL, QDir)
from PyQt4.QtGui import (QDialog)

from sconcho.gui.ui_row_repeat_number_dialog import Ui_RowRepeatNumDialog



##########################################################################
#
# This widget allows users to select the number of times a row repeat
# is to be repeated
#
##########################################################################
class RowRepeatNumDialog(QDialog, Ui_RowRepeatNumDialog):


    def __init__(self, parent = None):
        """ Initialize the dialog. """

        super(RowRepeatNumDialog, self).__init__(parent)
        self.setupUi(self)



    @property
    def num_repeats(self):
        
        return self.numRepeatSpinner.value()
