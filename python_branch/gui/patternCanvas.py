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


from PyQt4.QtCore import Qt, QRectF
from PyQt4.QtGui import QGraphicsScene, QGraphicsItem, QPen, QColor
from PyQt4.QtSvg import QSvgWidget



#########################################################
## 
## class for managing the actual pattern canvas
##
#########################################################
class PatternCanvas(QGraphicsScene):

    def __init__(self, parent = None):

        QGraphicsScene.__init__(self, parent)

        self.set_up_main_grid()



    def set_up_main_grid(self):
        """
        This function draws the main grid.
        """

        foo = PatternCanvasItem(10, 10)
        self.addItem(foo)




#########################################################
## 
## class for managing a single pattern grid item
## (svg image, frame, background color)
##
#########################################################
class PatternCanvasItem(QGraphicsItem):

    def __init__(self, width, height, parent = None, scene = None):

        QGraphicsItem.__init__(self, parent, scene)

        self.__pen = QPen()
        self.__pen.setWidthF(1.0);
        self.__pen.setColor(Qt.black)

        self.__svgItem = None

#        self.


    def boundingRect(self):

        return QRectF(0,0,10,10)
        

    def paint(self, painter, option, widget):

        painter.setPen(self.__pen)
        painter.drawRect(0, 0, 30, 30)











