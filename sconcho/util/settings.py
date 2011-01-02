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

from PyQt4.QtCore import (QSettings, QString, QSize, QDir)
from PyQt4.QtGui import (QFont, QFontDatabase)


### some global settings (is there a better way to do this)
GRID_CELL_WIDTH  = "30"
GRID_CELL_HEIGHT = "30"


def initialize(settings):
    """ Initializes some basic settings if none exist. """

    labelFont = settings.value("global/labelFont" ).toString()
    if labelFont.isEmpty():
      settings.setValue("global/labelFont", "Arial,10,-1,5,50,0,0,0,0,0")

    legendFont = settings.value( "global/legendFont" ).toString()
    if legendFont.isEmpty():
      settings.setValue("global/legendFont", "Arial,10,-1,5,50,0,0,0,0,0")

    exportPatternGrid =  \
        settings.value("global/exportPatternGrid").toString()
    if exportPatternGrid.isEmpty():
        settings.setValue("global/exportPatternGrid", "True")

    exportLegend = settings.value("global/exportLegend").toString()
    if exportLegend.isEmpty():
        settings.setValue("global/exportLegend", "True")

    labelInterval = settings.value("global/labelInterval").toString()
    if labelInterval.isEmpty():
        settings.setValue("global/labelInterval", "1")

    cellWidth = settings.value("global/cellWidth").toString()
    if cellWidth.isEmpty():
        defaultWidth = QString(GRID_CELL_WIDTH)
        settings.setValue("global/cellWidth", defaultWidth )

    cellHeight = settings.value("global/cellHeight").toString()
    if cellHeight.isEmpty():
        defaultHeight = QString(GRID_CELL_HEIGHT)
        settings.setValue("global/cellHeight", defaultHeight)

    personalSymbolsPath = settings.value("global/personalSymbolPath").toString()
    if personalSymbolsPath.isEmpty():
        homePath = QDir.homePath()
        defaultDir = QDir.convertSeparators(homePath + "/sconcho_symbols")
        settings.setValue("global/personalSymbolPath", defaultDir)



def get_grid_dimensions(settings):
    """ Helper function returning a tuple with width and height
    for grid cells.
    """

    (cellWidth, widthStatus) = \
                settings.value("global/cellWidth").toString().toInt()
    (cellHeight, heightStatus) = \
                 settings.value("global/cellHeight").toString().toInt()

    if not widthStatus or not heightStatus:
        print("Error: Failed to retrieve grid dimensions from settings.")

    return QSize(cellWidth, cellHeight)



def get_personal_symbol_path(settings):
    """ Return the path where the user stores her/his personal symbols """

    path = settings.value("global/personalSymbolPath").toString()
    
    if not path:
        print("Error: Failed to retrieve personal symbol path.")
        return ""

    return path



def set_personal_symbol_path(settings, newPath):
    """ Helper function for setting the path for custom symbols. """

    settings.setValue("global/personalSymbolPath", newPath)



def get_text_font(settings):
    """ Helper function for extracting the currently selected text font
    from settings.
    """

    fontString = settings.value("global/font").toString()

    font = QFont()
    if not font.fromString(fontString):
        print("Error: Failed to retrieve font from settings.")

    return font



def get_label_font(settings):
    """ Helper function for extracting the currently label font
    from settings.
    """

    labelFontString = settings.value("global/labelFont").toString()

    font = QFont()
    if not font.fromString(labelFontString):
        print("Error: Failed to retrieve label font from settings.")

    return font



def set_label_font(settings, newLabelFont):
    """ Helper function for extracting the currently label font
    from settings.
    """

    if fontDatabase_has_font(newLabelFont):
        fontString = newLabelFont.toString()
        settings.setValue( "global/labelFont", fontString)



def get_legend_font(settings):
    """ Helper function for extracting the currently legend font
    from settings.
    """

    legendFontString = settings.value("global/legendFont").toString()

    font = QFont()
    if not font.fromString(legendFontString):
        print("Error: Failed to retrieve legend font from settings.")

    return font



def set_legend_font(settings, newLegendFont):
    """ Helper function for setting the currently legend font. """

    if fontDatabase_has_font(newLegendFont):
        fontString = newLegendFont.toString()
        settings.setValue("global/legendFont", fontString)



def get_label_interval(settings):
    """ Helper function for extracting the current interval
    with which the labels are spaced.
    """

    legendIntervalString = settings.value("global/labelInterval").toString()
    (legendInterval, status) = legendIntervalString.toInt()

    if not status:
        return 1

    return legendInterval



def set_label_interval(settings, interval):
    """ Helper function for setting the current interval
    with which the labels are spaced.
    """

    settings.setValue("global/labelInterval", QString(unicode(interval)))



def fontDatabase_has_font(font):
    """ This is helper function checks if a certain font family
    exists on the current system.
    """

    fontDatabase = QFontDatabase()
    families = fontDatabase.families()
    
    return families.contains(font.family())
