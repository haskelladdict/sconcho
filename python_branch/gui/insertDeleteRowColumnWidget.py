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


class InsertDeleteRowColumnWidget(QDialog, Ui_InsertDeleteRowColumnWidget):

    # install signals
    insert_row    = pyqtSignal(int, QString, int)
    delete_row    = pyqtSignal(int)
    insert_column = pyqtSignal(int, QString, int)
    delete_column = pyqtSignal(int)


    def __init__(self, parent = None):
        """
        Initialize the dialog.
        """

        QDialog.__init__(self, parent)
        self.setupUi(self)

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

        self.insert_row.emit(numRows, insertMode, pivot)
        
        
        
    def delete_row_button_pressed(self):
        """
        This method forwards clicks on the deleteRowButton.
        """

        deadRowID = self.deleteRowID.value()

        self.delete_row.emit(deadRowID)



    def insert_column_button_pressed(self):
        """
        This method forwards clicks on the insertColumnButton.
        """
        
        numColumns = self.numInsertColumns.value()
        pivot      = self.insertColumnPivot.value()
        insertMode = self.insertColumnMode.currentText()

        self.insert_column.emit(numColumns, insertMode, pivot)



    def delete_column_button_pressed(self):
        """
        This method forwards clicks on the deleteColumnButton.
        """

        deadColumnID = self.deleteColumnID.value()

        self.delete_column.emit(deadColumnID)
        
