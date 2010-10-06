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

from PyQt4.QtCore import SIGNAL, pyqtSignal, QString
from PyQt4.QtGui import QDialog
from ui_insertDeleteRowColumnWidget import Ui_InsertDeleteRowColumnWidget



##########################################################################
#
# This widget provides a dialog for inserting and deleting rows
# of the main pattern grid.
#
##########################################################################
class InsertDeleteRowColumnWidget(QDialog, Ui_InsertDeleteRowColumnWidget):

    # install signals
    insert_row    = pyqtSignal(int, QString, int)
    delete_row    = pyqtSignal(int)
    insert_column = pyqtSignal(int, QString, int)
    delete_column = pyqtSignal(int)


    def __init__(self, numRows, numCols, parent = None):
        """
        Initialize the dialog.
        """

        QDialog.__init__(self, parent)
        self.setupUi(self)

        # set the maximum of the spinbox
        self.__numRows = numRows
        self.set_upper_row_limit(numRows)

        self.__numColumns = numCols
        self.set_upper_column_limit(numCols)

        # install some connections
        self.connect(self.closeButton, SIGNAL("clicked()"), self.close)
        self.connect(self.insertRowButton, SIGNAL("clicked()"),
                     self.insert_row_button_pressed)
        self.connect(self.deleteRowButton, SIGNAL("clicked()"),
                     self.delete_row_button_pressed)
        self.connect(self.insertColumnButton, SIGNAL("clicked()"),
                     self.insert_column_button_pressed)
        self.connect(self.deleteColumnButton, SIGNAL("clicked()"),
                     self.delete_column_button_pressed)



    def insert_row_button_pressed(self):
        """
        This method forwards clicks on the insertRowButton.
        """

        numRows    = self.numInsertRows.value()
        pivot      = self.insertRowPivot.value()
        insertMode = self.insertRowMode.currentText()

        if pivot <= 0:
            return

        self.__numRows += numRows
        self.set_upper_row_limit(self.__numRows)
        self.insert_row.emit(numRows, insertMode, pivot)
        
        
        
    def delete_row_button_pressed(self):
        """
        This method forwards clicks on the deleteRowButton.
        """

        deadRowID = self.deleteRowID.value()

        if deadRowID <= 0:
            return

        self.__numRows -= 1
        self.set_upper_row_limit(self.__numRows)
        self.delete_row.emit(deadRowID)



    def insert_column_button_pressed(self):
        """
        This method forwards clicks on the insertColumnButton.
        """
        
        numColumns = self.numInsertColumns.value()
        pivot      = self.insertColumnPivot.value()
        insertMode = self.insertColumnMode.currentText()

        if pivot <= 0:
            return

        self.__numColumns += numColumns
        self.set_upper_column_limit(self.__numColumns)
        self.insert_column.emit(numColumns, insertMode, pivot)



    def delete_column_button_pressed(self):
        """
        This method forwards clicks on the deleteColumnButton.
        """

        deadColumnID = self.deleteColumnID.value()

        if deadColumnID <=0:
            return

        self.__numColumn -= 1
        self.set_upper_column_limit(self.__numColumns)
        self.delete_column.emit(deadColumnID)
        


    def set_upper_row_limit(self, numRows):
        """
        Sets the upper limit of the row selectors based
        on the number of available rows.
        """

        self.insertRowPivot.setMinimum(1)
        self.insertRowPivot.setMaximum(numRows)
        self.deleteRowID.setMinimum(1)
        self.deleteRowID.setMaximum(numRows)
        


    def set_upper_column_limit(self, numCols):
        """
        Sets the upper limit of the column selectors based
        on the number of available columns.
        """
        
        self.insertColumnPivot.setMinimum(1)
        self.insertColumnPivot.setMaximum(numCols)
        self.deleteColumnID.setMinimum(1)
        self.deleteColumnID.setMaximum(numCols)
