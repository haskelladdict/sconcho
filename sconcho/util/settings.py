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

from PyQt4.QtCore import (QSettings, QString, QSize, QDir, QVariant,
                          QPoint)
from PyQt4.QtGui import (QFont, QFontDatabase)


### some global settings (is there a better way to do this)
GRID_CELL_WIDTH  = "30"
GRID_CELL_HEIGHT = "30"



class DefaultSettings(QSettings):


    def __init__(self, organization, application, parent = None):

        super(DefaultSettings, self).__init__(organization,
                                              application,
                                              parent)

        self.load_defaults()
        self.set_session_values()



    def load_defaults(self):
        """ Initializes default settings if none exist. """

        labelFont = self.value("default/labelFont" ).toString()
        if labelFont.isEmpty():
            self.setValue("default/labelFont", "Arial,10,-1,5,50,0,0,0,0,0")

        legendFont = self.value( "default/legendFont" ).toString()
        if legendFont.isEmpty():
            self.setValue("default/legendFont", "Arial,10,-1,5,50,0,0,0,0,0")

        exportPatternGrid =  \
            self.value("default/exportPatternGrid").toString()
        if exportPatternGrid.isEmpty():
            self.setValue("default/exportPatternGrid", "True")

        exportLegend = self.value("defaul/exportLegend").toString()
        if exportLegend.isEmpty():
            self.setValue("default/exportLegend", "True")

        labelInterval = self.value("default/labelInterval").toString()
        if labelInterval.isEmpty():
            self.setValue("default/labelInterval", "1")

        cellWidth = self.value("default/cellWidth").toString()
        if cellWidth.isEmpty():
            defaultWidth = QString(GRID_CELL_WIDTH)
            self.setValue("default/cellWidth", defaultWidth )

        cellHeight = self.value("default/cellHeight").toString()
        if cellHeight.isEmpty():
            defaultHeight = QString(GRID_CELL_HEIGHT)
            self.setValue("default/cellHeight", defaultHeight)

        personalSymbolsPath = self.value("default/personalSymbolPath").toString()
        if personalSymbolsPath.isEmpty():
            homePath = QDir.homePath()
            defaultDir = QDir.convertSeparators(homePath + "/sconcho_symbols")
            self.setValue("default/personalSymbolPath", defaultDir)



    def set_session_values(self):
        """ Sets values for current session. """

        labelFont = self.value("default/labelFont" ).toString()
        self.setValue("session/labelFont", labelFont)

        legendFont = self.value( "default/legendFont" ).toString()
        self.setValue("session/legendFont", legendFont)

        doExportPatternGrid =  \
            self.value("default/exportPatternGrid").toString()
        self.setValue("session/exportPatternGrid", doExportPatternGrid)

        doExportLegend = self.value("defaul/exportLegend").toString()
        self.setValue("session/exportLegend", doExportLegend)

        labelInterval = self.value("default/labelInterval").toString()
        self.setValue("session/labelInterval", labelInterval)

        cellWidth = self.value("default/cellWidth").toString()
        self.setValue("session/cellWidth", cellWidth)

        cellHeight = self.value("default/cellHeight").toString()
        self.setValue("session/cellHeight", cellHeight)



    @property
    def grid_cell_width(self):
        """ Return the grid cell width. """

        (cellWidth, widthStatus) = \
                    self.value("session/cellWidth").toString().toInt()

        if not widthStatus:
            print("Error: Failed to retrieve grid cell width from settings.")

        return cellWidth



    @grid_cell_width.setter
    def grid_cell_width(self, width):
        """ Store the width of grid cells. """

        self.setValue("session/cellWidth", QString(unicode(width)))



    @property
    def grid_cell_height(self):
        """ Return the grid cell height. """

        (cellHeight, heightStatus) = \
                    self.value("session/cellHeight").toString().toInt()

        if not heightStatus:
            print("Error: Failed to retrieve grid dimensions from settings.")

        return cellHeight



    @grid_cell_height.setter
    def grid_cell_height(self, height):
        """ Store the grid cell height. """

        self.setValue("session/cellHeight", QString(unicode(height)))


        
    @property
    def personal_symbol_path(self):
        """ Return path where custom symbols are located. """

        path = self.value("default/personalSymbolPath").toString()

        if not path:
            print("Error: Failed to retrieve personal symbol path.")
            return("")

        return path


    
    @personal_symbol_path.setter
    def personal_symbol_path(self, newPath):
        """ Set the path where custom symbols are located. """

        self.setValue("session/personalSymbolPath", newPath)



    @property
    def text_font(self):
        """ Return the currently selected text font. """

        fontString = self.value("session/font").toString()

        font = QFont()
        if not font.fromString(fontString):
            print("Error: Failed to retrieve font from settings.")

        return font



    @property
    def label_font(self):
        """ Return the current label font. """

        labelFontString = self.value("session/labelFont").toString()

        font = QFont()
        if not font.fromString(labelFontString):
            print("Error: Failed to retrieve label font from settings.")

        return font



    @label_font.setter
    def label_font(self, newLabelFont):
        """ Set the current label font. """

        if fontDatabase_has_font(newLabelFont):
            fontString = newLabelFont.toString()
            self.setValue("session/labelFont", fontString)



    @property
    def legend_font(self):
        """ Return the current legend font. """

        legendFontString = self.value("session/legendFont").toString()

        font = QFont()
        if not font.fromString(legendFontString):
            print("Error: Failed to retrieve legend font from settings.")

        return font



    @legend_font.setter
    def legend_font(self, newLegendFont):
        """ Set the current legend font. """

        if fontDatabase_has_font(newLegendFont):
            fontString = newLegendFont.toString()
            self.setValue("session/legendFont", fontString)



    @property
    def label_interval(self):
        """ Return the interval with which the labels are spaced. """

        legendIntervalString = self.value("session/labelInterval").toString()
        (legendInterval, status) = legendIntervalString.toInt()

        if not status:
            return 1

        return legendInterval



    @label_interval.setter
    def label_interval(self, interval):
        """ Store the interval with which the labels are spaced. """

        self.setValue("session/labelInterval", QString(unicode(interval)))



    @property
    def main_window_size(self):
        """ Return the size of the main window. """

        return self.value("MainWindow/Size",
                          QVariant(QSize(1200, 800))).toSize()



    @main_window_size.setter
    def main_window_size(self, size):
        """ Set the size of the main window. """

        self.setValue("MainWindow/Size", QVariant(size))
                          


    @property
    def main_window_position(self):
        """ Return the position of the main window. """
        
        return self.value("MainWindow/Position",
                          QVariant(QPoint(0,0))).toPoint()



    @main_window_position.setter
    def main_window_position(self, position):
        """ Set the size of the main window. """

        self.setValue("MainWindow/Position", QVariant(position))



    @property
    def main_window_state(self):
        """ Return the saved state of the main window. """

        return self.value("MainWindow/State").toByteArray()



    @main_window_state.setter
    def main_window_state(self, state):
        """ Set the state of the main window. """

        self.setValue("MainWindow/State", QVariant(state))

    



#######################################################################
#
# some helper functions
#
#######################################################################
def fontDatabase_has_font(font):
    """ This is helper function checks if a certain font family
    exists on the current system.
    """

    fontDatabase = QFontDatabase()
    families = fontDatabase.families()
    
    return families.contains(font.family())
