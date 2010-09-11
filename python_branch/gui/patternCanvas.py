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



def paint_cells(symbol, allCells):
    """
    Given a collection of cells tries to place symbols
    in them. Need to check if we have the proper total
    number of cells and also if we have the proper number
    of neighboring tuples.
    """

    if symbol:
        for cell in allCells:
            cell.set_symbol(symbol)
        allCells.clear()


#########################################################
## 
## class for managing the actual pattern canvas
##
#########################################################
class PatternCanvas(QGraphicsScene):

    def __init__(self, settings, parent = None):

        super(PatternCanvas,self).__init__()

        self.__settings = settings
        self.__activeSymbol = None
        self.__selectedCells = set()
        self.set_up_main_grid()



    def set_up_main_grid(self):
        """
        This function draws the main grid.
        """

        unitCellDim = QSizeF(settings.get_grid_dimensions(self.__settings))
        width  = unitCellDim.width()
        height = unitCellDim.height()

        for row in range(0,10):
            for column in range(0,10):
                location = QPointF(row * width, column * height)
                item = PatternCanvasItem(location, unitCellDim, row, column)
                self.connect(item, SIGNAL("cell_selected(PyQt_PyObject)"),
                             self.grid_cell_activated)
                self.addItem(item)



    def set_active_symbol(self, activeKnittingSymbol):
        """
        This function receives the currently active symbol
        and stores it.
        """

        if activeKnittingSymbol:
            print("symbol changed --> " + activeKnittingSymbol["name"])
            
        self.__activeSymbol = activeKnittingSymbol
        paint_cells(self.__activeSymbol, self.__selectedCells)



    def grid_cell_activated(self, item):

        self.__selectedCells.add(item)
        paint_cells(self.__activeSymbol, self.__selectedCells)




#########################################################
## 
## class for managing a single pattern grid item
## (svg image, frame, background color)
##
#########################################################
class PatternCanvasItem(QGraphicsObject):

    # signal for notifying if active widget changes
    cell_selected = pyqtSignal("PyQt_PyObject")


    def __init__(self, origin, size, row, col,
                 parent = None, scene = None):

        super(PatternCanvasItem, self).__init__() 

        self.__origin  = origin
        self.__size    = size
        self.__row     = row
        self.__col     = col
        
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
            self.select()
        else:
            self.unselect()



    def unselect(self):
        """
        Unselects a given selected cell. 
        """

        self.__selected = False
        self.__color = self.__backColor
        self.update()



    def select(self):
        """
        Selects a given unselected cell. 
        """

        self.__selected = True
        self.__color = self.__highlightedColor
        self.update()

        self.cell_selected.emit(self)


            
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

        self.unselect()



    def boundingRect(self):
        """
        Return the bounding rectangle of the item.
        """
        
        return QRectF(self.__origin, self.__size)
        


    def paint(self, painter, option, widget):
        """
        Paint ourselves.
        """

        painter.setPen(self.__pen)
        brush = QBrush(self.__color)
        painter.setBrush(brush)
        painter.drawRect(QRectF(self.__origin, self.__size))











