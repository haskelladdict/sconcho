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

from PyQt4.QtCore import (SIGNAL)
from PyQt4.QtGui import (QDialog, QTableWidgetItem, QMessageBox)

import sconcho.util.messages as msg
from sconcho.gui.ui_pattern_row_repeat_editor_dialog import Ui_PatternRowRepeatEditor



##########################################################################
#
# This widget allows customization and deletion of pattern row repeats
#
##########################################################################
class PatternRowRepeatEditorDialog(QDialog, Ui_PatternRowRepeatEditor):

    ADD_MODE = 0
    UPDATE_MODE = 1


    def __init__(self, parent = None):
        """ Initialize the dialog. """

        super(PatternRowRepeatEditorDialog, self).__init__(parent)
        self.setupUi(self)

        # we need this to keep track of the ranges to be delated
        # during update mode
        self.previousStart = 0
        self.previousEnd = 0

        self.mode = None

        self.entryGrouper.setVisible(False)

        self.connect(self.closeButton, SIGNAL("clicked()"),
                     self.close)

        self.connect(self.addRepeatButton, SIGNAL("clicked()"),
                     self.add_repeat_dialog)

        self.connect(self.updateRepeatButton, SIGNAL("clicked()"),
                     self.update_repeat)

        self.connect(self.deleteRepeatButton, SIGNAL("clicked()"),
                     self.delete_repeat)

        self.connect(self.cancelButton, SIGNAL("clicked()"),
                     self.cancel_repeat)

        self.connect(self.acceptButton, SIGNAL("clicked()"),
                     self.accept_repeat)

        self.connect(self.startRowSpinner, SIGNAL("valueChanged(int)"),
                     self.start_row_changed)

        self.connect(self.endRowSpinner, SIGNAL("valueChanged(int)"),
                     self.end_row_changed)



    def add_repeat_dialog(self):
        """ Makes the dialog for adding a new row repeat
        visible.

        """
        
        self.entryGrouper.setVisible(True)
        self.controlGrouper.setEnabled(False)
        self.mode = PatternRowRepeatEditorDialog.ADD_MODE



    def cancel_repeat(self):
        """ Cancel the currently active row repeat entry action. """

        self.entryGrouper.setVisible(False)
        self.controlGrouper.setEnabled(True)

       
 
    def accept_repeat(self):
        """ Add a newly entered pattern repeat to the
        widget if it checks out ok.

        """

        startRow = self.startRowSpinner.value()
        endRow = self.endRowSpinner.value()
        numRepeat = self.repeatSpinner.value()

        if self.mode == PatternRowRepeatEditorDialog.ADD_MODE:
            if not self.check_ranges(startRow, endRow):
                return

            newRowID = self.repeatWidget.rowCount()
            self.repeatWidget.insertRow(newRowID)

            startRowItem = QTableWidgetItem(str(startRow))
            endRowItem = QTableWidgetItem(str(endRow))
            repeatItem = QTableWidgetItem(str(numRepeat))

            self.repeatWidget.setItem(newRowID, 0, startRowItem)
            self.repeatWidget.setItem(newRowID, 1, endRowItem)
            self.repeatWidget.setItem(newRowID, 2, repeatItem)
            
        elif self.mode == PatternRowRepeatEditorDialog.UPDATE_MODE:
            selection = self.repeatWidget.currentRow()
            if not self.check_ranges(startRow, endRow, selection):
                return

            self.repeatWidget.item(selection, 0).setText(str(startRow))
            self.repeatWidget.item(selection, 1).setText(str(endRow))
            self.repeatWidget.item(selection, 2).setText(str(numRepeat))

            # remove the previous repeat
            self.emit(SIGNAL("deleted_row_repeat"), self.previousStart, 
                      self.previousEnd)

        else:
            logger.error("Unknown mode in PatternRowRepeatEditor. "
                         "Expected either ADD_MODE or UPDATE_MODE. ")
            return
            
        self.entryGrouper.setVisible(False)
        self.controlGrouper.setEnabled(True)
        self.emit(SIGNAL("added_row_repeat"), startRow, endRow, numRepeat)

        # in the presence of row repeats we require "label all rows" mode
        self.emit(SIGNAL("allow_all_label_options"), False)



    def check_ranges(self, start, end, excludeRow = None):
        """ Make sure we don't overlap with any other repeats
        before accepting.

        If we're updating, we need to exclude the row we're updating
        from checking.

        """

        for row in range(0, self.repeatWidget.rowCount()):

            if (excludeRow != None) and row == excludeRow:
                continue
            
            startValue = int(self.repeatWidget.item(row, 0).text())
            endValue = int(self.repeatWidget.item(row, 1).text())

            existingSet = set(range(startValue, endValue+1))
            newSet = set(range(start, end+1))
            if newSet.intersection(existingSet):
                QMessageBox.critical(self, msg.badRepeatRowRangeTitle,
                                     msg.badRepeatRowRangeText, 
                                     QMessageBox.Close)
                logger.error(msg.badRepeatRowRangeText)
                return False

        return True



    def update_repeat(self):
        """ Open the dialog for updating a row repeat. """
        
        selection = self.repeatWidget.currentRow()
        if selection < 0:
            return

        # retrieve previous values and populate spinboxes
        prevStart = int(self.repeatWidget.item(selection, 0).text())
        prevEnd = int(self.repeatWidget.item(selection, 1).text())
        prevRepeat = int(self.repeatWidget.item(selection, 2).text())

        # store the values so we can delete the range when
        # the user accepts
        self.previousStart = prevStart
        self.previousEnd = prevEnd

        self.entryGrouper.setVisible(True)
        self.controlGrouper.setEnabled(False)
        self.mode = PatternRowRepeatEditorDialog.UPDATE_MODE

        self.startRowSpinner.setValue(prevStart)
        self.endRowSpinner.setValue(prevEnd)
        self.repeatSpinner.setValue(prevRepeat)



    def delete_repeat(self):
        """ Delete the selected row repeat. """

        selectionList = self.repeatWidget.selectedRanges()
        for selection in selectionList:
            for row in range(selection.bottomRow(), selection.topRow() + 1):
                prevStart = int(self.repeatWidget.item(row, 0).text())
                prevEnd = int(self.repeatWidget.item(row, 1).text())
                self.emit(SIGNAL("deleted_row_repeat"), prevStart, prevEnd)
                self.repeatWidget.removeRow(row)


        # in all row repeats are gone we can remove the requirement
        # of the "label all rows" mode
        if self.repeatWidget.rowCount() == 0:
            self.emit(SIGNAL("allow_all_label_options"), True)



    def start_row_changed(self, startValue):
        """ Make sure the start and end row SpinBoxes are properly
        synchronized.

        """

        if self.endRowSpinner.value() < startValue:
            self.endRowSpinner.setValue(startValue)



    def end_row_changed(self, endValue):
        """ Make sure the start and end row SpinBoxes are properly
        synchronized.

        """

        if self.startRowSpinner.value() > endValue:
            self.startRowSpinner.setValue(endValue)








