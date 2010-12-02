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
from functools import partial
from PyQt4.QtCore import (Qt, QRectF, QSize, QPointF, QSizeF, 
                          SIGNAL, QObject, QString, QPoint, QRect)
from PyQt4.QtGui import (QGraphicsScene, QGraphicsObject, QPen, QColor, 
                         QBrush, QGraphicsTextItem, QFontMetrics, QMenu, 
                         QAction, QGraphicsItem, QMessageBox, QRubberBand)
from PyQt4.QtSvg import (QGraphicsSvgItem, QSvgWidget, QSvgRenderer)
from util.settings import get_grid_dimensions, get_text_font
from util.canvas import (is_click_in_grid, is_click_on_labels, 
                            convert_pos_to_row_col)
from gui.insertDeleteRowColumnWidget import InsertDeleteRowColumnWidget
from util.misc import wait_cursor
import util.messages as msg




#########################################################
## 
## class for managing the actual pattern canvas
##
#########################################################
class PatternCanvas(QGraphicsScene):


    def __init__(self, theSettings, defaultSymbol, parent = None):

        super(PatternCanvas, self).__init__(parent)

        self.setBackgroundBrush(QBrush(Qt.white))

        self.__settings = theSettings

        self.__activeSymbol  = None
        self.__defaultSymbol = defaultSymbol
        self.__activeColor   = None
        self.__defaultColor  = QColor(Qt.white)
        self.__selectedCells = set()
        self.__copySelection = set()

        self.__unitCellDim = QSizeF(get_grid_dimensions(theSettings))
        self.__unitWidth   = self.__unitCellDim.width()
        self.__unitHeight  = self.__unitCellDim.height()
        self.__numRows     = 10
        self.__numColumns  = 10

        self.__textFont    = get_text_font(theSettings)
        self.__textLabels  = []

        self.addDeleteRowColDialog = None

        self.legend = {}

        self.set_up_main_grid()
        self.set_up_labels()



    def set_up_main_grid(self):
        """
        This function draws the main grid.
        """

        for row in range(0, self.__numRows):
            self.__create_row(row)



    def set_up_labels(self):
        """
        Add labels to the main grid.
        FIXME: This function currently recreates all labels instead
        of just shifting around existing ones. The latter should
        probably be more efficient.
        """

        for label in self.__textLabels:
            self.removeItem(label)
        self.__textLabels = []
            
        fm = QFontMetrics(self.__textFont)
        
        # row labels
        xPos = self.__unitWidth * self.__numColumns
        for row in range(0, self.__numRows):
            item = PatternLabelItem(unicode(self.__numRows - row))

            yPos = self.__unitHeight * row
            item.setPos(xPos, yPos)
            item.setFont(self.__textFont)
            self.addItem(item)
            self.__textLabels.append(item)

        # column labels
        yPos = self.__unitHeight * self.__numRows
        for col in range(0, self.__numColumns):
            labelText = QString(unicode(self.__numColumns - col))
            textWidth = fm.width(labelText)
            item = PatternLabelItem(labelText)
            
            xPos = self.__unitWidth * col + (self.__unitWidth * 0.6 -textWidth)
            item.setPos(xPos, yPos)
            item.setFont(self.__textFont)

            self.addItem(item)
            self.__textLabels.append(item)

            

    def set_active_symbol(self, activeKnittingSymbol):
        """
        This function receives the currently active symbol
        and stores it.
        """

        self.__activeSymbol = activeKnittingSymbol
        self.paint_cells()



    def set_active_color(self, color):
        """
        This function received the currently active
        background color and stores it.
        """

        self.__activeColor = color
        self.paint_cells()
            


    def add_to_legend(self, item):
        """
        Adds a newly created PatternGridItem to the legend database
        and updates the legend itself if needed.
        """

        legendID = generate_legend_id(item.symbol, item.color)
        if legendID in self.legend:
            entry = self.legend[legendID]
            new_entry = change_count(entry, 1)
            self.legend[legendID] = new_entry
        else:
            (item, textItem) = self.__add_legend_item(item.symbol, item.color)
            self.legend[legendID] = [1, item, textItem]



    def add_extra_symbol_to_legend(self, symbol):
        """ Adds a symbol to the legend per user request. 

        NOTE: This could be any symbol, especially one not
        currently in the pattern grid. In order to distinguisht 
        """

        
        print(symbol["name"])






    def __add_legend_item(self, symbol, color):
        """
        This adds a new legend entry including an PatternLegendItem
        and a textual description. This function also attemps to be
        sort of smart about where to put the item.
        """

        legendYmax = compute_max_legend_y_coordinate(self.legend)
        canvasYmax = (self.__numRows + 1) * self.__unitHeight

        yMax = max(legendYmax, canvasYmax)

        # add the symbol part of the legend
        width  = int(symbol["width"])
        height = 1
        itemLocation = QPointF(0, yMax + self.__unitHeight + 10)
        item = PatternLegendItem(self.__unitCellDim, width, height, symbol,
                                 color, 1)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setPos(itemLocation)
        self.addItem(item)

        # add the description part of the legend
        textLocation = QPointF((width+1) * self.__unitWidth,
                                yMax + self.__unitHeight + 10)
        textItem = QGraphicsTextItem()
        textItem.setPos(textLocation)
        textItem.setZValue(1)
        textItem.setFlag(QGraphicsItem.ItemIsMovable)
        textItem.setTextInteractionFlags(Qt.TextEditorInteraction);
        textItem.setPlainText(symbol["description"])
        self.addItem(textItem)

        self.emit(SIGNAL("adjust_view"))
        
        return (item, textItem)



    def remove_from_legend(self, item):
        """
        Removes a PatternGridItem from the legend database
        and updates the legend itself if needed.
        """


        legendID = generate_legend_id(item.symbol, item.color)
        assert(legendID in self.legend)

        entry = self.legend[legendID]
        if legendItem_count(entry) == 1:
            self.removeItem(legendItem_symbol(entry))
            self.removeItem(legendItem_text(entry))
            del self.legend[legendID]
        else:
            new_entry = change_count(entry, -1)
            self.legend[legendID] = new_entry




    def clear_all_selected_cells(self):
        """ Unselects all currently selected cells. """

        while self.__selectedCells:
            item = self.__selectedCells.pop()
            item.press_item()
            
            # FIXME: This is a hack to force qt to
            # redraw the items right away. There has
            # to be a better way
            item.hide()
            item.show()

        

    def grid_cell_activated(self, item):
        """
        If a grid cell notifies it has been activated add it
        to the collection of selected cells and try to paint
        them.
        """
        
        self.__selectedCells.add(item)
        self.paint_cells()



    def grid_cell_inactivated(self, item):
        """
        If a grid cell notifies it has been in-activated remove
        it from the collection of selected cells if present.
        """

        if item in self.__selectedCells:
            self.__selectedCells.remove(item)
        self.paint_cells()



    def create_pattern_grid_item(self, origin, unitDim, col, row,
                                    width, height, knittingSymbol,
                                    color):
        """
        Creates a new PatternGridItem of the specified dimension
        at the given location.
        """

        item = PatternGridItem(unitDim, col, row, width, height,
                                knittingSymbol, color)
        item.setPos(origin)
        self.connect(item, SIGNAL("cell_selected"), self.grid_cell_activated)
        self.connect(item, SIGNAL("cell_unselected"), self.grid_cell_inactivated)
        return item



    def addItem(self, item):
        """
        This overload of addItem makes sure that we perform QGraphicsItem
        specific task such as updating the legend for svg items.
        """

        if isinstance(item, PatternGridItem):
            self.add_to_legend(item)

        super(PatternCanvas,self).addItem(item)



    def removeItem(self, item):
        """
        This overload of removeItem makes sure that we perform QGraphicsItem
        specific task such as updating the legend for svg items.
        """

        if isinstance(item, PatternGridItem):
            self.remove_from_legend(item)

        super(PatternCanvas,self).removeItem(item)



    def paint_cells(self):
        """
        Attempts to paint the cells with the selected symbol.
        Has to make sure the geometry is appropriate.
        """

        if self.__activeSymbol:
            width = int(self.__activeSymbol["width"])
            chunks = chunkify_cell_arrangement(width, self.__selectedCells)

            if chunks:
                for chunk in chunks:
                    totalWidth = 0

                    # location of leftmost item in chunk
                    origin = chunk[0].pos()
                    row    = chunk[0].row
                    column = chunk[0].column

                    # compute total width and remove old items
                    for item in chunk:
                        totalWidth += item.width
                        self.removeItem(item)

                    # insert as many new items as we can fit
                    numNewItems = int(totalWidth/width)
                    for i in range(0,numNewItems):
                        item = self.create_pattern_grid_item(origin,
                                    self.__unitCellDim, column, row, width, 1,
                                    self.__activeSymbol, self.__activeColor)
                        self.addItem(item)
                        origin = QPointF(origin.x() + (width * self.__unitWidth),
                                         origin.y())
                        column = column + width

                self.__selectedCells.clear()



    def mousePressEvent(self, event):
        """
        Handle mouse press events directly on the canvas.
        """

        (row, col) = convert_pos_to_row_col(event.scenePos(),
                                            self.__unitWidth,
                                            self.__unitHeight)
        
        if event.button() == Qt.RightButton:

            if is_click_in_grid(col, row, self.__numColumns, self.__numRows):
                self.handle_right_click_on_grid(event, row, col)

            # don't propagate this events
            return

        elif event.button() == Qt.LeftButton:

            if is_click_on_labels(col, row, self.__numColumns, self.__numRows):
                 self.handle_right_click_on_labels(col, row)


        # tell our main window that something changed
        self.emit(SIGNAL("scene_changed"))

        return QGraphicsScene.mousePressEvent(self, event)



    def select_region(self, region):
        """ This function selects items based on a whole region.

        The region is typically a QPolygonF coming from our
        view via a rubberBand selection.
        """

        for item in self.items(region):
            if isinstance(item, PatternGridItem):
                item.press_item()



    def handle_right_click_on_labels(self, col, row):
        """ Deal with user clicks on the grid labels. """

        assert (row == self.__numRows) or (col == self.__numColumns)

        if row == self.__numRows:
            selectedItems = get_column_items(self.items(), col)
            
        else:
            selectedItems = get_row_items(self.items(), row)

        for item in selectedItems:
            item.press_item()




    def handle_right_click_on_grid(self, event, row, col):
        """
        Handles a right click on the pattern grid by
        displaying a QMenu with options.
        """

        gridMenu = QMenu()
        rowAction = gridMenu.addAction("Insert/Delete Rows and Columns")
        gridMenu.addSeparator();
        colorAction = gridMenu.addAction("Grab Color");

        self.connect(rowAction, SIGNAL("triggered()"),
                     partial(self.insert_delete_rows_columns, row, col))
        
        self.connect(colorAction, SIGNAL("triggered()"),
                     partial(self.grab_color_from_cell, event))

        gridMenu.exec_(event.screenPos())



    def insert_delete_rows_columns(self, row, col):
        """
        This method manages the addition and deletion of rows and columns
        via a widget.
        """

        if not self.addDeleteRowColDialog:
            self.addDeleteRowColDialog = \
                InsertDeleteRowColumnWidget(self.__numRows,
                                            self.__numColumns,
                                            row, col, self.parent())
        else:
            self.addDeleteRowColDialog.set_row_col(row,col)


        self.connect(self.addDeleteRowColDialog, SIGNAL("insert_row"), 
                     self.insert_grid_row)
        self.connect(self.addDeleteRowColDialog, SIGNAL("delete_row"), 
                     self.delete_grid_row)
        self.connect(self.addDeleteRowColDialog, SIGNAL("insert_column"), 
                     self.insert_grid_column)
        self.connect(self.addDeleteRowColDialog, SIGNAL("delete_column"), 
                     self.delete_grid_column)

        self.addDeleteRowColDialog.raise_()
        self.addDeleteRowColDialog.show()



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
        self.emit(SIGNAL("active_color_changed"), color)
        


    def insert_grid_row(self, num, mode, rowPivot):
        """
        Deals with requests to insert a row. This operation might
        take some time so we switch to a wait cursor.
        """

        pivot = self.convert_canvas_row_to_internal(rowPivot)
        assert(pivot >= 0 and pivot < self.__numRows)

        if mode == QString("above"):
            cmpOp = operator.__ge__
            shift = 0
        else:
            cmpOp = operator.__gt__
            shift = 1

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem):
                if cmpOp(graphicsItem.row, pivot):
                    shift_items_row_wise(graphicsItem, num, self.__unitHeight)

        for row in range(0, num):
            self.__create_row(pivot + shift + row)

        shift_legend_down(self.legend, num, self.__unitHeight,
                          self.__numColumns, self.__unitWidth)
        
        self.__numRows += num
        self.set_up_labels()
        self.emit(SIGNAL("adjust_view"))
        self.emit(SIGNAL("scene_changed"))
        self.addDeleteRowColDialog.set_upper_row_limit(self.__numRows)



    def delete_grid_row(self, canvasRow):
        """
        Deals with requests to delete a specific row.
        """
       
        row = self.convert_canvas_row_to_internal(canvasRow)

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem):
                if graphicsItem.row == row:
                    self.removeItem(graphicsItem)
                elif graphicsItem.row > row:
                    shift_items_row_wise(graphicsItem, -1, self.__unitHeight)

        self.__numRows -= 1
        self.__activeItems = []
        self.set_up_labels()
        self.emit(SIGNAL("adjust_view"))
        self.emit(SIGNAL("scene_changed"))
        self.addDeleteRowColDialog.set_upper_row_limit(self.__numRows)
        


    def insert_grid_column(self, num, mode, columnPivot):
        """
        Deals with requests to insert a column.
        """

        pivot = self.convert_canvas_column_to_internal(columnPivot)
        assert(pivot >= 0 and pivot < self.__numColumns)

        isExternalColumn = False
        if mode == QString("left of"):
            cmpOp = operator.__ge__
            shift = 0
            if pivot == 0:
                isExternalColumn = True
        else:
            cmpOp = operator.__gt__
            shift = 1
            if pivot == self.__numColumns - 1:
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
            if rowCounter != self.__numRows:
                QMessageBox.warning(None, msg.noColInsertLayoutTitle,
                                msg.noColInsertLayoutText,
                                QMessageBox.Close)
                return

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem):
                if cmpOp(graphicsItem.column, pivot):
                    shift_items_column_wise(graphicsItem, num, self.__unitWidth)

        for column in range(0, num):
            self.__create_column(pivot + shift + column)


        shift_legend_right(self.legend, num, self.__unitWidth,
                          self.__numRows, self.__unitHeight)
        
        self.__numColumns += num
        self.set_up_labels()
        self.emit(SIGNAL("adjust_view"))
        self.emit(SIGNAL("scene_changed"))
        self.addDeleteRowColDialog.set_upper_column_limit(self.__numColumns)



    def delete_grid_column(self, deadColumn):
        """
        Deals with requests to delete a specific column.
        """

        column = self.convert_canvas_column_to_internal(deadColumn)

        # in order for deleting of a column at deadColumn to succeed
        # there has to be a unit element at that column
        rowCounter = 0
        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem):
                if (graphicsItem.column == column) and \
                    (graphicsItem.width == 1):
                    rowCounter += 1

        if rowCounter != self.__numRows:
            QMessageBox.warning(None, msg.noColDeleteLayoutTitle,
                                msg.noColDeleteLayoutText,
                                QMessageBox.Close)
            return

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternGridItem):
                if graphicsItem.column == column:
                    self.removeItem(graphicsItem)
                elif graphicsItem.column > column:
                    shift_items_column_wise(graphicsItem, -1, self.__unitWidth)

        self.__numColumns -= 1
        self.__activeItems = []
        self.set_up_labels()
        self.emit(SIGNAL("adjust_view"))
        self.emit(SIGNAL("scene_changed"))
        self.addDeleteRowColDialog.set_upper_column_limit(self.__numColumns)



    def convert_canvas_row_to_internal(self, row):
        """
        Internally rows are numbered 0 through numRows-1
        from the top to bottom whereas they appear as numRows to 1
        on the canvas. This function does the conversion.
        """

        return self.__numRows - row



    def convert_canvas_column_to_internal(self, column):
        """
        Internally columns are numbered 0 through numColumns-1
        from the left to right whereas they appear as numColumns to 1
        on the canvas. This function does the conversion.
        """

        return self.__numColumns - column



    def __create_row(self, rowID):
        """
        Creates a new row at rowID, nothing else. In particular
        this function does not attempt to make space for the row or
        anything else along these lines. This is a private and 
        very stupid function.
        """

        for column in range(0, self.__numColumns):
            location = QPointF(column * self.__unitWidth,
                                rowID * self.__unitHeight)
            item = self.create_pattern_grid_item(location, self.__unitCellDim,
                                                    column, rowID, 1, 1,
                                                    self.__defaultSymbol,
                                                    self.__defaultColor)
            self.addItem(item)



    def __create_column(self, columnID):
        """
        Creates a new column at columnID, nothing else. In particular
        this function does not attempt to make space for the column or
        anything else along these lines. This is a private and very
        stupid function.
        """

        for row in range(0, self.__numRows):
            location = QPointF(columnID * self.__unitWidth,
                                row * self.__unitHeight)
            item = self.create_pattern_grid_item(location, self.__unitCellDim,
                                                    columnID, row, 1, 1,
                                                    self.__defaultSymbol,
                                                    self.__defaultColor)
            self.addItem(item)



    def __clear_canvas(self):
        """
        Clear the complete canvas. 
        """

        # clear GraphicsScene
        self.clear()
        self.update()

        # clear all caches
        self.legend.clear()



    def create_new_canvas(self, numRows = 10, numColumns = 10):
        """
        Create a complete new and blank canvas.
        """

        # reset the number of columns/rows to 10
        # we probably should add a dialog here
        self.__numRows    = numRows
        self.__numColumns = numColumns
        self.addDeleteRowColDialog = None
        
        self.__clear_canvas()
        self.__textLabels = []
        self.set_up_main_grid()
        self.set_up_labels()

        self.emit(SIGNAL("adjust_view"))
        


    @wait_cursor
    def load_previous_pattern(self, knittingSymbols, patternGridItemInfo,
                          legendItemInfo):
        """
        Clear curent canvas and establishes a new canvas
        based on the passed canvas items. Returns True on success
        and False otherwise.
        NOTE: We have to be able to deal with bogus data (from a
        corrupted file perhaps).
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
                symbolID = category + "::" + name
                location = QPointF(colID * self.__unitWidth,
                                    rowID * self.__unitHeight)
                symbol   = knittingSymbols[symbolID]
                allPatternGridItems.append((location, self.__unitCellDim, 
                                            colID, rowID, width, 
                                            height, symbol, color))

                # update trackers
                maxCol = max(maxCol, colID)
                maxRow = max(maxRow, rowID)
        except KeyError as e:
            QMessageBox.critical(None, msg.errorLoadingGridTitle,
                                 msg.errorLoadingGridText % e,
                                 QMessageBox.Close)
            return False

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
            return False

        self.__clear_canvas()
        for entry in allPatternGridItems:
            item = self.create_pattern_grid_item(*entry)
            self.addItem(item)

        for entry in allLegendItems:
            arrange_label_item(self.legend, *entry)

        # need to clear our label cache, otherwise set_up_labels()
        # will try to remove non-existing items
        self.__numRows    = maxRow + 1
        self.__numColumns = maxCol + 1
        self.__textLabels = []
        self.set_up_labels()

        self.emit(SIGNAL("adjust_view"))
        return True



    def toggle_label_visibility(self, status):
        """
        Per request from main window toggle
        the visibility of the labels.
        """

        for item in self.items():
            if isinstance(item, PatternLabelItem):
                if status:
                    item.show()
                else:
                    item.hide()




    def toggle_legend_visibility(self, status):
        """
        Per request from main window toggle the legend
        visibility on or off.
        """

        if status:
            for item in self.legend.values():
                legendItem_symbol(item).show()
                legendItem_text(item).show()

        else:
            for item in self.legend.values():
                legendItem_symbol(item).hide()
                legendItem_text(item).hide()
            



    def toggle_pattern_grid_visibility(self, status):
        """
        Per request from main window toggle the pattern grid
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

        self.origin  = QPointF(0.0, 0.0)
        self.unitDim = unitDim
        self.row     = row
        self.column  = col
        self.width   = width
        self.height  = height
        self.size    = QSizeF(self.unitDim.width() * width,
                              self.unitDim.height() * height)

        self.__penSize = 1.0
        self.__pen = QPen()
        self.__pen.setWidthF(self.__penSize)
        self.__pen.setJoinStyle(Qt.MiterJoin)
        self.__pen.setColor(Qt.black)

        self.__selected  = False
        self.color       = defaultColor
        self.__backColor = self.color
        self.__highlightedColor = QColor(Qt.gray)

        self.symbol = None
        self.__set_symbol(defaultSymbol)



    def mousePressEvent(self, event):
        """
        Handle user press events on the item.
        """

        self.press_item()



    def press_item(self):
        """
        This functions dispatches all events triggered
        by a press event on the item.
        """

        if not self.__selected:
            self.__select()
        else:
            self.__unselect()



    def __unselect(self):
        """
        Unselects a given selected cell. 
        """

        self.__selected = False
        self.__backColor = self.color
        self.update()
        self.emit(SIGNAL("cell_unselected"), self)



    def __select(self):
        """
        Selects a given unselected cell. 
        """

        self.__selected = True
        self.__backColor = self.__highlightedColor
        self.update()
        self.emit(SIGNAL("cell_selected"), self)


            
    def __set_symbol(self, newSymbol):
        """
        Adds a new svg image of a knitting symbol to the
        scene.
        """

        self.symbol = newSymbol
        svgPath = newSymbol["svgPath"]
        if not self.renderer().load(svgPath):
            print("failed to load")
            return

        # apply color if present
        if "backgroundColor" in newSymbol:
            self.__backColor = QColor(newSymbol["backgroundColor"])

        self.update()



    def boundingRect(self):
        """
        Return the bounding rectangle of the item.
        """

        halfPen = self.__penSize * 0.5
        return QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
                                                       halfPen, halfPen)
        


    def paint(self, painter, option, widget):
        """
        Paint ourselves.
        """

        painter.setPen(self.__pen)
        brush = QBrush(self.__backColor)
        painter.setBrush(brush)
        halfPen = self.__penSize * 0.5
        painter.drawRect(QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
                                                                 halfPen, halfPen))
        painter.drawRect(QRectF(self.origin, self.size))
        self.renderer().render(painter, QRectF(self.origin, self.size))




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
        
        self.setZValue(zValue)

        self.origin  = QPointF(0.0, 0.0)
        self.unitDim = unitDim
        self.width   = width
        self.height  = height
        self.size    = QSizeF(self.unitDim.width() * width,
                              self.unitDim.height() * height)

        self.color  = defaultColor

        self.symbol = None
        self.__set_symbol(defaultSymbol)
        
        self.__penSize = 1.0
        self.__pen = QPen()
        self.__pen.setWidthF(self.__penSize)
        self.__pen.setJoinStyle(Qt.MiterJoin)
        self.__pen.setColor(Qt.black)




    def __set_symbol(self, newSymbol):
        """
        Adds a new svg image of a knitting symbol to the
        scene.
        """

        self.symbol = newSymbol
        svgPath = newSymbol["svgPath"]
        if not self.renderer().load(svgPath):
            print("failed to load")
            return

        # apply color if present
        if "backgroundColor" in newSymbol:
            self.color = QColor(newSymbol["backgroundColor"])


    def boundingRect(self):
        """
        Return the bounding rectangle of the item.
        """

        halfPen = self.__penSize * 0.5
        return QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
                                                       halfPen, halfPen)
        


    def paint(self, painter, option, widget):
        """
        Paint ourselves.
        """

        painter.setPen(self.__pen)
        brush = QBrush(self.color)
        painter.setBrush(brush)
        halfPen = self.__penSize * 0.5
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

def chunkify_cell_arrangement(width, allCells):
    """
    Given a collection of selected cells verifies that we
    can place a symbol of given width. If so, return a
    list of consecutive chunks of cells all of a multiple of width
    that can be filled with the new symbol.
    """

    # check 1: number of active cells has to be a multiple
    # of width
    if num_unitcells(allCells) % width != 0:
        return []

    cellsByRow = {}
    for cell in allCells:
        if not cell.row in cellsByRow:
            cellsByRow[cell.row] = [cell]
        else:
            cellsByRow[cell.row].append(cell)

    # check 2: each row has to be a multiple of width
    for row in cellsByRow.values():
        if num_unitcells(row) % width != 0:
            return []


    chunkList = chunk_all_rows(width, cellsByRow)

    return chunkList



def chunk_all_rows(width, cellsByRow):
    """
    Separate each row into chunks at least as long as
    the items we want to place. Then we check if each
    chunk is consecutive.
    """
    
    chunkList = []
    for row in cellsByRow.values():
        row.sort(lambda x, y: cmp(x.column, y.column))

        chunks = []
        chunk = []
        length = 0
        for item in row:
            chunk.append(item)
            length += item.width
            if length % width == 0:
               chunks.append(chunk)
               chunk = []
               length = 0

        if not are_consecutive(chunks):
            return []

        chunkList.extend(chunks)

    return chunkList



def are_consecutive(chunks):
    """
    Checks if each chunk in a list of chunks consists
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
    """
    Compute the total number of unit cells in the
    selection.
    """

    totalWidth = 0
    for item in cells:
        totalWidth += item.width

    return totalWidth



def shift_items_row_wise(item, num, unitCellHeight):
    """
    Shifts the given item by num rows given unitCellHeight.
    """
    
    yShift = num * unitCellHeight
    item.prepareGeometryChange()
    item.row += num
    item.setPos(item.pos() + QPointF(0.0, yShift))



def shift_items_column_wise(item, num, unitCellWidth):
    """
    Shifts the given item by num columns given unitCellWidth.
    """
    
    xShift = num * unitCellWidth
    item.prepareGeometryChange()
    item.column += num
    item.setPos(item.pos() + QPointF(xShift, 0.0))



def shift_legend_down(legendList, numAdditionalRows, unitCellHeight,
                      numColumns, unitWidth):
    """ Shift all legend items below the grid down by
    numAdditionalRows """

    yShift = numAdditionalRows * unitCellHeight

    for item in legendList.values():
        symbol = legendItem_symbol(item)
        text   = legendItem_text(item)

        # we ignore all items above or right of the
        # pattern grid
        if (symbol.scenePos().y() >= 0) and \
           (symbol.scenePos().x() <= numColumns * unitWidth):

            symbol.prepareGeometryChange()
            symbol.setPos(symbol.pos() + QPointF(0.0, yShift))
            
            text.prepareGeometryChange()
            text.setPos(text.pos() + QPointF(0.0, yShift))

    

def shift_legend_right(legendList, numAdditionalColumns, unitCellWidth,
                      numRows, unitHeight):
    """ Shift all legend items to the right of the grid right by
    numAdditionalColumns """

    xShift = numAdditionalColumns * unitCellWidth

    for item in legendList.values():
        symbol = legendItem_symbol(item)
        text   = legendItem_text(item)

        # we ignore all items above or right of the
        # pattern grid
        if (symbol.scenePos().x() >= 0) and \
           (symbol.scenePos().y() >= 0) and \
           (symbol.scenePos().y() <= numRows * unitHeight):

            symbol.prepareGeometryChange()
            symbol.setPos(symbol.pos() + QPointF(xShift, 0.0))
            
            text.prepareGeometryChange()
            text.setPos(text.pos() + QPointF(xShift, 0.0))



def compute_max_legend_y_coordinate(legendList):
    """
    Given the current list of existing legend items
    figure out the largest y coordinate among them all.
    """

    yList = [0]
    for item in legendList.values():
        yList.append(legendItem_symbol(item).scenePos().y())
        yList.append(legendItem_text(item).scenePos().y())
    
    return max(yList)



def change_count(item, count):
    """
    Convenience wrapper changing the count for a particular
    legend entry.
    """

    item[0] += count
    return item



def legendItem_count(item):
    """
    Convenience wrapper returning the reference count for the
    particular legend item.
    """

    return item[0]



def legendItem_symbol(item):
    """
    Convenience wrapper returning the current symbol for a
    particular legend item.
    """

    return item[1]



def legendItem_text(item):
    """
    Convenience wrapper returning the current description text
    for a particular legend item.
    """

    return item[2]



def generate_legend_id(symbol, color):
    """
    Based on a symbol/legend info, generate an id tag. Currently
    this is just based on name and category.
    """

    name = symbol["name"]
    category = symbol["category"]

    return (name, category, color.name())




def arrange_label_item(legendItems, legendID, itemXPos, itemYPos, labelXPos, 
                       labelYPos, description):
    """
    Position all label items (pairs of PatternGridItem
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



def get_column_items(items, column):
    """ Returns list of all PatternGridItems in column

    NOTE: There is an issue if we encounter an item
    which spans multiple columns. For now we ignore these.
    """

    colItems = []
    for item in items:
        if isinstance(item, PatternGridItem):
            if (item.column == column) and (item.width == 1):
                colItems.append(item)

    return colItems
    



def get_row_items(items, row):
    """ Returns list of all PatternGridItems in row.

    NOTE: Since we want to select the whole row, we
    have to make sure to deliver the items left to
    right and *not* out of order.
    """

    rowItems = []
    for item in items:
        if isinstance(item, PatternGridItem):
            if item.row == row:
                rowItems.append(item)
                
    rowItems.sort(lambda x, y: cmp(x.column, y.column))
    
    return rowItems





