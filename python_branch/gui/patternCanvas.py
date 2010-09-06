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
                         pyqtSignal, QObject
from PyQt4.QtGui import QGraphicsScene, QGraphicsItem, QPen, QColor, \
                        QBrush
from PyQt4.QtSvg import QSvgWidget
import sconchoHelpers.settings as settings


#########################################################
## 
## class for managing the actual pattern canvas
##
#########################################################
class PatternCanvas(QGraphicsScene):

    def __init__(self, settings, parent = None):

        QGraphicsScene.__init__(self, parent)

        self.__settings = settings
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
                foo = PatternCanvasItem(location, unitCellDim)
                self.addItem(foo)




#########################################################
## 
## class for managing a single pattern grid item
## (svg image, frame, background color)
##
#########################################################
class PatternCanvasItem(QGraphicsItem):

    # signal for notifying if active widget changes
    item_selected = pyqtSignal("PyQt_PyObject")


    def __init__(self, origin, size, parent = None, scene = None):

        QGraphicsItem.__init__(self, parent)
        QObject.__init__(self, parent)

        self.__pen = QPen()
        self.__pen.setWidthF(1.0)
        self.__pen.setColor(Qt.black)

        self.__selected  = False
        self.__backColor = Qt.white
        self.__highlightedColor = Qt.gray
        self.__color     = self.__backColor
        
        self.__svgItem = None
        self.__origin  = origin
        self.__size    = size


    def mousePressEvent(self, event):
        """
        Handle user press events on the item.
        """

        if not self.__selected:
            self.__selected = True
            #self.item_selected.emit(self)
            self.__color = self.__highlightedColor
        else:
            self.__selected = False
            self.__color = self.__backColor

        self.update()



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











