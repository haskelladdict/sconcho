# -*- coding: utf-8 -*-
######################################################################## #
# (c) 2009-2013 Markus Dittrich
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


import logging
from platform import system
from functools import partial

from PyQt4.QtCore import (QLineF,
                          QPointF,
                          QRectF,
                          QSizeF,
                          Qt,
                          SIGNAL,
                          QT_VERSION)

from PyQt4.QtGui import (QAction,
                         QApplication,
                         QBrush,
                         QColor,
                         QCursor,
                         QFontMetrics,
                         QGraphicsItem,
                         QGraphicsItemGroup,
                         QGraphicsLineItem,
                         QGraphicsObject,
                         QGraphicsRectItem,
                         QGraphicsScene,
                         QGraphicsTextItem,
                         QIcon,
                         QMenu,
                         QMessageBox,
                         QPen,
                         QPainterPath,
                         QUndoStack)

from PyQt4.QtSvg import (QGraphicsSvgItem)

from sconcho.util.canvas import *
from sconcho.util.misc import wait_cursor
from sconcho.gui.pattern_repeat_dialog import PatternRepeatDialog
from sconcho.gui.row_repeat_number_dialog import RowRepeatNumDialog
from sconcho.gui.num_row_column_dialog import NumRowColumnDialog
from sconcho.gui.undo_framework import *
from sconcho.gui.pattern_canvas_objects import *
import sconcho.util.messages as msg

# module lever logger:
logger = logging.getLogger(__name__)


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

        # are we currently visible?
        self.isVisible = True

        self.selectionMode = 0

        # should row/column labels be updated?
        # NOTE: We initialize to True, then build the main grid
        # and then update the properties with the default settings
        self.updateRowLabels = True
        self.rowLabels = {}
        self.updateColumnLabels = True
        self.columnLabels = {}

        self.selectionMode = SELECTION_MODE

        self.hiddenCellsByRow = {}
        self.alignRowLabelsToVisibleCells = \
                self.settings.alignRowLabelsToVisibleCells.value

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

        self.gridLegend = {}
        self.repeatLegend = {}
        self.canvasTextBoxes = {}
        self.patternRepeats = set()

        self.set_up_main_grid()
        self.set_up_labels()

        self.set_up_highlighted_rows()

        # NOTE: This is a hack to force Qt to leave a margin on
        # the left/upper edges. There should be a better way short
        # of managing my own sceneRect which is tricky
        dummy = QGraphicsRectItem(-100,-100,1,1)
        self.addItem(dummy)
        dummy.setVisible(False)



    @property
    def cell_height(self):
        """ return the unit cell height """
        return self._unitCellDim.height()


    @property
    def cell_width(self):
        """ return the unit cell width """
        return self._unitCellDim.width()



    def set_up_main_grid(self):
        """ This function draws the main grid.

        NOTE: Since the grid is drawn via rows
        we need to update the column labels by
        hand (this would otherwise be done by
        _create_column)

        """

        for row in range(0, self._numRows):
            self._create_row(row)

        # create the corresponding column entry
        for colID in range(0, self._numColumns):
            labelItem = PatternLabelItem("    ", False,
                                         not self.updateColumnLabels)
            labelItem.setToolTip("Shift-Click to select whole column")
            self.addItem(labelItem)
            self.columnLabels[colID] = labelItem

        # finally we need to make sure the labels have the proper
        # visibility;
        # NOTE: We need to create the labels first before changing
        #       editability, otherwise they will never be created
        #       if the default edit setting is true
        self.set_up_labels()
        if self.settings.rowLabelsEditable.value == 1:
            self.toggle_row_label_editing(True)
        if self.settings.columnLabelsEditable.value == 1:
            self.toggle_column_label_editing(True)



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

                origin_x = graphicsItem.column * self.cell_width
                origin_y = graphicsItem.row * self.cell_height
                unitWidth = graphicsItem.width
                element = PatternHighlightItem(origin_x, origin_y,
                                               self.cell_width * unitWidth,
                                               self.cell_height,
                                               QColor(color),
                                               opacity)
                element.setZValue(1)
                if visibility == 0:
                    element.hide()

                if graphicsItem.isHidden:
                    element.setOpacity(HIDE_OPACITY)
                self.addItem(element)



    def set_up_labels(self):
        """ Add labels to the main grid. """

        labelFont = self.settings.labelFont.value
        fm = QFontMetrics(labelFont)

        self._set_up_row_labels(labelFont, fm)
        self._set_up_column_labels(labelFont, fm)

        # hide row/column labels again if they are turned off
        # FIXME: This seems a little clunky - we need it
        # only because of the row repeats
        if not self.settings.showRowLabels.value:
            self.toggle_rowLabel_visibility(False)

        if not self.settings.showColumnLabels.value:
            self.toggle_columnLabel_visibility(False)



    def _set_up_row_labels(self, labelFont, fontMetric):
        """ Set up row labels. """

        rightMostColumns = []
        leftMostColumns = []
        if self.alignRowLabelsToVisibleCells:
            for row in range(0, self._numRows):
                columnIDs = set(range(0, self._numColumns))
                if row in self.hiddenCellsByRow:
                    columnIDs = \
                            columnIDs.difference(self.hiddenCellsByRow[row])
                if len(columnIDs) == 0:
                    rightMostColumns.append(-1)
                    leftMostColumns.append(-1)
                else:
                    rightMostColumns.append(max(columnIDs))
                    leftMostColumns.append(min(columnIDs))
        else:
            rightMostColumns = [self._numColumns-1]*self._numRows
            leftMostColumns = [0]*self._numRows

        # we use lamda function so we can control positioning
        # based on the actual labeltext
        rightXPosNew = lambda x, y: self.cell_width * (rightMostColumns[y]+1)
        leftXPosNew = lambda x, y: - (0.5 - leftMostColumns[y]) * \
                self.cell_width - fontMetric.width(x)

        evenRowLabelLocation = self.settings.evenRowLabelLocation.value
        if evenRowLabelLocation == "LEFT_OF":
            evenXPos = leftXPosNew
        else:
            evenXPos = rightXPosNew

        oddRowLabelLocation = self.settings.oddRowLabelLocation.value
        if oddRowLabelLocation == "LEFT_OF":
            oddXPos = leftXPosNew
        else:
            oddXPos = rightXPosNew

        if self.updateRowLabels:
            rowLabelList = self.rowLabelTracker.get_labels()
            rowLabelList.reverse()
            for (row, rowLabels) in enumerate(rowLabelList):
                item = self.rowLabels[row]
                
                if not rowLabels:
                    labelText = ""
                else:    
                    labelText = str(rowLabels[0])
                    for label in rowLabels[1:]:
                        labelText += ", " + str(label)

                    yPos = self.cell_height * row
                    if rowLabels[0] % 2 == 0:
                        item.setPos(evenXPos(labelText, row), yPos)
                    else:
                        item.setPos(oddXPos(labelText, row), yPos)

                item.setPlainText(labelText)
                item.setFont(labelFont)
        else:
            for (row, item) in self.rowLabels.items():
                yPos = self.cell_height * row
                labelText = item.toPlainText()
                item.setPos(evenXPos(labelText, row), yPos)
                item.setFont(labelFont)
                item.update()   # OSX hack to force redrawing



    def _set_up_column_labels(self, labelFont, fontMetric):
        """ Set up column labels. """

        yPos = self.cell_height * self._numRows
        columnLabelList = self.columnLabelTracker.get_labels()
        columnLabelList.reverse()

        if self.updateColumnLabels:
            for (col, colLabel) in enumerate(columnLabelList):
                if not colLabel:
                    labelText = ""
                else:
                    labelText = str(colLabel)

                textWidth = fontMetric.width(labelText)
                item = self.columnLabels[col]
                item.setPlainText(labelText)
                xPos = self.cell_width * col + \
                    (self.cell_width * 0.6 - textWidth)
                item.setPos(xPos, yPos)
                item.setFont(labelFont)
        else:
            for (col, item) in self.columnLabels.items():
                labelText = item.toPlainText()
                textWidth = fontMetric.width(labelText)
                xPos = self.cell_width * col + \
                    (self.cell_width * 0.6 - textWidth)
                item.setPos(xPos, yPos)
                item.setFont(labelFont)
                item.update()   # OSX hack to force redrawing


    def finalize_grid_change(self):
        """ This function is a wrapper encapsulating all changes
        to elements on the canvas that need to be done after some
        change to the grid (cell size, adding of rows/columns, etc.)

        """

        self.set_up_labels()
        self.set_up_highlighted_rows()

        # NOTE: This is a windows hack, without it the view
        # doesn't reset, no scrollbars appear and the canvas
        # is partially hidden
        # WINDOWS
        if system() == 'Windows':
            self.sceneRect()

        self.invalidate()



    def select_mode(self, mode):
        """ Set the selection mode to mode """

        self.selectionMode = mode



    def set_active_symbol(self, activeKnittingSymbol):
        """ This function receives the currently active symbol
        and stores it so we know what to paint selected cells
        with. In order to have consistent undo/redo bahaviour
        this has to be fully reversible.

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



    def add_pattern_repeat_to_legend(self, patternRepeatItem):
        """ Adds a newly created PatternRepeatItem to the legend
        database and updates the legend if needed.
        
        """

        legendID = patternRepeatItem.itemID
        if legendID in self.gridLegend:
            entry = self.gridLegend[legendID]
            new_entry = change_count(entry, 1)
            self.gridLegend[legendID] = new_entry
        else:
            (item, textItem) = \
                self._add_pattern_repeat_legend_item(patternRepeatItem, 
                                                     legendID)
            self.gridLegend[legendID] = [1, item, textItem, True]



    def add_knitting_symbol_to_legend(self, item):
        """ Adds a newly created PatternGridItem to the legend database
        and updates the legend itself if needed.

        """

        legendID = generate_legend_id(item.symbol, item.color)
        if legendID in self.gridLegend:
            entry = self.gridLegend[legendID]
            new_entry = change_count(entry, 1)
            self.gridLegend[legendID] = new_entry
        else:
            (item, textItem) = \
                self._add_knitting_symbol_legend_item(item.symbol,
                                                      item.color,
                                                      legendID)
            self.gridLegend[legendID] = [1, item, textItem, True]



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
                                 self.cell_width,
                                 graphicsItem.row * \
                                 self.cell_height)
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
        canvasYmax = (self._numRows + 1) * self.cell_height
        yMax = max(legendYmax, canvasYmax)
        return yMax



    def _add_pattern_repeat_legend_item(self, pathItem, legendID):
        """ This adds a new legend entry for a patter repeat
        
        consisting of a RepeatLegendItem and a textual description. 
        This function also attemps to be sort of smart about where to 
        put the item.

        """

        yMax = self._get_legend_y_coordinate_for_placement()

        # add the symbol part of the legend
        itemLocation = QPointF(0, yMax + self.cell_height + 20)
        item = RepeatLegendItem(pathItem.color)
        item.setPos(itemLocation)
        self.addItem(item)

        # add the description part of the legend
        textLocation = QPointF(item.width + 30,
                               yMax + self.cell_height + 10)
        textItem = PatternLegendText("pattern repeat", legendID)
        textItem.setPos(textLocation)
        textItem.setFont(self.settings.legendFont.value)
        self.addItem(textItem)

        return (item, textItem)



    def _add_knitting_symbol_legend_item(self, symbol, color, legendID):
        """ This adds a new legend entry for a knitting symbol 
        
        consisting of a PatternLegendItem and a textual description. 
        This function also attemps to be sort of smart about where to 
        put the item.

        """

        yMax = self._get_legend_y_coordinate_for_placement()

        # add the symbol part of the legend
        width  = int(symbol["width"])
        height = 1
        itemLocation = QPointF(0, yMax + self.cell_height + 10)
        item = PatternLegendItem(self._unitCellDim, width, height, symbol,
                                 legendID, color, 1)
        item.setPos(itemLocation)
        self.addItem(item)

        # add the description part of the legend
        textLocation = QPointF((width+1) * self.cell_width,
                                yMax + self.cell_height + 10)
        textItem = PatternLegendText(symbol["description"], legendID)
        textItem.setPos(textLocation)
        textItem.setFont(self.settings.legendFont.value)
        self.addItem(textItem)

        return (item, textItem)



    def remove_from_legend(self, item, legendID):
        """ Removes a PatternGridItem from the legend database
        and updates the legend itself if needed.

        """

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

        self.emit(SIGNAL("canvas_dimensions_changed"))
        moveCommand = MoveCanvasItem(canvasItem, oldPosition, newPosition)
        self._undoStack.push(moveCommand)



    def create_pattern_grid_item(self, origin, col, row, width, height,
                                 knittingSymbol, color, isHidden = False):
        """ Creates a new PatternGridItem of the specified dimension
        at the given location.

        """

        item = PatternGridItem(self._unitCellDim, col, row, width, height,
                               knittingSymbol, color)
        item.setPos(origin)

        if isHidden:
            item.hide_cell()
            add_to_hidden_cells_tracker(self.hiddenCellsByRow, item)

        self.connect(item, SIGNAL("cell_selected"), self.grid_cell_activated)
        self.connect(item, SIGNAL("cell_unselected"),
                     self.grid_cell_inactivated)

        self.connect(item, SIGNAL("cell_hidden"), self.hide_cell_event)
        self.connect(item, SIGNAL("cell_visible"), self.unhide_cell_event)

        return item



    def hide_cell_event(self, items):
        """ This function is a wrapper calling the undo framwork
        to hide the collection of pattern grid cells.

        """

        hideCommand = HideCells(self, items)

        self._undoStack.beginMacro("hide cells")
        self.clear_all_selected_cells()
        self._undoStack.push(hideCommand)
        self._undoStack.endMacro()



    def unhide_cell_event(self, items):
        """ This function is a wrapper calling the undo framwork
        to unhide the collection of pattern grid cells.

        """

        unhideCommand = UnhideCells(self, items)

        self._undoStack.beginMacro("unhide cells")
        self.clear_all_selected_cells()
        self._undoStack.push(unhideCommand)
        self._undoStack.endMacro()



    def addItem(self, item):
        """ This overload of addItem makes sure that we perform
        QGraphicsItem specific task such as updating the legend for
        svg items.

        """

        if isinstance(item, PatternGridItem):
            self.add_knitting_symbol_to_legend(item)
        elif isinstance(item, PatternRepeatItem):
            self.add_pattern_repeat_to_legend(item)

        super(PatternCanvas,self).addItem(item)



    def removeItem(self, item):
        """ This overload of removeItem makes sure that we perform
        QGraphicsItem specific task such as updating the legend for svg
        items.

        """

        if isinstance(item, PatternGridItem):
            legendID = generate_legend_id(item.symbol, item.color)
            self.remove_from_legend(item, legendID)
        elif isinstance(item, PatternRepeatItem):
            legendID = item.itemID
            self.remove_from_legend(item, legendID)

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
                                              self.cell_width,
                                              self.cell_height)

        if column >= 0 and column <= self._numColumns:
            columnString = self._numColumns - column
        else:
            columnString = "NA"
        self.emit(SIGNAL("col_count_changed"), columnString)

        rowLabelOffset = self.settings.rowLabelStart.value - 1
        if row >= 0 and row <= self._numRows:
            rowString = self._numRows - row + rowLabelOffset
        else:
            rowString = "NA"
        self.emit(SIGNAL("row_count_changed"), rowString)

        return QGraphicsScene.mouseMoveEvent(self, event)



    def mousePressEvent(self, event):
        """ Handle mouse press events directly on the canvas. """

        (col, row) = convert_pos_to_col_row(event.scenePos(),
                                            self.cell_width,
                                            self.cell_height)

        shiftPressed = event.modifiers() & Qt.ShiftModifier
        ctrlPressed = event.modifiers() & Qt.ControlModifier

        if (event.button() == Qt.RightButton) and \
            not (shiftPressed or ctrlPressed):
            self.handle_right_click_on_canvas(event, col, row)

            # don't propagate this event
            return

        elif (event.button() == Qt.LeftButton) and shiftPressed:

            if is_click_on_labels(col, row, self._numColumns,
                                  self._numRows):
                self.select_column_row_cells(col, row)

                # don't propagate this event
                return

        # tell our main window that something changed
        self.emit(SIGNAL("scene_changed"))

        return QGraphicsScene.mousePressEvent(self, event)



    def select_region(self, region):
        """ This function selects items based on a whole region.

        The region is typically a QPolygonF coming from our
        view via a rubberBand selection.

        """

        items = []
        for item in self.items(region):
            if isinstance(item, PatternGridItem):
                items.append(item)

        self.select_cells(items)



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

        self.select_cells(selectedItems)



    def select_cells(self, items):
        """ This function selects all cells in the items list. """

        if self.selectionMode == SELECTION_MODE:
            selection = set()
            unselection = set()
            for item in items:
                itemID = get_item_id(item.column, item.row)
                entry = PatternCanvasEntry(item.column, item.row, item.width,
                                            item.color, item.symbol)
                if itemID in self._selectedCells:
                    unselection.add(entry)
                elif item.isHidden:
                    continue
                else:
                    selection.add(entry)

            self._paint_cells(selection, unselection)

        elif self.selectionMode == HIDE_MODE:
            self.hide_cell_event(items)

        elif self.selectionMode == UNHIDE_MODE:
            self.unhide_cell_event(items)



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


    
    def hide_legend_item_menu(self, screenPos, labelItem):
        """ Menu for hiding existing label items.

        This menu appears when the user right clicks on a 
        PatternLegendText object.

        NOTE: labelItem can either be a PatternLegendItem or
        a PatternLegendItem.

        """

        hideLegendItemMenu = QMenu()
        hideAction = hideLegendItemMenu.addAction("hide legend entry")
        self.connect(hideAction, SIGNAL("triggered()"),
                     partial(self.hide_legend_text_item, labelItem));
        hideLegendItemMenu.exec_(screenPos)
           


    def hide_legend_text_item(self, clickedLegendItem):
        """ Hides the selected legendTextItem. """

        itemID = clickedLegendItem.itemID
        hideLegendCommand = HideLegendItem(self.gridLegend[itemID]) 
        self._undoStack.push(hideLegendCommand)



    def handle_right_click_on_canvas(self, event, col, row):
        """ Handles a right click on the canvas grid by

        Dispatches the proper menu display function.

        """

        clickInGrid = is_click_in_grid(col, row, self._numColumns,
                                       self._numRows)

        # check if the click was on a text label
        items = self.items(event.scenePos())
        labelTextItems = \
            list(filter(lambda x: isinstance(x, PatternTextItem), items))
        legendItems = \
            list(filter(lambda x: isinstance(x, PatternLegendItem), items))
        legendTextItems = \
            list(filter(lambda x: isinstance(x, PatternLegendText), items))


        if labelTextItems:
            self.show_delete_text_item_menu(event.screenPos(), 
                                            labelTextItems[0])
        elif legendItems:
            self.hide_legend_item_menu(event.screenPos(), 
                                       legendItems[0])
        elif legendTextItems:
            self.hide_legend_item_menu(event.screenPos(), 
                                       legendTextItems[0])
        else: 
            self.show_grid_menu(event, col, row)



    def show_grid_menu(self, event, col, row):
        """ Shows the grid action menu.

        If the click occured outside the pattern grid we show
        the menu only if there is a pattern repeat item
        under the cursor. In this case all the other items are
        disabled.

        """

        scenePos = event.scenePos()
        patternRepeats = extract_patternItems([self.itemAt(scenePos)],
                                              PatternRepeatItem)

        gridMenu = QMenu()

        # grab color actoin
        grabColorAction = gridMenu.addAction("&Grab Color and Insert Into "
                                             "Color Selector")
        self.connect(grabColorAction, SIGNAL("triggered()"),
                     partial(self.grab_color_from_cell_add_to_widget,
                             scenePos))

        # select color action
        selectColorAction = gridMenu.addAction("Select All Grid Cells "
                                               "With Same Co&lor As Cell")
        self.connect(selectColorAction, SIGNAL("triggered()"),
                     partial(self.select_all_cells_with_same_color,
                             scenePos))

        # select symbol action
        symbolAction = gridMenu.addAction("Select All Grid Cells With "
                                          "Same &Symbol As Cell")
        self.connect(symbolAction, SIGNAL("triggered()"),
                     partial(self.select_all_cells_with_same_symbol,
                             scenePos))

        gridMenu.addSeparator()
        self.insert_pattern_repeat_menu(gridMenu, patternRepeats)
        self.insert_delete_columns_menu(gridMenu) 
        self.insert_delete_rows_menu(gridMenu) 
        self.insert_row_repeat_menu(gridMenu) 
        gridMenu.addSeparator()

        # copy action
        copyIcon = QIcon(":/icons/copy.png")
        copyAction = gridMenu.addAction(copyIcon, "&Copy")
        self.connect(copyAction, SIGNAL("triggered()"),
                     self.copy_selection)

        # paste action
        pasteIcon = QIcon(":/icons/paste.png")
        pasteAction = gridMenu.addAction(pasteIcon, "&Paste")
        self.connect(pasteAction, SIGNAL("triggered()"),
                     partial(self.paste_selection, col, row))

        gridMenu.exec_(event.screenPos())



    def insert_pattern_repeat_menu(self, gridMenu, patternRepeats): 
        """ Show menu for adding/deleting pattern repeats. """

        repeatIcon = QIcon(":/icons/pattern_repeat.png")
        patternRepeatMenu = gridMenu.addMenu(repeatIcon, "Pattern Repeats")

        # add repeat box action
        addRepeatAction = \
                patternRepeatMenu.addAction("&Create Pattern Repeat")
        self.connect(addRepeatAction, SIGNAL("triggered()"),
                     self.add_pattern_repeat)
        if not can_outline_selection(self._selectedCells.values()):
            addRepeatAction.setEnabled(False)

        # edit repeat box action
        editRepeatAction = \
                patternRepeatMenu.addAction("&Edit Pattern Repeat")
        if patternRepeats:
            self.connect(editRepeatAction, SIGNAL("triggered()"),
                         partial(self.edit_pattern_repeat,
                                 patternRepeats[0]))
        else:
            editRepeatAction.setEnabled(False)

        # delete repeat box action
        deleteRepeatAction = \
                patternRepeatMenu.addAction("&Delete Pattern Repeat")
        if patternRepeats:
            self.connect(deleteRepeatAction, SIGNAL("triggered()"),
                         partial(self.delete_pattern_repeat,
                                 patternRepeats[0]))
        else:
            deleteRepeatAction.setEnabled(False)

 

    def insert_delete_columns_menu(self, gridMenu): 
        """ Show menu for deleting columns. """

        rowColMenu = gridMenu.addMenu("Add/Delete Co&lumns")

        deleteIcon = QIcon(":/icons/delete_column.png")
        deleteColsAction = rowColMenu.addAction(deleteIcon,
                "delete selected &columns")
        self.connect(deleteColsAction, SIGNAL("triggered()"),
                     self.delete_marked_columns)

        addIcon = QIcon(":/icons/insert_column.png")
        addColRightAction = rowColMenu.addAction(addIcon, "insert column")
        self.connect(addColRightAction, SIGNAL("triggered()"),
                     self.insert_grid_columns)
        rowColMenu.addSeparator()



    def insert_delete_rows_menu(self, gridMenu): 
        """ Show menu for deleting rows. """

        rowColMenu = gridMenu.addMenu("Add/Delete &Rows")

        deleteIcon = QIcon(":/icons/delete_row.png")
        deleteRowsAction = rowColMenu.addAction(deleteIcon,
                "delete selected &rows")
        self.connect(deleteRowsAction, SIGNAL("triggered()"),
                     self.delete_marked_rows)

        addIcon = QIcon(":/icons/insert_row.png")
        addRowAction = rowColMenu.addAction(addIcon, "&insert rows")
        self.connect(addRowAction, SIGNAL("triggered()"),
                     self.insert_grid_rows)
        rowColMenu.addSeparator()


       
    def insert_row_repeat_menu(self, gridMenu): 
        """ Show menu for inserting and deleting row repeats. """

        repeatIcon = QIcon(":/icons/row_repeats.png")
        rowRepeatMenu = gridMenu.addMenu(repeatIcon, 
                "Add/Delete R&ow Repeats")

        # row repeat actions
        addRowRepeatAction = rowRepeatMenu.addAction("&add row repeat")
        self.connect(addRowRepeatAction, SIGNAL("triggered()"),
                     self.add_row_repeat)

        deleteRowRepeatAction = rowRepeatMenu.addAction("&delete row repeat")
        self.connect(deleteRowRepeatAction, SIGNAL("triggered()"),
                     self.delete_row_repeat)



    def apply_color_to_selection(self, color = None):
        """ This slot changes the background color of all selected cells
        to the currently active color.

        """

        # if noting is selected we are done but let the user now
        if not self._selectedCells:
            logger.error(msg.noSelectionText)
            QMessageBox.critical(None, msg.noSelectionTitle,
                                 msg.noSelectionText,
                                 QMessageBox.Close)
            return

        colorCommand = ColorSelectedCells(self, color)
        self._undoStack.push(colorCommand)
        self.clear_all_selected_cells()



    def add_pattern_repeat(self):
        """ Adds a pattern repeat around the current selection. """

        # if noting is selected we are done but let the user now
        if not self._selectedCells:
            logger.error(msg.noSelectionText)
            QMessageBox.critical(None, msg.noSelectionTitle,
                                 msg.noSelectionText,
                                 QMessageBox.Close)
            return

        # the below code computes what edges to draw.
        # It subdivides the whole pattern grid into 1x1
        # cells whose edges are described by edgeID as
        # [upper edge, left edge, right edge, bottom edget]
        # where each descriptor is of the form 'x1:y1:x2:y2'.
        # Then, all edges are collected. Edges that appear twice
        # are internal and are not drawn. Edges that appear once
        # are external and are drawn.
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

        lineTuples = []
        for (edgeID, switch) in edges.items():
            if switch:
                (col1, row1, col2, row2) = map(int, edgeID.split(":"))
                lineTuples.append(((col1, row1), (col2, row2)))

        vertices = sort_vertices(lineTuples)
        if not vertices:
            logger.error(msg.badPatternRepeatText)
            QMessageBox.critical(None, msg.badPatternRepeatTitle,
                                 msg.badPatternRepeatText,
                                 QMessageBox.Close)
            return

        points = []
        for vertex in vertices:
            points.append(QPointF(vertex[0]*self.cell_width,
                                  vertex[1]*self.cell_height))
        repeatPolygon = QPolygonF(points)
        repeatItem = PatternRepeatItem(repeatPolygon)

        patternRepeatCommand = AddPatternRepeat(self, repeatItem)
        self._undoStack.push(patternRepeatCommand)



    def delete_pattern_repeat(self, patternRepeat):
        """ Delete the selected pattern repeat. """

        patternRepeatCommand = DeletePatternRepeat(self, patternRepeat)
        self._undoStack.push(patternRepeatCommand)
        self.emit(SIGNAL("scene_changed"))



    def edit_pattern_repeat(self, patternRepeat):
        """ Edit the provided pattern repeat item. """

        patternRepeat.highlight()

        dialog = PatternRepeatDialog(patternRepeat.width,
                                     patternRepeat.color)
        status = dialog.exec_()
        if status > 0:
            oldColor = patternRepeat.color
            self._undoStack.beginMacro("edit pattern repeat")
            patternRepeatCommand = EditPatternRepeat(patternRepeat,
                                                     dialog.color,
                                                     dialog.width)
            self._undoStack.push(patternRepeatCommand)
            patternLegendCommand = \
                    EditPatternRepeatLegend(dialog.color,
                                            self.gridLegend,
                                            patternRepeat.itemID)
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
            logger.error(errorString)
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
                logger.error(errorString)
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



    def copy_selection(self):
        """ This slot copies the current selection if rectangular. """

        # if nothing is selected don't do anything
        if not self._selectedCells:
            return

        self._copySelection.clear()
        self._copySelection = self._selectedCells.copy()
        self.clear_all_selected_cells()



    def _patternCanvasEntries_in_rectangle(self, xPos, yPos, xDim, yDim):
        """ Returns the canvas items under the given rectangle
        as PatternCanvasEntries. """

        deadItems = self._get_pattern_grid_items_in_rectangle(xPos, yPos,
                                                              xDim, yDim)
        deadSelection = {}
        for item in deadItems:
            itemID = get_item_id(item.column, item.row)
            deadSelection[itemID] = PatternCanvasEntry(item.column,
                                                       item.row,
                                                       item.width,
                                                       item.color,
                                                       item.symbol,
                                                       item.isHidden)

        return deadSelection



    def _get_pattern_grid_items_in_rectangle(self, column, row, numCols,
                                             numRows):
        """ Given a (col, row) origin and the number of columns
        and rows returns all PatternGridItems under the selection.

        """

        upperLeftCorner  = convert_col_row_to_pos(column,
                                    row,
                                    self.cell_width,
                                    self.cell_height)

        lowerRightCorner = convert_col_row_to_pos(column + numCols - 1,
                                    row + numRows - 1,
                                    self.cell_width,
                                    self.cell_height)

        # we need to add a small fraction to witdh and height
        # in case of single row column selections (otherwise Qt
        # doesn recognize the selection as a rectangle)
        lowerRightCorner += QPointF(self.cell_width * 0.01,
                                    self.cell_height * 0.01)

        allItems = self.items(QRectF(upperLeftCorner, lowerRightCorner))
        patternGridItems = extract_patternItems(allItems, PatternGridItem)

        return patternGridItems



    def paste_selection(self, column = None, row = None):
        """ This slot pastes the current copy selection at column
        and row if possible given the target location and layout.

        Note: There are two ways for this function to be called,
        with and without column/row info. Pasting proceeds according
        to the following steps:

        1) If cells are selected on the canvas try to paste the
        selection into it. For this, the selection has to be
        multiples of the size of the copy selection (rectangular
        in particular) . Depending on the number of multiples sconcho
        will paste as many copies into the selection.

        2) If no cells are selected and the user pasted via a right
        mouse click (in this case we will receive column/row info)
        on the canvas, sconcho will paste a single copy
        of the selection on the canvas assuming it fits.

        3) Otherwise, we can't paste and let the user know.

        """

        # check first if we can paste at all
        if not self._copySelection:
            logger.error(msg.noCopySelectionText)
            QMessageBox.critical(None, msg.noCopySelectionTitle,
                                 msg.noCopySelectionText,
                                 QMessageBox.Close)
            return

        # case 1: copy and paste selection are both rectangular
        (status1, (pasteColDim, pasteRowDim)) = \
            is_selection_rectangular(self._selectedCells.values())
        (status2, (copyColDim, copyRowDim)) = \
            is_selection_rectangular(self._copySelection.values())
        (pasteUpperLHRow, pasteUpperLHColumn, dummy) = \
            get_upper_left_hand_corner(self._selectedCells.values())
        (copyUpperLHRow, copyUpperLHColumn, dummy) = \
            get_upper_left_hand_corner(self._copySelection.values())

        # we have a rectangular copy and paste selection
        # in this we always insert into the selection
        if status1 and status2:
            (n_col, r_col) = divmod(pasteColDim, copyColDim)
            (n_row, r_row) = divmod(pasteRowDim, copyRowDim)

            # only paste if selection is a multiple of what's on the
            # clipboard
            if r_col == 0 and r_row == 0:

                self._undoStack.beginMacro("paste selection")
                self.clear_all_selected_cells()
                for rowRepeat in range(0, n_row):

                    rowID = pasteUpperLHRow + (rowRepeat * copyRowDim)
                    for colRepeat in range(0, n_col):

                        colID = pasteUpperLHColumn + (colRepeat * copyColDim)
                        deadSelection = \
                            self._patternCanvasEntries_in_rectangle(colID,
                                    rowID, copyColDim, copyRowDim)

                        pasteCommand = PasteCells(self,
                                                  self._copySelection,
                                                  deadSelection, colID,
                                                  rowID, copyUpperLHColumn,
                                                  copyUpperLHRow)
                        self._undoStack.push(pasteCommand)
                self._undoStack.endMacro()

            else:
                logger.error(msg.noPasteGeometryText)
                QMessageBox.critical(None, msg.noPasteGeometryTitle,
                                    msg.noPasteGeometryText,
                                    QMessageBox.Close)
                return

        # if neither copy or paste selection is rectangular and we have
        # a paste selection we check if it fits and place it if possible
        elif (not status1 and not status2) and self._selectedCells:
            (minCopyCol, minCopyRow, minPasteCol, minPasteRow,
                    deadSelection) = match_selections(self._copySelection,
                                                      self._selectedCells)

            if not deadSelection:
                logger.error(msg.badPasteSelectionText)
                QMessageBox.critical(None, msg.noPasteGeometryTitle1,
                                    msg.noPasteGeometryText1,
                                    QMessageBox.Close)
                return

            else:
                self.clear_all_selected_cells()
                pasteCommand = PasteCells(self, self._copySelection,
                                        deadSelection, minPasteCol,
                                        minPasteRow, minCopyCol,
                                        minCopyRow)
                self._undoStack.push(pasteCommand)

        # user clicked directly on canvas
        elif (column != None and row != None):
            (minRow, minCol, deadSelection) = \
                    self._check_for_partial_overlaps(column, row)
            if not deadSelection:
                logger.error(msg.badPasteSelectionText)
                QMessageBox.critical(None, msg.badPasteSelectionTitle,
                                    msg.badPasteSelectionText,
                                    QMessageBox.Close)
                return

            else:
                self.clear_all_selected_cells()
                pasteCommand = PasteCells(self, self._copySelection,
                                        deadSelection, column, row,
                                        minCol, minRow)
                self._undoStack.push(pasteCommand)

        # without selection or user mouse clicking on canvas we can't
        # paste
        else:
            logger.error(msg.noPasteSelectionText)
            QMessageBox.critical(None, msg.noPasteSelectionTitle,
                                 msg.noPasteSelectionText,
                                 QMessageBox.Close)
            return



    def _check_for_partial_overlaps(self, columnId, rowId):
        """ This function checks if the current copy selection can
        be pasted at the requested location without leaving symbols
        partially covered.

        """

        invalid = (None, None, None)
        deadItems = set()

        (minRow, minCol, cellsByRow) = \
                get_upper_left_hand_corner(self._copySelection.values())
        for (row, rowItems) in cellsByRow.items():
            tempStorage = {}

            actRow = rowId + (row - minRow)
            # make sure we don't copy outside of canvas
            if (actRow >= self._numRows):
                return invalid

            for rowItem in rowItems:
                actColStart = columnId + (rowItem.column - minCol)

                for col in range(0, rowItem.width):
                    actColumn = actColStart + col

                    # make sure we don't copy outside of canvas
                    if (actColumn >= self._numColumns or actColumn < 0):
                        return invalid

                    canvasItem = self._item_at_row_col(actRow, actColumn)
                    deadItems.add(canvasItem)
                    itemID = id(canvasItem)
                    if itemID in tempStorage:
                        (width, count) = tempStorage[itemID]
                        tempStorage[itemID] = (width, count+1)
                    else:
                        tempStorage[itemID] = (canvasItem.width, 1)

            # check for item coverage
            for (width, coverage) in tempStorage.values():
                if coverage != width:
                    return invalid
            tempStorage.clear()

        # all good - assemble dead items now
        deadSelection = {}
        for item in deadItems:
            itemID = get_item_id(item.column, item.row)
            deadSelection[itemID] = PatternCanvasEntry(item.column,
                                                       item.row,
                                                       item.width,
                                                       item.color,
                                                       item.symbol,
                                                       item.isHidden)
        return (minRow, minCol, deadSelection)



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

        pos = convert_col_row_to_pos(column, row, self.cell_width,
                                     self.cell_height)

        # we really only expect one PatternItem of given type to be present;
        # however there may in principle be others (legend items etc)
        # so we have to pick it out
        allItems = self.items(pos)
        patternItems = extract_patternItems(allItems, patternType)
        if len(patternItems) > 1:
            errorString = "_item_at_row_col: expected <=1 item, found %d" %\
                          len(patternItems)
            logger.error(errorString)
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
        allItems = self.items((colStart + 0.25) * self.cell_width,
                              (rowStart + 0.25) * self.cell_height,
                              (colEnd - colStart + 0.25) * self.cell_width,
                              (rowEnd - rowStart + 0.25) * self.cell_height)

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
        completely marked columns or an empty list if there are any
        partially marked columns. An exception is the case of a single
        marked column with *one* jagged edge which is returned as a single
        column.

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

        markedRows = self.marked_rows()
        if (not markedRows) or (not self.can_delete_row_repeat()):
            logger.error(msg.cannotAddRowRepeatText)
            QMessageBox.critical(None, msg.cannotDeleteRowRepeatTitle,
                                 msg.cannotDeleteRowRepeatText,
                                 QMessageBox.Close)
            return

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

        markedRows = self.marked_rows()
        if (not markedRows) or (not self.can_add_row_repeat()):
            logger.error(msg.cannotAddRowRepeatText)
            QMessageBox.critical(None, msg.cannotAddRowRepeatTitle,
                                 msg.cannotAddRowRepeatText,
                                 QMessageBox.Close)
            return

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



    def insert_grid_rows(self):
        """ Deals with requests to insert a row.

        NOTE: Call clear_all_selected_cells() before messing with
        the grid layout in InsertRows.

        """

        # make sure that a single comple row is selected, otherwise
        # tell the user
        pivotRows = self.marked_rows()
        if len(pivotRows) != 1:
            logger.error(msg.selectSingleRowText)
            QMessageBox.critical(None, msg.selectSingleRowTitle,
                                 msg.selectSingleRowText,
                                 QMessageBox.Close)
            return

        rowPivot = pivotRows[0]
        numRowDialog = NumRowColumnDialog("rows")
        if numRowDialog.exec_():
            numRows = numRowDialog.num
            location = numRowDialog.location

            # figure out if any pattern repeats need to be moved
            patternRepeats = \
              repeats_to_be_shifted_after_insert_row(self.patternRepeats,
                                                     self.cell_height,
                                                     rowPivot, numRows)

            insertRowCommand = InsertRows(self, numRows, rowPivot, location)
            self._undoStack.beginMacro("insert rows")
            self.clear_all_selected_cells()
            self._undoStack.push(insertRowCommand)

            for (item, oldPos, newPos) in patternRepeats:
                moveCommand = MoveCanvasItem(item, oldPos, newPos)
                self._undoStack.push(moveCommand)

            self._undoStack.endMacro()



    def delete_marked_rows(self):
        """ Delete all currently marked rows.

        NOTE: Call clear_all_selected_cells() before messing with
        the grid layout in DeleteRows.

        """

        # make sure only complete rows are selected, otherwise
        # tell the user
        deadRows = self.marked_rows()
        if not deadRows:
            logger.error(msg.selectCompleteRowsText)
            QMessageBox.critical(None, msg.selectCompleteRowsTitle,
                                 msg.selectCompleteRowsText,
                                 QMessageBox.Close)
            return

        # figure out if any pattern repeats need to be moved
        patternRepeats = \
          repeats_to_be_shifted_after_delete_rows(self.patternRepeats,
                                                  self.cell_height,
                                                  deadRows)

        deleteRowsCommand = DeleteRows(self, deadRows)
        self._undoStack.beginMacro("delete marked rows")
        self.clear_all_selected_cells()
        self._undoStack.push(deleteRowsCommand)

        for (item, oldPos, newPos) in patternRepeats:
            moveCommand = MoveCanvasItem(item, oldPos, newPos)
            self._undoStack.push(moveCommand)

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
        if mode == "left of":
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



    def insert_grid_columns(self):
        """ Deals with requests to insert a column.

        NOTE: Call clear_all_selected_cells() before messing with
        the grid layout in InsertColumns.

        """

        # make sure the user selected only a single column
        pivotColumns = self.marked_columns()
        if len(pivotColumns) != 1:
            logger.error(msg.selectSingleColumnText)
            QMessageBox.critical(None, msg.selectSingleColumnTitle,
                                 msg.selectSingleColumnText,
                                 QMessageBox.Close)
            return


        pivot = pivotColumns[0]
        numColumnDialog = NumRowColumnDialog("columns")
        if numColumnDialog.exec_():
            numColumns = numColumnDialog.num
            location = numColumnDialog.location

            # make sure we can insert the column given the current
            # pattern geometry. If not, tell the user and
            # return
            if not self.can_insert_grid_columns(location):
                logger.error(msg.noColInsertLayoutText)
                QMessageBox.critical(None, msg.noColInsertLayoutTitle,
                                     msg.noColInsertLayoutText,
                                     QMessageBox.Close)
                return

            # figure out if any pattern repeats need to be moved
            patternRepeats = \
              repeats_to_be_shifted_after_insert_col(self.patternRepeats,
                                                     self.cell_width,
                                                     pivot, numColumns)

            insertColCommand = InsertColumns(self, numColumns, pivot,
                                             location)
            self._undoStack.beginMacro("insert columns")
            self.clear_all_selected_cells()
            self._undoStack.push(insertColCommand)

            for (item, oldPos, newPos) in patternRepeats:
                moveCommand = MoveCanvasItem(item, oldPos, newPos)
                self._undoStack.push(moveCommand)

            self._undoStack.endMacro()



    def can_delete_grid_columns(self, deadColumns):
        """ Checks if the selected columns can be deleted.

        The selected columns can only be deleted if the current
        layout allows it (we can't delete only parts of multi
        stitch repeats.

        """

        if not self._selectedCells:
            return

        selection = []
        allItems = extract_patternItems(self.items(), PatternGridItem)
        for item in allItems:
            if set(range(item.column, item.column + item.width)) \
                   & set(deadColumns):
                selection.append(PatternCanvasEntry(item.column,
                                                    item.row,
                                                    item.width,
                                                    item.color,
                                                    item.symbol))

        orderedByColumn = order_selection_by_columns(selection)
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
                is_selection_rectangular(chunk)

            if not status:
                return False

        return True



    def delete_marked_columns(self):
        """ Delete all currently marked columns.

        NOTE: Call clear_all_selected_cells() before messing with
        the grid layout in DeleteColumns.

        """

        # make sure only complete are selected, and we span
        # complete columns
        deadColumns = self.marked_columns()
        if not deadColumns or not self.can_delete_grid_columns(deadColumns):
            logger.error(msg.noColDeleteLayoutText)
            QMessageBox.critical(None, msg.noColDeleteLayoutTitle,
                                 msg.noColDeleteLayoutText,
                                 QMessageBox.Close)
            return


        patternRepeats = \
          repeats_to_be_shifted_after_delete_cols(self.patternRepeats,
                                                  self.cell_width,
                                                  deadColumns)

        deleteColumnsCommand = DeleteColumns(self, deadColumns)
        self._undoStack.beginMacro("delete columns")
        self.clear_all_selected_cells()
        self._undoStack.push(deleteColumnsCommand)

        for (item, oldPos, newPos) in patternRepeats:
            moveCommand = MoveCanvasItem(item, oldPos, newPos)
            self._undoStack.push(moveCommand)

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
            location = QPointF(column * self.cell_width,
                                rowID * self.cell_height)
            item = self.create_pattern_grid_item(location, column, rowID,
                                                 1, 1,
                                                 self._defaultSymbol,
                                                 self._defaultColor)
            self.addItem(item)

        # create the corresponding row entry
        labelItem = PatternLabelItem("    ", True, not self.updateRowLabels)
        labelItem.setToolTip("Shift-Click to select whole row")
        self.addItem(labelItem)
        self.rowLabels[rowID] = labelItem



    def _create_column(self, columnID):
        """ Creates a new column at columnID, nothing else. In particular
        this function does not attempt to make space for the column or
        anything else along these lines. This is a private and very
        stupid function.

        """

        for row in range(0, self._numRows):
            location = QPointF(columnID * self.cell_width,
                                row * self.cell_height)
            item = self.create_pattern_grid_item(location, columnID, row,
                                                 1, 1, self._defaultSymbol,
                                                 self._defaultColor)
            self.addItem(item)

        # create the corresponding column entry
        labelItem = PatternLabelItem("    ", False,
                                     not self.updateColumnLabels)
        labelItem.setToolTip("Shift-Click to select whole row")
        self.addItem(labelItem)
        self.columnLabels[columnID] = labelItem



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
        self.patternRepeats.clear()
        self.rowLabels.clear()
        self.columnLabels.clear()
        self._undoStack.clear()
        self._copySelection = {}
        self.hiddenCellsByRow = {}



    def create_new_canvas(self, numRows = 10, numColumns = 10):
        """ Create a complete new and blank canvas. """

        # reset the number of columns/rows to 10
        # we probably should add a dialog here
        self._numRows    = numRows
        self._numColumns = numColumns

        self._clear_canvas()
        self.set_up_main_grid()
        self.finalize_grid_change()



    @wait_cursor
    def load_previous_pattern(self, knittingSymbols, patternGridItemInfo,
                              legendItemInfo, patternRepeats,
                              repeatLegends, rowRepeats, textItems,
                              rowLabels, columnLabels):
        """ Clear curent canvas and establishes a new canvas
        based on the passed canvas items. Returns True on success
        and False otherwise.

        NOTE: We have to be able to deal with bogus data (from a
        corrupted file perhaps).

        NOTE1: No checking is done for rowRepeats since it is not a
        dictionary but a list of tuples so there won't be a key error.

        NOTE2: In the tests below do NOT replace "X == NONE" with "not X"
        since X can be legally [], for example.

        """

        allPatternGridItems = load_pattern_grid_items(patternGridItemInfo,
                                           knittingSymbols,
                                           self.cell_width,
                                           self.cell_height)
        if allPatternGridItems == None:
            return False

        allLegendItems = load_legend_items(legendItemInfo)
        if allLegendItems == None:
            return False

        allPatternRepeats = load_patternRepeat_items(patternRepeats)
        if allPatternRepeats == None:
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

        for (repeatID, entry) in allPatternRepeats.items():

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


        self.load_row_column_labels(rowLabels, columnLabels)

        # need to clear our caches, otherwise we'll try
        # to remove non-existing items
        self.finalize_grid_change()
        self.change_grid_cell_dimensions()
        self.clear_undo_stack()

        return True



    def add_patternRepeatItem(self, itemPolygonInfo, itemLineWidth,
                              itemPosition, itemColor, legendInfo):
        """ Recreates a pattern repeat item and its legend based on
        itemInfo and legendInfo. """

        # create the legend entry
        legendItem = RepeatLegendItem(itemColor)

        if legendInfo:
            (legendIsVisible, legendItemPos, legendTextPos, \
                    legendText) = legendInfo
        else:
            legendText = "pattern repeat"
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

        visible = 1
        if not legendIsVisible:
            legendItem.hide()
            legendTextItem.hide()
            visible = 0

        self.addItem(legendItem)
        self.addItem(legendTextItem)

        # create the actual pattern repeat
        repeatItem = PatternRepeatItem(itemPolygonInfo, itemLineWidth,
                                       itemColor, legendIsVisible)
        repeatItem.setPos(itemPosition)
        self.addItem(repeatItem)
        self.patternRepeats.add(repeatItem)

        # connect repeat box and legend
        self.repeatLegend[repeatItem.itemID] = \
            (visible, legendItem, legendTextItem)



    def load_row_column_labels(self, rowLabels, columnLabels):
        """ Establish the proper row and column labels after
        reading an spf file.

        """

        for rowID in range(0, self._numRows):

            if rowID in rowLabels:
                name = rowLabels[rowID]
            else:
                name = str(self._numRows - rowID)

            labelItem = PatternLabelItem(name, False,
                                         not self.updateRowLabels)
            labelItem.setToolTip("Shift-Click to select whole row")
            self.addItem(labelItem)
            self.rowLabels[rowID] = labelItem

        for colID in range(0, self._numColumns):

            if colID in columnLabels:
                name = columnLabels[colID]
            else:
                name = str(self._numColumns - colID)

            labelItem = PatternLabelItem(name, False,
                                         not self.updateColumnLabels)
            labelItem.setToolTip("Shift-Click to select whole column")
            self.addItem(labelItem)
            self.columnLabels[colID] = labelItem

        # finally we need to make sure the labels have the proper
        # visibility;
        # NOTE: We need to create the labels first before changing
        #       editability, otherwise they will never be created
        #       if the default edit setting is true
        if self.settings.rowLabelsEditable.value == 1:
            self.updateRowLabels = False
        if self.settings.columnLabelsEditable.value == 1:
            self.updateColumnLabels = False



    def toggle_row_label_visibility(self, status):
        """ Per request from main window toggle
        the visibility of the row labels.

        """

        labelItems = extract_patternItems(self.items(), PatternLabelItem)
        for item in labelItems:
            if item.is_rowLabel:
                if status:
                    item.show()
                else:
                    item.hide()



    def toggle_row_label_alignment(self, status):
        """ Per request from main window toggles the alignment
        of the row labels to the visible cells.

        """

        self.alignRowLabelsToVisibleCells = status
        self.set_up_labels()



    def toggle_column_label_visibility(self, status):
        """ Per request from main window toggle
        the visibility of the column labels.

        """

        labelItems = extract_patternItems(self.items(), PatternLabelItem)
        for item in labelItems:
            if not item.is_rowLabel:
                if status:
                    item.show()
                else:
                    item.hide()



    def toggle_row_label_editing(self, status):
        """ Per request from main window toggles the ability
        to edit the row labels.

        """

        self.updateRowLabels = not status
        labelItems = extract_patternItems(self.items(), PatternLabelItem)
        for item in labelItems:
            if item.is_rowLabel:
                item.editable(status)

        # if we just turned editing off make sure to reset labels
        # to the currently selected auto labeling; if we turned
        # editing on this call is a no op
        self.set_up_labels()



    def toggle_column_label_editing(self, status):
        """ Per request from main window toggles the ability
        to edit the column labels.

        """

        self.updateColumnLabels = not status
        labelItems = extract_patternItems(self.items(), PatternLabelItem)
        for item in labelItems:
            if not item.is_rowLabel:
                item.editable(status)

        # if we just turned editing off make sure to reset labels
        # to the currently selected auto labeling; if we turned
        # editing on this call is a no op
        self.set_up_labels()



    def label_font_changed(self):
        """ This slot is called when the label font has
        been changed.

        """

        labelFont = self.settings.labelFont.value
        for item in self.items():
            if isinstance(item, PatternLabelItem):
                item.setFont(labelFont)




    def show_hidden_legend_items(self):
        """ Shows all currently hidden legend items. """

        for item in self.gridLegend.values():
            legendItem_symbol(item).show()
            legendItem_text(item).show()




    def toggle_legend_visibility(self, status):
        """ Per request from main window toggle the legend
        visibility on or off.

        """

        if status:
            for item in self.gridLegend.values():
                legendItem_symbol(item).show()
                legendItem_text(item).show()

            # only show repeat legends which are visible
            for item in self.repeatLegend.values():
                if legendItem_count(item):
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

        self.isVisible = status
        for item in self.items():
            if isinstance(item, PatternGridItem) \
            or isinstance(item, PatternLabelItem) \
            or isinstance(item, PatternHighlightItem) \
            or isinstance(item, PatternRepeatItem):
                if status:
                    item.show()
                else:
                    item.hide()

        if status:
            # need this to make sure the labels have the
            # proper visibility
            self.set_up_labels()



    def add_text_item(self, itemPos = None,
                      itemText = "My Label"):
        """ Adds a text item to the canvas.

        NOTE: The main reason for keeping track of text boxes in
        self.canvasTextBoxes is that it allows faster access when
        changing, e.g., the font size and when saving. Since there
        probably aren't that many the memory cost is probably small.

        """

        addTextBoxCommand = AddTextBox(self, itemPos, itemText)
        self._undoStack.push(addTextBoxCommand)



    def delete_text_item(self, deadItem):
        """ Removes a text item to the canvas. """

        deleteTextBoxCommand = DeleteTextBox(self, deadItem)
        self._undoStack.push(deleteTextBoxCommand)



    def contains_symbol(self, symbolName):
        """ Returns True if the canvas contains a PatternGridItem

        with symbol of symbolName and False otherwise.

        """

        for item in self.items():
            if isinstance(item, PatternGridItem):
                if item.name == symbolName:
                    return True

        return False
