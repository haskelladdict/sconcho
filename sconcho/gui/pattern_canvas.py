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

from functools import partial

try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str
 
from PyQt4.QtCore import (Qt, 
                          QRectF, 
                          QPointF, 
                          QSizeF, 
                          QLineF,
                          SIGNAL, 
                          QT_VERSION)
from PyQt4.QtGui import (QGraphicsScene, 
                         QGraphicsObject, 
                         QPen, 
                         QAction,
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
from sconcho.util.misc import wait_cursor
from sconcho.gui.pattern_repeat_dialog import PatternRepeatDialog
from sconcho.gui.row_repeat_number_dialog import RowRepeatNumDialog
from sconcho.gui.num_row_column_dialog import NumRowColumnDialog
from sconcho.util.misc import errorLogger
from sconcho.gui.undo_framework import *
from sconcho.gui.pattern_canvas_objects import *
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
        self.rowRepeatTracker = RowRepeatTracker()
        self.rowLabelTracker = RowLabelTracker(self)
        self.columnLabelTracker = ColumnLabelTracker(self)

        self._copySelection = {}
        self._copySelectionDim = None

        self._textLabels = []
        self.gridLegend = {}
        self.repeatLegend = {}
        self.canvasTextBoxes = {}

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

        """

        # clear all previous labels
        for label in self._textLabels:
            self.removeItem(label)
            del label
        self._textLabels = []
        
        labelFont = self.settings.labelFont.value
        fm = QFontMetrics(labelFont)

        self._set_up_row_labels(labelFont, fm)

        # hide row labels again if they are turned off
        # FIXME: This seems a little clunky - we need it
        # only because of the row repeats
        if not self.settings.showRowLabels.value:
            self.toggle_rowLabel_visibility(False)

        self._set_up_column_labels(labelFont, fm)



    def _set_up_row_labels(self, labelFont, fontMetric):
        """ Set up row labels. """

        unitWidth = self._unitCellDim.width()
        
        # we use lamda function so we can control positioning 
        # based on the actual labeltext
        rightXPos = lambda x: unitWidth * self._numColumns
        leftXPos = lambda x: - 0.5*unitWidth - fontMetric.width(x) 

        evenRowLabelLocation = self.settings.evenRowLabelLocation.value
        if evenRowLabelLocation == "LEFT_OF":
            evenXPos = leftXPos
        else:
            evenXPos = rightXPos

        oddRowLabelLocation = self.settings.oddRowLabelLocation.value
        if oddRowLabelLocation == "LEFT_OF":
            oddXPos = leftXPos
        else:
            oddXPos = rightXPos

        rowLabelList = self.rowLabelTracker.get_labels()
        for (row, rowLabels) in enumerate(rowLabelList):
            if not rowLabels:
                continue

            labelText = unicode(rowLabels[0])
            for label in rowLabels[1:]:
                labelText += ", " + unicode(label)
            
            item = PatternLabelItem(str(labelText), isRowLabel = True)
            yPos = self._unitCellDim.height() * (self._numRows - row - 1)
            if rowLabels[0] % 2 == 0:
                item.setPos(evenXPos(labelText), yPos)
            else:
                item.setPos(oddXPos(labelText), yPos)

            item.setFont(labelFont)
            item.setToolTip("Shift-Click to select whole row")
            self.addItem(item)
            self._textLabels.append(item)


    
    def _set_up_column_labels(self, labelFont, fontMetric):
        """ Set up column labels. """

        unitWidth = self._unitCellDim.width()
        yPos = self._unitCellDim.height() * self._numRows
        
        columnLabelList = self.columnLabelTracker.get_labels()
        for (col, colLabel) in enumerate(columnLabelList):
            if not colLabel:
                continue

            labelText = QString(unicode(colLabel))
            textWidth = fontMetric.width(labelText)
            item = PatternLabelItem(labelText, isRowLabel = False)
            
            xPos = unitWidth * (self._numColumns - col - 1) + \
                (unitWidth * 0.6 -textWidth)
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
        self.invalidate()



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
        """ Change the currently active color """

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
            (item, textItem) = self._add_legend_item(item.symbol, 
                                                     item.color)
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
                graphicsItem.change_geometry(self._unitCellDim)


        # fix labels
        self.finalize_grid_change()



    def _get_legend_y_coordinate_for_placement(self):
        """ Computes a conservative good value of the y
        coordinate for placing the next legend item. 

        """

        legendYmax = compute_max_legend_y_coordinate(self.gridLegend,
                                                     self.repeatLegend)
        canvasYmax = (self._numRows + 1) * self._unitCellDim.height()
        yMax = max(legendYmax, canvasYmax)
        return yMax
        


    def _add_legend_item(self, symbol, color):
        """ This adds a new legend entry including an PatternLegendItem
        and a textual description. This function also attemps to be
        sort of smart about where to put the item.
        
        """

        yMax = self._get_legend_y_coordinate_for_placement()

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

        self._paint_cells(None, self._selectedCells.values())



    def grid_cell_activated(self, item):
        """ If a grid cell notifies it has been activated add it
        to the collection of selected cells and try to paint
        them.
        
        """
       
        activatedItem = PatternCanvasEntry(item.column, item.row, 
                                           item.width, item.color, 
                                           item.symbol) 
        self._paint_cells([activatedItem])



    def grid_cell_inactivated(self, item):
        """ If a grid cell notifies it has been in-activated remove
        it from the collection of selected cells if present.
        
        """


        inactivatedItem = PatternCanvasEntry(item.column, item.row, 
                                             item.width, item.color, 
                                             item.symbol) 
        self._paint_cells(None, [inactivatedItem])



    def canvas_item_position_changed(self, canvasItem, oldPosition, 
                                     newPosition):
        """ A canvas item calls this function if its position on the
        canvas has changed via a user action.

        """

        moveCommand = MoveCanvasItem(canvasItem, oldPosition, newPosition)
        self._undoStack.push(moveCommand)

        

    def create_pattern_grid_item(self, origin, col, row, width, height, 
                                 knittingSymbol, color):
        """ Creates a new PatternGridItem of the specified dimension
        at the given location.
        
        """

        item = PatternGridItem(self._unitCellDim, col, row, width, height,
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

        self._paint_cells(None)



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
            self.handle_right_click_on_canvas(event, col, row)

            # don't propagate this event
            return

        elif (event.button() == Qt.LeftButton) and \
             (event.modifiers() & Qt.ShiftModifier):

            if is_click_on_labels(col, row, self._numColumns, 
                                  self._numRows):
                 self.select_column_row_cells(col, row)

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

        self._paint_cells(selection, unselection)



    def select_column_row_cells(self, col, row):
        """ Deal with user clicks on the grid labels. 

        These select whole rows or columns depending on
        if a column or row label was clicked on.

        """

        assert ((row == self._numRows) or (col == self._numColumns) or
                (row == -1) or (col == -1))

        if (row == -1) or (row == self._numRows):
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

        self._paint_cells(selection, unselection)




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

   

    def show_delete_text_item_menu(self, screenPos, textItem):
        """ Menu for deleting PatternTextItems.

        This menu appears when the user right clicks on a
        PatternTextItem.

        """
        
        deleteTextMenu = QMenu()
        deleteAction = deleteTextMenu.addAction("delete text box")
        self.connect(deleteAction, SIGNAL("triggered()"),
                     partial(self.delete_text_item, textItem))
        deleteTextMenu.exec_(screenPos)



    def insert_delete_columns_rows_menu(self, screenPos, col, row):
        """ Show menu for deleting rows or columns. """

        rowColMenu = QMenu()

        markedRows = self.marked_rows()
        markedColumns = self.marked_columns()

        # row options
        deleteRowsAction = rowColMenu.addAction("delete selected &rows")
        self.connect(deleteRowsAction, SIGNAL("triggered()"),
                     self.delete_marked_rows)
        if not markedRows:
            deleteRowsAction.setEnabled(False)

        addRowAboveAction = rowColMenu.addAction("&insert rows above")
        self.connect(addRowAboveAction, SIGNAL("triggered()"),
                     partial(self.insert_grid_rows, "above"))

        addRowBelowAction = rowColMenu.addAction("insert rows &below")
        self.connect(addRowBelowAction, SIGNAL("triggered()"),
                     partial(self.insert_grid_rows, "below"))
        if len(markedRows) != 1:
            addRowBelowAction.setEnabled(False)
            addRowAboveAction.setEnabled(False)

        rowColMenu.addSeparator()
        addRowRepeatAction = rowColMenu.addAction("&add row repeat")
        self.connect(addRowRepeatAction, SIGNAL("triggered()"),
                     self.add_row_repeat)
        if (not markedRows) or (not self.can_add_row_repeat()):
            addRowRepeatAction.setEnabled(False)
        
        deleteRowRepeatAction = rowColMenu.addAction("&delete row repeat")
        self.connect(deleteRowRepeatAction, SIGNAL("triggered()"),
                     self.delete_row_repeat)
        if (not markedRows) or (not self.can_delete_row_repeat()):
            deleteRowRepeatAction.setEnabled(False)

        rowColMenu.addSeparator()
        # column options
        deleteColsAction = rowColMenu.addAction("delete selected &columns")
        self.connect(deleteColsAction, SIGNAL("triggered()"),
                     self.delete_marked_columns)
        if not markedColumns or not self.can_delete_grid_columns():
            deleteColsAction.setEnabled(False)

        addColRightAction = rowColMenu.addAction("insert column right of")
        self.connect(addColRightAction, SIGNAL("triggered()"),
                     partial(self.insert_grid_columns, "right of"))
        if len(markedColumns) != 1 or \
           not self.can_insert_grid_columns("right of"):
            addColRightAction.setEnabled(False)

        addColLeftAction = rowColMenu.addAction("insert column left of")
        self.connect(addColLeftAction, SIGNAL("triggered()"),
                     partial(self.insert_grid_columns, "left of"))
        if len(markedColumns) != 1 or \
           not self.can_insert_grid_columns("left of"):
            addColLeftAction.setEnabled(False)

        rowColMenu.exec_(screenPos)
        rowColMenu.raise_()



    def handle_right_click_on_canvas(self, event, col, row):
        """ Handles a right click on the canvas grid by

        Dispatches the proper menu display function. 

        """

        clickInGrid = is_click_in_grid(col, row, self._numColumns,
                                       self._numRows)

        # check if the click was on a text label
        items = self.items(event.scenePos())
        textItems = \
            list(filter(lambda x: isinstance(x, PatternTextItem), items))

        if textItems:
            self.show_delete_text_item_menu(event.screenPos(), textItems[0])
        elif clickInGrid:
            self.show_grid_menu(event, col, row)
        else:
            self.insert_delete_columns_rows_menu(event.screenPos(),
                                                 col, row)



    def show_grid_menu(self, event, col, row):
        """ Shows the grid action menu. 

        If the click occured outside the pattern grid we show
        the menu only if there is a pattern repeat item 
        under the cursor. In this case all the other items are
        disabled.

        """

        searchArea = QRectF(event.scenePos(), QSizeF(1, 1))
        searchArea = searchArea.adjusted(-4.0, -4.0, 4.0, 4.0)
        patternRepeats = extract_patternItems(self.items(searchArea),
                                              PatternRepeatItem)

        gridMenu = QMenu()
        scenePos = event.scenePos()

        # grab color actoin
        grabColorAction = gridMenu.addAction("&Grab Color and Insert Into "
                                             "Color Selector")
        self.connect(grabColorAction, SIGNAL("triggered()"),
                     partial(self.grab_color_from_cell_add_to_widget, 
                             scenePos))

        # select color action
        selectColorAction = gridMenu.addAction("&Select All Grid Cells "
                                               "With Same Color As Cell")
        self.connect(selectColorAction, SIGNAL("triggered()"),
                     partial(self.select_all_cells_with_same_color, 
                             scenePos))

        # select symbol action
        symbolAction = gridMenu.addAction("&Select All Grid Cells With "
                                          "Same Symbol As Cell")
        self.connect(symbolAction, SIGNAL("triggered()"),
                     partial(self.select_all_cells_with_same_symbol, 
                             scenePos))
        gridMenu.addSeparator()

        # add repeat box action
        addRepeatAction = gridMenu.addAction("&Add Pattern Repeat "
                                             "Around Selection")
        self.connect(addRepeatAction, SIGNAL("triggered()"),
                     self.add_pattern_repeat)
        if not can_outline_selection(self._selectedCells.values()):
            addRepeatAction.setEnabled(False)

        # edit repeat box action
        editRepeatAction = gridMenu.addAction("&Edit Pattern Repeat")
        if patternRepeats:
            self.connect(editRepeatAction, SIGNAL("triggered()"),
                         partial(self.edit_pattern_repeat, 
                                 patternRepeats[0]))
        else:
            editRepeatAction.setEnabled(False)
        gridMenu.addSeparator()

        # copy action
        copyAction = gridMenu.addAction("&Copy Rectangular Selection")
        (status, (colDim, rowDim)) = \
                is_active_selection_rectangular(self._selectedCells.values())
        self.connect(copyAction, SIGNAL("triggered()"),
                     partial(self.copy_selection, colDim, rowDim))
        if not status:
            copyAction.setEnabled(False)

        # paste action
        pasteAction = gridMenu.addAction("&Paste Rectangular Selection")
        self.connect(pasteAction, SIGNAL("triggered()"),
                     partial(self.paste_selection, col, row))
        pasteAction.setEnabled(False)
        if self._copySelectionDim:
            pasteColDim = self._copySelectionDim[0]
            pasteRowDim = self._copySelectionDim[1]
            if self._rectangle_self_contained(col, row, pasteColDim,
                                              pasteRowDim):
                pasteAction.setEnabled(True)

        gridMenu.exec_(event.screenPos())



    def apply_color_to_selection(self, color = None):
        """ This slot changes the background color of all selected cells
        to the currently active color.

        """

        if not self._selectedCells:
            return

        colorCommand = ColorSelectedCells(self, color)
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

        self._undoStack.beginMacro("add pattern repeat")
        patternRepeatCommand = AddPatternRepeat(self, repeatItem)
        self._undoStack.push(patternRepeatCommand)
        patternLegendCommand = AddPatternRepeatLegend(self, repeatItem)
        self._undoStack.push(patternLegendCommand)
        self._undoStack.endMacro()
        


    def edit_pattern_repeat(self, patternRepeat):
        """ Edit the provided pattern repeat item. """

        patternRepeat.highlight()
        if patternRepeat.hasLegend:
            legendCheckStatus = Qt.Checked
        else:
            legendCheckStatus = Qt.Unchecked
        
        dialog = PatternRepeatDialog(patternRepeat.width,
                                     patternRepeat.color,
                                     legendCheckStatus)
        status = dialog.exec_()
        if status > 0:
            self._undoStack.beginMacro("edit pattern repeat")
            patternRepeatCommand = EditPatternRepeat(patternRepeat,
                                                     dialog.color,
                                                     dialog.width)
            self._undoStack.push(patternRepeatCommand)
            patternLegendCommand = EditPatternRepeatLegend(self, 
                                                           patternRepeat,
                                                           dialog.showInLegend)
            self._undoStack.push(patternLegendCommand) 
            self._undoStack.endMacro()
            self.emit(SIGNAL("scene_changed"))
        elif status < 0:
            self._undoStack.beginMacro("delete pattern repeat")
            patternRepeatCommand = DeletePatternRepeat(self, patternRepeat)
            self._undoStack.push(patternRepeatCommand)
            patternLegendCommand = DeletePatternRepeatLegend(self,
                                                             patternRepeat)
            self._undoStack.push(patternLegendCommand)
            self._undoStack.endMacro()
            self.emit(SIGNAL("scene_changed"))

        patternRepeat.unhighlight()



    def grab_color_from_cell(self, scenePosition):
        """ Extract the color from the selected cell
        (the one at scenePosition) 
        
        """

        allItems = self.items(scenePosition)
        patternGridItems = extract_patternItems(allItems, PatternGridItem)
        if len(patternGridItems) != 1:
            errorString = "grab_color_from_cell: expected 1 item, found %d" % \
                          len(patternGridItems)
            errorLogger.write(errorString)
            return

        color = patternGridItems[0].color
        return color



    def grab_color_from_cell_add_to_widget(self, scenePosition):
        """ Apply the color of the selected cell to the active
        color selector.
        
        """

        selectedColor = self.grab_color_from_cell(scenePosition)
        self.change_active_color(selectedColor)



    def select_all_cells_with_same_color(self, scenePosition):
        """ Select all cells with the same color as the selected
        cells.
        
        """

        selectedColor = self.grab_color_from_cell(scenePosition)

        selection = set()
        for item in self.items():
            if isinstance(item, PatternGridItem):
                if item.color == selectedColor:
                    entry = PatternCanvasEntry(item.column, item.row, 
                                               item.width, item.color,
                                               item.symbol)
                    selection.add(entry)

        if selection:
            self._paint_cells(selection, self._selectedCells.values())



    def select_all_cells_with_same_symbol(self, scenePosition):
        """ Select all cells with the same symbol as the selected
        cells.
        
        """

        items = self.items(scenePosition)
        patternGridItems = extract_patternItems(items, PatternGridItem)
       
        if patternGridItems:
            if len(patternGridItems) > 1:
                errorString = ("_item_at_row_col: expected <=1 item, "
                               "found %d" % len(patternGridItems))
                errorLogger.write(errorString)
                return 
            
            selectedItem = patternGridItems[0]
        
            selection = set()
            for item in self.items():
                if isinstance(item, PatternGridItem):
                    if item.name == selectedItem.name:
                        entry = PatternCanvasEntry(item.column, item.row, 
                                                   item.width, item.color,
                                                   item.symbol)
                        selection.add(entry)

            if selection:
                self._paint_cells(selection, self._selectedCells.values())



    def _paint_cells(self, selection, unselection = None):
        """ This function selects all grid cells in selection
        and un-selects all cells in unselection.

        selection and unselection should be a collection
        (set, list) of PatternCanvasEntries.

        """

        paintCommand = PaintCells(self, selection, unselection)
        self._undoStack.push(paintCommand)



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
        patternGridItems = extract_patternItems(allItems, PatternGridItem)

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
                errorString = ("_rectangle_self_contained: trying to "
                               "access nonexistent leftItem.")
                errorLogger.write(errorString)
                return False

            if (leftItem.width > 1) and (leftItem.column < column):
                return False

            # make sure we don't fall off at the right
            if (column + colDim < self._numColumns):
                rightItem = self._item_at_row_col(rowCount, column + colDim)

                if not rightItem:
                    errorString = ("_rectangle_self_contained: trying to "
                                   "access nonexistent rightItem.")
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
        patternGridItems = extract_patternItems(allItems, PatternGridItem)

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
                items.sort(key=(lambda x: x.width))

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



    def _item_at_row_col(self, row, column, patternType = None):
        """ Returns the PatternCanvasItem at the given column and row
        or None if there isn't one.

        """

        # no type is provided we default to PatternGridItems
        if not patternType:
            patternType = PatternGridItem

        pos = convert_col_row_to_pos(column, row, self._unitCellDim.width(),
                                     self._unitCellDim.height())

        # we really only expect one PatternItem of given type to be present;
        # however there may in principle be others (legend items etc)
        # so we have to pick it out
        allItems = self.items(pos)
        patternItems = extract_patternItems(allItems, patternType)
        if len(patternItems) > 1:
            errorString = "_item_at_row_col: expected <=1 item, found %d" %\
                          len(patternItems)
            errorLogger.write(errorString)
            return None
        elif len(patternItems) == 0:
            return None
        else:
            return patternItems[0]



    def _items_in_col_row_range(self, colStart, colEnd, rowStart, rowEnd,
                                patternType = None):
        """ This function selects all items of patternType in a given
        range.

        NOTE: This is much faster than calling item at row col individually
        and should be done for any reasonable range.

        """

        if not patternType:
            patternType = PatternGridItem

        # select cells
        cellWidth = self._unitCellDim.width()
        cellHeight = self._unitCellDim.height()
        allItems = self.items((colStart + 0.25) * cellWidth,
                              (rowStart + 0.25) * cellHeight,
                              (colEnd - colStart + 0.25) * cellWidth,
                              (rowEnd - rowStart + 0.25) * cellHeight)

        selection = set()
        for item in allItems:
            if isinstance(item, patternType):
                selection.add(item)

        return selection



    def marked_rows(self):
        """ Based on the currently selected cells, returns a list of 
        completely marked rows or an empty list otherwise. 

        """

        markedRows = get_marked_rows(self._selectedCells.values(),
                                     self._numColumns)
        return markedRows



    def marked_columns(self):
        """ Based on the currently selected cells, returns a list of 
        completely marked columns or an empty list otherwise. 

        """

        markedColumns = get_marked_columns(self._selectedCells.values(),
                                           self._numRows)
        return markedColumns
    


    def delete_row_repeat(self):
        """ Delete the row repeat corresponding the the
        selected rows. 

        NOTE: This function expects that all marked rows are
        part of a single repeat.
        """

        assert(self.marked_rows())
        deleteRowRepeatCommand = DeleteRowRepeat(self) 
        self._undoStack.beginMacro("delete rows")
        self._undoStack.push(deleteRowRepeatCommand)
        self.clear_all_selected_cells()
        self._undoStack.endMacro()

        if not self.rowRepeatTracker:
            self.emit(SIGNAL("no_more_row_repeats"))




    def can_delete_row_repeat(self):
        """ Checks whether we can delete a row repeat given the
        currently active row selection.

        We allow a user to delete a row repeat if all selected
        rows are within the same row repeat (not all repeat rows
        have to be selected)
        """
        
        rows = self.marked_rows()
        return self.rowRepeatTracker.rows_are_in_a_single_repeat(rows)



    def add_row_repeat(self):
        """ Add a row repeat for all selected rows. """

        # fire up dialog to ask for number of repeats
        repeatDialog = RowRepeatNumDialog()
        if repeatDialog.exec_():
            numRepeats = repeatDialog.num_repeats
            addRowRepeatCommand = AddRowRepeat(self, numRepeats) 
            self._undoStack.beginMacro("add repeat")
            self._undoStack.push(addRowRepeatCommand)
            self.clear_all_selected_cells()
            self._undoStack.endMacro()

            self.emit(SIGNAL("row_repeat_added"))



    def can_add_row_repeat(self):
        """ Checks whether we can add a row repeat given the
        currently selected row selection.

        In order for them to be selectable the cells have
        to form a contiguous block and none of the selected
        rows can be part of an already existing block.

        """

        if self.rowRepeatTracker.rows_are_in_any_repeat(self.marked_rows()):
            return False

        allRows = list(self.marked_rows())
        allRows.sort()
        previous = allRows[0]
        for row in allRows[1:]:
            if row - previous != 1:
                return False
            previous = row

        return True



    def insert_grid_rows(self, mode):
        """ Deals with requests to insert a row. This operation might
        take some time so we switch to a wait cursor.

        NOTE: Call clear_all_selected_cells() before messing with
        the grid layout in InsertRows.

        """

        rowPivot = self.marked_rows()[0] 
        numRowDialog = NumRowColumnDialog("rows")
        if numRowDialog.exec_():
            numRows = numRowDialog.num
            insertRowCommand = InsertRows(self, numRows, rowPivot, mode)
            self._undoStack.beginMacro("insert rows")
            self.clear_all_selected_cells()
            self._undoStack.push(insertRowCommand)
            self._undoStack.endMacro()

        

    def delete_marked_rows(self):
        """ Delete all currently marked rows.

        NOTE: Call clear_all_selected_cells() before messing with
        the grid layout in DeleteRows.

        """

        deadRows = self.marked_rows() 

        deleteRowsCommand = DeleteRows(self, deadRows)
        self._undoStack.beginMacro("delete marked rows")
        self.clear_all_selected_cells()
        self._undoStack.push(deleteRowsCommand)
        self._undoStack.endMacro()



    def can_insert_grid_columns(self, mode):
        """ Check if columns can be inserted as requested.

        This function checks if given the currently
        marked columns we can insert the requested
        columns.

        """

        num = 1
        pivot = self.marked_columns()[0]

        assert(len(self.marked_columns()) == 1)
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
                return False
       
        if not isExternalColumn:
            for row in range(0, self._numRows):
                item = self._item_at_row_col(row, pivot + shift)
                if not item:
                    return False
                
                if isinstance(item, PatternGridItem):
                    if item.column != (pivot + shift):
                        return False

        return True



    def insert_grid_columns(self, mode):
        """ Deals with requests to insert a column. 

        NOTE: Call clear_all_selected_cells() before messing with
        the grid layout in InsertColumns.

        """

        pivot = self.marked_columns()[0]
        numColumnDialog = NumRowColumnDialog("columns")
        if numColumnDialog.exec_():
            numColumns = numColumnDialog.num
            insertColCommand = InsertColumns(self, numColumns, pivot, mode)
            self._undoStack.beginMacro("insert columns")
            self.clear_all_selected_cells()
            self._undoStack.push(insertColCommand)
            self._undoStack.endMacro()



    def can_delete_grid_columns(self):
        """ Checks if the selected columns can be deleted.

        The selected columns can only be deleted if the current
        layout allows it (we can't delete only parts of multi
        stitch repeats.

        """

        if not self._selectedCells:
            return

        orderedByColumn = \
            order_selection_by_columns(self._selectedCells.values())

        colIDs = list(orderedByColumn.keys())
        colIDs.sort()

        columnChunks = []
        previousCol = colIDs[0]
        chunk = orderedByColumn[previousCol]
        for column in colIDs[1:]:
            if column - previousCol == 1:
                chunk += orderedByColumn[column]
                previousCol = column
            else:
                columnChunks.append(chunk)
                chunk = orderedByColumn[column]
                previousCol = column
        columnChunks.append(chunk)
        
        # check if selection is rectangular 
        for chunk in columnChunks:

            (status, (colDim, rowDim)) = \
                is_active_selection_rectangular(chunk)

            # check if we have complete columns
            deadColumns = get_marked_columns(chunk, self._numRows)

            if not status or not deadColumns:
                return False

        return True



    def delete_marked_columns(self):
        """ Delete all currently marked columns. 

        NOTE: Call clear_all_selected_cells() before messing with
        the grid layout in DeleteColumns.

        """

        deadColumns = self.marked_columns() 
        deleteColumnsCommand = DeleteColumns(self, deadColumns)
        self._undoStack.beginMacro("delete columns")
        self.clear_all_selected_cells()
        self._undoStack.push(deleteColumnsCommand)
        self._undoStack.endMacro()



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
            item = self.create_pattern_grid_item(location, column, rowID, 1, 1,
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
            item = self.create_pattern_grid_item(location, columnID, row, 1, 1,
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
        self.repeatLegend.clear()
        self.canvasTextBoxes.clear()
        self._selectedCells = {}                                          
        self._undoStack.clear()
        self._copySelection = {}



    def create_new_canvas(self, numRows = 10, numColumns = 10):
        """ Create a complete new and blank canvas. """

        # reset the number of columns/rows to 10
        # we probably should add a dialog here
        self._numRows    = numRows
        self._numColumns = numColumns
        
        self._clear_canvas()
        self._textLabels = []
        self.set_up_main_grid()
        self.finalize_grid_change()



    @wait_cursor
    def load_previous_pattern(self, knittingSymbols, patternGridItemInfo,
                              legendItemInfo, patternRepeats, 
                              repeatLegends, rowRepeats, textItems):
        """ Clear curent canvas and establishes a new canvas
        based on the passed canvas items. Returns True on success
        and False otherwise.
        
        NOTE: We have to be able to deal with bogus data (from a
        corrupted file perhaps).
        
        NOTE1: No checking is done for rowRepeats since it is not a dictionary
        but a list of tuples so there won't be a key error.

        NOTE2: In the tests below do NOT replace "X == NONE" with "not X" since
        X can be legally [], for example.
        
        """

        allPatternGridItems = load_pattern_grid_items(patternGridItemInfo,
                                                      knittingSymbols,
                                                      self._unitCellDim.width(),
                                                      self._unitCellDim.height())
        if allPatternGridItems == None:
            return False

        allLegendItems = load_legend_items(legendItemInfo)
        if allLegendItems == None:
            return False

        allRepeatBoxes = load_patternRepeat_items(patternRepeats)
        if allRepeatBoxes == None:
            return False

        allRepeatBoxLegends = load_patternRepeatLegend_items(repeatLegends)
        if allRepeatBoxLegends == None:
            return False

        allTextItems = load_text_items(textItems)
        if allTextItems == None:
            return False

        # now that we have all canvas items, let's put them back in place
        self._clear_canvas()

        (self._numRows, self._numColumns) = \
            extract_num_rows_columns(allPatternGridItems)

        for entry in allPatternGridItems:
            item = self.create_pattern_grid_item(*entry)
            self.addItem(item)

        for entry in allLegendItems:
            arrange_label_item(self.gridLegend, *entry)

        for (repeatID, entry) in allRepeatBoxes.items():

            # also retrieve the proper legend
            if repeatID in allRepeatBoxLegends:
                self.add_patternRepeatItem(*entry, legendInfo = \
                                                allRepeatBoxLegends[repeatID])
            else:
                self.add_patternRepeatItem(*entry, 
                                            legendInfo = None)
            
        for rowRepeat in rowRepeats:
            self.rowRepeatTracker.add_repeat(*rowRepeat)

        for textItem in allTextItems:
            self.add_text_item(*textItem)

        # need to clear our caches, otherwise we'll try 
        # to remove non-existing items
        self._textLabels = []
        self.finalize_grid_change()
        self.change_grid_cell_dimensions()
        self.clear_undo_stack()

        return True



    def add_patternRepeatItem(self, itemLineInfo, itemLineWidth, itemPosition,
                              itemColor, legendInfo):
        """ Recreates a pattern repeat item and its legend based on 
        itemInfo and legendInfo. """

        # create the legend entry
        legendItem = RepeatLegendItem(itemColor)

        if legendInfo:
            (legendIsVisible, legendItemPos, legendTextPos, legendText) = legendInfo
        else:
            legendText = QString("pattern repeat")
            yCoord = self._get_legend_y_coordinate_for_placement()
            legendItemPos = QPointF(0, yCoord + legendItem.height + 30)
            legendTextPos = QPointF(legendItem.width + 30, 
                                    yCoord + legendItem.height + 20)
            legendIsVisible = False
        
        # now that we know the text and positions create the text
        # item and move it in place
        legendTextItem = PatternLegendText(legendText)
        legendItem.setPos(legendItemPos)
        legendTextItem.setPos(legendTextPos)

        if not legendIsVisible:
            legendItem.hide()
            legendTextItem.hide()

        self.addItem(legendItem)
        self.addItem(legendTextItem)

        # create the actual pattern repeat
        repeatItem = PatternRepeatItem(itemLineInfo, itemLineWidth, itemColor,
                                       legendIsVisible)
        repeatItem.setPos(itemPosition)
        self.addItem(repeatItem)

        # connect repeat box and legend
        self.repeatLegend[repeatItem.itemID] = \
            (1, legendItem, legendTextItem)



    def toggle_rowLabel_visibility(self, status):
        """ Per request from main window toggle
        the visibility of the row labels.
        
        """

        for item in self.items():
            if isinstance(item, PatternLabelItem):
                if item.isRowLabel:
                    if status:
                        item.show()
                    else:
                        item.hide()



    def toggle_columnLabel_visibility(self, status):
        """ Per request from main window toggle
        the visibility of the column labels.
        
        """

        for item in self.items():
            if isinstance(item, PatternLabelItem):
                if not item.isRowLabel:
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
            for item in self.repeatLegend.values():
                legendItem_symbol(item).show()
                legendItem_text(item).show()
        else:
            for item in self.gridLegend.values():
                legendItem_symbol(item).hide()
                legendItem_text(item).hide()
            for item in self.repeatLegend.values():
                legendItem_symbol(item).hide()
                legendItem_text(item).hide()



    def legend_font_changed(self):
        """ This slot is called when the label font has
        been changed.
        
        """
        
        legendFont = self.settings.legendFont.value
        for item in self.gridLegend.values(): 
            legendItem_text(item).setFont(legendFont)
            legendItem_text(item).adjust_size()
        for item in self.repeatLegend.values():
            legendItem_text(item).setFont(legendFont)
            legendItem_text(item).adjust_size()
        for item in self.canvasTextBoxes.values():
            item.setFont(legendFont)
            item.adjust_size()



    def toggle_pattern_grid_visibility(self, status):
        """ Per request from main window toggle the pattern grid
        visibility on or off.
        
        """

        for item in self.items():
            if isinstance(item, PatternGridItem) \
            or isinstance(item, PatternLabelItem) \
            or isinstance(item, PatternHighlightItem) \
            or isinstance(item, PatternRepeatItem):
                if status:
                    item.show()
                else:
                    item.hide()



    def add_text_item(self, itemPos = None,
                      itemText = "Star Cruiser Crash Crash."):
        """ Adds a text item to the canvas. 

        NOTE: The main reason for keeping track of text boxes in
        self.canvasTextBoxes is that it allows faster access when
        changing, e.g., the font size and when saving. Since there
        probably aren't that many the memory cost is probably small.
        
        """

        textItem = PatternTextItem(itemText)
        if not itemPos:
            yMax = self._get_legend_y_coordinate_for_placement()
            itemPos = QPointF(0, yMax + self._unitCellDim.height() + 10)
        textItem.setPos(itemPos)
        textItem.setFont(self.settings.legendFont.value)
        self.addItem(textItem)
        self.canvasTextBoxes[textItem] = textItem



    def delete_text_item(self, deadItem):
        """ Removes a text item to the canvas. """

        self.removeItem(deadItem)
        del self.canvasTextBoxes[deadItem]
        del deadItem



############################################################################
#
# Helper Functions
#
############################################################################
def extract_patternItems(allItems, patternType):
    """ From a list of QGraphicsItems extracts and returns
    all PatternGridItems.

    """

    patternItems = []
    for item in allItems:
        if isinstance(item, patternType):
            patternItems.append(item)

    return patternItems


