# -*- coding: utf-8 -*-
######################################################################## #
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


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import operator
import copy
from functools import partial

from PyQt4.QtCore import (Qt, QRectF, QSize, QPointF, QSizeF, 
                          SIGNAL, QObject, QString, QPoint, QRect)
from PyQt4.QtGui import (QGraphicsScene, QGraphicsObject, QPen, QColor, 
                         QBrush, QGraphicsTextItem, QFontMetrics, QMenu, 
                         QAction, QGraphicsItem, QMessageBox, 
                         QGraphicsItemGroup, 
                         QUndoStack, QUndoCommand)
from PyQt4.QtSvg import (QGraphicsSvgItem, QSvgWidget, QSvgRenderer)

from sconcho.util.canvas import (is_click_in_grid, is_click_on_labels, 
                                 convert_pos_to_col_row, convert_col_row_to_pos)
from sconcho.gui.insertDeleteRowColumnDialog import InsertDeleteRowColumnDialog
from sconcho.util.misc import wait_cursor
import sconcho.util.messages as msg




#########################################################
## 
## class for managing the actual pattern canvas
##
#########################################################
class PatternCanvas(QGraphicsScene):


    def __init__(self, theSettings, defaultSymbol, parent = None):

        super(PatternCanvas, self).__init__(parent)

        self.setBackgroundBrush(QBrush(Qt.white))

        self.settings = theSettings

        self._activeSymbol = None
        self._defaultSymbol = defaultSymbol
        self._activeColorObject = None
        self._defaultColor = QColor(Qt.white)
        self._selectedCells = {}

        self._undoStack = QUndoStack(self)

        self._unitCellDim = QSizeF(self.settings.grid_cell_width,
                                   self.settings.grid_cell_height)
        self._numRows = 10
        self._numColumns = 10

        self._copySelection = {}
        self._copySelectionDim = None

        self._textLabels = []

        self.insertDeleteRowColDialog = None

        self.gridLegend = {}

        self.set_up_main_grid()
        self.set_up_labels()



    def set_up_main_grid(self):
        """ This function draws the main grid. """

        for row in range(0, self._numRows):
            self._create_row(row)



    def set_up_labels(self):
        """ Add labels to the main grid.
        
        FIXME: This function currently recreates all labels instead
        of just shifting around existing ones. The latter should
        probably be more efficient.

        NOTE: The ranges below are somewhat weird because we count
        backward.
        
        """

        interval = self.settings.label_interval
        labelFont = self.settings.label_font

        for label in self._textLabels:
            self.removeItem(label)
            del label
        self._textLabels = []
           
        fm = QFontMetrics(labelFont)
        unitWidth = self._unitCellDim.width()
        
        # row labels
        xPos = unitWidth * self._numColumns
        for row in range(self._numRows - 1, -1, -interval):
            item = PatternLabelItem(unicode(self._numRows - row))

            yPos = self._unitCellDim.height() * row
            item.setPos(xPos, yPos)
            item.setFont(labelFont)
            item.setToolTip("Control-Click to select whole row")
            self.addItem(item)
            self._textLabels.append(item)

        # column labels
        yPos = self._unitCellDim.height() * self._numRows
        for col in range(self._numColumns - 1, -1, -interval):
            labelText = QString(unicode(self._numColumns - col))
            textWidth = fm.width(labelText)
            item = PatternLabelItem(labelText)
            
            xPos = unitWidth * col + (unitWidth * 0.6 -textWidth)
            item.setPos(xPos, yPos)
            item.setFont(labelFont)
            item.setToolTip("Control-Click to select whole column")

            self.addItem(item)
            self._textLabels.append(item)

            

    def set_active_symbol(self, activeKnittingSymbol):
        """ This function receives the currently active symbol
        and stores it so we know what to paint selected cells
        with. In order to have consistent undo/redo bahaviour
        this has to be full reversible.

        """

        selectCommand = ActivateSymbol(self, activeKnittingSymbol)
        self._undoStack.push(selectCommand)



    def set_active_colorObject(self, colorObject):
        """ This function received the currently active
        background color and stores it.

        """

        selectCommand = ActivateColor(self, colorObject)
        self._undoStack.push(selectCommand)



    def change_active_color(self, newColor):

        selectCommand = ActivateColor(self, self._activeColorObject, newColor)
        self._undoStack.push(selectCommand)
            


    def add_to_legend(self, item):
        """ Adds a newly created PatternGridItem to the legend database
        and updates the legend itself if needed.
        
        """

        legendID = generate_legend_id(item.symbol, item.color)
        if legendID in self.gridLegend:
            entry = self.gridLegend[legendID]
            new_entry = change_count(entry, 1)
            self.gridLegend[legendID] = new_entry
        else:
            (item, textItem) = self._add_legend_item(item.symbol, item.color)
            self.gridLegend[legendID] = [1, item, textItem]



    def undo(self):
        """ Simple helper slot to undo last action. """

        if self._undoStack.canUndo():
            self._undoStack.undo()



    def redo(self):
        """ Simple helper slot to redo last action. """

        if self._undoStack.canRedo():
            self._undoStack.redo()



    def change_grid_cell_dimensions(self):
        """ This function adjust the grid cell dimensions if either
        cell height, width or both have changed.

        """

        self._unitCellDim = QSizeF(self.settings.grid_cell_width,
                                   self.settings.grid_cell_height)
        self._redraw_canvas_after_grid_dimension_change()

        


    def _redraw_canvas_after_grid_dimension_change(self):
        """ Redraws all involved items on the canvas after a change 
        of unit grid cell dimensions. 

        NOTE: Presently, we do not shift the legend around after
              unit cell changes. I am not sure if we should do this
              automatically or just have the user fix it up themselves.
        """

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem):
                graphicsItem.prepareGeometryChange()
                graphicsItem.change_geometry(self._unitCellDim)
                origin = QPointF(graphicsItem.column * \
                                 self._unitCellDim.width(),
                                 graphicsItem.row * \
                                 self._unitCellDim.height())
                graphicsItem.setPos(origin)

            elif isinstance(graphicsItem, PatternLegendItem):
                graphicsItem.prepareGeometryChange()
                graphicsItem.change_geometry(self._unitCellDim)


        # fix labels
        self.set_up_labels()



    def _add_legend_item(self, symbol, color):
        """ This adds a new legend entry including an PatternLegendItem
        and a textual description. This function also attemps to be
        sort of smart about where to put the item.
        
        """

        legendYmax = compute_max_legend_y_coordinate(self.gridLegend)
        canvasYmax = (self._numRows + 1) * self._unitCellDim.height()

        yMax = max(legendYmax, canvasYmax)

        # add the symbol part of the legend
        width  = int(symbol["width"])
        height = 1
        itemLocation = QPointF(0, yMax + self._unitCellDim.height() + 10)
        item = PatternLegendItem(self._unitCellDim, width, height, symbol,
                                 color, 1)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setPos(itemLocation)
        self.addItem(item)

        # add the description part of the legend
        textLocation = QPointF((width+1) * self._unitCellDim.width(),
                                yMax + self._unitCellDim.height() + 10)
        textItem = QGraphicsTextItem()
        textItem.setPos(textLocation)
        textItem.setZValue(1)
        textItem.setFlag(QGraphicsItem.ItemIsMovable)
        textItem.setTextInteractionFlags(Qt.TextEditorInteraction);
        textItem.setPlainText(symbol["description"])
        textItem.setFont(self.settings.legend_font)
        self.addItem(textItem)

        self.emit(SIGNAL("adjust_view"))
        return (item, textItem)



    def remove_from_legend(self, item):
        """ Removes a PatternGridItem from the legend database
        and updates the legend itself if needed.
        
        """


        legendID = generate_legend_id(item.symbol, item.color)
        assert(legendID in self.gridLegend)

        entry = self.gridLegend[legendID]
        if legendItem_count(entry) == 1:
            symbol = legendItem_symbol(entry)
            text   = legendItem_text(entry)
            self.removeItem(symbol)
            self.removeItem(text)
            del self.gridLegend[legendID]
            del symbol
            del text
        else:
            new_entry = change_count(entry, -1)
            self.gridLegend[legendID] = new_entry



    def clear_undo_stack(self):
        """ Completely clears the undo stack. """

        self._undoStack.clear()



    def clear_all_selected_cells(self):
        """ Unselects all currently selected cells. """

        paintCommand = PaintCells(self, None, self._selectedCells.values())
        self._undoStack.push(paintCommand)



    def grid_cell_activated(self, item):
        """ If a grid cell notifies it has been activated add it
        to the collection of selected cells and try to paint
        them.
        
        """
       
        activatedItem = PatternCanvasEntry(item.column, item.row, item.width, 
                                           item.color, item.symbol) 
        paintCommand = PaintCells(self, [activatedItem])
        self._undoStack.push(paintCommand)



    def grid_cell_inactivated(self, item):
        """ If a grid cell notifies it has been in-activated remove
        it from the collection of selected cells if present.
        
        """


        inactivatedItem = PatternCanvasEntry(item.column, item.row, item.width, 
                                             item.color, item.symbol) 
        paintCommand = PaintCells(self, None, [inactivatedItem])
        self._undoStack.push(paintCommand)



    def create_pattern_grid_item(self, origin, unitDim, col, row,
                                 width, height, knittingSymbol,
                                 color):
        """ Creates a new PatternGridItem of the specified dimension
        at the given location.
        
        """

        item = PatternGridItem(unitDim, col, row, width, height,
                                knittingSymbol, color)
        item.setPos(origin)
        self.connect(item, SIGNAL("cell_selected"), self.grid_cell_activated)
        self.connect(item, SIGNAL("cell_unselected"),
                     self.grid_cell_inactivated)
        return item



    def addItem(self, item):
        """ This overload of addItem makes sure that we perform
        QGraphicsItem specific task such as updating the legend for svg items.
        
        """

        if isinstance(item, PatternGridItem):
            self.add_to_legend(item)

        super(PatternCanvas,self).addItem(item)



    def removeItem(self, item):
        """ This overload of removeItem makes sure that we perform
        QGraphicsItem specific task such as updating the legend for svg
        items.
        
        """

        if isinstance(item, PatternGridItem):
            self.remove_from_legend(item)

        super(PatternCanvas,self).removeItem(item)



    def paint_cells(self):
        """ Attempts to paint the cells with the selected symbol.
        Has to make sure the geometry is appropriate.
        
        """

        paintCommand = PaintCells(self) 
        self._undoStack.push(paintCommand)

        

    def mousePressEvent(self, event):
        """ Handle mouse press events directly on the canvas. """

        (col, row) = convert_pos_to_col_row(event.scenePos(),
                                            self._unitCellDim.width(),
                                            self._unitCellDim.height())
       
        if event.button() == Qt.RightButton:

            if is_click_in_grid(col, row, self._numColumns, self._numRows):
                self.handle_right_click_on_grid(event, row, col)

                # don't propagate this event
                return

        elif (event.button() == Qt.LeftButton) and \
             (event.modifiers() & Qt.ControlModifier):

            if is_click_on_labels(col, row, self._numColumns, self._numRows):
                 self.handle_right_click_on_labels(col, row)

        # tell our main window that something changed
        self.emit(SIGNAL("scene_changed"))

        return QGraphicsScene.mousePressEvent(self, event)



    def select_region(self, region):
        """ This function selects items based on a whole region.

        The region is typically a QPolygonF coming from our
        view via a rubberBand selection.

        """

        selection = []
        for item in self.items(region):
            if isinstance(item, PatternGridItem):
                selection.append(PatternCanvasEntry(item.column, item.row, 
                                    item.width, item.color, item.symbol))

        paintCommand = PaintCells(self, selection)
        self._undoStack.push(paintCommand)



    def handle_right_click_on_labels(self, col, row):
        """ Deal with user clicks on the grid labels. 

        These select whole rows or columns depending on
        if a column or row label was clicked on.

        """

        assert (row == self._numRows) or (col == self._numColumns)

        if row == self._numRows:
            selectedItems = self.get_column_items(col)
        else:
            selectedItems = self.get_row_items(row)

        selection = []
        for item in selectedItems:
            selection.append(PatternCanvasEntry(item.column, item.row, 
                                      item.width, item.color, item.symbol))

        paintCommand = PaintCells(self, selection)
        self._undoStack.push(paintCommand)



    def get_column_items(self, column):
        """ Returns list of all PatternGridItems in column. """

        colItems = set()
        for row in range(0, self._numRows):
            item = self._item_at_row_col(column, row)
            if item:
                colItems.add(item)

        return colItems
        


    def get_row_items(self, row):
        """ Returns list of all PatternGridItems in row.

        NOTE: Since we want to select the whole row, we
        have to make sure to deliver the items left to
        right and *not* out of order.
        """

        rowItems = set()
        for column in range(0, self._numColumns):
            item = self._item_at_row_col(column, row)
            if item:
                rowItems.add(item)
           
        return rowItems



    def handle_right_click_on_grid(self, event, row, col):
        """ Handles a right click on the pattern grid by
        displaying a QMenu with options.

        """

        gridMenu = QMenu()
        rowAction = gridMenu.addAction("Insert/Delete Rows and Columns")
        gridMenu.addSeparator()
        colorAction = gridMenu.addAction("&Grab Color")
        gridMenu.addSeparator()

        copyAction = gridMenu.addAction("&Copy Selection")
        (status, (colDim, rowDim)) = \
                is_active_selection_rectangular(self._selectedCells.values())
        if not status:
            copyAction.setEnabled(False)

        pasteAction = gridMenu.addAction("&Paste Selection") 
        pasteAction.setEnabled(False)
        if self._copySelectionDim:
            colDim = self._copySelectionDim[0]
            rowDim = self._copySelectionDim[1]
            if self._rectangle_self_contained(col, row, colDim, rowDim):
                pasteAction.setEnabled(True)

        self.connect(rowAction, SIGNAL("triggered()"),
                     partial(self.insert_delete_rows_columns, col, row))
        
        self.connect(colorAction, SIGNAL("triggered()"),
                     partial(self.grab_color_from_cell, event))

        self.connect(copyAction, SIGNAL("triggered()"),
                     partial(self.copy_selection, colDim, rowDim))

        self.connect(pasteAction, SIGNAL("triggered()"),
                     partial(self.paste_selection, col, row))

        gridMenu.exec_(event.screenPos())



    def insert_delete_rows_columns(self, col, row):
        """ This method manages the addition and deletion of rows and columns
        via a widget.

        NOTE: Make sure the signals are only connected *once* inside the
        if. Otherwise weird things are bound to happen (like multiple
        deletes, inserts, etc.).
        
        """

        if not self.insertDeleteRowColDialog:
            self.insertDeleteRowColDialog = \
                InsertDeleteRowColumnDialog(self._numRows,
                                            self._numColumns,
                                            row, col, self.parent())
            self.connect(self.insertDeleteRowColDialog, SIGNAL("insert_rows"), 
                         self.insert_grid_row)
            self.connect(self.insertDeleteRowColDialog, SIGNAL("delete_rows"), 
                         self.delete_grid_row)
            self.connect(self.insertDeleteRowColDialog, SIGNAL("insert_columns"), 
                         self.insert_grid_column)
            self.connect(self.insertDeleteRowColDialog, SIGNAL("delete_columns"), 
                         self.delete_grid_column)
        else:
            self.insertDeleteRowColDialog.set_row_col(row,col)

        self.insertDeleteRowColDialog.raise_()
        self.insertDeleteRowColDialog.show()



    def grab_color_from_cell(self, event):
        """ Extract the color from the selected cell
        and add it to the currently active color selector.
        
        """

        allItems = self.items(event.scenePos())
        
        if len(allItems) != 1:
            print("Error: Grab Color: expected 1 item, found %d" % \
                  len(allItems))
            return

        color = allItems[0].color
        self.change_active_color(color)



    def copy_selection(self, colDim, rowDim):
        """ This slot copies the current selection. """

        if not self._selectedCells:
            return

        self._copySelection.clear()
        self._copySelection    = self._selectedCells.copy()
        self._copySelectionDim = (colDim, rowDim)
        self.clear_all_selected_cells()



    def _get_pattern_grid_items_in_rectangle(self, column, row, numCols,
                                             numRows):
        """ Given a (col, row) origin and the number of columns
        and rows returns all PatternGridItems under the selection.

        """

        upperLeftCorner  = convert_col_row_to_pos(column, 
                                    row, 
                                    self._unitCellDim.width(),
                                    self._unitCellDim.height())

        lowerRightCorner = convert_col_row_to_pos(column + numCols - 1, 
                                    row + numRows - 1, 
                                    self._unitCellDim.width(),
                                    self._unitCellDim.height())

        
        allItems = self.items(QRectF(upperLeftCorner, lowerRightCorner))
        patternGridItems = []
        for item in allItems:
            if isinstance(item, PatternGridItem):
                patternGridItems.append(item)

        return patternGridItems



    def paste_selection(self, column, row):
        """ This slot pastes the current copy selection at column
        and row.
        
        """

        # remove each row completely first, then insert the 
        # selection
        deadItems = self._get_pattern_grid_items_in_rectangle(column, row,
                                                self._copySelectionDim[0],
                                                self._copySelectionDim[1])

        deadSelection = {}
        for item in deadItems:
            itemID = get_item_id(item.column, item.row) 
            deadSelection[itemID] = PatternCanvasEntry(item.column, item.row, 
                                        item.width, item.color, item.symbol)

        if self._copySelection and deadSelection:
            pasteCommand = PasteCells(self, self._copySelection,
                                     deadSelection, column, row,
                                     self._copySelectionDim[0],
                                     self._copySelectionDim[1])
            self._undoStack.push(pasteCommand)



    def _rectangle_self_contained(self, column, row, colDim, rowDim):
        """ This function checks if the rectangle given by the upper
        left hand corner at (column, row) and width, height of
        (colDim, rowDim) is self contained, i.e., there are no cells 
        of width >= 2 not fully contained within.

        """

        if (row + rowDim > self._numRows) or \
           (column + colDim > self._numColumns):
            return False

        for rowCount in range(row, row + rowDim):

            # check item at left and past (!) right edge of rectangle
            leftItem = self._item_at_row_col(column, rowCount)

            if (leftItem.width > 1) and (leftItem.column < column):
                return False

            # make sure we don't fall off at the right
            if (column + colDim < self._numColumns):
                rightItem = self._item_at_row_col(column + colDim, rowCount)
                if (rightItem.width > 1) and \
                   (rightItem.column < column + colDim):
                    return False

        return True


    
    def check_pattern_grid(self):
        """ NOTE: this is a temporary function which will be removed
        in the production version. It allows to query the pattern grid
        to make sure there are no overlapping PatternGridItems as has
        happened in the past after copy and past actions.
        If such items are detected they are removed (but one).

        """

        allItems = self.items()
        patternGridItems = []
        for item in allItems:
            if isinstance(item, PatternGridItem):
                patternGridItems.append(item)


        tracker = {}
        for item in patternGridItems:
            for i in range(0,item.width):
                itemID = get_item_id(item.column+i, item.row)
               
                # check for trouble
                if itemID in tracker:
                    tracker[itemID].append(item)
                    break
                else:
                    tracker[itemID] = [item]

        removedItems = []
        for items in tracker.values():
            # check for duplicate values
            if len(items) > 1:
                # we remove the item with the smallest width
                # to avoid leaving holes
                items.sort(lambda x,y: cmp(x.width, y.width))

                # remove all but the last one
                for index in range(0, len(items)-1):
                    item = items[index]
                    canvasRow = \
                         self.convert_canvas_row_to_internal(item.row)
                    canvasColumn = \
                         self.convert_canvas_column_to_internal(item.column)
                    removedItems.append((item.symbol["name"], canvasColumn,
                                         canvasRow))
                    item = items[index]
                    self.removeItem(item)
                    del item

        return removedItems 



    def _item_at_row_col(self, column, row):
        """ Returns the PatternGridItem at the given column and row
        or None if there isn't one.

        """

        pos = convert_col_row_to_pos(column, row, self._unitCellDim.width(),
                                     self._unitCellDim.height())

        # we really only expect one PatternCanvasItem to be present;
        # however there may in principle be others (legend items etc)
        # so we have to pick it out
        items = self.items(pos)
        for item in items:
            if isinstance(item, PatternGridItem):
                return item

        return None



    def insert_grid_row(self, num, mode, rowPivot):
        """ Deals with requests to insert a row. This operation might
        take some time so we switch to a wait cursor.

        """

        pivot = self.convert_canvas_row_to_internal(rowPivot)
        assert(pivot >= 0 and pivot < self._numRows)

        insertRowCommand = InsertRow(self, num, pivot, mode)
        self._undoStack.push(insertRowCommand)

        

    def delete_grid_row(self, num, mode, rowPivot):
        """ Deals with requests to delete a specific row. """
       
        pivot = self.convert_canvas_row_to_internal(rowPivot)
        assert(pivot >= 0 and pivot < self._numRows)

        # make sure we can delete num rows above/below rowPivot
        if mode == "above":
            if (pivot - num) < 0:
                QMessageBox.warning(None, msg.canNotDeleteRowAboveTitle,
                                    msg.canNotDeleteRowAboveText,
                                    QMessageBox.Close)
                return

        else:
            if (pivot + num) >= self._numRows:
                QMessageBox.warning(None, msg.canNotDeleteRowBelowTitle,
                                    msg.canNotDeleteRowBelowText,
                                    QMessageBox.Close)
                return

       
        deleteRowCommand = DeleteRow(self, num, pivot, mode)
        self._undoStack.push(deleteRowCommand)
 


    def insert_grid_column(self, num, mode, columnPivot):
        """ Deals with requests to insert a column. """

        pivot = self.convert_canvas_column_to_internal(columnPivot)
        assert(pivot >= 0 and pivot < self._numColumns)

        # first we need to check if we can actually insert num
        # columns given the current configuration
        isExternalColumn = False
        if mode == QString("left of"):
            shift = 0
            if pivot == 0:
                isExternalColumn = True
        else:
            shift = 1
            if pivot == self._numColumns - 1:
                isExternalColumn = True

        # in order for inserting of a column at left or right of a
        # pivot to work each row has to have a cell that starts at
        # this pivot or right of it.
        # Obviously, we can always add columns at the edges.
        rowCounter = 0
        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem):
                if graphicsItem.column == (pivot + shift):
                    rowCounter += 1

        if not isExternalColumn:
            if rowCounter != self._numRows:
                QMessageBox.warning(None, msg.noColInsertLayoutTitle,
                                msg.noColInsertLayoutText,
                                QMessageBox.Close)
                return
       
        if not isExternalColumn:
            for row in range(0, self._numRows):
                item = self._item_at_row_col(pivot + shift, row)
                if isinstance(item, PatternGridItem):
                    if item.column != (pivot + shift):
                        QMessageBox.warning(None, msg.noColInsertLayoutTitle,
                                            msg.noColInsertLayoutText,
                                            QMessageBox.Close)
                        return

        # ok we're good to insert then 
        insertColumnCommand = InsertColumn(self, num, pivot, mode)
        self._undoStack.push(insertColumnCommand)



    def delete_grid_column(self, num, mode, columnPivot):
        """ Deals with requests to delete a specific number of columns. """

        pivot = self.convert_canvas_column_to_internal(columnPivot)
        assert(pivot >= 0 and pivot < self._numColumns)

        # make sure we can delete num columns left of/right of columnPivot
        if mode == "left of":
            if (pivot - num) < 0:
                QMessageBox.warning(None, msg.canNotDeleteColumnLeftOfTitle,
                                    msg.canNotDeleteColumnLeftOfText,
                                    QMessageBox.Close)
                return

        else:
            if (pivot + num) > self._numColumns:
                QMessageBox.warning(None, msg.canNotDeleteColumnRightOfTitle,
                                    msg.canNotDeleteColumnRightOfText,
                                    QMessageBox.Close)
                return

        # in order for us to be able to delete the requested number
        # of columns the selection has to be rectangular (this is
        # similar to the check we do when before allowing to copy
        # a selection
        if mode == QString("left of"):
            colRange = range(pivot - num, pivot)
        else:
            colRange = range(pivot, pivot + num)
            
        selection = []
        for rowID in range(0, self._numRows):
            for colID in colRange:
                item = self._item_at_row_col(colID, rowID)
                selection.append(PatternCanvasEntry(item.column, item.row, 
                                                    item.width, item.color,
                                                    item.symbol))
        (status, (colDim, rowDim)) = is_active_selection_rectangular(selection)
        
        if not status:
            QMessageBox.warning(None, msg.noColDeleteLayoutTitle,
                                msg.noColDeleteLayoutText,
                                QMessageBox.Close)
            return


        # ok we're good to delete then 
        deleteColumnCommand = DeleteColumn(self, num, pivot, mode)
        self._undoStack.push(deleteColumnCommand)



    def convert_canvas_row_to_internal(self, row):
        """ This function does the conversion from canvas
        to internal rows.

        Internally rows are numbered 0 through numRows-1
        from the top to bottom whereas they appear as numRows to 1
        on the canvas. 

        """

        return self._numRows - row



    def convert_canvas_column_to_internal(self, column):
        """ This function does the conversion from canvas
        to internal columns.

        Internally columns are numbered 0 through numColumns-1
        from the left to right whereas they appear as numColumns to 1
        on the canvas. 

        """

        return self._numColumns - column



    def _create_row(self, rowID):
        """ Creates a new row at rowID, nothing else. In particular
        this function does not attempt to make space for the row or
        anything else along these lines. This is a private and 
        very stupid function.
        
        """

        for column in range(0, self._numColumns):
            location = QPointF(column * self._unitCellDim.width(),
                                rowID * self._unitCellDim.height())
            item = self.create_pattern_grid_item(location, self._unitCellDim,
                                                    column, rowID, 1, 1,
                                                    self._defaultSymbol,
                                                    self._defaultColor)
            self.addItem(item)



    def _create_column(self, columnID):
        """ Creates a new column at columnID, nothing else. In particular
        this function does not attempt to make space for the column or
        anything else along these lines. This is a private and very
        stupid function.
        
        """

        for row in range(0, self._numRows):
            location = QPointF(columnID * self._unitCellDim.width(),
                                row * self._unitCellDim.height())
            item = self.create_pattern_grid_item(location, self._unitCellDim,
                                                    columnID, row, 1, 1,
                                                    self._defaultSymbol,
                                                    self._defaultColor)
            self.addItem(item)



    def _clear_canvas(self):
        """ Clear the complete canvas. """

        # clear GraphicsScene
        self.clear()
        self.update()

        # clear all caches
        self.gridLegend.clear()



    def create_new_canvas(self, numRows = 10, numColumns = 10):
        """ Create a complete new and blank canvas. """

        # reset the number of columns/rows to 10
        # we probably should add a dialog here
        self._numRows    = numRows
        self._numColumns = numColumns
        self.insertDeleteRowColDialog = None
        
        self._clear_canvas()
        self._textLabels = []
        self.set_up_main_grid()
        self.set_up_labels()

        self.emit(SIGNAL("adjust_view"))
        


    @wait_cursor
    def load_previous_pattern(self, knittingSymbols, patternGridItemInfo,
                          legendItemInfo):
        """ Clear curent canvas and establishes a new canvas
        based on the passed canvas items. Returns True on success
        and False otherwise.
        
        NOTE: We have to be able to deal with bogus data (from a
        corrupted file perhaps).
        
        """

        (status, allPatternGridItems) = \
                 self._load_pattern_grid_items(patternGridItemInfo,
                                               knittingSymbols)
        if not status:
            return status

        (status, allLegendItems) = \
                 self._load_legend_items(legendItemInfo)

        if not status:
            return status
        

        # not that we have all canvas items, let's put them back in place
        self._clear_canvas()
        for entry in allPatternGridItems:
            item = self.create_pattern_grid_item(*entry)
            self.addItem(item)

        for entry in allLegendItems:
            arrange_label_item(self.gridLegend, *entry)

        # need to clear our label cache, otherwise set_up_labels()
        # will try to remove non-existing items
        self._textLabels = []
        self.set_up_labels()
        self.change_grid_cell_dimensions()

        self.emit(SIGNAL("adjust_view"))
        return True



    def _load_pattern_grid_items(self, patternGridItemInfo, knittingSymbols):
        """ Re-create all patternGridItems based on loaded
        sconcho project.

        """

        # need this to determine the number of columns and rows
        maxCol = 0
        maxRow = 0
        allPatternGridItems = []
        
        try:
            for newItem in patternGridItemInfo:
                colID    = newItem["column"]
                rowID    = newItem["row"]
                width    = newItem["width"]
                height   = newItem["height"]
                name     = newItem["name"]
                color    = QColor(newItem["color"])
                category = newItem["category"]
                location = QPointF(colID * self._unitCellDim.width(),
                                    rowID * self._unitCellDim.height())
                symbol   = knittingSymbols[name]

                allPatternGridItems.append((location, self._unitCellDim, 
                                            colID, rowID, width, 
                                            height, symbol, color))

                # update trackers
                maxCol = max(maxCol, colID)
                maxRow = max(maxRow, rowID)

        except KeyError as e:
            QMessageBox.critical(None, msg.errorLoadingGridTitle,
                                 msg.errorLoadingGridText % e,
                                 QMessageBox.Close)
            return (False, [])

        # set limits
        self._numRows    = maxRow + 1
        self._numColumns = maxCol + 1
        
        return (True, allPatternGridItems)



    def _load_legend_items(self, legendItemInfo):
        """ Re-create all legend items based on loaded sconcho project. """       

        allLegendItems = []
        try:
            for item in legendItemInfo:
                legendID  = generate_legend_id(item, item["color"])
                itemXPos  = item["itemXPos"]
                itemYPos  = item["itemYPos"]
                labelXPos = item["labelXPos"]
                labelYPos = item["labelYPos"]
                description = item["description"]
                allLegendItems.append((legendID, itemXPos, itemYPos, 
                                       labelXPos, labelYPos, description))
        except KeyError as e:
            QMessageBox.critical(None, msg.errorLoadingLegendTitle,
                                 msg.errorLoadingLegendText % e,
                                 QMessageBox.Close)
            return (False, [])

        return (True, allLegendItems)



    def toggle_label_visibility(self, status):
        """ Per request from main window toggle
        the visibility of the labels.
        
        """

        for item in self.items():
            if isinstance(item, PatternLabelItem):
                if status:
                    item.show()
                else:
                    item.hide()



    def label_font_changed(self):
        """ This slot is called when the label font has
        been changed.
        
        """
        
        labelFont = self.settings.label_font
        for item in self.items():
            if isinstance(item, PatternLabelItem):
                item.setFont(labelFont)
                


    def toggle_legend_visibility(self, status):
        """ Per request from main window toggle the legend
        visibility on or off.
        
        """

        if status:
            for item in self.gridLegend.values():
                legendItem_symbol(item).show()
                legendItem_text(item).show()

        else:
            for item in self.gridLegend.values():
                legendItem_symbol(item).hide()
                legendItem_text(item).hide()



    def legend_font_changed(self):
        """ This slot is called when the label font has
        been changed.
        
        """
        
        legendFont = self.settings.legend_font
        for item in self.gridLegend.values():
            legendItem_text(item).setFont(legendFont)



    def toggle_pattern_grid_visibility(self, status):
        """ Per request from main window toggle the pattern grid
        visibility on or off.
        
        """

        for item in self.items():
            if isinstance(item, PatternGridItem):
                if status:
                    item.show()
                else:
                    item.hide()




#########################################################
## 
## class for managing a single pattern grid item
## (svg image, frame, background color)
##
#########################################################
class PatternGridItem(QGraphicsSvgItem):

    Type = 70000 + 1


    def __init__(self, unitDim, col, row, width, height,
                 defaultSymbol, defaultColor = QColor(Qt.white),
                 parent = None):

        super(PatternGridItem, self).__init__(parent)
      
        # NOTE: need this for >= Qt 4.7 otherwise
        # rendering of our scene is broken
        self.setCacheMode(QGraphicsItem.NoCache)

        self.origin = QPointF(0.0, 0.0)
        self.unitDim = unitDim
        self.row = row
        self.column = col
        self.width = width
        self.height = height
        self.size = QSizeF(self.unitDim.width() * width,
                              self.unitDim.height() * height)

        self._penSize = 1.0
        self._pen = QPen()
        self._pen.setWidthF(self._penSize)
        self._pen.setJoinStyle(Qt.MiterJoin)
        self._pen.setColor(Qt.black)

        self._selected = False
        self.color = defaultColor
        self._backColor = self.color
        self._highlightedColor = QColor(Qt.gray)

        self.symbol = None
        self._set_symbol(defaultSymbol)



    def mousePressEvent(self, event):
        """ Handle user press events on the item. """

        if not self._selected:
            #self._select()
            self.emit(SIGNAL("cell_selected"), self)
        else:
            #self._unselect()
            self.emit(SIGNAL("cell_unselected"), self)



    def change_geometry(self, newDim):
        """ This slot changes the unit dimensions of the item. """

        self.unitDim = newDim
        self.size    = QSizeF(self.unitDim.width() * self.width,
                              self.unitDim.height() * self.height)



    def _unselect(self):
        """ Unselects a given selected cell. """

        self._selected = False
        self._backColor = self.color
        self.update()



    def _select(self):
        """ Selects a given unselected cell. """

        self._selected = True
        self._backColor = self._highlightedColor
        self.update()


            
    def _set_symbol(self, newSymbol):
        """ Adds a new svg image of a knitting symbol to the scene. """

        self.symbol = newSymbol
        svgPath = newSymbol["svgPath"]
        if not self.renderer().load(svgPath):
            print("failed to load")
            return

        # apply color if present
        if "backgroundColor" in newSymbol:
            self._backColor = QColor(newSymbol["backgroundColor"])

        self.update()



    def boundingRect(self):
        """ Return the bounding rectangle of the item. """

        halfPen = self._penSize * 0.5
        return QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
                                                       halfPen, halfPen)
        


    def paint(self, painter, option, widget):
        """ Paint ourselves. """

        painter.setPen(self._pen)
        brush = QBrush(self._backColor)
        painter.setBrush(brush)
        halfPen = self._penSize * 0.5
        scaledRect = QRectF(self.origin, self.size).adjusted(halfPen, halfPen, 
                                                             halfPen, halfPen)
        painter.drawRect(scaledRect)
        self.renderer().render(painter, scaledRect)




#########################################################
## 
## class for managing a single legend item
## (svg image, frame, background color)
##
#########################################################
class PatternLegendItem(QGraphicsSvgItem):

    Type = 70000 + 2


    def __init__(self, unitDim, width, height,
                 defaultSymbol, defaultColor = QColor(Qt.white),
                 zValue = 1, parent = None):

        super(PatternLegendItem, self).__init__(parent)

        # NOTE: need this for >= Qt 4.7 otherwise
        # rendering of our scene is broken
        self.setCacheMode(QGraphicsItem.NoCache)
        
        self.setZValue(zValue)

        self.origin = QPointF(0.0, 0.0)
        self.unitDim = unitDim
        self.width = width
        self.height = height
        self.size = QSizeF(self.unitDim.width() * width,
                              self.unitDim.height() * height)

        self.color = defaultColor

        self.symbol = None
        self._set_symbol(defaultSymbol)
        
        self._penSize = 1.0
        self._pen = QPen()
        self._pen.setWidthF(self._penSize)
        self._pen.setJoinStyle(Qt.MiterJoin)
        self._pen.setColor(Qt.black)



    def change_geometry(self, newDim):
        """ This slot changes the unit dimensions of the item. """

        self.unitDim = newDim
        self.size    = QSizeF(self.unitDim.width() * self.width,
                              self.unitDim.height() * self.height)



    def _set_symbol(self, newSymbol):
        """ Adds a new svg image of a knitting symbol to the scene. """

        self.symbol = newSymbol
        svgPath = newSymbol["svgPath"]
        if not self.renderer().load(svgPath):
            print("failed to load")
            return

        # apply color if present
        if "backgroundColor" in newSymbol:
            self.color = QColor(newSymbol["backgroundColor"])



    def boundingRect(self):
        """ Return the bounding rectangle of the item. """

        halfPen = self._penSize * 0.5
        return QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
                                                       halfPen, halfPen)



    def paint(self, painter, option, widget):
        """ Paint ourselves. """

        painter.setPen(self._pen)
        brush = QBrush(self.color)
        painter.setBrush(brush)
        halfPen = self._penSize * 0.5
        painter.drawRect(QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
                                                                 halfPen, halfPen))

        self.renderer().render(painter, QRectF(self.origin, self.size))




#########################################################
## 
## class for managing a single pattern grid label
## (this does nothing spiffy at all, we just need
## it to identify the item on the canvas)
##
#########################################################
class PatternLabelItem(QGraphicsTextItem):

    Type = 70000 + 3


    def __init__(self, text, parent = None):

        super(PatternLabelItem, self).__init__(text, parent)




############################################################################
##
## Helper functions
##
############################################################################

def shift_item_row_wise(item, num, unitCellHeight):
    """ Shifts the given item by num rows given unitCellHeight. """
    
    yShift = num * unitCellHeight
    item.prepareGeometryChange()
    item.row += num
    item.setPos(item.pos() + QPointF(0.0, yShift))



def shift_item_column_wise(item, num, unitCellWidth):
    """ Shifts the given item by num columns given unitCellWidth. """
    
    xShift = num * unitCellWidth
    item.prepareGeometryChange()
    item.column += num
    item.setPos(item.pos() + QPointF(xShift, 0.0))



def shift_legend_vertically(legendList, rowShift, unitCellHeight, numColumns, 
                            unitWidth):
    """ Shift all legend items below the grid down by rowShift. """

    yShift = rowShift * unitCellHeight

    for item in legendList.values():
        symbol = legendItem_symbol(item)
        text   = legendItem_text(item)

        # we ignore all items above or right of the pattern grid
        if (symbol.scenePos().y() >= 0) and \
           (symbol.scenePos().x() <= numColumns * unitWidth):

            symbol.prepareGeometryChange()
            symbol.setPos(symbol.pos() + QPointF(0.0, yShift))
            
            text.prepareGeometryChange()
            text.setPos(text.pos() + QPointF(0.0, yShift)) 



def shift_selection_vertically(selection, pivot, rowShift):
        """ Shifts all items in the current selection that are below the 
        pivot down. 
        
        """

        newSelection = {}
        for (key, entry) in selection.items():

            if entry.row >= pivot:
                entry.row += rowShift

            newID = get_item_id(entry.column, entry.row)
            newSelection[newID] = entry

        return newSelection



def shift_legend_horizontally(legendList, columnShift, unitCellWidth,
                              numRows, unitHeight):
    """ Shift all legend items to the right of the grid right by
    columnShift.
    
    """

    xShift = columnShift * unitCellWidth

    for item in legendList.values():
        symbol = legendItem_symbol(item)
        text = legendItem_text(item)

        # we ignore all items above or right of the
        # pattern grid
        if (symbol.scenePos().x() >= 0) and \
           (symbol.scenePos().y() >= 0) and \
           (symbol.scenePos().y() <= numRows * unitHeight):

            symbol.prepareGeometryChange()
            symbol.setPos(symbol.pos() + QPointF(xShift, 0.0))
            
            text.prepareGeometryChange()
            text.setPos(text.pos() + QPointF(xShift, 0.0))



def shift_selection_horizontally(selection, pivot, columnShift):
        """ Shifts all items in the current selection that are right
        of the pivot to the right. 
        
        """

        newSelection = {}
        for (key, entry) in selection.items():

            if entry.column >= pivot:
                entry.column += columnShift

            newID = get_item_id(entry.column, entry.row)
            newSelection[newID] = entry

        return newSelection



def compute_max_legend_y_coordinate(gridLegend):
    """ Given the current list of existing legend items
    figure out the largest y coordinate among them all.

    """

    yList = [0]
    for item in gridLegend.values():
        yList.append(legendItem_symbol(item).scenePos().y())
        yList.append(legendItem_text(item).scenePos().y())

    return max(yList)



def change_count(item, count):
    """ Convenience wrapper changing the count for a particular
    legend entry.

    """

    item[0] += count
    return item



def legendItem_count(item):
    """ Convenience wrapper returning the reference count for the
    particular legend item.

    """

    return item[0]



def legendItem_symbol(item):
    """ Convenience wrapper returning the current symbol for a
    particular legend item.

    """

    return item[1]



def legendItem_text(item):
    """ Convenience wrapper returning the current description text
    for a particular legend item.

    """

    return item[2]



def generate_legend_id(symbol, color):
    """ Based on a symbol/legend info, generate an id tag. Currently
    this is just based on name and category.

    """

    name = symbol["name"]
    category = symbol["category"]

    return (name, color.name())



def arrange_label_item(legendItems, legendID, itemXPos, itemYPos, labelXPos, 
                       labelYPos, description):
    """ Position all label items (pairs of PatternGridItem
    and PatternLegendItem) as requested in dict legendItems
    which comes from a parsed spf file.

    """

    if legendID in legendItems:
        
        legendItem = legendItems[legendID]
        legendPatternItem = legendItem_symbol(legendItem)
        legendTextItem = legendItem_text(legendItem)
        legendPatternItem.setPos(itemXPos, itemYPos)
        legendTextItem.setPos(labelXPos, labelYPos)
        legendTextItem.setPlainText(description)

    else:
        QMessageBox.critical(None, msg.errorMatchingLegendItemTitle,   
                             msg.errorMatchingLegendItemText,
                             QMessageBox.Close)



def is_active_selection_rectangular(selectedCells):
    """ This function checks if the currently active selection 
    is rectangular (i.e., not jagged or disconnected).
    The function returns (True, (col, row)) if yes and (False, (0,0)) 
    otherwise. Here, col and row and the number of columns and rows
    of the selected rectangle.

    """

    if not selectedCells:
        return (False, (0,0))

    cellsByRow = order_selection_by_rows(selectedCells)
   
    # make sure the rows are consecutive
    rowIDs = cellsByRow.keys()
    rowIDs.sort()
    for item in range(1, len(rowIDs)):
        if (rowIDs[item] - rowIDs[item-1]) != 1:
            return(False, (0,0))

    # check that each row has the same number of unit cells
    values = set(num_unitcells(row) for row in cellsByRow.values())
    if len(values) != 1:
        return (False, (0,0))

    # look for "holes"
    for row in cellsByRow.values():
        row.sort(lambda x, y: cmp(x.column, y.column))
        if not are_consecutive([row]):
            return (False, (0,0))
    
    numCols = values.pop()
    numRows = len(cellsByRow)
    return (True, (numCols, numRows))



def order_selection_by_rows(selection):
    """ Given a list of selected grid cells order them by row. """

    cellsByRow = {}
    if selection:
        for cell in selection:
            if not cell.row in cellsByRow:
                cellsByRow[cell.row] = [cell]
            else:
                cellsByRow[cell.row].append(cell)

    return cellsByRow



def order_selection_by_columns(selection):
    """ Given a list of selected grid cells order them by column. """

    cellsByColumn = {}
    if selection:
        for cell in selection:
            if not cell.column in cellsByColumn:
                cellsByColumn[cell.column] = [cell]
            else:
                cellsByColumn[cell.column].append(cell)

    return cellsByColumn



def chunkify_cell_arrangement(width, allCellsDict):
    """ Given a collection of selected cells verifies that we
    can place a symbol of given width. If so, return a
    list of consecutive chunks of cells all of a multiple of width
    that can be filled with the new symbol.
    
    """

    allCells = allCellsDict.values()

    # check 1: number of active cells has to be a multiple
    # of width
    if num_unitcells(allCells) % width != 0:
        return []

    cellsByRow = order_selection_by_rows(allCells)

    # check 2: each row has to be a multiple of width
    for row in cellsByRow.values():
        if num_unitcells(row) % width != 0:
            return []

    chunkList = chunk_all_rows(width, cellsByRow)

    return chunkList



def chunk_all_rows(width, cellsByRow):
    """ Separate each row into chunks at least as long as
    the items we want to place. Then we check if each
    chunk is consecutive.
    
    """
    
    chunkList = []
    for row in cellsByRow.values():
        row.sort(lambda x, y: cmp(x.column, y.column))

        chunks = []
        chunk = []
        length = 0
        for entry in row:
            chunk.append(entry)
            length += entry.width
            if length % width == 0:
               chunks.append(chunk)
               chunk = []
               length = 0

        if not are_consecutive(chunks):
            return []

        chunkList.extend(chunks)

    return chunkList



def are_consecutive(chunks):
    """ Checks if each chunk in a list of chunks consists
    of consecutive items.
    
    """

    if not chunks:
        return True

    for chunk in chunks:
        if not chunk:
            return False

        consecutiveCol = chunk[0].column + chunk[0].width
        for cell in chunk[1:]:
            if cell.column != consecutiveCol:
                return False
            
            consecutiveCol = cell.column + cell.width
            
    return True
        


def num_unitcells(cells):
    """ Compute the total number of unit cells in the
    selection.
    
    """

    totalWidth = 0
    for item in cells:
        totalWidth += item.width

    return totalWidth



def get_item_id(column, row):
    """ Returns an items id based on its row and column location. """

    return str(column) + ":" + str(row)



class PatternCanvasEntry(object):
    """ This is a small helper class for storing all relevant information
    to track a PatternGridItem. 

    """

    def __init__(self,  column, row, width, color, symbol):

        self.column = column
        self.row    = row
        self.width  = width
        self.color  = color
        self.symbol = symbol



#############################################################################
#
# the following classes encapsulate actions for the Undo/Redo framework
#
#############################################################################

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
            item = self.canvas._item_at_row_col(entry.column, entry.row)
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

                item = self.canvas._item_at_row_col(colID, rowID)
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
                shiftedItems.add(self.canvas._item_at_row_col(colID, rowID))

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
                selection.add(self.canvas._item_at_row_col(colID, rowID))

        for item in selection:
            self.canvas.removeItem(item)
            del item

        # shift the rest back into place
        selection.clear()
        for colID in range(0, self.numColumns):
            for rowID in range(self.pivot + self.rowShift, 
                               self.numRows + self.rowShift):
                selection.add(self.canvas._item_at_row_col(colID, rowID))

        for item in selection:
            shift_item_row_wise(item, rowUpShift, self.unitHeight)
 
        self.canvas._numRows -= self.rowShift
        self._finalize()
       


    def _finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.set_up_labels()
        self.canvas.emit(SIGNAL("adjust_view"))
        self.canvas.emit(SIGNAL("scene_changed"))
        self.canvas.insertDeleteRowColDialog.set_upper_row_limit( \
                self.canvas._numRows)




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
                selection.add(self.canvas._item_at_row_col(colID, rowID))


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
                selection.add(self.canvas._item_at_row_col(colID, rowID))

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
                shiftItems.add(self.canvas._item_at_row_col(colID, rowID))

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

        self.canvas.set_up_labels()
        self.canvas.emit(SIGNAL("adjust_view"))
        self.canvas.emit(SIGNAL("scene_changed"))
        self.canvas.insertDeleteRowColDialog.set_upper_row_limit( \
                self.canvas._numRows)





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
                shiftedItems.add(self.canvas._item_at_row_col(colID, rowID))

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
                selection.add(self.canvas._item_at_row_col(colID, rowID))

        for item in selection:
            self.canvas.removeItem(item)
            del item

        # shift the rest back into place
        selection.clear()
        for rowID in range(0, self.numRows):
            for colID in range(self.pivot + self.columnShift, 
                               self.numColumns + self.columnShift):
                selection.add(self.canvas._item_at_row_col(colID, rowID))

        for item in selection:
            shift_item_column_wise(item, columnLeftShift, self.unitWidth)
 
        self.canvas._numColumns -= self.columnShift
        self._finalize()
       


    def _finalize(self):
        """ Common stuff for redo/undo after the canvas has been adjusted
        appropriately.

        """

        self.canvas.set_up_labels()
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
                selection.add(self.canvas._item_at_row_col(colID, rowID))

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
                selection.add(self.canvas._item_at_row_col(colID, rowID))

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
                shiftItems.add(self.canvas._item_at_row_col(colID, rowID))

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

        self.canvas.set_up_labels()
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
            self.oldColor = canvas._activeColorObject.get_content()
            
        self.newColorObject = newColorObject
        if newColor:
            self.newColor = newColor
        else:
            self.newColor = newColorObject.get_content()



    def redo(self):
        """ The redo action. """

        self.canvas._activeColorObject = self.newColorObject
        self.canvas._activeColorObject.set_content(self.newColor)
        self.canvas.emit(SIGNAL("activate_color_selector"),
                         self.newColorObject)




    def undo(self):
        """ The undo action. """

        # we need this check to make sure that we don't call
        # with a None color object before the stack unwinds
        if self.oldColorObject:
            self.oldColorObject.set_content(self.oldColor)
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
        self.activeColor = canvas._activeColorObject.get_content()
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
        """ Redo action for selected cells """

        if self.selectedCells:
            for item in self.selectedCells:
                itemID = get_item_id(item.column, item.row) 
                self.canvas._selectedCells[itemID] = \
                        PatternCanvasEntry(item.column, item.row, 
                                           item.width, item.color,
                                           item.symbol) 
                item = self.canvas._item_at_row_col(item.column, item.row)
                item._select()



    def _redo_unselectedCells(self):
        """ Redo action for unselected cells """

        # if we have inactivated cells, remove them
        if self.unselectedCells:
            for item in self.unselectedCells:
                itemID = get_item_id(item.column, item.row) 
                del self.canvas._selectedCells[itemID]

                item = self.canvas._item_at_row_col(item.column, item.row)
                item._unselect()



    def _redo_paintActiveSymbol(self):
        """ Redo action for painting the active symbol into
        selected cells.

        """

        self.oldSelection = self.canvas._selectedCells.copy()
        self.activeSymbolContent = self.activeSymbol.get_content()
        self.width = int(self.activeSymbolContent["width"])
        self.chunks = chunkify_cell_arrangement(self.width, self.oldSelection)
        if self.chunks:
            self.didInsertActiveSymbol = True

        # FIXME: This might require a bit more thinking
        # If the symbol itself provides a color other than
        # white it overrides the active color
        if "backgroundColor" in self.activeSymbolContent:
            itemColor = QColor(self.activeSymbolContent["backgroundColor"])
        else:
            itemColor = self.activeColor

        for chunk in self.chunks:
            totalWidth = 0

            # location of leftmost item in chunk
            column = chunk[0].column
            row = chunk[0].row
            item = self.canvas._item_at_row_col(column, row)
            origin = item.pos()

            # compute total width and remove old items
            for entry in chunk:
                totalWidth += entry.width
                gridItem = self.canvas._item_at_row_col(entry.column, 
                                                        entry.row)
                self.canvas.removeItem(gridItem)
                del gridItem

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
                del self.canvas._selectedCells[itemID]

                item = self.canvas._item_at_row_col(item.column, item.row)
                item._unselect()



    def _undo_unselectedCells(self):
        """ Undo action for unseleced cells """

        if self.unselectedCells:
            for item in self.unselectedCells:
                itemID = get_item_id(item.column, item.row) 
                self.canvas._selectedCells[itemID] = \
                        PatternCanvasEntry(item.column, item.row, 
                                           item.width, item.color, item.symbol) 
                item = self.canvas._item_at_row_col(item.column, item.row)
                item._select()



    def _undo_paintActiveSymbol(self):
        """ Undo action for painting the active symbol. """

        # get rid of previous selection
        for entry in self.newSelection.values():
            gridItem = self.canvas._item_at_row_col(entry.column, 
                                                    entry.row)
            self.canvas.removeItem(gridItem)
            del gridItem

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


