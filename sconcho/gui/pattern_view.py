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
from PyQt4.QtCore import (Qt, QRect, QSize, QPointF, QSizeF,
                          QRectF) 
from PyQt4.QtGui import (QGraphicsView, QRubberBand, QPainter)

from sconcho.util.canvas import visible_bounding_rect


#########################################################
## 
## class for managing the actual pattern canvas
##
#########################################################
class PatternView(QGraphicsView):


    def __init__(self, parent = None):

        super(PatternView, self).__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        # initialize the rubberBand
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.rubberBand.hide()
        self.rubberBandOrigin = None



    def mousePressEvent(self, event):
        """ Handles mouse press events.

        We override this function to check if the user requested
        a rubberBand selection.
        NOTE: We only propagate the event if no rubberBand was selected
        to avoid selection of the pattern grid item where the click
        occured.
        """

        if event.modifiers() & Qt.ShiftModifier:
            self.rubberBandOrigin = event.pos()
            self.rubberBand.setGeometry(QRect(self.rubberBandOrigin, 
                                              QSize()))
            self.rubberBand.show()
        
        return QGraphicsView.mousePressEvent(self, event)



    def mouseMoveEvent(self, event):
        """ Handle mouse move events.

        If a rubberBand is active we adjust the size otherwise
        we just hand off the signal.
        """

        if self.rubberBandOrigin:
            self.rubberBand.setGeometry(QRect(self.rubberBandOrigin,
                                              event.pos()).normalized())

        return QGraphicsView.mouseMoveEvent(self, event)
        


    def mouseReleaseEvent(self, event):
        """ Handle mouse release events.

        If a rubberBand is active we tell our GraphicsScene what are
        was selected and then disable the rubberBand.
        """
        
        if self.rubberBandOrigin:
            self.scene().select_region((self.mapToScene(
                self.rubberBand.geometry())))
            self.rubberBandOrigin = None
            self.rubberBand.hide()
        
        return QGraphicsView.mouseReleaseEvent(self, event)


    
    def wheelEvent(self, event):
        """ Mouse wheel events cause zooming in and out. """

        if event.modifiers() & Qt.ControlModifier:
            if event.delta() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            QGraphicsView.wheelEvent(self, event)



    def zoom_in(self):
        """ Zoom in by 10% """

        self.scale(1.1, 1.1)



    def zoom_out(self):
        """ Zoom out by 10% """

        self.scale(0.9, 0.9)



    def fit_scene(self):
        """ Fit scene into canvas. """
        
        margin = 50.0
        rawBoundary = visible_bounding_rect(self.scene().items())
        rawBoundary.adjust(-margin, -margin, margin, margin)
        self.fitInView(rawBoundary, Qt.KeepAspectRatio)



    def normal_view(self):
        """ Resets scene to normal (initial) view. """

        self.resetMatrix()
