# -*- coding: utf-8 -*-
########################################################################
#
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

from PyQt4.QtCore import (QFile, QTextStream, QIODevice, 
                          Qt, QRectF, QDataStream, QSize, QRect, 
                          QFileInfo, QLineF, QPointF, QThread,
                          QReadWriteLock, QWriteLocker, SIGNAL)
from PyQt4.QtGui import (QColor, QMessageBox, QImage, QPainter,
                         QFont)
from PyQt4.QtXml import (QDomDocument, QDomNode, QDomElement)
from PyQt4.QtSvg import QSvgGenerator

from gui.pattern_canvas_objects import (PatternGridItem, 
                                        PatternLegendItem,
                                        PatternRepeatItem, 
                                        NostitchVisualizer)
from util.canvas import (legendItem_symbol, legendItem_text)
from util.misc import wait_cursor
from util.exceptions import PatternReadError
import util.messages as msg


# magic number to specify binary API
MAGIC_NUMBER = 0xA3D1
API_VERSION  = 2


###########################################################################
#
# this is a simple wrapper around QThread to allow saving of projects
# to take place in a separate thread
#
###########################################################################
class SaveThread(QThread):

    lock = QReadWriteLock()

    def __init__(self, canvas, colors, activeSymbol, settings,
                 saveFileName, markProjectClean, parent = None):

        super(SaveThread, self).__init__(parent)

        self.canvas = canvas
        self.colors = colors
        self.activeSymbol = activeSymbol
        self.settings = settings
        self.saveFileName = saveFileName
        self.markProjectClean = markProjectClean


    def start(self):
        """ Main start routine of our SaveThread. Simply calls
        save_project and emits a signal with the results when
        done.

        """

        with QWriteLocker(SaveThread.lock):
            (status, errorMsg) = save_project(self.canvas, self.colors,
                                              self.activeSymbol,
                                              self.settings,
                                              self.saveFileName)

            self.emit(SIGNAL("saving_done"), status, errorMsg,
                      self.saveFileName, self.markProjectClean)
           
    


###########################################################################
#
# routines for writing a project.
#
###########################################################################
@wait_cursor
def save_project(canvas, colors, activeSymbol, settings, saveFileName):
    """ Toplevel writer routine. 

    NOTE: Make sure that the settings are written last since 
    they are the most volatile. That way, the API has the
    largest chance of surviving as long as possible.
    """

    # prepare data structures
    patternGridItems = get_patternGridItems(canvas)
    legendItems = canvas.gridLegend.values()
    patternRepeats = get_patternRepeats(canvas)
    repeatLegends = canvas.repeatLegend
    rowRepeats = canvas.rowRepeatTracker
    textItems = canvas.canvasTextBoxes
    assert(len(patternRepeats) == len(repeatLegends))

    status = None
    handle = None
    try:
        handle = QFile(saveFileName)
        if not handle.open(QIODevice.WriteOnly | QIODevice.Truncate):
            raise IOError(unicode(handle.errorString()))

        stream = QDataStream(handle)

        # write header
        stream.writeInt32(MAGIC_NUMBER)
        stream.writeInt32(API_VERSION)
        stream.setVersion(QDataStream.Qt_4_5)

        stream.writeInt32(len(patternGridItems))
        stream.writeInt32(len(legendItems))
        stream.writeInt32(len(colors))
        stream.writeInt32(len(patternRepeats))
        stream.writeInt32(len(repeatLegends))
        stream.writeInt32(len(rowRepeats))
        stream.writeInt32(len(textItems))
        
        # the next is 1 dummy entry so we can add more
        # output within the same API
        for count in range(1):
            stream.writeInt32(0)

        # write content
        write_patternGridItems(stream, patternGridItems)
        write_legendItems(stream, legendItems)
        write_colors(stream, colors)
        write_active_symbol(stream, activeSymbol)
        write_patternRepeats(stream, patternRepeats)
        write_settings(stream, settings)
        write_repeatLegends(stream, repeatLegends)
        write_rowRepeats(stream, rowRepeats)
        write_textItems(stream, textItems)


    except (IOError, OSError) as e:
        status = "Failed to save: %s " % e

    finally:
        if handle is not None:
            handle.close()
        if status is not None:
            return (False, status)

    return (True, None)



def get_patternGridItems(canvas):
    """ Extract all the patternGridItems """

    patternGridItems = []

    for item in canvas.items():
        if isinstance(item, PatternGridItem):
            patternGridItems.append(item)

    return patternGridItems



def write_patternGridItems(stream, items):
    """ Write all patternGridItems to our output stream """

    for item in items:
        stream.writeQString(item.symbol["category"]) 
        stream.writeQString(item.symbol["name"])
        stream.writeInt32(item.column)
        stream.writeInt32(item.row)
        stream.writeInt32(item.width)
        stream.writeInt32(item.height)
        stream << item.color



def write_legendItems(stream, items):
    """ Write all legendItems to our output stream. """

    for item in items:

        symbolItem = legendItem_symbol(item)
        textItem   = legendItem_text(item)

        stream.writeQString(symbolItem.symbol["category"])
        stream.writeQString(symbolItem.symbol["name"])
        stream.writeDouble(symbolItem.pos().x())
        stream.writeDouble(symbolItem.pos().y())
        stream.writeDouble(textItem.pos().x())
        stream.writeDouble(textItem.pos().y())
        stream << symbolItem.color                        
        stream.writeQString(textItem.toPlainText())



def write_colors(stream, items):
    """ Write all colors to our output stream. """
    
    for (color, state) in items:
        stream << color
        stream.writeInt16(state)



def write_active_symbol(stream, activeSymbol):
    """ Write the info regarding the active symbol """

    if activeSymbol:
        stream.writeQString(activeSymbol["category"])
        stream.writeQString(activeSymbol["name"])
    else:
        stream.writeQString("None") 
        stream.writeQString("None")



def write_settings(stream, settings):
    """ Write all settings such as fonts for labels and legend """

    stream << settings.labelFont.value
    
    rowIntervalMode = get_row_label_interval(settings.rowLabelMode.value)
    stream.writeInt32(rowIntervalMode) 
    
    stream << settings.legendFont.value
    stream.writeInt32(settings.gridCellWidth.value)
    stream.writeInt32(settings.gridCellHeight.value)

    # row label info
    stream.writeInt32(settings.rowLabelStart.value)
    evenRowLabelLocation = \
        get_row_label_location(settings.evenRowLabelLocation.value)
    stream.writeInt32(evenRowLabelLocation)

    # row highlighting info
    stream.writeInt32(settings.highlightRows.value)
    stream.writeInt32(settings.highlightRowsOpacity.value)
    stream.writeInt32(settings.highlightRowsStart.value)
    stream.writeQString(settings.highlightRowsColor.value)

    # write rest of row/column settings
    # NOTE: The row settings aren't combined with the rest to
    # remain backward compatible.
    oddRowLabelLocation = \
        get_row_label_location(settings.oddRowLabelLocation.value)
    stream.writeInt32(oddRowLabelLocation)
    stream.writeInt32(settings.rowLabelsShowInterval.value)
    stream.writeInt32(settings.rowLabelsShowIntervalStart.value)

    columnIntervalMode = \
        get_column_label_interval(settings.columnLabelMode.value)
    stream.writeInt32(columnIntervalMode) 
    stream.writeInt32(settings.columnLabelsShowInterval.value)
    stream.writeInt32(settings.columnLabelsShowIntervalStart.value)

    # write 200 dummy bytes so we can add more items
    for i in range(0,200):
        stream.writeInt32(0)



def get_patternRepeats(canvas):
    """ Extract all the patternGridItems """

    patternRepeats = []

    for item in canvas.items():
        if isinstance(item, PatternRepeatItem):
            patternRepeats.append(item)

    return patternRepeats



def write_patternRepeats(stream, repeats):
    """ Write all patternGridItems to our output stream.

    NOTE: This is a little bit more work. For each pattern
    repeat item, we extract the lines that make it up, and
    then store pairs of points together with color and
    line width information.

    """

    for repeat in repeats:

        points = []
        for element in repeat.lineElements:

            line = element.line()
            points.append(line.p1())
            points.append(line.p2())

        stream.writeInt32(len(points))
        for point in points:
            stream << point

        stream << repeat.pos()

        # store 16 bit of the id to we can match the repeat
        # with the proper legend entry
        stream.writeUInt16(repeat.itemID.fields[1])

        stream.writeInt16(repeat.width)
        stream << repeat.color



def write_repeatLegends(stream, repeatLegends):
    """ write the legends for all repeat items.

    NOTE: We also store 16 bits of the id so we can
    properly match it with its repeat item.

    """

    for (legendID, (dummy, item, textItem)) in repeatLegends.items():
    
        if item.isVisible():
            isVisible = 1
        else:
            isVisible = 0
    
        stream.writeUInt16(legendID.fields[1])
        stream.writeUInt16(isVisible)
        stream << item.pos()
        stream << textItem.pos()
        stream.writeQString(textItem.toPlainText())



def write_rowRepeats(stream, rowRepeats):
    """ write the row repeats if any. """

    for (rowList, multiplicity, dummy) in rowRepeats:
        stream.writeInt32(multiplicity)
        stream.writeInt32(len(rowList))
        for row in rowList:
            stream.writeInt32(row)



def write_textItems(stream, textItems):
    """ write the text items """

    for item in textItems.values():
        stream << item.pos()
        stream.writeQString(item.toPlainText())





#############################################################################
#
# routines for writing a project.
#
#############################################################################
@wait_cursor
def read_project(settings, openFileName):
    """ Toplevel reader routine. """

    status = None
    handle = None
    try:
        handle = QFile(openFileName)
        if not handle.open(QIODevice.ReadOnly):
            raise IOError(handle.errorString())

        stream = QDataStream(handle)

        # check header
        magic = stream.readInt32()
        if magic != MAGIC_NUMBER:
            status = ("Unrecognized file type - \n{0}\nis not "
                           "a sconcho spf file!").format(openFileName)
            raise IOError(status)

        version = stream.readInt32()
        stream.setVersion(QDataStream.Qt_4_5)

        # start parsing
        numGridItems = stream.readInt32()
        numLegendItems = stream.readInt32()
        numColors = stream.readInt32()
        numRepeats = stream.readInt32()
        numRepeatLegends = stream.readInt32()
        numRowRepeats = stream.readInt32()
        numTextItems = stream.readInt32()

        # the next are 4 dummy entries we just skip
        for count in range(1):
            stream.readInt32()

        # read elements
        patternGridItems = read_patternGridItems(stream, numGridItems)
        legendItems = read_legendItems(stream, numLegendItems)
        colors = read_colors(stream, numColors)
        activeSymbol = read_active_symbol(stream)

        # with API_VERSION 2 the settings are always read last
        if version == 1:
            read_settings(stream, settings, version)
            patternRepeats = read_patternRepeats(stream, numRepeats)
            # API version 1 knows nothing about legends for pattern
            # repeats and rowRepeats
            repeatLegends = {}
            rowRepeats = []
            textItems = []
        elif version == 2:
            patternRepeats = read_patternRepeats(stream, numRepeats)
            read_settings(stream, settings, version)
            repeatLegends = read_patternRepeatLegends(stream, numRepeatLegends)
            rowRepeats = read_rowRepeats(stream, numRowRepeats)
            textItems = read_textItems(stream, numTextItems)
        else:
            raise IOError("unsupported API version")
            

    except (IOError, OSError) as e:
        status = "Failed to open %s: %s " % (openFileName, e)

    finally:
        if handle is not None:
            handle.close()
        if status is not None:
            return (False, status, None, None, None, None, None, None, 
                    None, None)

    return (True, None, patternGridItems, legendItems, colors, 
            activeSymbol, patternRepeats, repeatLegends, rowRepeats,
            textItems)



def read_patternGridItems(stream, numItems):
    """ Read all patternGridItems from our output stream """

    patternGridItems = []
    for count in range(numItems):
        category = stream.readQString() 
        name = stream.readQString() 
        column = stream.readInt32()
        row    = stream.readInt32()
        width  = stream.readInt32()
        height = stream.readInt32()
       
        color  = QColor()
        stream >> color

        newItem = { "category" : category,
                    "name"     : name,
                    "column"   : column,
                    "row"      : row,
                    "width"    : width,
                    "height"   : height,
                    "color"    : color}

        patternGridItems.append(newItem)

    return patternGridItems



def read_legendItems(stream, numItems):
    """ Read all legendItems from our output stream """

    legendItems = []
    for count in range(numItems):
        category = stream.readQString() 
        name = stream.readQString() 
        itemXPos  = stream.readDouble()
        itemYPos  = stream.readDouble()
        labelXPos = stream.readDouble()
        labelYPos = stream.readDouble()
       
        color  = QColor()
        stream >> color

        description = stream.readQString() 
        newItem = { "category"    : category,
                    "name"        : name,
                    "itemXPos"    : itemXPos,
                    "itemYPos"    : itemYPos,
                    "labelXPos"   : labelXPos,
                    "labelYPos"   : labelYPos, 
                    "color"       : color,
                    "description" : description}

        legendItems.append(newItem)

    return legendItems



def read_colors(stream, numItems):
    """ Write all colors to our output stream. """
   
    colors = []
    for count in range(numItems):
        color = QColor()
        stream >> color
        state = stream.readInt16()

        colors.append((color, state))

    return colors



def read_active_symbol(stream):
    """ Read the previously active symbol if any """

    category = stream.readQString()
    name = stream.readQString() 
    activeSymbol = {}
    if category != "None":
        activeSymbol ["category"] = category
        activeSymbol ["name"]     = name

    return activeSymbol



def read_settings(stream, settings, version):
    """ Write all settings such as fonts for labels and legend.
    
    NOTE: This function doesn't return anything and changes
    the settings directly."""

    labelFont     = QFont()
    legendFont    = QFont()

    stream >> labelFont

    labelInterval = stream.readInt32()
    labelState = get_row_label_identifier(labelInterval)

    stream >> legendFont
    gridCellWidth = stream.readInt32()
    gridCellHeight = stream.readInt32()

    # make sure we parsed something sensible before 
    # touching the settings
    if labelFont.family():
        settings.labelFont.value = labelFont

    if labelState:
        settings.rowLabelMode.value = labelState

    if legendFont.family():
        settings.legendFont.value = legendFont

    if gridCellWidth != 0:
        settings.gridCellWidth.value = gridCellWidth

    if gridCellHeight != 0:
        settings.gridCellHeight.value = gridCellHeight

    # new stuff in API_VERSION 2 and onward
    # NOTE: To accomodate additional data written to spf files within the
    # same API we rely on stream.readInt32 and friends to return 0 on EOF
    if version > 1:
        labelStart = stream.readInt32()
        if labelStart:
            settings.rowLabelStart.value = labelStart

        evenRowLabelLocation = stream.readInt32()
        if evenRowLabelLocation:
            settings.evenRowLabelLocation.value = \
                get_row_label_location_string(evenRowLabelLocation)

        highlightRows = stream.readInt32()
        if highlightRows:
            settings.highlightRows.value = highlightRows

        highlightRowsOpacity = stream.readInt32()
        if highlightRowsOpacity:
            settings.highlightRowsOpacity.value = highlightRowsOpacity

        highlightRowsStart = stream.readInt32()
        if highlightRowsStart:
            settings.highlightRowsStart.value = highlightRowsStart

        highlightRowsColor = stream.readQString()
        if highlightRowsColor:
            settings.highlightRowsColor.value = highlightRowsColor

        # write rest of row/column settings
        # NOTE: The row settings aren't combined with the rest to
        # remain backward compatible.
        oddRowLabelLocation = stream.readInt32()
        if oddRowLabelLocation:
            settings.oddRowLabelLocation.value = \
                get_row_label_location_string(oddRowLabelLocation)

        rowLabelsShowInterval = stream.readInt32()
        if rowLabelsShowInterval:
            settings.rowLabelsShowInterval.value = rowLabelsShowInterval

        rowLabelsShowIntervalStart = stream.readInt32()
        if rowLabelsShowIntervalStart:
            settings.rowLabelsShowIntervalStart.value = \
                rowLabelsShowIntervalStart

        columnLabelMode = stream.readInt32()
        if columnLabelMode:
            settings.columnLabelMode.value = \
                get_column_label_identifier(columnLabelMode)

        columnLabelsShowInterval = stream.readInt32()
        if columnLabelsShowInterval:
            settings.columnLabelsShowInterval.value = \
                columnLabelsShowInterval

        columnLabelsShowIntervalStart = stream.readInt32()
        if columnLabelsShowIntervalStart:
            settings.columnLabelsShowIntervalStart.value = \
                columnLabelsShowIntervalStart

        # reat 200 dummy bytes so we can add more items
        for i in range(0,200):
            stream.readInt32()


def read_patternRepeats(stream, numRepeats):
    """ Read all patternRepeats from our output stream """

    patternRepeats = []
    for count in range(numRepeats):

        # read all lines
        lines = []
        numPoints = stream.readInt32()
        for pointCount in range(0, numPoints, 2):

            point1 = QPointF()
            stream >> point1
            
            point2 = QPointF()
            stream >> point2
            
            lines.append(QLineF(point1, point2))

        # read width and color
        position = QPointF()
        stream >> position
        legendID = stream.readUInt16()
        width = stream.readInt16()
        color = QColor()
        stream >> color 
        
        newItem = { "lines"     : lines,
                    "position"  : position,
                    "width"     : width,
                    "color"     : color,
                    "legendID"  : legendID}
 
        patternRepeats.append(newItem)

    return patternRepeats



def read_patternRepeatLegends(stream, numRepeatLegends):
    """ Read in the info for the pattern repeat legends. 

    NOTE: In contrast to the other read routine this
    one returns a dictionary with the legendID as key
    so we can match it effeciently with the corresponding
    repeat.

    """

    patternRepeatLegends = {}
    for count in range(numRepeatLegends):
        
        legendID = stream.readUInt16()
        isVisible = stream.readUInt16()

        itemPos = QPointF()
        stream >> itemPos

        textItemPos = QPointF()
        stream >> textItemPos 

        itemText = stream.readQString() 
 
        newItem = { "legendID"    : legendID,
                    "isVisible"   : isVisible,
                    "itemPos"     : itemPos,
                    "textItemPos" : textItemPos,
                    "itemText"    : itemText}
 
        patternRepeatLegends[legendID] = newItem


    return patternRepeatLegends



def read_rowRepeats(stream, numRowRepeats):
    """ Read in the info for the row repeats. """

    rowRepeatList = []
    for count in range(numRowRepeats):
        
        multiplicity = stream.readInt32()
        length = stream.readInt32()
        rowList = []
        for index in range(length):
            item = stream.readInt32()
            rowList.append(item)

        rowRepeatList.append((rowList, multiplicity))

    return rowRepeatList



def read_textItems(stream, numTextItems):
    """ Read in the list of text items """

    textItemList = []
    for count in range(numTextItems):
        itemPos = QPointF()
        stream >> itemPos
        itemText = stream.readQString()

        newItem = { "itemPos" : itemPos,
                    "itemText" : itemText }

        textItemList.append(newItem)

    return textItemList



###########################################################################
#
# routines for exporting a project to an image file
#
###########################################################################
@wait_cursor
def export_scene(canvas, width, height, dpi, hideNostitchSymbols,
                 exportFileName):
    """ This function exports the scene to a file. """

    # need this to make sure we take away focus from
    # any currently selected legend items
    canvas.clearFocus()


    with NostitchVisualizer(canvas, hideNostitchSymbols):

        # NOTE: We seem to need the 1px buffer region to avoid
        # the image being cut off
        margin = 10
        theScene = canvas.itemsBoundingRect()
        theScene.adjust(-margin, -margin, margin, margin)

        # check if user requested an svg file
        svg = True if QFileInfo(exportFileName).completeSuffix() == "svg" \
                else False

        if svg:
            generator = QSvgGenerator()
            generator.setFileName(exportFileName)
            generator.setSize(QSize(width, height))
            generator.setViewBox(QRect(0, 0, width, height))
            generator.setTitle("sconcho generated SVG image")
            generator.setDescription("this svg image was exported from "
                                     "a sconcho project")
            generator.setResolution(dpi)
        else:
            generator = QImage(width+2*margin, height+2*margin, 
                               QImage.Format_ARGB32_Premultiplied)
            generator.fill(1)

            inchesToMeter = 39.3700787
            generator.setDotsPerMeterX(dpi*inchesToMeter)
            generator.setDotsPerMeterY(dpi*inchesToMeter)


        painter = QPainter(generator)
        painter.setRenderHints(QPainter.SmoothPixmapTransform )
        painter.setRenderHints(QPainter.HighQualityAntialiasing )
        painter.setRenderHints(QPainter.TextAntialiasing )
        painter.setBackgroundMode(Qt.TransparentMode )

        canvas.render(painter, QRectF(), theScene )
        painter.end()

        if not svg:
            generator.save(exportFileName)



############################################################################
#
# routines for printing a project 
#
############################################################################
def printer(canvas, printer):
    """ The main print routine. """

    theScene = canvas.itemsBoundingRect()
    theScene.adjust(-10, -10, 10, 10)

    painter = QPainter(printer)
    painter.setRenderHints(QPainter.SmoothPixmapTransform)
    painter.setRenderHints(QPainter.HighQualityAntialiasing)
    painter.setRenderHints(QPainter.TextAntialiasing)
    canvas.render(painter, QRectF(), theScene)
    painter.end()



############################################################################
#
# helper functions
#
############################################################################

def get_row_label_identifier(intervalState):
    """ This function is the inverse of get_row_label_interval.

    It converts a stored integer into the the proper row
    label state.
 
    NOTE: Previously we used the labelInterval Int field to store 
    a true interval. Since this option is gone we re-use the Int
    to store the row label interval state. Since label
    intervals previously had to be <= 100 we can reuse values
    > 100 for this purpose. For folks who load an old spf file that
    still has a true label interval field we map to the default
    of LABEL_ALL_ROWS.

    """

    intervalIdentifier = "LABEL_ALL_ROWS"
    if intervalState == 102:
        intervalIdentifier = "SHOW_ROWS_WITH_INTERVAL"   
    if intervalState == 104:
        intervalIdentifier = "SHOW_ODD_ROWS"   
    elif intervalState == 105:
        intervalIdentifier = "SHOW_EVEN_ROWS"   
    

    return intervalIdentifier



def get_row_label_interval(labelType):
    """ This function is the inverse of get_row_label_identifier.

    It converts a row label state into an integer state stored
    within the spf file.

    This function is the inverse of get_row_label_indentifier.
    See this function for more comments.

    NOTE: There is a gap in the ids since some lagacy options
    were removed.
    
    """

    intervalState = 101
    if labelType == "SHOW_ROWS_WITH_INTERVAL":
        intervalState = 102
    elif labelType == "SHOW_ODD_ROWS":
        intervalState = 104
    elif labelType == "SHOW_EVEN_ROWS":
        intervalState = 105

    return intervalState



def get_row_label_location(rowLabelLocation):
    """ Turn string with row label location into integer identifier """

    locationState = 10
    if rowLabelLocation == "LEFT_OF":
        locationState = 11

    return locationState
        



def get_row_label_location_string(state):
    """ Turn a row label identifier into the corresponding string.

    This function is the inverse of get_row_label_location.

    """

    locationString = "RIGHT_OF"
    if state == 11:
        locationString = "LEFT_OF"

    return locationString



def get_column_label_identifier(intervalState):
    """ This function is the inverse of get_column_label_interval.

    It converts a stored integer into the the proper column
    label state.
 
    NOTE: Previously we used the labelInterval Int field to store 
    a true interval. Since this option is gone we re-use the Int
    to store the row label interval state. Since label
    intervals previously had to be <= 100 we can reuse values
    > 100 for this purpose. For folks who load an old spf file that
    still has a true label interval field we map to the default
    of LABEL_ALL_ROWS.

    """

    intervalIdentifier = "LABEL_ALL_COLUMNS"
    if intervalState == 102:
        intervalIdentifier = "SHOW_COLUMNS_WITH_INTERVAL"   

    return intervalIdentifier



def get_column_label_interval(labelType):
    """ This function is the inverse of get_column_label_identifier.

    It converts a column label state into an integer state stored
    within the spf file.

    This function is the inverse of get_column_label_indentifier.
    See this function for more comments.

    """

    intervalState = 101
    if labelType == "SHOW_COLUMNS_WITH_INTERVAL":
        intervalState = 102

    return intervalState

