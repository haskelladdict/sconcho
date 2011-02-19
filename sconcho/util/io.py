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

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from PyQt4.QtCore import (QFile, QTextStream, QIODevice, QString,
                          Qt, QRectF, QDataStream, QSize, QRect, 
                          QFileInfo)
from PyQt4.QtGui import (QColor, QMessageBox, QImage, QPainter,
                         QPrinter, QPrintDialog, QDialog, QFont)
from PyQt4.QtXml import (QDomDocument, QDomNode, QDomElement)
from PyQt4.QtSvg import QSvgGenerator

from sconcho.gui.pattern_canvas import (PatternGridItem, PatternLegendItem,
                                        legendItem_symbol, legendItem_text)
from sconcho.util.misc import wait_cursor
from sconcho.util.exceptions import PatternReadError
import sconcho.util.messages as msg


# magic number to specify binary API
MAGIC_NUMBER = 0xA3D1
API_VERSION  = 1


#############################################################################
#
# routines for writing a project.
#
#############################################################################
@wait_cursor
def save_project(canvas, colors, activeSymbol, settings, saveFileName):
    """ Toplevel writer routine. """

    # prepare data structures
    patternGridItems = get_patternGridItems(canvas)
    legendItems      = canvas.gridLegend.values()

    status = None
    handle = None
    try:
        handle = QFile(saveFileName)
        if not handle.open(QIODevice.WriteOnly | QIODevice.Truncate):
            raise IOError, unicode(handle.errorString())

        stream = QDataStream(handle)

        # write header
        stream.writeInt32(MAGIC_NUMBER)
        stream.writeInt32(API_VERSION)
        stream.setVersion(QDataStream.Qt_4_5)

        stream.writeInt32(len(patternGridItems))
        stream.writeInt32(len(legendItems))
        stream.writeInt32(len(colors))

        # the next are 5 dummy entries so we can add more
        # output within the same API
        for count in range(5):
            stream.writeInt32(0)

        # write content
        write_patternGridItems(stream, patternGridItems)
        write_legendItems(stream, legendItems)
        write_colors(stream, colors)
        write_active_symbol(stream, activeSymbol)
        write_settings(stream, settings)

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
        stream << QString(item.symbol["category"])  \
               << QString(item.symbol["name"])
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

        stream << QString(symbolItem.symbol["category"]) \
               << QString(symbolItem.symbol["name"])
        stream.writeDouble(symbolItem.pos().x())
        stream.writeDouble(symbolItem.pos().y())
        stream.writeDouble(textItem.pos().x())
        stream.writeDouble(textItem.pos().y())
        stream << symbolItem.color                        
        stream << QString(textItem.toPlainText())



def write_colors(stream, items):
    """ Write all colors to our output stream. """
    
    for (color, state) in items:
        stream << color
        stream.writeInt16(state)



def write_active_symbol(stream, activeSymbol):
    """ Write the info regarding the active symbol """

    if activeSymbol:
        stream << QString(activeSymbol["category"])
        stream << QString(activeSymbol["name"])
    else:
        stream << QString("None") << QString("None")



def write_settings(stream, settings):
    """ Write all settings such as fonts for labels and legend """

    stream << settings.label_font
    stream.writeInt32(settings.label_interval)
    stream << settings.legend_font
    stream.writeInt32(settings.grid_cell_width)
    stream.writeInt32(settings.grid_cell_height)



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
            raise IOError, unicode(handle.errorString())

        stream = QDataStream(handle)

        # check header
        magic = stream.readInt32()
        if magic != MAGIC_NUMBER:
            raise IOError, "unrecogized file Type"

        version = stream.readInt32()
        if version != API_VERSION:
            raise IOError, "unsupported API version"

        stream.setVersion(QDataStream.Qt_4_5)

        # start parsing
        numGridItems   = stream.readInt32()
        numLegendItems = stream.readInt32()
        numColors      = stream.readInt32()

        # the next are 5 dummy entries we just skip
        for count in range(5):
            stream.readInt32()

        # write elements
        patternGridItems = read_patternGridItems(stream, numGridItems)
        legendItems      = read_legendItems(stream, numLegendItems)
        colors           = read_colors(stream, numColors)
        activeSymbol     = read_active_symbol(stream)
        read_settings(stream, settings)


    except (IOError, OSError) as e:
        status = "Failed to open %s: %s " % (openFileName, e)

    finally:
        if handle is not None:
            handle.close()
        if status is not None:
            return (False, status, None, None, None, None)

    return (True, None, patternGridItems, legendItems, colors, activeSymbol)



def read_patternGridItems(stream, numItems):
    """ Read all patternGridItems from our output stream """

    patternGridItems = []
    for count in range(numItems):
        category = QString()
        stream >> category

        name = QString()
        stream >> name

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
        category = QString()
        stream >> category

        name = QString()
        stream >> name

        itemXPos  = stream.readDouble()
        itemYPos  = stream.readDouble()
        labelXPos = stream.readDouble()
        labelYPos = stream.readDouble()
       
        color  = QColor()
        stream >> color

        description = QString()
        stream >> description

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

    category = QString()
    stream >> category

    name = QString()
    stream >> name

    activeSymbol = {}
    if category != "None":
        activeSymbol ["category"] = category
        activeSymbol ["name"]     = name

    return activeSymbol



def read_settings(stream, settings):
    """ Write all settings such as fonts for labels and legend.
    
    NOTE: This function doesn't return anything and changes
    the settings directly."""

    labelFont     = QFont()
    legendFont    = QFont()

    stream >> labelFont
    labelInterval = stream.readInt32()
    stream >> legendFont
    gridCellWidth = stream.readInt32()
    gridCellHeight = stream.readInt32()

    # make sure we parsed something sensible before 
    # touching the settings
    if labelFont.family():
        settings.label_font = labelFont

    if labelInterval != 0:
        settings.label_interval = labelInterval

    if legendFont.family():
        settings.legend_font = legendFont

    if gridCellWidth != 0:
        settings.grid_cell_width = gridCellWidth

    if gridCellHeight != 0:
        settings.grid_cell_height = gridCellHeight



#############################################################################
#
# routines for exporting a project to an image file
#
#############################################################################
@wait_cursor
def export_scene(canvas, width, height, hideNostitchSymbols,
                 exportFileName):
    """ This function exports the scene to a file. """

    canvas.clear_all_selected_cells()

    if hideNostitchSymbols:
        canvas.toggle_nostitch_symbol_visbility(False)

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
        generator.setDescription("this svg image was exported from"
                                 "a sconcho project")
    else:
        generator = QImage(width+2*margin, height+2*margin, 
                           QImage.Format_ARGB32_Premultiplied)
        generator.fill(1)

    painter = QPainter(generator)
    painter.setRenderHints(QPainter.SmoothPixmapTransform )
    painter.setRenderHints(QPainter.Antialiasing )
    painter.setRenderHints(QPainter.TextAntialiasing )
    painter.setBackgroundMode(Qt.TransparentMode )

    canvas.render(painter, QRectF(), theScene )
    painter.end()

    if not svg:
        generator.save(exportFileName)

    if hideNostitchSymbols:
        canvas.toggle_nostitch_symbol_visbility(True)




#############################################################################
#
# routines for printing a project 
#
#############################################################################
def print_scene(canvas):
    """
    This function prints the content of the canvas.
    """

    aPrinter = QPrinter(QPrinter.HighResolution)
    printDialog = QPrintDialog(aPrinter)
    
    if printDialog.exec_() == QDialog.Accepted:
        
        theScene = canvas.itemsBoundingRect()
        theScene.adjust(-10, -10, 10, 10)

        painter = QPainter(aPrinter)
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)
        painter.setRenderHints(QPainter.TextAntialiasing)
        canvas.render(painter, QRectF(), theScene)
        painter.end()
