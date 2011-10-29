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

import operator
import copy
from functools import partial

from PyQt4.QtCore import (Qt, 
                          QRectF, 
                          QPointF, 
                          QSizeF, 
                          QLineF,
                          SIGNAL, 
                          QT_VERSION,
                          QString) 
from PyQt4.QtGui import (QGraphicsScene, 
                         QGraphicsObject, 
                         QPen, 
                         QColor, 
                         QBrush, 
                         QGraphicsTextItem, 
                         QFontMetrics, 
                         QMenu, 
                         QGraphicsItem, 
                         QGraphicsRectItem,
                         QMessageBox, 
                         QGraphicsLineItem, 
                         QPainterPath, 
                         QUndoStack, 
                         QGraphicsItemGroup,
                         QApplication, 
                         QCursor)
from PyQt4.QtSvg import (QGraphicsSvgItem) 

from sconcho.util.canvas import * 
from sconcho.gui.manage_grid_dialog import ManageGridDialog
from sconcho.util.misc import wait_cursor
from sconcho.gui.pattern_repeat_dialog import PatternRepeatDialog
from sconcho.util.misc import errorLogger
from sconcho.gui.undo_framework import (PasteCells, 
                                        InsertRow, 
                                        DeleteRow,
                                        InsertColumn, 
                                        DeleteColumn,
                                        ActivateSymbol, 
                                        ActivateColor, 
                                        PaintCells, 
                                        MoveCanvasItem, 
                                        AddPatternRepeat,
                                        EditPatternRepeat, 
                                        DeletePatternRepeat,
                                        ColorSelectedCells) 
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

        self._unitCellDim = QSizeF(self.settings.gridCellWidth.value,
                                   self.settings.gridCellHeight.value)
        self._numRows = 10
        self._rowLabelOffset = self.settings.rowLabelStart.value
        self._numColumns = 10

        self._copySelection = {}
        self._copySelectionDim = None

        self._textLabels = []

        self.insertDeleteRowColDialog = None

        self.gridLegend = {}

        self.set_up_main_grid()
        self.set_up_labels()

        self.set_up_highlighted_rows()



    def set_up_main_grid(self):
        """ This function draws the main grid. """

        for row in range(0, self._numRows):
            self._create_row(row)



    def set_up_highlighted_rows(self):
        """ If the user has selected to highlight all even
        rows in the pattern - this function does it.

        NOTE: Right now this function is not super efficient.
        In particular, we deleted and re-create all PatternHighlightItems
        for every change, even just changing the color. On the other
        hand, the user hopefully won't do these changes very often.

        """

        visibility = self.settings.highlightRows.value
        color = self.settings.highlightRowsColor.value
        opacity = self.settings.highlightRowsOpacity.value/100.0
        start = self.settings.highlightRowsStart.value
        offset = self._numRows % 2

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternHighlightItem):
                self.removeItem(graphicsItem)
                del graphicsItem

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem) and \
               (graphicsItem.name != "nostitch") and \
               ((graphicsItem.row + offset + start) % 2 != 0):
                    
                origin_x = graphicsItem.column * self._unitCellDim.width()
                origin_y = graphicsItem.row * self._unitCellDim.height()
                width = graphicsItem.width * self._unitCellDim.width()
                height = self._unitCellDim.height()
                element = PatternHighlightItem(origin_x, origin_y, width, 
                                               height, QColor(color), 
                                               opacity)
                element.setZValue(1)
                if visibility == 0:
                    element.hide()
                self.addItem(element)



    def set_up_labels(self):
        """ Add labels to the main grid.
        
        FIXME: This function currently recreates all labels instead
        of just shifting around existing ones. The latter should
        probably be more efficient.

        NOTE: The ranges below are somewhat weird because we count
        backward.
        
        """

        labelIntervalState = self.settings.rowLabelInterval.value
        labelOffset = self.settings.rowLabelStart.value - 1
        labelFont = self.settings.labelFont.value
        
        # figure out how to show the row labels
        interval = 1
        labelStart = self._numRows - 1
        counter_func = lambda x: (self._numRows - x + labelOffset)
        if labelIntervalState == "LABEL_EVEN_ROWS":
            interval = 2
            labelStart -= (labelOffset+1) % 2
        elif labelIntervalState == "LABEL_ODD_ROWS":
            interval = 2
            labelStart -= labelOffset % 2
        elif labelIntervalState == "SHOW_EVEN_ROWS":
            labelStart -= (labelOffset+1) % 2
            counter_func = lambda x: 2*(self._numRows-x)-1+labelOffset 
        elif labelIntervalState == "SHOW_ODD_ROWS":
            labelStart -= labelOffset % 2
            counter_func = lambda x: 2*(self._numRows-x)-1+labelOffset

        for label in self._textLabels:
            self.removeItem(label)
            del label
        self._textLabels = []
           
        fm = QFontMetrics(labelFont)
        unitWidth = self._unitCellDim.width()
        
        # row labels (figure out if even row labels should be on left/right
        evenRowLabelLocation = self.settings.evenRowLabelLocation.value
        oddXPos = unitWidth * self._numColumns
        if evenRowLabelLocation == "LEFT_OF":
            evenXPos = -unitWidth
        else:
            evenXPos = oddXPos

        for row in range(labelStart, -1, -interval):
            rowValue = counter_func(row)
            item = PatternLabelItem(unicode(rowValue))

            yPos = self._unitCellDim.height() * row
            if rowValue % 2 == 0:
                item.setPos(evenXPos, yPos)
            else:
                item.setPos(oddXPos, yPos)

            item.setFont(labelFont)
            item.setToolTip("Shift-Click to select whole row")
            self.addItem(item)
            self._textLabels.append(item)

        # column labels
        yPos = self._unitCellDim.height() * self._numRows
        for col in range(self._numColumns - 1, -1, -1):
            labelText = QString(unicode(self._numColumns - col))
            textWidth = fm.width(labelText)
            item = PatternLabelItem(labelText)
            
            xPos = unitWidth * col + (unitWidth * 0.6 -textWidth)
            item.setPos(xPos, yPos)
            item.setFont(labelFont)
            item.setToolTip("Shift-Click to select whole column")

            self.addItem(item)
            self._textLabels.append(item)

   

    def finalize_grid_change(self):
        """ This function is a wrapper encapsulating all changes
        to elements on the canvas that need to be done after some
        change to the grid (cell size, adding of rows/columns, etc.)

        """

        self.set_up_labels()
        self.set_up_highlighted_rows()



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

        selectCommand = ActivateColor(self, self._activeColorObject, 
                                      newColor)
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

        # probably inefficient but otherwise there are caching
        # artifacts
        self.invalidate()



    def redo(self):
        """ Simple helper slot to redo last action. """

        if self._undoStack.canRedo():
            self._undoStack.redo()

        # probably inefficient but otherwise there are caching
        # artifacts
        self.invalidate()



    def change_grid_cell_dimensions(self):
        """ This function adjust the grid cell dimensions if either
        cell height, width or both have changed.

        """

        self._unitCellDim = QSizeF(self.settings.gridCellWidth.value,
                                   self.settings.gridCellHeight.value)
        self._redraw_canvas_after_grid_dimension_change()

       

    def toggle_row_highlighting(self):
        """ This member function hides or makes visible the
        odd row highlighting. 

        """

        status = self.settings.highlightRows.value;
        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternHighlightItem):
                if status == 0:
                    graphicsItem.hide()
                else:
                    graphicsItem.show()



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
        self.finalize_grid_change()



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
        item.setPos(itemLocation)
        self.addItem(item)

        # add the description part of the legend
        textLocation = QPointF((width+1) * self._unitCellDim.width(),
                                yMax + self._unitCellDim.height() + 10)
        textItem = PatternLegendText(symbol["description"])
        textItem.setPos(textLocation)
        textItem.setFont(self.settings.legendFont.value)
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



    def toggle_nostitch_symbol_visbility(self, status):
        """ Toggles the visibility of all nostitch symbols to on
        or off via show() and hide().

        WARNING: This should only be done temporary while no user
        interaction with the canvas is possible, e.g. during
        exporting. Otherwise it will screw up the undo/redo framwork
        completely.

        """
        
        # make sure to redraw the highlighted areas so highlighting
        # underneath nostitch symbols is disabled
        self.set_up_highlighted_rows()

        nostitchItem = None
        for item in self.items():
            if isinstance(item, PatternGridItem):
                if item.name == "nostitch":
                    nostitchItem = item
                    if status:
                        item.show()
                    else:
                        item.hide()
                        
        if nostitchItem:
            legendID = generate_legend_id(nostitchItem.symbol,
                                          nostitchItem.color)
            (dummy, legendItem, legendTextItem) = self.gridLegend[legendID]
            if status:
                legendItem.show()
                legendTextItem.show()
            else:
                legendItem.hide()
                legendTextItem.hide()

            

    def grid_cell_activated(self, item):
        """ If a grid cell notifies it has been activated add it
        to the collection of selected cells and try to paint
        them.
        
        """
       
        activatedItem = PatternCanvasEntry(item.column, item.row, 
                                           item.width, item.color, 
                                           item.symbol) 
        paintCommand = PaintCells(self, [activatedItem])
        self._undoStack.push(paintCommand)



    def grid_cell_inactivated(self, item):
        """ If a grid cell notifies it has been in-activated remove
        it from the collection of selected cells if present.
        
        """


        inactivatedItem = PatternCanvasEntry(item.column, item.row, 
                                             item.width, item.color, 
                                             item.symbol) 
        paintCommand = PaintCells(self, None, [inactivatedItem])
        self._undoStack.push(paintCommand)



    def canvas_item_position_changed(self, canvasItem, oldPosition, 
                                     newPosition):
        """ A canvas item calls this function if its position on the
        canvas has changed via a user action.

        """

        moveCommand = MoveCanvasItem(canvasItem, oldPosition, newPosition)
        self._undoStack.push(moveCommand)

        

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
        QGraphicsItem specific task such as updating the legend for 
        svg items.
        
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



    def mouseMoveEvent(self, event):
        """ Here we intercept mouse move events on the canvas.

        For now, we just transmit our current position in terms
        of columns and rows.

        """

        (column, row) = convert_pos_to_col_row(event.scenePos(),
                                              self._unitCellDim.width(),
                                              self._unitCellDim.height())

        if column >= 0 and column <= self._numColumns:
            columnString = unicode(self._numColumns - column)
        else:
            columnString = "NA"
        self.emit(SIGNAL("col_count_changed"), columnString)

        rowLabelOffset = self.settings.rowLabelStart.value - 1
        if row >= 0 and row <= self._numRows:
            rowString = unicode(self._numRows - row + rowLabelOffset)
        else:
            rowString = "NA"
        self.emit(SIGNAL("row_count_changed"), rowString)

        return QGraphicsScene.mouseMoveEvent(self, event)

        

    def mousePressEvent(self, event):
        """ Handle mouse press events directly on the canvas. """

        (col, row) = convert_pos_to_col_row(event.scenePos(),
                                            self._unitCellDim.width(),
                                            self._unitCellDim.height())
       
        if event.button() == Qt.RightButton:

            #if is_click_in_grid(col, row, self._numColumns, self._numRows):
            self.handle_right_click_on_grid(event, row, col)

            # don't propagate this event
            return

        elif (event.button() == Qt.LeftButton) and \
             (event.modifiers() & Qt.ShiftModifier):

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

        selection = set()
        unselection = set()
        for item in self.items(region):
            if isinstance(item, PatternGridItem):
                itemID = get_item_id(item.column, item.row)
                entry = PatternCanvasEntry(item.column, item.row, 
                                           item.width, item.color,
                                           item.symbol)
                if itemID in self._selectedCells:
                    unselection.add(entry)
                else:
                    selection.add(entry)

        paintCommand = PaintCells(self, selection, unselection)
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

        selection = set()
        unselection = set()
        for item in selectedItems:
            itemID = get_item_id(item.column, item.row)
            entry = PatternCanvasEntry(item.column, item.row, 
                                       item.width, item.color,
                                       item.symbol)
            if itemID in self._selectedCells:
                unselection.add(entry)
            else:
                selection.add(entry)

        paintCommand = PaintCells(self, selection, unselection)
        self._undoStack.push(paintCommand)



    def get_column_items(self, column):
        """ Returns list of all PatternGridItems in column. """

        colItems = set()
        for row in range(0, self._numRows):
            item = self._item_at_row_col(row, column)
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
            item = self._item_at_row_col(row, column)
            if item:
                rowItems.add(item)
           
        return rowItems



    def handle_right_click_on_grid(self, event, row, col):
        """ Handles a right click on the pattern grid by
        displaying a QMenu with options.

        If the click occured outside the pattern grid we show
        the menu only if there is a pattern repeat item 
        under the cursor. In this case all the other items are
        disabled.

        """

        # search for pattern repeats; we search a slightly extended 
        # area otherwise clicking on them is tricky
        clickInGrid = is_click_in_grid(col, row, self._numColumns,
                                       self._numRows)
        searchArea = QRectF(event.scenePos(), QSizeF(1, 1))
        searchArea = searchArea.adjusted(-4.0, -4.0, 4.0, 4.0)
        patternRepeats = extract_patternRepeatItems(self.items(searchArea))
        if (not patternRepeats) and (not clickInGrid):
            return

        gridMenu = QMenu()
        rowAction = gridMenu.addAction("Insert/Delete Rows and Columns")
        self.connect(rowAction, SIGNAL("triggered()"),
                     partial(self.insert_delete_rows_columns, col, row))
        gridMenu.addSeparator()

        scenePos = event.scenePos()
        colorAction = gridMenu.addAction("&Grab Color")
        self.connect(colorAction, SIGNAL("triggered()"),
                     partial(self.grab_color_from_cell, scenePos))
        gridMenu.addSeparator()

        addRepeatAction = gridMenu.addAction("&Add Pattern Repeat "
                                             "Around Selection")
        self.connect(addRepeatAction, SIGNAL("triggered()"),
                     self.add_pattern_repeat)
        if not can_outline_selection(self._selectedCells.values()):
            addRepeatAction.setEnabled(False)

        
        editRepeatAction = gridMenu.addAction("&Edit Pattern Repeat")
        if patternRepeats:
            self.connect(editRepeatAction, SIGNAL("triggered()"),
                         partial(self.edit_pattern_repeat, 
                                 patternRepeats[0]))
        else:
            editRepeatAction.setEnabled(False)
        gridMenu.addSeparator()

        copyAction = gridMenu.addAction("&Copy Selection")
        (status, (colDim, rowDim)) = \
                is_active_selection_rectangular(self._selectedCells.values())
        self.connect(copyAction, SIGNAL("triggered()"),
                     partial(self.copy_selection, colDim, rowDim))
        if not status:
            copyAction.setEnabled(False)

        pasteAction = gridMenu.addAction("&Paste Selection")
        self.connect(pasteAction, SIGNAL("triggered()"),
                     partial(self.paste_selection, col, row))
        pasteAction.setEnabled(False)
        if self._copySelectionDim:
            pasteColDim = self._copySelectionDim[0]
            pasteRowDim = self._copySelectionDim[1]
            if self._rectangle_self_contained(col, row, pasteColDim,
                                              pasteRowDim):
                pasteAction.setEnabled(True)

        # if the click was outside the grid we can't past and grab colors
        if not clickInGrid:
            pasteAction.setEnabled(False)
            colorAction.setEnabled(False)

        gridMenu.exec_(event.screenPos())



    def adjust_manage_grid_dialog_after_row_label_offset(self, offset):
        """ Change limits in add/delete dialog after row label offset 
        change.

        """

        self._rowLabelOffset = offset
        if self.insertDeleteRowColDialog:
            self.insertDeleteRowColDialog.set_row_limit(\
                self._rowLabelOffset, self._numRows)


    def insert_delete_rows_columns(self, col, row):
        """ This method manages the addition and deletion of rows and 
        columns via a widget.

        NOTE: Make sure the signals are only connected *once* inside the
        if. Otherwise weird things are bound to happen (like multiple
        deletes, inserts, etc.).
        
        """

        if not self.insertDeleteRowColDialog:
            self.insertDeleteRowColDialog = \
                ManageGridDialog(self._rowLabelOffset, self._numRows, 
                                 self._numColumns, row, col, self.parent())
            self.connect(self.insertDeleteRowColDialog, 
                         SIGNAL("insert_rows"), 
                         self.insert_grid_rows)
            self.connect(self.insertDeleteRowColDialog, 
                         SIGNAL("delete_rows"), 
                         self.delete_grid_rows)
            self.connect(self.insertDeleteRowColDialog, 
                         SIGNAL("insert_columns"), 
                         self.insert_grid_columns)
            self.connect(self.insertDeleteRowColDialog, 
                         SIGNAL("delete_columns"), 
                         self.delete_grid_columns)
        else:
            self.insertDeleteRowColDialog.set_row_col(row,col)

        self.insertDeleteRowColDialog.raise_()
        self.insertDeleteRowColDialog.show()



    def apply_color_to_selection(self):
        """ This slot changes the background color of all selected cells
        to the currently active color.

        """

        if not self._selectedCells:
            return

        colorCommand = ColorSelectedCells(self)
        self._undoStack.push(colorCommand)
        self.clear_all_selected_cells()



    def add_pattern_repeat(self):
        """ Adds a pattern repeat around the current selection. """

        # if noting is selected we are done
        if not self._selectedCells:
            return

        edges = {}
        for entry in self._selectedCells.values():

            row = entry.row
            col = entry.column
            for shift in range(entry.width):
                edgeIDs = [get_edge_id((col + shift, row),
                                       (col + 1 + shift, row)),
                           get_edge_id((col + shift, row),
                                       (col + shift, row + 1)),
                           get_edge_id((col + shift + 1, row),
                                       (col + shift + 1, row + 1)),
                           get_edge_id((col + shift, row + 1),
                                       (col + shift + 1, row + 1))]

                for edgeID in edgeIDs:
                    if edgeID in edges:
                        edges[edgeID] = 0
                    else:
                        edges[edgeID] = 1
                
        lines = []
        cellWidth = self._unitCellDim.width()
        cellHeight = self._unitCellDim.height()
        for (edgeID, switch) in edges.items():
            if switch:
                (col1, row1, col2, row2) = map(int, edgeID.split(":"))

                line = QLineF(col1 * cellWidth, row1 * cellHeight,
                              col2 * cellWidth, row2 * cellHeight)
                lines.append(line)

        repeatItem = PatternRepeatItem(lines)
        patternRepeatCommand = AddPatternRepeat(self, repeatItem)
        self._undoStack.push(patternRepeatCommand)
        


    def edit_pattern_repeat(self, patternRepeat):
        """ Edit the provided pattern repeat item. """

        patternRepeat.highlight()
        dialog = PatternRepeatDialog(patternRepeat.line_width,
                                     patternRepeat.line_color)
        status = dialog.exec_()
        if status > 0:
            patternRepeatCommand = EditPatternRepeat(patternRepeat,
                                                     dialog.color,
                                                     dialog.width)
            self._undoStack.push(patternRepeatCommand)
        elif status < 0:
            patternRepeatCommand = DeletePatternRepeat(self, patternRepeat)
            self._undoStack.push(patternRepeatCommand)
            
        patternRepeat.unhighlight()



    def grab_color_from_cell(self, scenePosition):
        """ Extract the color from the selected cell
        (the one at scenePosition) and add it to the currently active
        color selector.
        
        """

        allItems = self.items(scenePosition)
        patternGridItems = extract_patternGridItems(allItems)
        if len(patternGridItems) != 1:
            errorString = "grab_color_from_cell: expected 1 item, found %d" % \
                          len(patternGridItems)
            errorLogger.write(errorString)
            return

        color = patternGridItems[0].color
        self.change_active_color(color)



    def copy_selection(self, colDim, rowDim):
        """ This slot copies the current selection. """

        if not self._selectedCells:
            return

        self._copySelection.clear()
        self._copySelection = self._selectedCells.copy()
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

        # we need to add a small fraction to witdh and height
        # in case of single row column selections (otherwise Qt
        # doesn recognize the selection as a rectangle)
        lowerRightCorner += QPointF(self._unitCellDim.width() * 0.01,
                                    self._unitCellDim.height() * 0.01)

        allItems = self.items(QRectF(upperLeftCorner, lowerRightCorner))
        patternGridItems = extract_patternGridItems(allItems)

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
            deadSelection[itemID] = PatternCanvasEntry(item.column, 
                                                       item.row, 
                                                       item.width, 
                                                       item.color, 
                                                       item.symbol)

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
            leftItem = self._item_at_row_col(rowCount, column)

            if not leftItem:
                errorString = ("_rectangle_self_contained: trying to access "
                               "nonexistent leftItem.")
                errorLogger.write(errorString)
                return False

            if (leftItem.width > 1) and (leftItem.column < column):
                return False

            # make sure we don't fall off at the right
            if (column + colDim < self._numColumns):
                rightItem = self._item_at_row_col(rowCount, column + colDim)

                if not rightItem:
                    errorString = ("_rectangle_self_contained: trying to access "
                                   "nonexistent rightItem.")
                    errorLogger.write(errorString)
                    return False
                    
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
        patternGridItems = extract_patternGridItems(allItems)

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
                    removedItems.append((item.name, canvasColumn, canvasRow))
                    item = items[index]
                    self.removeItem(item)
                    del item

        return removedItems 



    def _item_at_row_col(self, row, column):
        """ Returns the PatternGridItem at the given column and row
        or None if there isn't one.

        """

        pos = convert_col_row_to_pos(column, row, self._unitCellDim.width(),
                                     self._unitCellDim.height())

        # we really only expect one PatternGridItem to be present;
        # however there may in principle be others (legend items etc)
        # so we have to pick it out
        allItems = self.items(pos)
        patternGridItems = extract_patternGridItems(allItems)
        if len(patternGridItems) > 1:
            errorString = "_item_at_row_col: expected <=1 item, found %d" % \
                          len(patternGridItems)
            errorLogger.write(errorString)
            return None
        elif len(patternGridItems) == 0:
            return None
        else:
            return patternGridItems[0]



    def insert_grid_rows(self, num, mode, rowPivot):
        """ Deals with requests to insert a row. This operation might
        take some time so we switch to a wait cursor.

        """

        pivot = self.convert_canvas_row_to_internal(rowPivot)
        assert(pivot >= 0 and pivot < self._numRows)

        insertRowCommand = InsertRow(self, num, pivot, mode)
        self._undoStack.push(insertRowCommand)

        

    def delete_grid_rows(self, num, mode, rowPivot):
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
            if ((pivot + num) > self._numRows) or (num >= self._numRows):
                QMessageBox.warning(None, msg.canNotDeleteRowBelowTitle,
                                    msg.canNotDeleteRowBelowText,
                                    QMessageBox.Close)
                return

       
        deleteRowCommand = DeleteRow(self, num, pivot, mode)
        self._undoStack.push(deleteRowCommand)
 


    def insert_grid_columns(self, num, mode, columnPivot):
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
                item = self._item_at_row_col(row, pivot + shift)
                if not item:
                    return
                
                if isinstance(item, PatternGridItem):
                    if item.column != (pivot + shift):
                        QMessageBox.warning(None, msg.noColInsertLayoutTitle,
                                            msg.noColInsertLayoutText,
                                            QMessageBox.Close)
                        return

        # ok we're good to insert then 
        insertColumnCommand = InsertColumn(self, num, pivot, mode)
        self._undoStack.push(insertColumnCommand)



    def delete_grid_columns(self, num, mode, columnPivot):
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
            if ((pivot + num) > self._numColumns) or (num >= self._numColumns):
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

        selectedItems = set()
        for rowID in range(0, self._numRows):
            for colID in colRange:
                item = self._item_at_row_col(rowID, colID)
                if item:
                    selectedItems.add(item)

        selection = []
        for item in selectedItems:
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

        return (self._numRows + self._rowLabelOffset - row - 1)



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
        self.finalize_grid_change()

        self.emit(SIGNAL("adjust_view"))
        


    @wait_cursor
    def load_previous_pattern(self, knittingSymbols, patternGridItemInfo,
                              legendItemInfo, patternRepeats):
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
        

        # now that we have all canvas items, let's put them back in place
        self._clear_canvas()
        for entry in allPatternGridItems:
            item = self.create_pattern_grid_item(*entry)
            self.addItem(item)

        for entry in allLegendItems:
            arrange_label_item(self.gridLegend, *entry)

        for entry in patternRepeats:
            self._load_patternRepeatItem(entry)
        

        # need to clear our caches, otherwise we'll try 
        # to remove non-existing items
        self._textLabels = []
        self.finalize_grid_change()
        self.change_grid_cell_dimensions()

        self.emit(SIGNAL("adjust_view"))
        return True



    def _load_patternRepeatItem(self, itemInfo):
        """ Recreates a pattern repeat item based on itemInfo. """
        
        repeatItem = PatternRepeatItem(itemInfo["lines"],
                                       itemInfo["width"],
                                       itemInfo["color"])
        self.addItem(repeatItem)
        repeatItem.setPos(itemInfo["position"])



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
        
        labelFont = self.settings.labelFont.value
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
        
        legendFont = self.settings.legendFont.value
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
      
        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if QT_VERSION < 0x040703:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

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
        self._backBrush = QBrush(self.color)
        self._highlightBrush = QBrush(QColor(Qt.darkGray), Qt.Dense2Pattern)

        self.symbol = None
        self._set_symbol(defaultSymbol)



    def mousePressEvent(self, event):
        """ Handle user press events on the item.

        NOTE: We ignore all events with shift or control clicked.

        """

        if (event.modifiers() & Qt.ControlModifier) or \
               (event.modifiers() & Qt.ShiftModifier):
            event.ignore()
            return

        if not self._selected:
            self.emit(SIGNAL("cell_selected"), self)
        else:
            self.emit(SIGNAL("cell_unselected"), self)



    def change_geometry(self, newDim):
        """ This slot changes the unit dimensions of the item. """

        self.unitDim = newDim
        self.size    = QSizeF(self.unitDim.width() * self.width,
                              self.unitDim.height() * self.height)



    def change_color(self, newColor):
        """ This slot changes the color of the items. """

        self.color = newColor
        self._backBrush = QBrush(self.color)

        

    @property
    def name(self):
        """ Return the name of the symbol we contain """

        return self.symbol["name"]
    


    def _unselect(self):
        """ Unselects a given selected cell. """

        self._selected = False
        self._backBrush = QBrush(self.color)
        self.update()



    def _select(self):
        """ Selects a given unselected cell. """

        self._selected = True
        self._backBrush = self._highlightBrush
        self.update()


            
    def _set_symbol(self, newSymbol):
        """ Adds a new svg image of a knitting symbol to the scene. """

        self.symbol = newSymbol
        svgPath = newSymbol["svgPath"]
        if not self.renderer().load(svgPath):
            errorMessage = ("PatternGridItem._set_symbol: failed to load "
                           "symbol %s" % svgPath)
            errorLogger.write(errorMessage)
            return

        # apply color if present
        if "backgroundColor" in newSymbol:
            self._backColor = QColor(newSymbol["backgroundColor"])
            self._backBrush = QBrush(QColor(newSymbol["backgroundColor"]))

        self.update()



    def boundingRect(self):
        """ Return the bounding rectangle of the item. """

        halfPen = self._penSize * 0.5
        return QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
                                                       halfPen, halfPen)
        


    def paint(self, painter, option, widget):
        """ Paint ourselves. """

        painter.setPen(self._pen)
        painter.setBrush(self._backBrush)
        halfPen = self._penSize * 0.5
        scaledRect = \
            QRectF(self.origin, self.size).adjusted(halfPen, halfPen, 
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

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if QT_VERSION < 0x040703:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
       
        self.setZValue(zValue)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

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



    def mousePressEvent(self, event):
        """ We reimplement this function to store the position of
        the item when a user issues a mouse press.

        """

        self._position = self.pos()
        
        if (event.modifiers() & Qt.ControlModifier):
            QApplication.setOverrideCursor(QCursor(Qt.SizeAllCursor))
        else:
            event.ignore()

        return QGraphicsSvgItem.mousePressEvent(self, event)

    

    def mouseReleaseEvent(self, event):
        """ We reimplement this function to check if its position
        has changed since the last mouse click. If yes we
        let the canvas know so it can store the action as
        a Redo/Undo event.

        """
        
        QApplication.restoreOverrideCursor()

        # this is needed for redo/undo
        if self._position != self.pos():
           self.scene().canvas_item_position_changed(self, self._position,
                                                     self.pos())
           
        return QGraphicsSvgItem.mouseReleaseEvent(self, event)



    def change_geometry(self, newDim):
        """ This slot changes the unit dimensions of the item. """

        self.unitDim = newDim
        self.size    = QSizeF(self.unitDim.width() * self.width,
                              self.unitDim.height() * self.height)



    @property
    def name(self):
        """ Return the name of the knitting symbol we contain. """

        return self.symbol["name"]



    def _set_symbol(self, newSymbol):
        """ Adds a new svg image of a knitting symbol to the scene. """

        self.symbol = newSymbol
        svgPath = newSymbol["svgPath"]
        if not self.renderer().load(svgPath):
            errorMessage = ("PatternLegendItem._set_symbol: failed to load "
                           "symbol %s" % svgPath)
            errorLogger.write(errorMessage)
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
## class for managing the descriptive text of a legend
## item
##
#########################################################
class PatternLegendText(QGraphicsTextItem):

    Type = 70000 + 3


    def __init__(self, text, parent = None):

        super(PatternLegendText, self).__init__(text, parent)

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if QT_VERSION < 0x040703:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)

        self._position = self.pos()



    def mousePressEvent(self, event):
        """ We reimplement this function to store the position of
        the item when a user issues a mouse press.

        """

        self._position = self.pos()

        if (event.modifiers() & Qt.ControlModifier):
            QApplication.setOverrideCursor(QCursor(Qt.SizeAllCursor))
            self.setTextInteractionFlags(Qt.NoTextInteraction)
        else:
            event.ignore()

        return QGraphicsTextItem.mousePressEvent(self, event)



    def mouseReleaseEvent(self, event):
        """ We reimplement this function to check if its position
        has changed since the last mouse click. If yes we
        let the canvas know so it can store the action as
        a Redo/Undo event.

        """

        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        QApplication.restoreOverrideCursor()

        # this is needed for undo/redo
        if self._position != self.pos():
           self.scene().canvas_item_position_changed(self, self._position,
                                                     self.pos()) 

        return QGraphicsTextItem.mouseReleaseEvent(self, event)



#########################################################
## 
## class for managing a single pattern grid label
## (this does nothing spiffy at all, we just need
## it to identify the item on the canvas)
##
#########################################################
class PatternLabelItem(QGraphicsTextItem):

    Type = 70000 + 4


    def __init__(self, text, parent = None):

        super(PatternLabelItem, self).__init__(text, parent)


        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if QT_VERSION < 0x040703:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)



#########################################################
## 
## class for managing a single pattern grid label
## (this does nothing spiffy at all, we just need
## it to identify the item on the canvas)
##
#########################################################
class PatternRepeatItem(QGraphicsItemGroup):
    """ NOTE: For some reason QGraphicsItemGroup's scenePos()
    does not seem to return the scene coordinate but rather
    the item coordinates. Thus, we have to compute the canvas
    coordinate by means of initially computing the uper left
    corner of the group.

    """

    Type = 70000 + 5

    def __init__(self, lines, width = None, color = None, parent = None):

        super(PatternRepeatItem, self).__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setZValue(1)

        # set up group
        self.lineElements = []
        points = []
        for line in lines:
            points.append(line.p1())
            points.append(line.p2())
            lineElement = QGraphicsLineItem(line)
            self.lineElements.append(lineElement)
            self.addToGroup(lineElement)

        # extract right and top bounds 
        if points:
            self.leftBound = points[0]
            self.topBound = points[0]
            for point in points[1:]:
                if point.x() < self.leftBound.x():
                    self.leftBound = point
                if point.y() < self.topBound.y():
                    self.topBound = point
           
        # default pen
        if width:
            self.width = width
        else:
            self.width = 5

        if color:
            self.color = color
        else:
            self.color = QColor(Qt.red)
            
        self.paint_elements()



    def paint_elements(self, brushStyle = None):
        """ This member paints our path with the current
        color and line width.

        """

        if brushStyle:
            brush = QBrush(self.color, brushStyle)
        else:
            brush = QBrush(self.color)

        pen = QPen()
        pen.setWidth(self.width)
        pen.setBrush(brush)
        for line in self.lineElements:
            line.setPen(pen)



    def highlight(self):
        """ Highlights the cells somewhat so users can tell
        what they clicked on.

        """

        self.paint_elements(Qt.Dense2Pattern)



    def unhighlight(self):
        """ Revert hightlighting of cells and go back to normal
        brush.

        """

        self.paint_elements(Qt.NoBrush)



    @property
    def line_color(self):
        """ Returns a the current line color. """

        return self.color
        


    @property
    def line_width(self):
        """ Returns a the current line width. """

        return self.width



    def set_properties(self, color, width):
        """ Sets the color and width to the requested values.

        NOTE: the fact that we call paint_elements in addition to
        updating the attributes is a bit dirty but hopefully ok.

        """

        self.color = color
        self.width = width
        self.paint_elements()

         

    def mousePressEvent(self, event):
        """ Deal with mouse press events on the area spanned
        by a PatternRepeatItem.

        We only accept mouse press events with Control key
        pressed to allow the motion of the item across the
        canvas.

        NOTE: We also change the cursor type to make the
        motion of pattern repeat items a bit more visible.

        """

        self._position = self.pos()
        
        if (event.modifiers() & Qt.ControlModifier):
            QApplication.setOverrideCursor(QCursor(Qt.SizeAllCursor))
        else:
            event.ignore()

        return QGraphicsItemGroup.mousePressEvent(self, event)

    
    def _snap_to_grid(self):
        """ Snap to nearest grid point. 

        TODO: Currently we only use the left and top edge for this. A 
        more sophisticated algorithm would probably also use the right and
        bottom edget.

        """
        
        numRows = self.scene()._numRows
        numCols = self.scene()._numColumns
        cellXDim = self.scene()._unitCellDim.width()
        cellYDim = self.scene()._unitCellDim.height()
        bound = self.scenePos()
  
        curX = self.leftBound.x()+bound.x()
        curY = self.topBound.y()+bound.y()       
        withinGrid = (curX > -(0.5*cellXDim) \
                      and curX < (numCols+0.5)*cellXDim \
                      and curY > -(0.5*cellYDim) \
                      and curY < (numRows+0.5)*cellYDim)

        if withinGrid:
            # snap in X
            if curX % cellXDim < 0.5*cellXDim:
                self.moveBy(-(curX % cellXDim), 0)
            else:
                self.moveBy(cellXDim - curX % cellXDim, 0)

            # snap in Y
            if curY % cellYDim < 0.5*cellYDim:
                self.moveBy(0, -(curY % cellYDim))
            else:
                self.moveBy(0, cellYDim - curY % cellYDim)
            


    def mouseReleaseEvent(self, event):
        """ Deal with mouse release events after a previous
        mousePressEvent. Mostly, we just have to revert
        the cursor back.

        """

        if self.scene().settings.snapPatternRepeatToGrid.value == Qt.Checked:
            self._snap_to_grid()

        if self._position != self.pos():
            self.scene().canvas_item_position_changed(self, self._position,
                                                      self.pos()) 

        QApplication.restoreOverrideCursor()

       
        return QGraphicsItemGroup.mouseReleaseEvent(self, event)





#########################################################
## 
## class for managing a rectangular item for 
## highlighting odd rows
##
#########################################################
class PatternHighlightItem(QGraphicsRectItem):

    Type = 70000 + 6

   
    def __init__(self, x, y, width, height, color, alpha,
                 parent = None):

        super(PatternHighlightItem, self).__init__(x, y, width, height, 
                                                   parent)

        # we don't want to show the outline so draw it
        # in white
        self._pen = QPen(Qt.NoPen) 
        self.setPen(self._pen)

        color.setAlphaF(alpha)
        self._brush = QBrush(color) 
        self.setBrush(self._brush)




############################################################################
#
# Helper Functions
#
############################################################################
def extract_patternGridItems(allItems):
    """ From a list of QGraphicsItems extracts and returns
    all PatternGridItems.

    """

    patternGridItems = []
    for item in allItems:
        if isinstance(item, PatternGridItem):
            patternGridItems.append(item)

    return patternGridItems



def extract_patternRepeatItems(allItems):
    """ From a list of QGraphicsItems extracts and returns
    all PatternRepeatItems.

    """

    patternRepeatItems = []
    for item in allItems:
        if isinstance(item, PatternRepeatItem):
            patternRepeatItems.append(item)

    return patternRepeatItems





