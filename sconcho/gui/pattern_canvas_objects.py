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

import logging
import uuid

from PyQt4.QtCore import (Qt,
                          QRectF,
                          QPointF,
                          QSizeF,
                          QLineF,
                          SIGNAL,
                          QT_VERSION)
from PyQt4.QtGui import (QPen,
                         QColor,
                         QBrush,
                         QGraphicsTextItem,
                         QGraphicsItem,
                         QGraphicsRectItem,
                         QGraphicsLineItem,
                         QGraphicsItemGroup,
                         QApplication,
                         QTextCursor,
                         QCursor)
from PyQt4.QtSvg import (QGraphicsSvgItem)


# determine if we can to caching of items
# it seems screwed up for older QT versions
# and Windows XP seems to choke as well so
# we turn it off
from platform import system
if QT_VERSION < 0x040703 or system() == 'Windows':
    NO_ITEM_CACHING = True
else:
    NO_ITEM_CACHING = False


from sconcho.util.canvas import *
import sconcho.util.messages as msg

# module lever logger:
logger = logging.getLogger(__name__)


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

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if NO_ITEM_CACHING:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

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
        self._highlightBrush = QBrush(QColor(Qt.lightGray), Qt.SolidPattern)

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
            logger.error(errorMessage)
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
        scaledRect = \
            QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
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

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if NO_ITEM_CACHING:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

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

        self.setAcceptsHoverEvents(True)
        self._outline = None



    def hoverEnterEvent(self, event):
        """ Stuff related to hover enter events.

        For now we just show a rectangular outline.

        """

        if not self._outline:
            self._outline = QGraphicsRectItem(\
                self.boundingRect().adjusted(-1,-1,1,1), self)
            highlightColor = QColor(Qt.blue)
            highlightColor.setAlpha(30)
            self._outline.setBrush(highlightColor)
            highlightPen = QPen(Qt.blue)
            highlightPen.setWidth(2)
            self._outline.setPen(highlightPen)
        else:
            self._outline.show()



    def hoverLeaveEvent(self, event):
        """ Stuff related to hover leave events.

        For now we just show a rectangular outline.

        """

        self._outline.hide()



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
            logger.error(errorMessage)
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
        painter.drawRect(\
            QRectF(self.origin, self.size).adjusted(halfPen, halfPen,
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

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if NO_ITEM_CACHING:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)

        self._position = self.pos()
        self._outline = None


    def hoverEnterEvent(self, event):
        """ Stuff related to hover enter events.

        For now we just show a rectangular outline.

        """

        if not self._outline:
            self._outline = QGraphicsRectItem(self.boundingRect(), self)
            highlightColor = QColor(Qt.blue)
            highlightColor.setAlpha(30)
            self._outline.setBrush(highlightColor)
            highlightPen = QPen(Qt.blue)
            highlightPen.setWidth(2)
            self._outline.setPen(highlightPen)
        else:
            self._outline.show()



    def hoverLeaveEvent(self, event):
        """ Stuff related to hover leave events.

        For now we just show a rectangular outline.

        """

        self._outline.hide()



    def keyPressEvent(self, event):
        """ Stuff to do during key press events.

        For now we have to adjust the outline box.

        """

        QGraphicsTextItem.keyPressEvent(self, event)
        self.adjust_size()



    def adjust_size(self):
        """ This function takes care of changing the size of the

        outline rectangle, e.g., when text is added or removed or
        during font size changes.

        """

        if self._outline:
            self._outline.setRect(self.boundingRect())



    def mousePressEvent(self, event):
        """ We reimplement this function to store the position of
        the item when a user issues a mouse press.

        """

        self._position = self.pos()

        if (event.modifiers() & Qt.ControlModifier):
            QApplication.setOverrideCursor(QCursor(Qt.SizeAllCursor))
            self.setTextInteractionFlags(Qt.NoTextInteraction)

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


    def __init__(self, text, isRowLabel = True, parent = None):

        super(PatternLabelItem, self).__init__(text, parent)

        self.isRowLabel = isRowLabel

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if NO_ITEM_CACHING:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)



    @property
    def is_rowLabel(self):
        """ Return True if we are a row label and False otherwise """

        return self.isRowLabel



#########################################################
##
## class for managing a pattern repeat item
##
#########################################################
class PatternRepeatItem(QGraphicsItemGroup):

    Type = 70000 + 5

    def __init__(self, lines,  width = None, color = None,
                 hasLegend = True, parent = None):

        super(PatternRepeatItem, self).__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setZValue(1)

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if NO_ITEM_CACHING:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # we keep track of some of our legends properties
        self.hasLegend = hasLegend

        # we use this ID for tracking our legend entry
        self.itemID = uuid.uuid4()

        # set up group
        self.lineElements = []
        points = []
        for line in lines:
            points.append(line.p1())
            points.append(line.p2())
            lineElement = QGraphicsLineItem(line)
            self.lineElements.append(lineElement)
            self.addToGroup(lineElement)

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
        """ Revert hightlighting of cells and go back to normal brush.

        """

        self.paint_elements(Qt.NoBrush)



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



    @property
    def canvas_pos(self):
        """ Returns the item's canvas position. """

        return QPointF(self.boundingRect().x() + self.scenePos().x(),
                       self.boundingRect().y() + self.scenePos().y())



    def _snap_to_grid(self):
        """ Snap to nearest grid point.

        NOTE: For some reason QGraphicsItemGroup's scenePos()
        does not seem to return the scene coordinate but rather
        the item coordinates. Thus, we have to compute the canvas
        coordinate by means of initially computing the uper left
        corner of the group.

        TODO: Currently we only use the left and top edge for this. A
        more sophisticated algorithm would probably also use the right and
        bottom edget.

        """

        numRows = self.scene()._numRows
        numCols = self.scene()._numColumns
        cellXDim = self.scene()._unitCellDim.width()
        cellYDim = self.scene()._unitCellDim.height()

        curX = self.canvas_pos.x()
        curY = self.canvas_pos.y()
        withinGrid = (curX > -(0.5*cellXDim) \
                      and curX < (numCols+0.5)*cellXDim \
                      and curY > -(0.5*cellYDim) \
                      and curY < (numRows+0.5)*cellYDim)

        if withinGrid:
            # snap in X
            if curX % cellXDim < 0.5*cellXDim:
                self.moveBy(-(curX % cellXDim), 0)
            else:
                self.moveBy(cellXDim - curX % cellXDim, 0)

            # snap in Y
            if curY % cellYDim < 0.5*cellYDim:
                self.moveBy(0, -(curY % cellYDim))
            else:
                self.moveBy(0, cellYDim - curY % cellYDim)



    def mouseReleaseEvent(self, event):
        """ Deal with mouse release events after a previous
        mousePressEvent. Mostly, we just have to revert
        the cursor back.

        """

        if self.scene().settings.snapPatternRepeatToGrid.value == Qt.Checked:
            self._snap_to_grid()

        if self._position != self.pos():
            self.scene().canvas_item_position_changed(self, self._position,
                                                      self.pos())

        QApplication.restoreOverrideCursor()
        return QGraphicsItemGroup.mouseReleaseEvent(self, event)





#########################################################
##
## class for highling every other row on grid if requested
## by a user
##
#########################################################
class PatternHighlightItem(QGraphicsRectItem):

    Type = 70000 + 6


    def __init__(self, x, y, width, height, color, alpha,
                 parent = None):

        super(PatternHighlightItem, self).__init__(x, y, width, height,
                                                   parent)

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if NO_ITEM_CACHING:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # we don't want to show the outline so draw it
        # in white
        self._pen = QPen(Qt.NoPen)
        self.setPen(self._pen)

        color.setAlphaF(alpha)
        self._brush = QBrush(color)
        self.setBrush(self._brush)




#########################################################
##
## class for managing the legend item corresponding
## to pattern repeat
##
#########################################################
class RepeatLegendItem(QGraphicsRectItem):

    Type = 70000 + 7


    def __init__(self, color, parent = None):

        super(RepeatLegendItem, self).__init__(parent)

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if NO_ITEM_CACHING:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self._position = self.pos()

        self.penColor = color
        self.itemHeight = 20
        self.itemWidth = 40

        self._pen = QPen()
        self._pen.setWidthF(3.0)
        self._pen.setColor(self.penColor)
        self.setPen(self._pen)

        self.setRect(0, 0, self.itemWidth, self.itemHeight)

        self.setAcceptsHoverEvents(True)
        self._outline = None


    @property
    def height(self):
        return self.itemHeight


    @property
    def width(self):
        return self.itemWidth



    @property
    def color(self):
        return self.penColor



    @color.setter
    def color(self, newColor):

        self.penColor = newColor
        self._pen.setColor(self.penColor)
        self.setPen(self._pen)



    def hoverEnterEvent(self, event):
        """ Stuff related to hover enter events.

        For now we just show a rectangular outline.

        """

        if not self._outline:
            self._outline = QGraphicsRectItem(\
                self.boundingRect().adjusted(-1,-1,1,1), self)
            highlightColor = QColor(Qt.blue)
            highlightColor.setAlpha(30)
            self._outline.setBrush(highlightColor)
            highlightPen = QPen(Qt.blue)
            highlightPen.setWidth(2)
            self._outline.setPen(highlightPen)
        else:
            self._outline.show()



    def hoverLeaveEvent(self, event):
        """ Stuff related to hover leave events.

        For now we just show a rectangular outline.

        """

        self._outline.hide()



    def mousePressEvent(self, event):
        """ We reimplement this function to store the position of
        the item when a user issues a mouse press.

        """

        self._position = self.pos()

        if (event.modifiers() & Qt.ControlModifier):
            QApplication.setOverrideCursor(QCursor(Qt.SizeAllCursor))
        else:
            event.ignore()

        return QGraphicsRectItem.mousePressEvent(self, event)



    def mouseReleaseEvent(self, event):
        """ We reimplement this function to check if its position
        has changed since the last mouse click. If yes we
        let the canvas know so it can store the action as
        a Redo/Undo event.

        """

        QApplication.restoreOverrideCursor()

        # this is needed for undo/redo
        if self._position != self.pos():
           self.scene().canvas_item_position_changed(self, self._position,
                                                     self.pos())

        return QGraphicsRectItem.mouseReleaseEvent(self, event)




#########################################################
##
## class for managing a text label on the canvas
##
#########################################################
class PatternTextItem(PatternLegendText):
    """ NOTE: This is just a very thin wrapper around PatternLegendText
    that has its own type.

    """

    Type = 70000 + 8

    def __init__(self, text, parent = None):

        super(PatternTextItem, self).__init__(text, parent)

        # NOTE: need this distinction for cache mode based on
        # the Qt version otherwise rendering is broken
        if NO_ITEM_CACHING:
            self.setCacheMode(QGraphicsItem.NoCache)
        else:
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)



######################################################################
#
# context manager taking care of hiding nostitch symbols and
# underlying PatternHighlightItems if present
#
######################################################################
class NostitchVisualizer(object):

    def __init__(self, canvas, active):
        """ Toggles the visibility of all nostitch symbols to on
        or off via show() and hide().

        WARNING: This should only be done temporary while no user
        interaction with the canvas is possible, e.g. during
        exporting. Otherwise it will screw up the undo/redo framwork
        completely.

        """

        self.isPatternVisible = canvas.isVisible
        self.isActive = active
        if self.isActive:
            self.highlightItems = []
            self.nostitchItems = []
            for item in canvas.items():
                if isinstance(item, PatternGridItem):
                    if item.name == "nostitch":
                        self.nostitchItems.append(item)

                        highlightItem = \
                            canvas._item_at_row_col(item.row,
                                                    item.column,
                                                    PatternHighlightItem)
                        if highlightItem:
                            self.highlightItems.append(highlightItem)

            if self.nostitchItems:
                legendID = generate_legend_id(self.nostitchItems[0].symbol,
                                              self.nostitchItems[0].color)
                (_, self.item, self.textItem) = canvas.gridLegend[legendID]



    def __enter__(self):
        """ Entry method of NostitchVisualizer context manager. """

        if self.isActive:
             for item in self.nostitchItems:
                item.hide()

             for item in self.highlightItems:
                 item.hide()

             if self.nostitchItems:
                 self.item.hide()
                 self.textItem.hide()

        return self



    def __exit__(self, exc_class, exc_instance, traceback):
        """ Exit method of NostitchVisualizer context manager. """

        # only show no-stitches if pattern grid is visible
        if self.isActive and self.isPatternVisible:
             for item in self.nostitchItems:
                 item.show()

             for item in self.highlightItems:
                 item.show()

        if self.isActive:
             if self.nostitchItems:
                 self.item.show()
                 self.textItem.show()




####################################################################
#
# helper class for creating the proper row labels
#
####################################################################
class RowLabelTracker(object):

    def __init__(self, canvas):

        self.settings = canvas.settings
        self.canvas = canvas
        self.rangeMap = canvas.rowRepeatTracker



    def get_basic_parameters(self):
        """ set up the basic parameters based on the current
        settings.

        """

        labelIntervalState = self.settings.rowLabelMode.value
        labelOffset = self.settings.rowLabelStart.value - 1

        labelInterval = 1
        labelStart = 1
        rowShift = 1

        withInterval = (labelIntervalState == "SHOW_ROWS_WITH_INTERVAL")

        counter_func = lambda x: (x + labelOffset)
        if withInterval:
            labelInterval = self.settings.rowLabelsShowInterval.value
            labelStart = self.settings.rowLabelsShowIntervalStart.value
        elif labelIntervalState == "SHOW_EVEN_ROWS" \
             or labelIntervalState == "SHOW_ODD_ROWS":
            counter_func = lambda x: 2*x - 1 + labelOffset
            rowShift = 2

        return (counter_func, labelInterval, labelStart, rowShift,
                withInterval)



    def get_labels(self):
        """ Main routine computing the current set of labels. """

        (counter_func, labelInterval, labelStart, rowShift, withInterval) =\
            self.get_basic_parameters()

        labels = []
        numRows = self.canvas._numRows
        if withInterval:
            for row in range(1, numRows + 1):
                rowEntry = counter_func(row)
                if (rowEntry - labelStart) % labelInterval == 0 \
                and rowEntry >= labelStart:
                    labels.append([rowEntry])
                else:
                    labels.append(None)

        else:
            # running label shift due to preceding row repeats and ID
            # of current repeat
            nextCount = 0
            prevID = 0

            # label shift due to preceding row repeats
            repeatShift = 0

            for row in range(1, numRows+1):
                rowEntry = counter_func(row)
                realRow = numRows - row

                # check if the current row is part of a repeat.
                # if yes figure out the labels
                # NOTE: This is pretty messy right now - there
                # should be a better way
                if realRow in self.rangeMap:
                    (rowRange, mult, repeatID) = self.rangeMap[realRow]
                    if repeatID != prevID:
                        repeatShift = nextCount
                        prevID = repeatID
                    length = len(rowRange)
                    rowLabel = []
                    for i in range(0, mult):
                        rowLabel.append(rowEntry + repeatShift
                                        + i * length * rowShift)
                    nextCount += (mult - 1) * rowShift
                    labels.append(rowLabel)
                else:
                    repeatShift = nextCount
                    labels.append([rowEntry + repeatShift])

        return labels




####################################################################
#
# helper class for creating the proper column labels
#
####################################################################
class ColumnLabelTracker(object):

    def __init__(self, canvas):

        self.settings = canvas.settings
        self.canvas = canvas



    def get_basic_parameters(self):
        """ set up the basic parameters based on the current settings. """

        labelIntervalState = self.settings.columnLabelMode.value

        labelInterval = 1
        labelOffset = 0
        labelStart = 1

        withInterval = (labelIntervalState == "SHOW_COLUMNS_WITH_INTERVAL")

        counter_func = lambda x: (x + labelOffset)
        if withInterval:
            labelInterval = self.settings.columnLabelsShowInterval.value
            labelStart = self.settings.columnLabelsShowIntervalStart.value

        return (counter_func, labelInterval, labelStart, withInterval)



    def get_labels(self):
        """ Main routine computing the current set of column labels. """

        (counter_func, labelInterval, labelStart, withInterval) =\
            self.get_basic_parameters()

        labels = []
        numColumns = self.canvas._numColumns
        if withInterval:
            for column in range(1, numColumns + 1):
                columnEntry = counter_func(column)
                if (columnEntry - labelStart) % labelInterval == 0 \
                and columnEntry >= labelStart:
                    labels.append(columnEntry)
                else:
                    labels.append(None)

        else:
            labels = range(1, numColumns + 1)

        return labels



###################################################################
#
# this class tracks all row repeats on the canvas
#
###################################################################
class RowRepeatTracker(object):

    def __init__(self, repeats = []):
        """ NOTE: A row repeat is stored as a triple

        (repeatRange, multiplicity, ID)

        where:   repeatRange  = range of rows in this repeat
                                (as a internal canvas row count)
                 multiplicity = number of repeats
                 ID           = unique per repeat ID

        """

        self.repeats = repeats

        # counter for iterator
        self.current = 0



    def __iter__(self):

        self.current = 0
        return self



    def __next__(self):
        """ python3 iterator version of next. """

        return self.next()



    def next(self):
        """ Simple next function to allow iteration over content. """

        if self.current == len(self.repeats):
            raise StopIteration
        else:
            iterValue = self.repeats[self.current]
            self.current += 1
            return iterValue



    def __len__(self):
        """ Length of tracker is given by the number of repeats. """

        return len(self.repeats)



    def __getitem__(self, row):
        """ Return the repeat length and number or repeats of the repeat
        row belongs to.

        """

        for (theRange, mult, repeatID) in self.repeats:
            if row in theRange:
                return (theRange, mult, repeatID)



    def __contains__(self, row):
        """ Checks is row is within one of the ranges. """

        if not self.repeats:
            return False

        status = False
        for (theRange, mult, repeatID) in self.repeats:
            if row in theRange:
                status = True
                break

        return status



    def add_repeat(self, rows, numRepeats):
        """ Add a new row repeat. """

        if not rows:
            return

        rows.sort()
        repeatRange = range(rows[0], rows[-1]+1)
        repeatID = uuid.uuid4()
        self.repeats.append((repeatRange, numRepeats, repeatID))



    def restore_repeat(self, restoreInfo):
        """ This function restores a given row repeat to a previous
        state.

        restoreInfo is a triple with the currentRange as well
        as the previousRange (to be reestablished) and multiplicity.
        The multiplicity is needed since it is possible that we
        are restoring a repeat that had been completely removed
        and for which we've thus lost all multiplicity info.

        """

        for item in restoreInfo:
            (deadRange, newRange, mult) = item
            if deadRange:
                self.delete_repeat(deadRange)
            self.add_repeat(newRange, mult)



    def change_repeat(self, startRow, numRows):
        """ This function is used to change row repeats.

        Currently, the only user of this function is the undo
        framework when deleting a block of rows of length numRows
        starting at startRow.

        The function detects any row repeats that are affected
        by the deleting rows and removes them from the range.
        It returns a triple of (newRange, oldRange, multiplicity).
        This information is then used by restore_repeat to restore
        the previous state.

        """

        changedRepeats = []
        removeRange = set(range(startRow, startRow + numRows))
        repeats = list(self.repeats)
        for index in range(len(repeats)):
            (theRange, mult, repeatID) = repeats[index]
            originalRange = set(theRange)

            if originalRange.intersection(removeRange):
                newRange = list(originalRange.difference(removeRange))
                newRange.sort()
                if newRange:
                    self.repeats[index] = (newRange, mult, repeatID)
                else:
                    del self.repeats[index]
                changedRepeats.append((newRange, theRange, mult))

        return changedRepeats



    def delete_repeat(self, rows):
        """ Delete the repeat corresponding to the given rows.

        NOTE: We assume that the rows passed in are all within
        a single pattern repeat.

        """

        if not rows:
            return

        firstRow = rows[0]
        for index in range(len(self.repeats)):
            theRange = self.repeats[index][0]
            if firstRow in theRange:
                self.repeats.pop(index)
                return



    def rows_are_in_any_repeat(self, rows):
        """ Check if the given rows are within any of the
        currently existing row repeats.

        """

        for row in rows:
            for (theRange, mult, repeatID) in self.repeats:
                if row in theRange:
                    return True

        return False



    def rows_are_in_a_single_repeat(self, deadRows):
        """ Check if all rows within dead rows are part
        of a single repeat. """

        matches = {}
        for row in deadRows:
            rowInRepeat = False
            for (i, (theRange, mult, repeatID)) in enumerate(self.repeats):
                if (row in theRange):
                    matches[i] = True
                    rowInRepeat = True

            if not rowInRepeat:
                return False

        return len(matches) == 1



    def shift_and_expand_repeats(self, pivot, rowShift):
        """ Shift and expand row repeats after inserting of canvas
        rows.

        """

        for index in range(len(self.repeats)):
            (theRange, mult, repeatID) = self.repeats[index]

            # extend the range by row shift
            if pivot in theRange[1:]:
                newRange = range(theRange[0], theRange[-1]+rowShift+1)
            # just shift
            elif pivot <= min(theRange):
                newRange = range(theRange[0]+rowShift,
                                 theRange[-1]+rowShift+1)
            # don't do anything
            else:
                newRange = theRange

            self.repeats[index] = (newRange, mult, repeatID)
