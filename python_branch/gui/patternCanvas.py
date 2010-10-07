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

import operator
from PyQt4.QtCore import Qt, QRectF, QSize, QPointF, QSizeF, \
                         pyqtSignal, SIGNAL, QObject, QString, \
                         QPoint
from PyQt4.QtGui import QGraphicsScene, QGraphicsObject, QPen, QColor, \
                        QBrush, QGraphicsTextItem, QFontMetrics, QMenu, \
                        QAction
from PyQt4.QtSvg import QGraphicsSvgItem, QSvgWidget, QSvgRenderer
from sconchoHelpers.settings import get_grid_dimensions, get_text_font
import sconchoHelpers.canvas as canvasHelpers
from insertDeleteRowColumnWidget import InsertDeleteRowColumnWidget




#########################################################
## 
## class for managing the actual pattern canvas
##
#########################################################
class PatternCanvas(QGraphicsScene):

    # signals
    row_col_count_changed = pyqtSignal(QString, int)
    

    def __init__(self, theSettings, parent = None):

        super(PatternCanvas,self).__init__()

        self.__settings = theSettings

        self.__activeSymbol  = None
        self.__selectedCells = set()
        self.__copySelection = set()
        self.__rightClickPos = QPoint() # (row, col) position of last right click

        self.__unitCellDim = QSizeF(get_grid_dimensions(theSettings))
        self.__unitWidth   = self.__unitCellDim.width()
        self.__unitHeight  = self.__unitCellDim.height()
        self.__numRows     = 10
        self.__numColumns  = 10

        self.__textFont    = get_text_font(theSettings)
        self.__textLabels  = []

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
            item = QGraphicsTextItem(str(self.__numRows - row))

            yPos = self.__unitHeight * row
            item.setPos(xPos, yPos)
            item.setFont(self.__textFont)
            self.addItem(item)
            self.__textLabels.append(item)

        # column labels
        yPos = self.__unitHeight * self.__numRows
        for col in range(0, self.__numColumns):
            labelText = QString(str(self.__numColumns - col))
            textWidth = fm.width(labelText)
            item = QGraphicsTextItem(labelText)
            
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

        if activeKnittingSymbol:
            print("symbol changed --> " + activeKnittingSymbol["name"])
            
        self.__activeSymbol = activeKnittingSymbol
        self.paint_cells()



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
        it from the collectoin of selected cells.
        """

        self.__selectedCells.remove(item)
        self.paint_cells()



    def create_item(self, origin, dim, col, row, width):
        """
        Creates a new PatternGridItem of the specified dimension
        at the given location.
        """

        item = PatternCanvasItem(origin, dim, col, row, width)
        self.connect(item, SIGNAL("cell_selected(PyQt_PyObject)"),
                     self.grid_cell_activated)
        self.connect(item, SIGNAL("cell_unselected(PyQt_PyObject)"),
                     self.grid_cell_inactivated)
        self.addItem(item)

        return item



    def paint_cells(self):
        """
        Attempts to paint the cells with the selected symbol.
        Has to make sure the geometry is appropriate.
        """
        
        if self.__activeSymbol:
            width = int(self.__activeSymbol["width"])
            chunks = chunkify_cell_arrangement(width, self.__selectedCells)
            dim = QSizeF(self.__unitWidth * width, self.__unitHeight)
            
            if chunks:
                for chunk in chunks:
                    totalWidth = 0

                    # location of leftmost item in chunk
                    origin = chunk[0].origin
                    row    = chunk[0].row
                    column = chunk[0].column

                    # compute total width and remove old items
                    for item in chunk:
                        totalWidth += item.width
                        self.removeItem(item)

                    # insert as many new items as we can fit
                    numNewItems = totalWidth/width
                    for i in range(0,numNewItems):
                        item = self.create_item(origin, dim, column, row, width)
                        item.set_symbol(self.__activeSymbol)
                        origin = QPointF(origin.x() + (width * self.__unitWidth),
                                         origin.y())
                        column = column + width

                self.__selectedCells.clear()



    def item_at(self, pos):
        """
        Returns the item at the given column and row.
        """

        scenePos = \
                 canvasHelpers.convert_row_col_to_pos(pos, self.__unitWidth,
                                                      self.__unitHeight)

        return self.itemAt(scenePos)



    def mousePressEvent(self, event):
        """
        Handle mouse press events directly on the canvas.
        """

        # we handle right clicks and propagate the rest
        if (event.button() == Qt.RightButton):
            self.__rightClickPos = \
                canvasHelpers.convert_pos_to_row_col(event.scenePos(),
                                                     self.__unitWidth,
                                                     self.__unitHeight)
            
            if canvasHelpers.is_row_col_in_grid(self.__rightClickPos,
                                                self.__numColumns,
                                                self.__numRows):
                self.handle_right_click_on_grid(event)
                
        else:
            return QGraphicsScene.mousePressEvent(self, event)



    def handle_right_click_on_grid(self, event):
        """
        Handles a right click on the pattern grid by
        displaying a QMenu with options.
        """
        
        gridMenu = QMenu()
        # TODO: copy and paste needs some thinking about
        # e.g. what should we do when a user pastes a selection
        # that does not fit into the target area 
        #copyAction = gridMenu.addAction("&Copy")
        #pasteAction = gridMenu.addAction("&Paste")
        #self.connect(copyAction, SIGNAL("triggered()"),
        #             self.copy_selection)
        #self.connect(pasteAction, SIGNAL("triggered()"),
        #             self.paste_selection)
        #gridMenu.addSeparator()
        rowAction = gridMenu.addAction("Insert/delete rows & columns")
        gridMenu.addSeparator();
        colorAction = gridMenu.addAction("Grab color");

        self.connect(rowAction, SIGNAL("triggered()"),
                     self.insert_delete_rows_columns)
        
        gridMenu.exec_(event.screenPos())



    def copy_selection(self):
        """
        Copies the currently active selection.
        """

        self.__copySelection.clear()
        self.__copySelection = self.__selectedCells

        

    def paste_selection(self):
        """
        Pastes the selection currently stored in copySelection.
        The upper left item in copySelection is copied into the
        clicked cell.
        NOTE: Pasting is not easy. We need to make sure that
        the copied selection can fit seamlessly into the target
        ares.
        """

        if not canvasHelpers.is_row_col_in_grid(self.__rightClickPos,
                                                self.__numColumns,
                                                self.__numRows):
            return
        



    def insert_delete_rows_columns(self):
        """
        This method manages the addition and deletion of rows and columns
        via a widget.
        """

        addDeleteDialog = InsertDeleteRowColumnWidget(self.__numRows,
                                                      self.__numColumns)

        self.connect(addDeleteDialog, SIGNAL("insert_row(int, QString, int)"), 
                     self.insert_row)
        self.connect(addDeleteDialog, SIGNAL("delete_row(int)"),
                     self.delete_row)
        self.connect(addDeleteDialog, SIGNAL("insert_column(int, QString, int)"),
                     self.insert_column)
        self.connect(addDeleteDialog, SIGNAL("delete_column(int)"),
                     self.delete_column)
        self.connect(self, SIGNAL("row_col_count_changed(QString, int)"),
                     addDeleteDialog.row_col_count_changed)
        
        addDeleteDialog.exec_()



    def insert_row(self, num, mode, rowPivot):
        """
        Deals with requests to insert a row.
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
            if isinstance(graphicsItem, PatternCanvasItem):
                if cmpOp(graphicsItem.row, pivot):
                    shift_items_row_wise(graphicsItem, num, self.__unitHeight)

        for row in range(0, num):
            self.__create_row(pivot + shift + row)

        self.__numRows += num
        self.set_up_labels()
        self.row_col_count_changed.emit("numRows", self.__numRows)

        

    def delete_row(self, canvasRow):
        """
        Deals with requests to delete a specific row.
        """

        row = self.convert_canvas_row_to_internal(canvasRow)

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternCanvasItem):
                if graphicsItem.row == row:
                    self.removeItem(graphicsItem)
                elif graphicsItem.row > row:
                    shift_items_row_wise(graphicsItem, -1, self.__unitHeight)

        self.__numRows -= 1
        self.__activeItems = []
        self.set_up_labels()
        self.row_col_count_changed.emit("numRows", self.__numRows)


    
    def insert_column(self, num, mode, columnPivot):
        """
        Deals with requests to insert a column.
        """

        pivot = self.convert_canvas_column_to_internal(columnPivot)
        assert(pivot >= 0 and pivot < self.__numColumns)

        if mode == QString("left of"):
            cmpOp = operator.__ge__
            shift = 0
        else:
            cmpOp = operator.__gt__
            shift = 1

        # in order for inserting of a column at left or right of a
        # pivot to work each row has to have a cell that starts at
        # this pivot or right of it.
        rowCounter = 0
        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternCanvasItem):
                if graphicsItem.column == (pivot + shift):
                    rowCounter += 1

        if rowCounter != self.__numRows:
            print("Error: Can not insert column(s) due to layout")
            return

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternCanvasItem):
                if cmpOp(graphicsItem.column, pivot):
                    shift_items_column_wise(graphicsItem, num, self.__unitWidth)

        for column in range(0, num):
            self.__create_column(pivot + shift + column)

        self.__numColumns += num
        self.set_up_labels()
        self.row_col_count_changed.emit("numColumns", self.__numColumns)          

        

    def delete_column(self, deadColumn):
        """
        Deals with requests to delete a specific column.
        """

        column = self.convert_canvas_column_to_internal(deadColumn)

        # in order for deleting of a column at deadColumn to succeed
        # there has to be a unit element at that column
        rowCounter = 0
        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternCanvasItem):
                if (graphicsItem.column == column) and \
                   (graphicsItem.width == 1):
                    rowCounter += 1

        if rowCounter != self.__numRows:
            print("Error: Can not delete column due to layout")
            return

        for graphicsItem in self.items():
            if isinstance(graphicsItem, PatternCanvasItem):
                if graphicsItem.column == column:
                    self.removeItem(graphicsItem)
                elif graphicsItem.column > column:
                    shift_items_column_wise(graphicsItem, -1, self.__unitWidth)

        self.__numColumns -= 1
        self.__activeItems = []
        self.set_up_labels()
        self.row_col_count_changed.emit("numColumns", self.__numColumns)          



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
            self.create_item(location, self.__unitCellDim, column, rowID, 1)



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
            self.create_item(location, self.__unitCellDim, columnID, row, 1)





#########################################################
## 
## class for managing a single pattern grid item
## (svg image, frame, background color)
##
#########################################################
class PatternCanvasItem(QGraphicsSvgItem):

    Type = 70000 + 1

    # signal for notifying if active widget changes
    cell_selected   = pyqtSignal("PyQt_PyObject")
    cell_unselected = pyqtSignal("PyQt_PyObject") 


    def __init__(self, origin, size, col, row, width,
                 parent = None, scene = None):

        super(QGraphicsSvgItem, self).__init__()

        self.origin  = origin
        self.size    = size
        self.row     = row
        self.column  = col
        self.width   = width
        self.height  = 1

        # we start off with an empty symbol
        self.symbol  = { "svgName" : "", "category" : "", "name" : "", \
                         "description" : "", "width" : "", \
                         "backgroundColor" : "" }
        
        self.__pen = QPen()
        self.__pen.setWidthF(1.0)
        self.__pen.setColor(Qt.black)

        self.__selected  = False
        self.__backColor = Qt.white
        self.__highlightedColor = Qt.gray
        self.color     = self.__backColor



    def mousePressEvent(self, event):
        """
        Handle user press events on the item.
        """

        if not self.__selected:
            self.__select()
            self.cell_selected.emit(self)
        else:
            self.__unselect()
            self.cell_unselected.emit(self)



    def __unselect(self):
        """
        Unselects a given selected cell. 
        """

        self.__selected = False
        self.color = self.__backColor
        self.update()



    def __select(self):
        """
        Selects a given unselected cell. 
        """

        self.__selected = True
        self.color = self.__highlightedColor
        self.update()


            
    def set_symbol(self, newSymbol):
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
        else:
            self.__backColor = Qt.white

        self.__unselect()



    def boundingRect(self):
        """
        Return the bounding rectangle of the item.
        """

        return QRectF(self.origin, self.size)
        


    def paint(self, painter, option, widget):
        """
        Paint ourselves.
        """

        painter.setPen(self.__pen)
        brush = QBrush(self.color)
        painter.setBrush(brush)
        painter.drawRect(QRectF(self.origin, self.size))
        self.renderer().render(painter, QRectF(self.origin, self.size))




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
    item.origin = QPointF(item.origin.x(), item.origin.y() + yShift)



def shift_items_column_wise(item, num, unitCellWidth):
    """
    Shifts the given item by num columns given unitCellWidth.
    """
    
    xShift = num * unitCellWidth
    item.prepareGeometryChange()
    item.column += num
    item.origin = QPointF(item.origin.x() + xShift, item.origin.y())
