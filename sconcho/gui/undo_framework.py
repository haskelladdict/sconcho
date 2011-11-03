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

from PyQt4.QtCore import (Qt, 
                          QPointF, 
                          SIGNAL, 
                          QString) 
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

from sconcho.util.misc import (errorLogger)


###########################################################################
#
# the following classes encapsulate actions for the Undo/Redo framework
#
###########################################################################
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
                                                     self.canvas._unitCellDim, 
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
                                                     self.canvas._unitCellDim, 
                                                     column, row,
                                                     entry.width, 1,
                                                     entry.symbol, 
                                                     entry.color)
            self.canvas.addItem(item)




class InsertRow(QUndoCommand):
    """ This class encapsulates the insertion of a row action. """


    def __init__(self, canvas, rowShift, pivot, mode, parent = None):

        super(InsertRow, self).__init__(parent)
        self.setText("insert row")
        self.canvas = canvas
        self.rowShift = rowShift
        self.numRows = canvas._numRows
        self.rowLabelOffset = canvas._rowLabelOffset
        self.numColumns = canvas._numColumns
        self.unitHeight = self.canvas._unitCellDim.height()
        self.unitWidth = self.canvas._unitCellDim.width()

        if mode == QString("above"):
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
    
        shiftedItems = set()
        for colID in range(0, self.numColumns):
            for rowID in range(self.pivot, self.numRows):
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    shiftedItems.add(item)

        for item in shiftedItems:
            shift_item_row_wise(item, self.rowShift, self.unitHeight)

        for row in range(0, self.rowShift):
            self.canvas._create_row(self.pivot + row)

        shift_legend_vertically(self.canvas.gridLegend, self.rowShift, 
                                self.unitHeight, self.numColumns, self.unitWidth)

        self.canvas._selectedCells = \
                shift_selection_vertically(self.canvas._selectedCells, self.pivot, 
                                           self.rowShift)
        
        self.canvas._numRows += self.rowShift
        self._finalize()



    def undo(self):
        """ The undo action.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.
        
        """

        # NOTE: Shifting up corresponds to a negative row shift
        rowUpShift = -1 * self.rowShift

        # shift first then remove
        shift_legend_vertically(self.canvas.gridLegend, rowUpShift, 
                                self.unitHeight, self.numColumns, self.unitWidth)
        self.canvas._selectedCells = \
                shift_selection_vertically(self.canvas._selectedCells, self.pivot, 
                                           rowUpShift)

        # remove all previously inserted rows
        selection = set()
        for colID in range(0, self.numColumns):
            for rowID in range(self.pivot, self.pivot + self.rowShift):
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    selection.add(item)

        for item in selection:
            self.canvas.removeItem(item)
            del item

        # shift the rest back into place
        selection.clear()
        for colID in range(0, self.numColumns):
            for rowID in range(self.pivot + self.rowShift, 
                               self.numRows + self.rowShift):
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    selection.add(item)

        for item in selection:
            shift_item_row_wise(item, rowUpShift, self.unitHeight)
 
        self.canvas._numRows -= self.rowShift
        self._finalize()
       


    def _finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.finalize_grid_change()
        self.canvas.emit(SIGNAL("adjust_view"))
        self.canvas.emit(SIGNAL("scene_changed"))

        # NOTE: We need to propagate the canvas' values for
        # numRows, rowLabelOffset
        self.canvas.insertDeleteRowColDialog.set_row_limit( \
                self.canvas._rowLabelOffset, self.canvas._numRows)




class DeleteRow(QUndoCommand):
    """ This class encapsulates the deletion of rows. """


    def __init__(self, canvas, rowShift, pivot, mode, parent = None):

        super(DeleteRow, self).__init__(parent)
        self.setText("delete row")
        self.canvas = canvas
        self.rowShift = rowShift
        self.pivot = pivot
        self.mode = mode
        self.numRows = canvas._numRows
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

        # deleting always implies shifting some things up
        rowUpShift = -1 * self.rowShift

        if self.mode == "above":
            deleteRange = range(self.pivot - self.rowShift, self.pivot)
            shiftRange = range(self.pivot, self.numRows)
        else:
            deleteRange = range(self.pivot, self.pivot + self.rowShift)
            shiftRange = range(self.pivot + self.rowShift, self.numRows)


        self._delete_requested_items(deleteRange)
        self._remove_selected_cells(deleteRange)
        self._redo_shift_remaining_items(shiftRange, rowUpShift)
        self.canvas._numRows -= self.rowShift
        self._finalize()
       


    def undo(self):
        """ The undo action.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        if self.mode == "above":
            shiftRange  = range(self.pivot - self.rowShift, 
                                self.numRows - self.rowShift)
        else:
            shiftRange  = range(self.pivot, self.numRows - self.rowShift)

            
        self._undo_shift_remaining_items(shiftRange)
        self._readd_selected_cells()
        self._readd_deleted_items()
        self.canvas._numRows += self.rowShift
        self._finalize()
       


    def _delete_requested_items(self, deleteRange):
        """ Delete the requested items. """ 
      
        selection = set()
        for colID in range(0, self.numColumns):
            for rowID in deleteRange:
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    selection.add(item)

        self.deletedCells = []
        for item in selection:
            self.deletedCells.append(PatternCanvasEntry(item.column, item.row, 
                                                        item.width, item.color,
                                                        item.symbol))
            self.canvas.removeItem(item)
            del item



    def _remove_selected_cells(self, deleteRange):
        """ Remove the deleted items from the current selection
        (if applicable).

        """

        self.deadSelectedCells = {}
        cellsByRow = order_selection_by_rows(self.canvas._selectedCells.values())
        for rowID in deleteRange:
            if rowID in cellsByRow:
                for entry in cellsByRow[rowID]:
                    entryID = get_item_id(entry.column, entry.row)
                    self.deadSelectedCells[entryID] = entry
                    del self.canvas._selectedCells[entryID]



    def _redo_shift_remaining_items(self, shiftRange, rowUpShift):
        """ Shift all remaining canvas elements to accomodate the
        inserted rows.

        """

        selection = set()
        for colID in range(0, self.numColumns):
            for rowID in shiftRange:
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    selection.add(item)

        for item in selection:
            shift_item_row_wise(item, rowUpShift, self.unitHeight)

        shift_legend_vertically(self.canvas.gridLegend, rowUpShift, 
                                self.unitHeight, self.numColumns, self.unitWidth)
        self.canvas._selectedCells = \
                shift_selection_vertically(self.canvas._selectedCells, self.pivot, 
                                           rowUpShift)



    def _undo_shift_remaining_items(self, shiftRange):
        """ Shift elements on canvas back to shifting done in redo. """

        # make sure to shift legend and selection first
        shift_legend_vertically(self.canvas.gridLegend, self.rowShift, 
                                self.unitHeight, self.numColumns, self.unitWidth)
        self.canvas._selectedCells = \
                shift_selection_vertically(self.canvas._selectedCells, self.pivot, 
                                           self.rowShift)

        shiftItems = set()
        for colID in range(0, self.numColumns):
            for rowID in shiftRange:
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    shiftItems.add(item)

        for item in shiftItems:
            shift_item_row_wise(item, self.rowShift, self.unitHeight)

            

    def _readd_selected_cells(self):
        """ Re-add the previously deleted selected cells. """
        
        for (key, entry) in self.deadSelectedCells.items():
            self.canvas._selectedCells[key] = entry



    def _readd_deleted_items(self):
        """ Re-add previously deleted items. """

        for entry in self.deletedCells:
            location = QPointF(entry.column * self.unitWidth,
                               entry.row * self.unitHeight)
            item = self.canvas.create_pattern_grid_item(location, 
                                                    self.canvas._unitCellDim,
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



    def _finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.finalize_grid_change()
        self.canvas.emit(SIGNAL("adjust_view"))
        self.canvas.emit(SIGNAL("scene_changed"))

        # NOTE: We need to propagate the canvas' values for
        # numRows, rowLabelOffset
        self.canvas.insertDeleteRowColDialog.set_row_limit( \
                self.canvas._rowLabelOffset, self.canvas._numRows)



class InsertColumn(QUndoCommand):
    """ This class encapsulates the insertion of columns. """


    def __init__(self, canvas, columnShift, pivot, mode, parent = None):

        super(InsertColumn, self).__init__(parent)
        self.setText("insert column")
        self.canvas = canvas
        self.columnShift = columnShift
        self.numRows = canvas._numRows
        self.numColumns = canvas._numColumns
        self.unitHeight = self.canvas._unitCellDim.height()
        self.unitWidth = self.canvas._unitCellDim.width()

        if mode == QString("left of"):
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
    
        shiftedItems = set()
        for rowID in range(0, self.numRows):
            for colID in range(self.pivot, self.numColumns):
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    shiftedItems.add(item)

        for item in shiftedItems:
            shift_item_column_wise(item, self.columnShift, self.unitWidth)

        for column in range(0, self.columnShift):
            self.canvas._create_column(self.pivot + column)

        shift_legend_horizontally(self.canvas.gridLegend, self.columnShift, 
                                  self.unitWidth, self.numColumns, self.unitHeight)
        self.canvas._selectedCells = \
                shift_selection_horizontally(self.canvas._selectedCells, self.pivot, 
                                             self.columnShift)
        
        self.canvas._numColumns += self.columnShift
        self._finalize()



    def undo(self):
        """ The undo action.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        # NOTE: Shifting left corresponds to a negative colunm shift
        columnLeftShift = -1 * self.columnShift

        # shift first then remove
        shift_legend_horizontally(self.canvas.gridLegend, columnLeftShift, 
                                  self.unitWidth, self.numRows, self.unitHeight)
        self.canvas._selectedCells = \
                shift_selection_horizontally(self.canvas._selectedCells, 
                                             self.pivot, columnLeftShift)

        # remove all previously inserted columns
        selection = set()
        for rowID in range(0, self.numRows):
            for colID in range(self.pivot, self.pivot + self.columnShift):
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    selection.add(item)

        for item in selection:
            self.canvas.removeItem(item)
            del item

        # shift the rest back into place
        selection.clear()
        for rowID in range(0, self.numRows):
            for colID in range(self.pivot + self.columnShift, 
                               self.numColumns + self.columnShift):
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    selection.add(item)

        for item in selection:
            shift_item_column_wise(item, columnLeftShift, self.unitWidth)
 
        self.canvas._numColumns -= self.columnShift
        self._finalize()
       


    def _finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.finalize_grid_change()
        self.canvas.emit(SIGNAL("adjust_view"))
        self.canvas.emit(SIGNAL("scene_changed"))
        self.canvas.insertDeleteRowColDialog.set_upper_column_limit( \
                self.canvas._numColumns)





class DeleteColumn(QUndoCommand):
    """ This class encapsulates the deletion of columns. """


    def __init__(self, canvas, columnShift, pivot, mode, parent = None):

        super(DeleteColumn, self).__init__(parent)
        self.setText("delete column")
        self.canvas = canvas
        self.columnShift = columnShift
        self.pivot = pivot
        self.mode = mode
        self.numRows = canvas._numRows
        self.numColumns = canvas._numColumns
        self.unitHeight = self.canvas._unitCellDim.height()
        self.unitWidth = self.canvas._unitCellDim.width()



    def redo(self):
        """ The redo action. 
        
        Delete items then shift remaining items left of or right of
        the pivot.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.
        
        """

        # deleting always implies shifting some things to the left
        columnLeftShift = -1 * self.columnShift

        if self.mode == "left of":
            deleteRange = range(self.pivot - self.columnShift, self.pivot)
            shiftRange = range(self.pivot, self.numColumns)
        else:
            deleteRange = range(self.pivot, self.pivot + self.columnShift)
            shiftRange = range(self.pivot + self.columnShift, self.numColumns)


        self._delete_requested_items(deleteRange)
        self._remove_selected_cells(deleteRange)
        self._redo_shift_remaining_items(shiftRange, columnLeftShift)
        self.canvas._numColumns -= self.columnShift
        self._finalize()
       


    def undo(self):
        """ The undo action.

        NOTE: When selecting items in loops over columns/rows
        we need to use a set in order to avoid duplicated
        elements.

        """

        if self.mode == "left of":
            shiftRange  = range(self.pivot - self.columnShift, 
                                self.numColumns - self.columnShift)
        else:
            shiftRange  = range(self.pivot, self.numColumns - self.columnShift)


        self._undo_shift_remaining_items(shiftRange)
        self._readd_selected_cells()
        self._readd_deleted_items()
        self.canvas._numColumns += self.columnShift
        self._finalize()
       


    def _delete_requested_items(self, deleteRange):
        """ Delete the requested items. """
        
        selection = set()
        for rowID in range(0, self.numRows):
            for colID in deleteRange:
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    selection.add(item)

        self.deletedCells = []
        for item in selection:
            self.deletedCells.append(PatternCanvasEntry(item.column, item.row, 
                                                        item.width, item.color, 
                                                        item.symbol))
            self.canvas.removeItem(item)
            del item



    def _remove_selected_cells(self, deleteRange):
        """ Remove the any deleted items from the current
        selection (if applicable).

        """
        
        self.deadSelectedCells = {}
        cellsByColumn = order_selection_by_columns(\
            self.canvas._selectedCells.values())
        for colID in deleteRange:
            if colID in cellsByColumn:
                for entry in cellsByColumn[colID]:
                    entryID = get_item_id(entry.column, entry.row)
                    self.deadSelectedCells[entryID] = entry
                    del self.canvas._selectedCells[entryID]



    def _redo_shift_remaining_items(self, shiftRange, columnLeftShift):
        """ Shift all remaining canvas elements to accomodate the
        inserted rows.

        """
        
        selection = set()
        for rowID in range(0, self.numRows):
            for colID in shiftRange:
                item = self.canvas._item_at_row_col(rowID, colID)
                selection.add(item)

        for item in selection:
            shift_item_column_wise(item, columnLeftShift, self.unitWidth)

        shift_legend_horizontally(self.canvas.gridLegend, columnLeftShift, 
                                  self.unitWidth, self.numRows, self.unitHeight)
        self.canvas._selectedCells = \
                shift_selection_horizontally(self.canvas._selectedCells,
                                             self.pivot, columnLeftShift)



    def _undo_shift_remaining_items(self, shiftRange):
        """ Shift elements on canvas back to shifting done in redo. """

        # make sure to shift legend and selection first
        shift_legend_horizontally(self.canvas.gridLegend, self.columnShift, 
                                  self.unitWidth, self.numRows,
                                  self.unitHeight)
        self.canvas._selectedCells = \
                shift_selection_horizontally(self.canvas._selectedCells,
                                             self.pivot, self.columnShift)


        shiftItems = set()
        for colID in shiftRange:
            for rowID in range(0, self.numRows):
                item = self.canvas._item_at_row_col(rowID, colID)
                if item:
                    shiftItems.add(item)

        for item in shiftItems:
            shift_item_column_wise(item, self.columnShift, self.unitWidth)



    def _readd_selected_cells(self):
        """ Re-add previously deleted selected cells. """

        for (key, entry) in self.deadSelectedCells.items():
            self.canvas._selectedCells[key] = entry



    def _readd_deleted_items(self):
        """ Re-add previously deleted items. """

        for entry in self.deletedCells:
            location = QPointF(entry.column * self.unitWidth,
                               entry.row * self.unitHeight)
            item = \
                 self.canvas.create_pattern_grid_item(location, 
                                                      self.canvas._unitCellDim,
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


            
    def _finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.finalize_grid_change()
        self.canvas.emit(SIGNAL("adjust_view"))
        self.canvas.emit(SIGNAL("scene_changed"))
        self.canvas.insertDeleteRowColDialog.set_upper_column_limit( \
                self.canvas._numColumns)




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

        self.selectedCells = selectedCells
        self.unselectedCells = unselectedCells 

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
                    errorLogger.write(errorString)

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
                    errorLogger.write(errorString)
                    
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
                        errorLogger.write(errorString)
                        

                # insert as many new items as we can fit
                numNewItems = int(totalWidth/self.width)
                for i in range(0, numNewItems):
                    item = self.canvas.create_pattern_grid_item(origin,
                                self.canvas._unitCellDim, column, row, self.width,
                                1, self.activeSymbolContent, itemColor)
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
                    errorLogger.write(errorString)

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
                errorLogger.write(errorString)


        # re-insert previous selection
        for entry in self.oldSelection.values():
            column = entry.column
            row    = entry.row
            location = QPointF(column * self.canvas._unitCellDim.width(),
                            row * self.canvas._unitCellDim.height())

            item = self.canvas.create_pattern_grid_item(location, 
                                                    self.canvas._unitCellDim, 
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




class AddPatternRepeat(QUndoCommand):
    """ This class encapsulates the creation of a pattern repeat
    item on the canvas.

    """
    
    def __init__(self, canvas, pathItem, parent = None):

        super(AddPatternRepeat, self).__init__(parent)

        self.canvas = canvas
        self.pathItem = pathItem 
        self.unselectedCells = canvas._selectedCells.values()



    def redo(self):
        """ The redo action. """

        self.canvas.addItem(self.pathItem)

        # unselect the currently selected cells
        if self.unselectedCells:
            for item in self.unselectedCells:
                itemID = get_item_id(item.column, item.row)
                if itemID in self.canvas._selectedCells:
                    del self.canvas._selectedCells[itemID]
                else:
                    errorString = ("AddPatternRepeat.redo: trying to delete "
                                   "invalid selected cell.")
                    errorLogger.write(errorString)

                item = self.canvas._item_at_row_col(item.row, item.column)
                if item:
                    item._unselect()



    def undo(self):
        """ The undo action. """

        self.canvas.removeItem(self.pathItem)

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



    def undo(self):
        """ The undo action. """

        self.canvas.addItem(self.patternRepeat)
         



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
