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

from PyQt4.QtCore import (Qt, QRectF, QSize, QPointF, QSizeF, QLineF,
                          SIGNAL, QObject, QString, QPoint, QRect)
from PyQt4.QtGui import (QGraphicsScene, QGraphicsObject, QPen, QColor, 
                         QBrush, QGraphicsTextItem, QFontMetrics, QMenu, 
                         QAction, QGraphicsItem, QGraphicsRectItem,
                         QMessageBox, QGraphicsLineItem, QPainterPath, 
                         QUndoStack, QUndoCommand, QGraphicsItemGroup,
                         QApplication, QCursor)
from PyQt4.QtSvg import (QGraphicsSvgItem, QSvgWidget, QSvgRenderer)

from sconcho.util.canvas import (is_click_in_grid, is_click_on_labels, 
                                 convert_pos_to_col_row,
                                 convert_col_row_to_pos)
from sconcho.gui.manage_grid_dialog import ManageGridDialog
from sconcho.util.misc import wait_cursor

from sconcho.gui.pattern_repeat_dialog import PatternRepeatDialog
from sconcho.util.misc import errorLogger
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

        self._highlightOddRows = True

        self._textLabels = []

        self.insertDeleteRowColDialog = None

        self.gridLegend = {}

        self.set_up_main_grid()
        self.set_up_labels()

        self.set_up_highlightOddRows()



    def set_up_main_grid(self):
        """ This function draws the main grid. """

        for row in range(0, self._numRows):
            self._create_row(row)



    def set_up_highlightOddRows(self):
        """ If the user has selected to highlight all even
        rows in the pattern - this function does it.

        NOTE: Right now this function is not super efficient.
        In particular, we deleted and re-create all PatternHighlightItems
        for every change, even just changing the color. On the other
        hand, the user hopefully won't do these changes very often.

        """

        visibility = self.settings.highlightOddRows.value
        color = self.settings.highlightOddRowsColor.value
        opacity = self.settings.highlightOddRowsOpacity.value/100.0

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternHighlightItem):
                self.removeItem(graphicsItem)
                del graphicsItem

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem) and \
               (graphicsItem.name != "nostitch") and \
               (graphicsItem.row % 2 != 0):
                    
                origin_x = graphicsItem.column * self._unitCellDim.width()
                origin_y = graphicsItem.row * self._unitCellDim.height()
                width = graphicsItem.width * self._unitCellDim.width()
                height = self._unitCellDim.height()
                element = PatternHighlightItem(origin_x, origin_y, width, 
                                               height, QColor(color), opacity)
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
        self.set_up_highlightOddRows()



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

        self._unitCellDim = QSizeF(self.settings.gridCellWidth.value,
                                   self.settings.gridCellHeight.value)
        self._redraw_canvas_after_grid_dimension_change()

       

    def change_odd_row_highlighting(self):
        """ This member function hides or makes visible the
        odd row highlighting. 

        """

        status = self.settings.highlightOddRows.value;
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
        self.set_up_highlightOddRows()

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



    def canvas_item_position_changed(self, canvasItem, oldPosition, newPosition):
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

        patternRepeatCommand = AddPatternRepeat(self, lines)
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
      
        # NOTE: need this for >= Qt 4.7 otherwise
        # rendering of our scene is broken
        #self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
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
        self.update()

        

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





#########################################################
## 
## class for managing a single pattern grid label
## (this does nothing spiffy at all, we just need
## it to identify the item on the canvas)
##
#########################################################
class PatternRepeatItem(QGraphicsItemGroup):

    Type = 70000 + 5

    def __init__(self, lines, width, color, parent = None):

        super(PatternRepeatItem, self).__init__(parent)

        # set up group
        self.lineElements = []
        for line in lines:
            lineElement = QGraphicsLineItem(line)
            self.lineElements.append(lineElement)
            self.addToGroup(lineElement)

        self.setZValue(1)
           
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

        self.setFlag(QGraphicsItem.ItemIsMovable, True)



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



    def mouseReleaseEvent(self, event):
        """ Deal with mouse release events after a previous
        mousePressEvent. Mostly, we just have to revert
        the cursor back.

        """

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
        self._pen = QPen(QColor("black"), 0.1)
        self.setPen(self._pen)

        color.setAlphaF(alpha)
        self._brush = QBrush(color) 
        self.setBrush(self._brush)





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



def can_outline_selection(selection):
    """ This function determines if the currently action selection
    can be outlined. This requires the selection to be connected
    without any holes.

    """

    if len(selection) == 0:
        return False

    # check that rows are consecutive
    cellsByRow = order_selection_by_rows(selection)
    keys = cellsByRow.keys()
    keys.sort()
    differences = set([(j-i) for (i,j) in zip(keys, keys[1:])])
    if len(differences) > 1: 
        return False
    elif len(differences) == 1 and (1 not in differences):
        return False

    # check that each row has no holes
    for row in cellsByRow.values():
        row.sort(lambda x, y: cmp(x.column, y.column))
        if not are_consecutive([row]):
            return False

    return True



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



def get_edge_id(gridPoint1, gridPoint2):
    """ Given the column and row values of two grid points
    return an string ID.

    NOTE: Each cell has 4 grid points. The upper left hand
    corner corresponds to the row/column id of the cell.
    The other corners each add +1 for row and/or column id.
    E.g. lower right hand corner has an id of (row + 1, column + 1).

    """

    return ":".join(map(str, gridPoint1 + gridPoint2))



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



############################################################################
#
# Helper Classes
#
############################################################################

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

    
    def __init__(self, canvas, lines, width = None, color = None,
                 parent = None):

        super(AddPatternRepeat, self).__init__(parent)

        self.canvas = canvas
        self.pathItem = PatternRepeatItem(lines, width, color)
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


    def __init__(self, canvas, parent = None):
        
        super(ColorSelectedCells, self).__init__(parent)
        
        self.setText("color selected cells")
        self.canvas = canvas

        # this keeps a dictionary of cell colors
        # of all selected items
        self.previousColors = {}

        self.selectedCells = canvas._selectedCells.copy()
        self.activeColor = canvas._activeColorObject.color



    def redo(self):
        """ This is the redo action.
        NOTE: Since we don't destroy/create items but just change
        their color, we have to take charge of adding/removing them
        from the legend.

        """

        for (id, item) in self.selectedCells.items():
            self.canvas.remove_from_legend(item)
            self.previousColors[id] = item.color
            canvasItem = self.canvas._item_at_row_col(item.row, item.column)
            canvasItem.change_color(self.activeColor)
            item.color = self.activeColor
            self.canvas.add_to_legend(item)

        self.canvas._selectedCells.clear()



    def undo(self):
        """ This is the undo action. 
        NOTE: Since we don't destroy/create items but just change
        their color, we have to take charge of adding/removing them
        from the legend.

        """

        for (id, item) in self.selectedCells.items():
            previousColor = self.previousColors[id]
            self.canvas.remove_from_legend(item)
            
            canvasItem = self.canvas._item_at_row_col(item.row, item.column)
            canvasItem.change_color(previousColor)
            item.color = previousColor
            self.canvas.add_to_legend(item)

        self.canvas._selectedCells = self.selectedCells.copy()
        
