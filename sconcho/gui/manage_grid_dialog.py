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

try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str

from PyQt4.QtCore import (Qt, SIGNAL)
from PyQt4.QtGui import (QDialog, QMessageBox)
from sconcho.gui.ui_manage_grid_dialog import Ui_ManageGridDialog
import sconcho.util.messages as msg


##########################################################################
#
# This widget provides a dialog for inserting and deleting rows
# of the main pattern grid.
#
##########################################################################
class ManageGridDialog(QDialog, Ui_ManageGridDialog):


    def __init__(self, rowOffset, numRows, numCols, row, col, 
                 parent = None):
        """ Initialize this dialog. """

        super(ManageGridDialog, self).__init__(parent)
        self.setupUi(self)

        # set the maximum of the spinbox
        self.set_row_limit(rowOffset, numRows)
        self.set_upper_column_limit(numCols)

        # set the current values for row/column to be changed
        self.set_row_col(row, col)

        # install some connections
        self.connect(self.closeButton, SIGNAL("clicked()"), self.close)
        self.connect(self.insertRowButton, SIGNAL("pressed()"),
                     self.insert_row_button_pressed)
        self.connect(self.deleteRowButton, SIGNAL("pressed()"),
                     self.delete_row_button_pressed)
        self.connect(self.insertColumnButton, SIGNAL("pressed()"),
                     self.insert_column_button_pressed)
        self.connect(self.deleteColumnButton, SIGNAL("pressed()"),
                     self.delete_column_button_pressed)
        self.connect(self.numDeleteColumns, SIGNAL("valueChanged(int)"),
                     self.adjust_delete_columns_combo_box)
        self.connect(self.numDeleteRows, SIGNAL("valueChanged(int)"),
                     self.adjust_delete_rows_combo_box)


    def insert_row_button_pressed(self):
        """ This method forwards clicks on the insertRowButton. """

        rowAdd = self.numInsertRows.value()
        pivot = self.insertRowPivot.value()
        insertMode = self.insertRowMode.currentText()

        self.emit(SIGNAL("insert_rows"), rowAdd, insertMode, pivot)

        
        
    def delete_row_button_pressed(self):
        """ This method forwards clicks on the deleteRowButton. """

        numRowsToDelete = self.numDeleteRows.value()
        pivot = self.deleteRowPivot.value()
        deleteMode = self.deleteRowMode.currentText()

        self.emit(SIGNAL("delete_rows"), numRowsToDelete, deleteMode, 
                  pivot)



    def insert_column_button_pressed(self):
        """ This method forwards clicks on the insertColumnButton. """
        
        numColumnsToAdd = self.numInsertColumns.value()
        pivot = self.insertColumnPivot.value()
        insertMode = self.insertColumnMode.currentText()

        self.emit(SIGNAL("insert_columns"), numColumnsToAdd, 
                  insertMode, pivot)



    def delete_column_button_pressed(self):
        """ This method forwards clicks on the deleteColumnButton. """

        numColumnsToDelete = self.numDeleteColumns.value()
        pivot = self.deleteColumnPivot.value()
        deleteMode = self.deleteColumnMode.currentText()

        self.emit(SIGNAL("delete_columns"), numColumnsToDelete, 
                  deleteMode, pivot)



    def set_row_limit(self, rowOffset, numRows):
        """ Sets the upper limit of the row selectors based
        on the number of available rows.
        
        """

        self.insertRowPivot.setMinimum(rowOffset)
        self.insertRowPivot.setMaximum(rowOffset + numRows - 1)

        self.deleteRowPivot.setMinimum(rowOffset)
        self.deleteRowPivot.setMaximum(rowOffset + numRows - 1)
        self._numRows = numRows
        self._rowLabelOffset = rowOffset
        


    def set_upper_column_limit(self, numCols):
        """ Sets the upper limit of the column selectors based
        on the number of available columns.
        
        """

        self.insertColumnPivot.setMinimum(1)
        self.insertColumnPivot.setMaximum(numCols)
        self.deleteColumnPivot.setMinimum(1)
        self.deleteColumnPivot.setMaximum(numCols)
        self._numColumns = numCols



    def set_row_col(self, row, col):
        """ Set the current value of row/column entry to
        be changed.

        NOTE: We don't check the row, col values at all
        and rely on the widget to make sure the values
        remain within the limits.
        
        """

        self.insertRowPivot.setValue(self._numRows + self._rowLabelOffset
                                     - row - 1)
        self.deleteRowPivot.setValue(self._numRows + self._rowLabelOffset
                                     - row - 1)
        self.insertColumnPivot.setValue(self._numColumns - col)
        self.deleteColumnPivot.setValue(self._numColumns - col)



    def adjust_delete_columns_combo_box(self, value):
        """ Adjust the first entry in the combo box for selecting
        the deletion mode dynamically depending on how many columns 
        are selected. 

        NOTE: Changing the UI like this seems sort of confusing
        but the hope is that it will be more easy to part that
        way.

        """

        if value == 1:
            self.deleteColumnMode.setItemText(0, "at")
        else:
            self.deleteColumnMode.setItemText(0, "at and to the right of")



    def adjust_delete_rows_combo_box(self, value):
        """ Adjust the first entry in the combo box for selecting the
        deletion mode dynamically depending on how many rows are selected. 

        NOTE: Changing the UI like this seems sort of confusing
        but the hope is that it will be more easy to part that
        way.

        """

        if value == 1:
            self.deleteRowMode.setItemText(0, "at")
        else:
            self.deleteRowMode.setItemText(0, "at and below")
