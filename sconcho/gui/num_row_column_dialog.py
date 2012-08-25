# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2009-2012 Markus Dittrich
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

from functools import partial

from PyQt4.QtCore import (QDir,
                          SIGNAL)

from PyQt4.QtGui import (QDialog)

from sconcho.gui.ui_num_row_column_dialog import Ui_NumRowColumnDialog



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

        numMessage = ("number of " + requestType + " to add")
        self.requestLabel.setText(numMessage)
        self.setWindowTitle("insert " + requestType)

        preLocationMessage = ""
        postLocationMessage = ""
        if requestType == "rows":
            self.locationChooser.addItem("above")
            self.locationChooser.addItem("below")
            preLocationMessage = "insert rows"
            postLocationMessage = "selected row."
        elif requestType =="columns":
            self.locationChooser.addItem("left of")
            self.locationChooser.addItem("right of")
            preLocationMessage = "insert columns"
            postLocationMessage = "selected column."

        self.preLocationLabel.setText(preLocationMessage)
        self.postLocationLabel.setText(postLocationMessage)



    @property
    def num(self):

        return self.numSpinner.value()


    @property
    def location(self):

        return self.locationChooser.currentText()
