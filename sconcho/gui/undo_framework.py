# -*- coding: utf-8 -*-
######################################################################## #
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

import logging
from copy import copy

from PyQt4.QtCore import (Qt, QPointF, SIGNAL)
from PyQt4.QtGui import (QUndoCommand, QColor)

from sconcho.util.canvas import (get_item_id,
                         chunkify_cell_arrangement,
                         order_selection_by_rows,
                         order_selection_by_columns,
                         shift_item_row_wise,
                         shift_item_column_wise,
                         shift_legend_vertically,
                         shift_selection_vertically,
                         shift_legend_horizontally,
                         shift_selection_horizontally,
                         PatternCanvasEntry)

from sconcho.gui.pattern_canvas_objects import (RepeatLegendItem,
                                        PatternLegendText,
                                        PatternTextItem)

# module lever logger:
logger = logging.getLogger(__name__)


###########################################################################
#
# the following classes encapsulate actions for the Undo/Redo framework
#
###########################################################################
class PasteCellsNew(QUndoCommand):
    """ This class encapsulates the paste action. I.e. all
    items in our copySelection are pasted into the dead Selection.

    NOTE: The calling code has to make sure that deadSelection
    has the proper dimension to fit copySelection.

    """



    def __init__(self, canvas, copySelection, deadSelection,
                 column, row, minCol, minRow, parent = None):

        super(PasteCellsNew, self).__init__(parent)
        self.setText("paste cells")
        self.canvas = canvas
        self.copySelection = copySelection.copy()
        self.deadSelection = deadSelection.copy()
        self.column = column
        self.row = row
        self.minColumn = minCol
        self.minRow = minRow



    def redo(self):
        """ The redo action. """

        # delete previous items
        for entry in self.deadSelection.values():
            item = self.canvas._item_at_row_col(entry.row, entry.column)
            if item:
                self.canvas.removeItem(item)
                del item

        # add new items; shift them to the proper column and row:
        # we shift the upper left corner to (0,0) and then the
        # whole selection to the target location (self.column, self.row)
        for entry in self.copySelection.values():
            column = entry.column - self.minColumn + self.column
            row    = entry.row - self.minRow + self.row

            location = QPointF(column * self.canvas._unitCellDim.width(),
                               row * self.canvas._unitCellDim.height())
            item = self.canvas.create_pattern_grid_item(location,
                                                     column, row,
                                                     entry.width, 1,
                                                     entry.symbol,
                                                     entry.color)
            self.canvas.addItem(item)



    def undo(self):
        """ The undo action. """

        # remove previously pasted cells
        #for colID in range(self.column, self.column + self.numColumns):
        #    for rowID in range(self.row, self.row + self.numRows):
        for entry in self.copySelection.values():
            column = entry.column - self.minColumn + self.column
            row = entry.row - self.minRow + self.row
            item = self.canvas._item_at_row_col(row, column)
            if item:
                self.canvas.removeItem(item)
                del item


        # re-add previously deleted cells
        for entry in self.deadSelection.values():
            column = entry.column
            row = entry.row

            location = QPointF(column * self.canvas._unitCellDim.width(),
                               row * self.canvas._unitCellDim.height())
            item = self.canvas.create_pattern_grid_item(location,
                                                     column, row,
                                                     entry.width, 1,
                                                     entry.symbol,
                                                     entry.color)
            self.canvas.addItem(item)



class PasteCells(QUndoCommand):
    """ This class encapsulates the paste action. I.e. all
    items in our copySelection are pasted into the dead Selection.

    NOTE: The calling code has to make sure that deadSelection
    has the proper dimension to fit copySelection.

    """



    def __init__(self, canvas, copySelection, deadSelection,
                 column, row, numCols, numRows, parent = None):

        super(PasteCells, self).__init__(parent)
        self.setText("paste cells")
        self.canvas = canvas
        self.copySelection = copySelection.copy()
        self.deadSelection = deadSelection.copy()
        self.column = column
        self.row = row
        self.numColumns = numCols
        self.numRows = numRows



    def _get_upper_left(self, selection):
        """ Determines the column and row of the upper left
        corner of the selection.

        """

        rows = []
        cols = []
        for entry in selection:
            cols.append(entry.column)
            rows.append(entry.row)

        return (min(cols), min(rows))



    def redo(self):
        """ The redo action. """

        (upperLeftCol, upperLeftRow) = \
                self._get_upper_left(self.copySelection.values())

        # delete previous items
        for entry in self.deadSelection.values():
            item = self.canvas._item_at_row_col(entry.row, entry.column)
            if item:
                self.canvas.removeItem(item)
                del item

        # add new items; shift them to the proper column and row:
        # we shift the upper left corner to (0,0) and then the
        # whole selection to the target location (self.column, self.row)
        for entry in self.copySelection.values():
            column = entry.column - upperLeftCol + self.column
            row    = entry.row - upperLeftRow + self.row

            location = QPointF(column * self.canvas._unitCellDim.width(),
                               row * self.canvas._unitCellDim.height())
            item = self.canvas.create_pattern_grid_item(location,
                                                     column, row,
                                                     entry.width, 1,
                                                     entry.symbol,
                                                     entry.color)
            self.canvas.addItem(item)



    def undo(self):
        """ The undo action. """

        # remove previously pasted cells
        for colID in range(self.column, self.column + self.numColumns):
            for rowID in range(self.row, self.row + self.numRows):

                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    self.canvas.removeItem(item)
                    del item


        # re-add previously deleted cells
        for entry in self.deadSelection.values():
            column = entry.column
            row = entry.row

            location = QPointF(column * self.canvas._unitCellDim.width(),
                               row * self.canvas._unitCellDim.height())
            item = self.canvas.create_pattern_grid_item(location,
                                                     column, row,
                                                     entry.width, 1,
                                                     entry.symbol,
                                                     entry.color)
            self.canvas.addItem(item)




class InsertRows(QUndoCommand):
    """ This class encapsulates the insertion of a row action. """


    def __init__(self, canvas, rowShift, pivot, mode, parent = None):

        super(InsertRows, self).__init__(parent)
        self.setText("insert row")
        self.canvas = canvas
        self.rowShift = rowShift
        self.numRows = canvas._numRows
        self.rowLabelOffset = canvas._rowLabelOffset
        self.numColumns = canvas._numColumns
        self.unitHeight = self.canvas._unitCellDim.height()
        self.unitWidth = self.canvas._unitCellDim.width()

        if mode == "above":
            self.pivot = pivot
        else:
            self.pivot = pivot + 1



    def redo(self):
        """ The redo action.

        Shift all existing items above or below the pivot
        then insert the new rows.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        shiftedItems = \
            self.canvas._items_in_col_row_range(0, self.numColumns,
                                                self.pivot,
                                                self.numRows)

        for item in shiftedItems:
            shift_item_row_wise(item, self.rowShift, self.unitHeight)

        for row in range(0, self.rowShift):
            self.canvas._create_row(self.pivot + row)

        legendList = list(self.canvas.gridLegend.values()) \
            + list(self.canvas.repeatLegend.values())
        shift_legend_vertically(legendList,
                                self.rowShift,
                                self.unitHeight,
                                self.numColumns,
                                self.unitWidth)

        self.canvas._selectedCells = \
                shift_selection_vertically(self.canvas._selectedCells,
                                           self.pivot, self.rowShift)

        self.redo_adjust_row_repeats(self.pivot, self.rowShift)

        self.canvas._numRows += self.rowShift
        self.finalize()



    def undo(self):
        """ The undo action.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        # NOTE: Shifting up corresponds to a negative row shift
        rowUpShift = -1 * self.rowShift

        # shift first then remove
        legendList = list(self.canvas.gridLegend.values()) \
            + list(self.canvas.repeatLegend.values())
        shift_legend_vertically(legendList,
                                rowUpShift,
                                self.unitHeight,
                                self.numColumns,
                                self.unitWidth)
        self.canvas._selectedCells = \
                shift_selection_vertically(self.canvas._selectedCells,
                                           self.pivot, rowUpShift)

        selection = \
            self.canvas._items_in_col_row_range(0, self.numColumns,
                                                self.pivot,
                                                self.pivot + self.rowShift - 1)
        for item in selection:
            self.canvas.removeItem(item)
            del item

        selection = \
            self.canvas._items_in_col_row_range(0, self.numColumns,
                                                self.pivot + self.rowShift,
                                                self.numRows + self.rowShift)

        for item in selection:
            shift_item_row_wise(item, rowUpShift, self.unitHeight)

        self.undo_adjust_row_repeats(self.pivot, self.rowShift)
        self.canvas._numRows -= self.rowShift
        self.finalize()



    def undo_adjust_row_repeats(self, pivot, rowShift):
        """ Adjust the row repeats such that they are consistent
        with the newly inserted rows.

        If a row is inserted within a row repeat we assume the user
        wants to extend the row repeat itself.

        """

        self.canvas.rowRepeatTracker.shift_and_expand_repeats(pivot,
                                                              -rowShift)



    def redo_adjust_row_repeats(self, pivot, rowShift):
        """ Adjust the row repeats such that they are consistent
        with the newly inserted rows.

        If a row is inserted within a row repeat we assume the user
        wants to extend the row repeat itself.

        """

        self.canvas.rowRepeatTracker.shift_and_expand_repeats(pivot,
                                                              rowShift)



    def finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.finalize_grid_change()
        self.canvas.emit(SIGNAL("scene_changed"))




class DeleteRows(QUndoCommand):
    """ This class encapsulates the deletion of rows. """


    def __init__(self, canvas, deadRows, parent = None):

        super(DeleteRows, self).__init__(parent)
        self.setText("delete row")
        self.canvas = canvas
        self.numRows = canvas._numRows

        self.deadRows = list(deadRows)
        self.deadRows.sort()
        self.deadRows.reverse()
        self.deadRanges = self.compute_dead_ranges()
        self.reverseDeadRanges = list(self.deadRanges)
        self.reverseDeadRanges.reverse()

        self.deadRepeatRows = {}

        self.numColumns = canvas._numColumns
        self.unitHeight = self.canvas._unitCellDim.height()
        self.unitWidth = self.canvas._unitCellDim.width()



    def redo(self):
        """ The redo action.

        Delete items then shift remaining items above or below the pivot

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        self.deletedCells = []
        for (pivot, num) in self.deadRanges:
            self.delete_requested_items(pivot, num)
            self.remove_selected_cells(pivot, num)
            self.redo_shift_remaining_items(pivot, -num)
            self.redo_adjust_row_repeats(pivot, num)
        self.canvas._numRows -= len(self.deadRows)
        self.finalize()



    def undo(self):
        """ The undo action.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        for (pivot, num) in self.reverseDeadRanges:
            self.undo_shift_remaining_items(pivot, num)
            self.undo_adjust_row_repeats(pivot, num)
        self.readd_selected_cells()
        self.readd_deleted_items()
        self.canvas._numRows += len(self.deadRows)
        self.finalize()



    def compute_dead_ranges(self):
        """ Compute the ranges of selected cells to be deleted. """

        deadRanges = []
        prevItem = self.deadRows[0]
        length = 1
        for item in self.deadRows[1:]:
            if prevItem - item == 1:
                length += 1
            else:
                deadRanges.append((prevItem, length))
                length = 1

            prevItem = item

        deadRanges.append((prevItem, length))
        return deadRanges



    def undo_adjust_row_repeats(self, pivot, rowShift):
        """ Adjust the row repeats such that they are consistent
        with the deleted rows.

        """

        self.canvas.rowRepeatTracker.shift_and_expand_repeats(pivot,
                                                              rowShift)
        if pivot in self.deadRepeatRows:
            item = self.deadRepeatRows[pivot]
            self.canvas.rowRepeatTracker.restore_repeat(item)



    def redo_adjust_row_repeats(self, pivot, rowShift):
        """ Adjust the row repeats such that they are consistent
        with the deleted rows.

        """

        item = self.canvas.rowRepeatTracker.change_repeat(pivot, rowShift)
        if item:
            self.deadRepeatRows[pivot] = item

        self.canvas.rowRepeatTracker.shift_and_expand_repeats(pivot,
                                                              -rowShift)



    def delete_requested_items(self, pivot, rowShift):
        """ Delete the requested items. """

        selection = self.canvas._items_in_col_row_range(0, self.numColumns,
                                                        pivot,
                                                        pivot + rowShift - 1)

        for item in selection:
            self.deletedCells.append(PatternCanvasEntry(item.column,
                                                        item.row,
                                                        item.width,
                                                        item.color,
                                                        item.symbol))
            self.canvas.removeItem(item)
            del item



    def remove_selected_cells(self, pivot, rowShift):
        """ Remove the deleted items from the current selection
        (if applicable).

        """

        self.deadSelectedCells = {}
        cellsByRow = \
            order_selection_by_rows(self.canvas._selectedCells.values())
        for rowID in range(pivot, pivot+rowShift):
            if rowID in cellsByRow:
                for entry in cellsByRow[rowID]:
                    entryID = get_item_id(entry.column, entry.row)
                    self.deadSelectedCells[entryID] = entry
                    del self.canvas._selectedCells[entryID]



    def redo_shift_remaining_items(self, pivot, rowUpShift):
        """ Shift all remaining canvas elements to accomodate the
        inserted rows.

        """

        selection = self.canvas._items_in_col_row_range(0, self.numColumns,
                                                        pivot, self.numRows)
        for item in selection:
            shift_item_row_wise(item, rowUpShift, self.unitHeight)

        legendList = list(self.canvas.gridLegend.values()) \
            + list(self.canvas.repeatLegend.values())
        shift_legend_vertically(legendList,
                                rowUpShift,
                                self.unitHeight,
                                self.numColumns,
                                self.unitWidth)
        self.canvas._selectedCells = \
                shift_selection_vertically(self.canvas._selectedCells,
                                           pivot, rowUpShift)



    def undo_shift_remaining_items(self, pivot, rowDownShift):
        """ Shift elements on canvas back to shifting done in redo. """

        # make sure to shift legend and selection first
        legendList = list(self.canvas.gridLegend.values()) \
            + list(self.canvas.repeatLegend.values())
        shift_legend_vertically(legendList,
                                rowDownShift,
                                self.unitHeight,
                                self.numColumns,
                                self.unitWidth)
        self.canvas._selectedCells = \
                shift_selection_vertically(self.canvas._selectedCells,
                                           pivot, rowDownShift)

        shiftItems = self.canvas._items_in_col_row_range(0, self.numColumns,
                                                         pivot, self.numRows)

        for item in shiftItems:
            shift_item_row_wise(item, rowDownShift, self.unitHeight)



    def readd_selected_cells(self):
        """ Re-add the previously deleted selected cells. """

        for (key, entry) in self.deadSelectedCells.items():
            self.canvas._selectedCells[key] = entry



    def readd_deleted_items(self):
        """ Re-add previously deleted items. """

        for entry in self.deletedCells:
            location = QPointF(entry.column * self.unitWidth,
                               entry.row * self.unitHeight)
            item = self.canvas.create_pattern_grid_item(location,
                                                    entry.column,
                                                    entry.row,
                                                    entry.width,
                                                    1,
                                                    entry.symbol,
                                                    entry.color)
            self.canvas.addItem(item)

            # if item was selected, press it
            itemID = get_item_id(entry.column, entry.row)
            if itemID in self.deadSelectedCells:
                item._select()



    def finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.finalize_grid_change()
        self.canvas.emit(SIGNAL("scene_changed"))




class InsertColumns(QUndoCommand):
    """ This class encapsulates the insertion of columns. """


    def __init__(self, canvas, columnShift, pivot, mode, parent = None):

        super(InsertColumns, self).__init__(parent)
        self.setText("insert column")
        self.canvas = canvas
        self.columnShift = columnShift
        self.numRows = canvas._numRows
        self.numColumns = canvas._numColumns
        self.unitHeight = self.canvas._unitCellDim.height()
        self.unitWidth = self.canvas._unitCellDim.width()

        if mode == "left of":
            self.pivot = pivot
        else:
            self.pivot = pivot + 1



    def redo(self):
        """ The redo action.

        Shift all existing items right of or left of the pivot
        then insert the new columns.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        shiftedItems = \
            self.canvas._items_in_col_row_range(self.pivot,
                                                self.numColumns,
                                                0, self.numRows)

        for item in shiftedItems:
            shift_item_column_wise(item, self.columnShift, self.unitWidth)

        for column in range(0, self.columnShift):
            self.canvas._create_column(self.pivot + column)

        legendList = list(self.canvas.gridLegend.values()) \
            + list(self.canvas.repeatLegend.values())
        shift_legend_horizontally(legendList,
                                  self.columnShift,
                                  self.unitWidth,
                                  self.numRows,
                                  self.unitHeight)
        self.canvas._selectedCells = \
                shift_selection_horizontally(self.canvas._selectedCells,
                                             self.pivot,
                                             self.columnShift)

        self.canvas._numColumns += self.columnShift
        self.finalize()



    def undo(self):
        """ The undo action.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        # NOTE: Shifting left corresponds to a negative colunm shift
        columnLeftShift = -1 * self.columnShift

        # shift first then remove
        legendList = list(self.canvas.gridLegend.values()) \
            + list(self.canvas.repeatLegend.values())
        shift_legend_horizontally(legendList,
                                  columnLeftShift,
                                  self.unitWidth,
                                  self.numRows,
                                  self.unitHeight)
        self.canvas._selectedCells = \
                shift_selection_horizontally(self.canvas._selectedCells,
                                             self.pivot, columnLeftShift)

        selection = self.canvas._items_in_col_row_range( \
                          self.pivot,
                          self.pivot + self.columnShift - 1,
                          0, self.numRows)

        for item in selection:
            self.canvas.removeItem(item)
            del item

        # shift the rest back into place
        selection.clear()
        selection = self.canvas._items_in_col_row_range( \
                          self.pivot + self.columnShift,
                          self.numColumns + self.columnShift,
                          0, self.numRows)
        for item in selection:
            shift_item_column_wise(item, columnLeftShift, self.unitWidth)

        self.canvas._numColumns -= self.columnShift
        self.finalize()



    def finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.finalize_grid_change()
        self.canvas.emit(SIGNAL("scene_changed"))




class DeleteColumns(QUndoCommand):
    """ This class encapsulates the deletion of columns. """


    def __init__(self, canvas, deadColumns, parent = None):

        super(DeleteColumns, self).__init__(parent)
        self.setText("delete column")
        self.canvas = canvas
        self.numRows = canvas._numRows
        self.numColumns = canvas._numColumns
        self.unitHeight = self.canvas._unitCellDim.height()
        self.unitWidth = self.canvas._unitCellDim.width()

        self.deadColumns = list(deadColumns)
        self.deadColumns.sort()
        self.deadColumns.reverse()
        self.deadRanges = self.compute_dead_ranges()
        self.reverseDeadRanges = list(self.deadRanges)
        self.reverseDeadRanges.reverse()



    def redo(self):
        """ The redo action.

        Delete items then shift remaining items left of or right of
        the pivot.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        self.deletedCells = []
        for (pivot, num) in self.deadRanges:
            self.delete_requested_items(pivot, num)
            self.remove_selected_cells(pivot, num)
            self.redo_shift_remaining_items(pivot, -num)
        self.canvas._numColumns -= len(self.deadColumns)
        self.finalize()



    def undo(self):
        """ The undo action.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        for (pivot, num) in self.reverseDeadRanges:
            self.undo_shift_remaining_items(pivot, num)
        self.readd_selected_cells()
        self.readd_deleted_items()
        self.canvas._numColumns += len(self.deadColumns)
        self.finalize()



    def compute_dead_ranges(self):
        """ Compute the ranges of selected cells to be deleted. """

        deadRanges = []
        prevItem = self.deadColumns[0]
        length = 1
        for item in self.deadColumns[1:]:
            if prevItem - item == 1:
                length += 1
            else:
                deadRanges.append((prevItem, length))
                length = 1

            prevItem = item

        deadRanges.append((prevItem, length))
        return deadRanges



    def delete_requested_items(self, pivot, columnShift):
        """ Delete the requested items. """

        selection = self.canvas._items_in_col_row_range(pivot,
                                                        pivot + columnShift - 1,
                                                        0,  self.numRows)


        for item in selection:
            self.deletedCells.append(PatternCanvasEntry(item.column,
                                                        item.row,
                                                        item.width,
                                                        item.color,
                                                        item.symbol))
            self.canvas.removeItem(item)
            del item



    def remove_selected_cells(self, pivot, columnShift):
        """ Remove the any deleted items from the current
        selection (if applicable).

        """

        self.deadSelectedCells = {}
        cellsByColumn = order_selection_by_columns(\
            self.canvas._selectedCells.values())
        for colID in range(pivot, pivot+columnShift):
            if colID in cellsByColumn:
                for entry in cellsByColumn[colID]:
                    entryID = get_item_id(entry.column, entry.row)
                    self.deadSelectedCells[entryID] = entry
                    del self.canvas._selectedCells[entryID]



    def redo_shift_remaining_items(self, pivot, columnLeftShift):
        """ Shift all remaining canvas elements to accomodate the
        inserted columns.

        """

        selection = \
            self.canvas._items_in_col_row_range(pivot, self.numColumns,
                                                0,  self.numRows)
        for item in selection:
            shift_item_column_wise(item, columnLeftShift, self.unitWidth)

        legendList = list(self.canvas.gridLegend.values()) \
            + list(self.canvas.repeatLegend.values())
        shift_legend_horizontally(legendList,
                                  columnLeftShift,
                                  self.unitWidth,
                                  self.numRows,
                                  self.unitHeight)
        self.canvas._selectedCells = \
                shift_selection_horizontally(self.canvas._selectedCells,
                                             pivot, columnLeftShift)



    def undo_shift_remaining_items(self, pivot, columnRightShift):
        """ Shift elements on canvas back to shifting done in redo. """

        # make sure to shift legend and selection first
        legendList = list(self.canvas.gridLegend.values()) \
            + list(self.canvas.repeatLegend.values())
        shift_legend_horizontally(legendList,
                                  columnRightShift,
                                  self.unitWidth,
                                  self.numRows,
                                  self.unitHeight)
        self.canvas._selectedCells = \
                shift_selection_horizontally(self.canvas._selectedCells,
                                             pivot, columnRightShift)

        shiftItems = \
            self.canvas._items_in_col_row_range(pivot, self.numColumns,
                                                0, self.numRows)
        for item in shiftItems:
            shift_item_column_wise(item, columnRightShift, self.unitWidth)



    def readd_selected_cells(self):
        """ Re-add previously deleted selected cells. """

        for (key, entry) in self.deadSelectedCells.items():
            self.canvas._selectedCells[key] = entry



    def readd_deleted_items(self):
        """ Re-add previously deleted items. """

        for entry in self.deletedCells:
            location = QPointF(entry.column * self.unitWidth,
                               entry.row * self.unitHeight)
            item = \
                 self.canvas.create_pattern_grid_item(location,
                                                      entry.column,
                                                      entry.row,
                                                      entry.width,
                                                      1,
                                                      entry.symbol,
                                                      entry.color)
            self.canvas.addItem(item)

            # if item was selected, press it
            itemID = get_item_id(entry.column, entry.row)
            if itemID in self.deadSelectedCells:
                item._select()



    def finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.finalize_grid_change()
        self.canvas.emit(SIGNAL("scene_changed"))



class ActivateSymbol(QUndoCommand):
    """ This class encapsulates the management of the currently
    active knitting symbol.

    """


    def __init__(self, canvas, newSymbol, parent = None):


        super(ActivateSymbol, self).__init__(parent)
        self.setText("activate symbol")
        self.canvas = canvas
        self.oldSymbol = canvas._activeSymbol
        self.newSymbol = newSymbol



    def redo(self):
        """ The redo action. """

        self.canvas._activeSymbol = self.newSymbol

        if self.newSymbol:
            self.canvas.emit(SIGNAL("activate_symbol"), self.newSymbol)
        else:
            self.canvas.emit(SIGNAL("unactivate_symbol"))

        # only paint if we have selected cells
        if self.canvas._selectedCells:
            self.canvas.paint_cells()



    def undo(self):
        """ The undo action. """

        self.canvas._activeSymbol = self.oldSymbol

        if self.oldSymbol:
            self.canvas.emit(SIGNAL("activate_symbol"), self.oldSymbol)
        else:
            self.canvas.emit(SIGNAL("unactivate_symbol"))




class ActivateColor(QUndoCommand):
    """ This class encapsulates the management of the currently
    active color.

    """


    def __init__(self, canvas, newColorObject, newColor = None,
                 parent = None):

        super(ActivateColor, self).__init__(parent)
        self.setText("activate color")
        self.canvas = canvas

        self.oldColorObject = canvas._activeColorObject
        if self.oldColorObject:
            self.oldColor = canvas._activeColorObject.color

        self.newColorObject = newColorObject
        if newColor:
            self.newColor = newColor
        else:
            self.newColor = newColorObject.color



    def redo(self):
        """ The redo action. """

        self.canvas._activeColorObject = self.newColorObject
        self.canvas._activeColorObject.color = self.newColor
        self.canvas.emit(SIGNAL("activate_color_selector"),
                         self.newColorObject)




    def undo(self):
        """ The undo action. """

        # we need this check to make sure that we don't call
        # with a None color object before the stack unwinds
        if self.oldColorObject:
            self.oldColorObject.color = self.oldColor
            self.canvas._activeColorObject = self.oldColorObject
            self.canvas.emit(SIGNAL("activate_color_selector"),
                             self.oldColorObject)



class PaintCells(QUndoCommand):
    """ This class encapsulates the canvas paint action. I.e. all
    currently selected cells are painted with the currently
    active symbol.

    """


    def __init__(self, canvas, selectedCells = None, unselectedCells = None,
                 parent = None):

        super(PaintCells, self).__init__(parent)
        self.setText("paint cells")
        self.canvas = canvas
        self.oldSelection = {}
        self.newSelection = {}

        if selectedCells:
            self.selectedCells = list(selectedCells)
        else:
            self.selectedCells = None

        if unselectedCells:
            self.unselectedCells = list(unselectedCells)
        else:
            self.unselectedCells = None

        self.activeSymbol = canvas._activeSymbol
        self.activeColor = canvas._activeColorObject.color
        self.didInsertActiveSymbol = False


    def redo(self):
        """ This is the redo action. """

        self._redo_selectedCells()
        self._redo_unselectedCells()

        # without an active symbol we are done
        if self.activeSymbol:
            self._redo_paintActiveSymbol()



    def undo(self):
        """ This is the undo action. """


        # only do this if we previously inserted an active
        # symbol in redo
        if self.didInsertActiveSymbol:
            self._undo_paintActiveSymbol()

        self._undo_selectedCells()
        self._undo_unselectedCells()



    def _redo_selectedCells(self):
        """ Redo action for selected cells. """

        if self.selectedCells:
            for item in self.selectedCells:
                itemID = get_item_id(item.column, item.row)
                self.canvas._selectedCells[itemID] = item
                item = self.canvas._item_at_row_col(item.row, item.column)
                if item:
                    item._select()



    def _redo_unselectedCells(self):
        """ Redo action for unselected cells """

        # if we have inactivated cells, remove them
        if self.unselectedCells:
            for item in self.unselectedCells:
                itemID = get_item_id(item.column, item.row)
                if itemID in self.canvas._selectedCells:
                    del self.canvas._selectedCells[itemID]
                else:
                    errorString = ("_redo_unselectedCells: trying to delete "
                                   "invalid selected cell.")
                    logger.error(errorString)

                item = self.canvas._item_at_row_col(item.row, item.column)
                if item:
                    item._unselect()



    def _redo_paintActiveSymbol(self):
        """ Redo action for painting the active symbol into
        selected cells.

        """

        self.oldSelection = self.canvas._selectedCells.copy()
        self.activeSymbolContent = self.activeSymbol.get_content()
        self.width = int(self.activeSymbolContent["width"])

        chunks = chunkify_cell_arrangement(self.width, self.oldSelection)
        if chunks:
            self.didInsertActiveSymbol = True

            # FIXME: This might require a bit more thinking
            # If the symbol itself provides a color other than
            # white it overrides the active color
            if "backgroundColor" in self.activeSymbolContent:
                itemColor = QColor(self.activeSymbolContent["backgroundColor"])
            else:
                itemColor = self.activeColor

            for chunk in chunks:
                totalWidth = 0

                # location of leftmost item in chunk
                column = chunk[0].column
                row = chunk[0].row
                item = self.canvas._item_at_row_col(row, column)
                if item:
                    origin = item.pos()
                else:
                    errorString = ("_redo_paintActiveSymbol: trying to find "
                                   "origin of nonexistent item.")
                    logger.error(errorString)

                # compute total width and remove old items
                for entry in chunk:
                    totalWidth += entry.width
                    gridItem = self.canvas._item_at_row_col(entry.row,
                                                            entry.column)
                    if gridItem:
                        self.canvas.removeItem(gridItem)
                        del gridItem
                    else:
                        errorString = ("_redo_paintActiveSymbol: trying to delete "
                                       "nonexistent item.")
                        logger.error(errorString)


                # insert as many new items as we can fit
                numNewItems = int(totalWidth/self.width)
                for i in range(0, numNewItems):
                    item = self.canvas.create_pattern_grid_item(origin,
                                column, row, self.width, 1,
                                self.activeSymbolContent, itemColor)
                    self.canvas.addItem(item)

                    itemID = get_item_id(column, row)

                    self.newSelection[itemID] = \
                            PatternCanvasEntry(column, row, self.width,
                                               itemColor,
                                               self.activeSymbolContent)

                    origin = QPointF(origin.x() + (self.width * \
                                     self.canvas._unitCellDim.width()),
                                     origin.y())
                    column = column + self.width

                self.canvas._selectedCells.clear()



    def _undo_selectedCells(self):
        """ Undo action for selected cells """

        # remove previously activated items
        if self.selectedCells:
            for item in self.selectedCells:
                itemID = get_item_id(item.column, item.row)
                if itemID in self.canvas._selectedCells:
                    del self.canvas._selectedCells[itemID]
                else:
                    errorString = ("_undo_unselectedCells: trying to delete "
                                   "invalid selected cell.")
                    logger.error(errorString)

                item = self.canvas._item_at_row_col(item.row, item.column)
                if item:
                    item._unselect()



    def _undo_unselectedCells(self):
        """ Undo action for unseleced cells """

        if self.unselectedCells:
            for item in self.unselectedCells:
                itemID = get_item_id(item.column, item.row)
                self.canvas._selectedCells[itemID] = item
                item = self.canvas._item_at_row_col(item.row, item.column)
                if item:
                    item._select()



    def _undo_paintActiveSymbol(self):
        """ Undo action for painting the active symbol. """

        # get rid of previous selection
        for entry in self.newSelection.values():
            gridItem = self.canvas._item_at_row_col(entry.row,
                                                    entry.column)
            if gridItem:
                self.canvas.removeItem(gridItem)
                del gridItem
            else:
                errorString = ("_undo_paintActiveSymbol: trying to delete "
                               "nonexistent item.")
                logger.error(errorString)


        # re-insert previous selection
        for entry in self.oldSelection.values():
            column = entry.column
            row    = entry.row
            location = QPointF(column * self.canvas._unitCellDim.width(),
                            row * self.canvas._unitCellDim.height())

            item = self.canvas.create_pattern_grid_item(location,
                                                    column, row,
                                                    entry.width,
                                                    1,
                                                    entry.symbol,
                                                    entry.color)

            self.canvas.addItem(item)
            item._select()

        self.canvas._selectedCells = self.oldSelection



class MoveCanvasItem(QUndoCommand):
    """ This class encapsulates the movement of legend items
    (PatternLabelItem or PatternLabelText).

    """


    def __init__(self, canvasItem, oldPosition, newPosition, parent = None):

        super(MoveCanvasItem, self).__init__(parent)
        self.setText("move legend item")

        self.canvasItem = canvasItem

        self.oldPosition = oldPosition
        self.newPosition = newPosition



    def redo(self):
        """ The redo action. """

        self.canvasItem.setPos(self.newPosition)



    def undo(self):
        """ The undo action. """

        self.canvasItem.setPos(self.oldPosition)




class AddPatternRepeatLegend(QUndoCommand):
    """ This class encapsulates the creation of a legend for a
    pattern repeat item the canvas.

    """

    def __init__(self, canvas, pathItem, parent = None):

        super(AddPatternRepeatLegend, self).__init__(parent)

        self.canvas = canvas
        self.pathItem = pathItem
        self.legendText = "pattern repeat"

        self.legendItem = RepeatLegendItem(self.pathItem.color)
        self.legendTextItem = PatternLegendText(self.legendText)

        yCoord = self.canvas._get_legend_y_coordinate_for_placement()
        self.itemPos = QPointF(0, yCoord + self.legendItem.height + 30)
        self.textPos = QPointF(self.legendItem.width + 30,
                               yCoord + self.legendItem.height + 20)



    def redo(self):

        self.canvas.addItem(self.legendItem)
        self.legendItem.setPos(self.itemPos)
        self.legendItem.update()

        self.canvas.addItem(self.legendTextItem)
        self.legendTextItem.setPos(self.textPos)
        self.legendTextItem.setFont(self.canvas.settings.legendFont.value)
        self.legendTextItem.update()

        if self.pathItem.hasLegend:
            visible = 1
        else:
            visible = 0
        self.canvas.repeatLegend[self.pathItem.itemID] = \
            (visible, self.legendItem, self.legendTextItem)



    def undo(self):

        self.itemPos = self.legendItem.scenePos()
        self.textPos = self.legendTextItem.scenePos()
        self.legendText = self.legendTextItem.toPlainText()

        self.canvas.removeItem(self.legendItem)
        self.canvas.removeItem(self.legendTextItem)
        del self.canvas.repeatLegend[self.pathItem.itemID]




class DeletePatternRepeatLegend(QUndoCommand):
    """ This class encapsulates the deletion of a legend for a
    pattern repeat item the canvas.

    """

    def __init__(self, canvas, pathItem, parent = None):

        super(DeletePatternRepeatLegend, self).__init__(parent)

        self.canvas = canvas
        self.pathItem = pathItem

        (self.visibility, self.legendItem, self.legendTextItem) = \
                self.canvas.repeatLegend[self.pathItem.itemID]



    def redo(self):

        # store position and content
        self.itemPos = self.legendItem.scenePos()
        self.textPos = self.legendTextItem.scenePos()
        self.legendText = self.legendTextItem.toPlainText()

        self.canvas.removeItem(self.legendItem)
        self.canvas.removeItem(self.legendTextItem)
        del self.canvas.repeatLegend[self.pathItem.itemID]



    def undo(self):

        # restore items at proper position and text
        self.canvas.addItem(self.legendItem)
        self.legendItem.setPos(self.itemPos)
        self.legendItem.update()

        self.canvas.addItem(self.legendTextItem)
        self.legendTextItem.setPos(self.textPos)
        self.legendTextItem.setFont(self.canvas.settings.legendFont.value)
        self.legendTextItem.update()

        self.canvas.repeatLegend[self.pathItem.itemID] = \
            (self.visibility, self.legendItem, self.legendTextItem)





class EditPatternRepeatLegend(QUndoCommand):
    """ This class encapsulates the editing of a legend for a
    pattern repeat item the canvas.

    """

    def __init__(self, canvas, pathItem, legendVisibility, parent = None):

        super(EditPatternRepeatLegend, self).__init__(parent)

        self.canvas = canvas
        self.pathItem = pathItem
        self.newColor = pathItem.color
        self.shownInLegend = pathItem.hasLegend
        if legendVisibility == Qt.Checked:
            self.newLegendVisibility = True
        else:
            self.newLegendVisibility = False



    def redo(self):
        """ redoing when editing a pattern repeat legend boils
        down to three cases:

        1) we don't want to show a legend but currently have one:
           store values of legend and then remove it. Note: We have
           to store positions and text within the PatternRepeatItem
           itself since these values won't persist between
           EditPatternRepeatLegend actions

        2) we don't want to show a legend and don't have one:
           nothing to do

        3) we want to show a legend and have one:
           update the legend color, that's it

        """

        (visbility, self.legendItem, self.legendTextItem) = \
            self.canvas.repeatLegend[self.pathItem.itemID]

        self.oldColor = self.legendItem.color
        self.legendItem.color = self.newColor
        self.legendItem.update()

        if self.shownInLegend and not self.newLegendVisibility:
            self.legendItem.hide()
            self.legendTextItem.hide()
            self.pathItem.hasLegend = False
            self.canvas.repeatLegend[self.pathItem.itemID] = \
                (0, self.legendItem, self.legendTextItem)

        elif not self.shownInLegend and self.newLegendVisibility:
            self.legendItem.show()
            self.legendTextItem.show()
            self.pathItem.hasLegend = True
            self.canvas.repeatLegend[self.pathItem.itemID] = \
                (1, self.legendItem, self.legendTextItem)



    def undo(self):
        """ See redo for an explanation of the possible actions. """


        self.legendItem.color = self.oldColor
        self.legendItem.update()

        if self.shownInLegend and not self.newLegendVisibility:
            self.legendItem.show()
            self.legendTextItem.show()
            self.pathItem.hasLegend = True
            self.canvas.repeatLegend[self.pathItem.itemID] = \
                (1, self.legendItem, self.legendTextItem)
        elif not self.shownInLegend and self.newLegendVisibility:
            self.legendItem.hide()
            self.legendTextItem.hide()
            self.pathItem.hasLegend = False
            self.canvas.repeatLegend[self.pathItem.itemID] = \
                (0, self.legendItem, self.legendTextItem)




class AddPatternRepeat(QUndoCommand):
    """ This class encapsulates the creation of a pattern repeat
    item on the canvas.

    """

    def __init__(self, canvas, patternRepeat, parent = None):

        super(AddPatternRepeat, self).__init__(parent)

        self.canvas = canvas
        self.patternRepeat = patternRepeat
        self.unselectedCells = list(canvas._selectedCells.values())



    def redo(self):
        """ The redo action. """

        self.canvas.addItem(self.patternRepeat)
        self.canvas.patternRepeats.add(self.patternRepeat)

        # unselect the currently selected cells
        if self.unselectedCells:
            for item in self.unselectedCells:
                itemID = get_item_id(item.column, item.row)
                if itemID in self.canvas._selectedCells:
                    del self.canvas._selectedCells[itemID]
                else:
                    errString = ("AddPatternRepeat.redo: trying to delete "
                                   "invalid selected cell.")
                    logger.error(errString)

                item = self.canvas._item_at_row_col(item.row, item.column)
                if item:
                    item._unselect()



    def undo(self):
        """ The undo action. """

        self.canvas.removeItem(self.patternRepeat)
        self.canvas.patternRepeats.remove(self.patternRepeat)

        # reselect the previously unselected cells again
        if self.unselectedCells:
            for item in self.unselectedCells:
                itemID = get_item_id(item.column, item.row)
                self.canvas._selectedCells[itemID] = item
                item = self.canvas._item_at_row_col(item.row, item.column)
                if item:
                    item._select()




class EditPatternRepeat(QUndoCommand):
    """ This class encapsulates the editing of a pattern repeat
    item on the canvas.

    """


    def __init__(self, patternRepeat, newColor, newWidth, parent = None):

        super(EditPatternRepeat, self).__init__(parent)

        self.patternRepeat = patternRepeat
        self.oldColor = patternRepeat.color
        self.oldWidth = patternRepeat.width
        self.newColor = newColor
        self.newWidth = newWidth



    def redo(self):
        """ The redo action. """

        self.patternRepeat.set_properties(self.newColor, self.newWidth)



    def undo(self):
        """ The undo action. """

        self.patternRepeat.set_properties(self.oldColor, self.oldWidth)




class DeletePatternRepeat(QUndoCommand):
    """ This class encapsulates the deletion of a pattern repeat
    item on the canvas.

    """


    def __init__(self, canvas, patternRepeat, parent = None):

        super(DeletePatternRepeat, self).__init__(parent)

        self.canvas = canvas
        self.patternRepeat = patternRepeat


    def redo(self):
        """ The redo action. """

        self.canvas.removeItem(self.patternRepeat)
        self.canvas.patternRepeats.remove(self.patternRepeat)



    def undo(self):
        """ The undo action. """

        self.canvas.addItem(self.patternRepeat)
        self.canvas.patternRepeats.add(self.patternRepeat)       




class ColorSelectedCells(QUndoCommand):
    """ This class encapsulates coloring of all currently
    selected cells on the canvas.

    """


    def __init__(self, canvas, color = None, parent = None):

        super(ColorSelectedCells, self).__init__(parent)

        self.setText("color selected cells")
        self.canvas = canvas

        # this keeps a dictionary of cell colors
        # of all selected items
        self.previousColors = {}

        self.selectedCells = canvas._selectedCells.copy()

        if color:
            self.activeColor = color
        else:
            self.activeColor = canvas._activeColorObject.color



    def redo(self):
        """ This is the redo action.
        NOTE: Since we don't destroy/create items but just change
        their color, we have to take charge of adding/removing them
        from the legend.

        """

        for (id, item) in self.selectedCells.items():
            self.previousColors[id] = item.color
            canvasItem = self.canvas._item_at_row_col(item.row, item.column)
            if item.symbol["name"] == "nostitch":
                canvasItem.change_color(item.color)
            else:
                self.canvas.remove_from_legend(item)
                canvasItem.change_color(self.activeColor)
                item.color = self.activeColor
                self.canvas.add_to_legend(item)



    def undo(self):
        """ This is the undo action.
        NOTE: Since we don't destroy/create items but just change
        their color, we have to take charge of adding/removing them
        from the legend.

        """

        for (id, item) in self.selectedCells.items():
            previousColor = self.previousColors[id]
            canvasItem = self.canvas._item_at_row_col(item.row, item.column)
            canvasItem.change_color(previousColor)
            if item.symbol["name"] != "nostitch":
                self.canvas.remove_from_legend(item)
                item.color = previousColor
                self.canvas.add_to_legend(item)





class AddRowRepeat(QUndoCommand):
    """ This class encapsulates the creation of a row repeat
    item on the canvas.

    """

    def __init__(self, canvas, multiplicity, parent = None):

        super(AddRowRepeat, self).__init__(parent)

        self.canvas = canvas
        self.rowRepeatTracker = canvas.rowRepeatTracker
        self.rows = canvas.marked_rows() #.keys()
        self.multiplicity = multiplicity



    def redo(self):
        """ The redo action. """

        self.rowRepeatTracker.add_repeat(self.rows, self.multiplicity)
        self.canvas.set_up_labels()




    def undo(self):
        """ The undo action. """

        self.rowRepeatTracker.delete_repeat(self.rows)
        self.canvas.set_up_labels()




class DeleteRowRepeat(QUndoCommand):
    """ This class encapsulates the deletion of a row repeat
    item on the canvas.

    """

    def __init__(self, canvas, parent = None):

        super(DeleteRowRepeat, self).__init__(parent)

        self.canvas = canvas
        self.rowRepeatTracker = canvas.rowRepeatTracker

        firstRow = canvas.marked_rows()[0] #.keys()[0]
        (rowRange, multiplicity, dummy) = self.rowRepeatTracker[firstRow]

        self.multiplicity = multiplicity
        self.rows = list(rowRange)



    def redo(self):
        """ The redo action. """

        self.rowRepeatTracker.delete_repeat(self.rows)
        self.canvas.set_up_labels()



    def undo(self):
        """ The undo action. """

        self.rowRepeatTracker.add_repeat(self.rows, self.multiplicity)
        self.canvas.set_up_labels()




class AddTextBox(QUndoCommand):
    """ This class encapsulates the addition of a text box
    item on the canvas.

    """

    def __init__(self, canvas, itemPos, itemText, parent = None):

        super(AddTextBox, self).__init__(parent)

        self.canvas = canvas
        self.itemPos = itemPos
        self.itemText = itemText

        self.textItem = PatternTextItem(self.itemText)
        if not self.itemPos:
            yMax = self.canvas._get_legend_y_coordinate_for_placement()
            self.itemPos = QPointF(0, yMax + self.canvas._unitCellDim.height() + 10)
        self.textItem.setPos(self.itemPos)
        self.textItem.setFont(self.canvas.settings.legendFont.value)



    def redo(self):
        """ The redo action. """

        self.canvas.addItem(self.textItem)
        self.canvas.canvasTextBoxes[self.textItem] = self.textItem



    def undo(self):
        """ The undo action. """

        if self.textItem:
            self.canvas.removeItem(self.textItem)
            del self.canvas.canvasTextBoxes[self.textItem]



class DeleteTextBox(QUndoCommand):
    """ This class encapsulates the deletion of a text box
    item on the canvas.

    """

    def __init__(self, canvas, deadTextBox, parent = None):

        super(DeleteTextBox, self).__init__(parent)

        self.canvas = canvas
        self.textItem = deadTextBox



    def redo(self):
        """ The redo action. """

        if self.textItem:
            self.canvas.removeItem(self.textItem)
            del self.canvas.canvasTextBoxes[self.textItem]



    def undo(self):
        """ The undo action. """

        self.canvas.addItem(self.textItem)
        self.canvas.canvasTextBoxes[self.textItem] = self.textItem
