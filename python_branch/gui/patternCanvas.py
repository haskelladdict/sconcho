# -*- coding: utf-8 -*-
########################################################################
#
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


from PyQt4.QtCore import Qt, QRectF, QSize, QPointF, QSizeF, \
                         pyqtSignal, SIGNAL, QObject
from PyQt4.QtGui import QGraphicsScene, QGraphicsObject, QPen, QColor, \
                        QBrush
from PyQt4.QtSvg import QGraphicsSvgItem
from PyQt4.QtSvg import QSvgWidget
import sconchoHelpers.settings as settings



def verify_cell_arrangement(width, allCells):
    """
    Given a collection of cells verifies that we can place
    the symbol. Need to check if we have the proper total
    number of cells and also if we have the proper number
    of neighboring tuples.
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

    # separate each row into chunks at least as long as
    # the items we want to place. Then we check if each
    # chunk is consecutive
    chunkList = []
    for row in cellsByRow.values():
        row.sort(lambda x, y: cmp(x.col, y.col))
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

        consecutiveCol = chunk[0].col + chunk[0].width
        for cell in chunk[1:]:
            if cell.col != consecutiveCol:
                return False
            
            consecutiveCol = cell.col + cell.width
            
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



#########################################################
## 
## class for managing the actual pattern canvas
##
#########################################################
class PatternCanvas(QGraphicsScene):

    def __init__(self, theSettings, parent = None):

        super(PatternCanvas,self).__init__()

        self.__activeSymbol = None
        self.__selectedCells = set()

        self.__unitCellDim = QSizeF(settings.get_grid_dimensions(theSettings))
        self.__unitWidth   = self.__unitCellDim.width()
        self.__unitHeight  = self.__unitCellDim.height()

        self.set_up_main_grid()



    def set_up_main_grid(self):
        """
        This function draws the main grid.
        """

        for row in range(0,10):
            for column in range(0,10):
                location = QPointF(column * self.__unitWidth,
                                   row * self.__unitHeight)
                self.create_item(location, self.__unitCellDim,
                                 row, column, 1)



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
        to the collectoin of selected cells and try to paint
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



    def create_item(self, origin, dim, row, col, width):
        """
        Creates a new PatternGridItem of the specified dimension
        at the given location.
        """

        item = PatternCanvasItem(origin, dim, row, col, width)
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
            chunks = verify_cell_arrangement(width, self.__selectedCells)
            dim = QSizeF(self.__unitWidth * width, self.__unitHeight)
            
            if chunks:
                for chunk in chunks:
                    totalWidth = 0
                    origin = chunk[0].origin
                    row    = chunk[0].row
                    col    = chunk[0].col
                    for item in chunk:
                        totalWidth += item.width
                        self.removeItem(item)

                    print(totalWidth, width, len(chunk))
                    assert(totalWidth % width == 0)
                    numNewItems = totalWidth/width
                    for i in range(0,numNewItems):
                        item = self.create_item(origin, dim, row, col, width)
                        item.set_symbol(self.__activeSymbol)
                        origin = QPointF(origin.x() + (width * self.__unitWidth),
                                         origin.y())
                        col    = col + width
                        

                self.__selectedCells.clear()




#########################################################
## 
## class for managing a single pattern grid item
## (svg image, frame, background color)
##
#########################################################
class PatternCanvasItem(QGraphicsObject):

    # signal for notifying if active widget changes
    cell_selected   = pyqtSignal("PyQt_PyObject")
    cell_unselected = pyqtSignal("PyQt_PyObject") 


    def __init__(self, origin, size, row, col, width,
                 parent = None, scene = None):

        super(PatternCanvasItem, self).__init__() 

        self.origin = origin
        self.size   = size
        self.row    = row
        self.col    = col
        self.width  = width
        
        self.__pen = QPen()
        self.__pen.setWidthF(1.0)
        self.__pen.setColor(Qt.black)

        self.__selected  = False
        self.__backColor = Qt.white
        self.__highlightedColor = Qt.gray
        self.__color     = self.__backColor
        
        self.__svgItem = None



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
        self.__color = self.__backColor
        self.update()



    def __select(self):
        """
        Selects a given unselected cell. 
        """

        self.__selected = True
        self.__color = self.__highlightedColor
        self.update()


            
    def set_symbol(self, newSymbol):
        """
        Adds a new svg image of a knitting symbol to the
        scene.
        """

        # make sure we remove the previous svgItem
        if self.__svgItem:
            self.__svgItem.scene().removeItem(self.__svgItem)

        svgPath = newSymbol["svgPath"]
        self.__svgItem = QGraphicsSvgItem(svgPath, self)

        # apply color if present
        if "backgroundColor" in newSymbol:
            self.__backColor = QColor(newSymbol["backgroundColor"])
        else:
            self.__backColor = Qt.white

        # move svg item into correct position
        itemBound = self.boundingRect()
        svgBound  = self.__svgItem.boundingRect()
        widthScale = float(itemBound.width())/svgBound.width()
        heightScale = float(itemBound.height())/svgBound.height()
        
        self.__svgItem.scale(widthScale, heightScale)
        self.__svgItem.setPos(itemBound.x(), itemBound.y())

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
        brush = QBrush(self.__color)
        painter.setBrush(brush)
        painter.drawRect(QRectF(self.origin, self.size))











