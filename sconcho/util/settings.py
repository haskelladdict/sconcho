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

from sconcho.util.misc import errorLogger



class DefaultSettings(QSettings):
    """ The DefaultSettings class encapsulates the infrastructure
    needed to interact with the currently active settings.

    There are two types of settings, default and session. The default
    settings are loaded on startup and also initialize the session settings.
    All further changes in the preferences dialog affect only the
    current session and are thus forgotten upon application shutdown
    (i.e. are session settings). The current session settings for a
    given category (labels, legend, etc.) can be made the default via
    pressing the corresponding 'Make Defaults' button.

    """

    # defaults 
    DEFAULT_GRID_CELL_WIDTH  = "30"
    DEFAULT_GRID_CELL_HEIGHT = "30"
    DEFAULT_FONT = "Arial,10,-1,5,50,0,0,0,0,0"
    DEFAULT_INTERVAL = "1"


    def __init__(self, organization, application, parent = None):

        super(DefaultSettings, self).__init__(organization,
                                              application,
                                              parent)

        # remove old "global" namespace
        self.remove("global")

        self.load_defaults()
        self.set_session_values()



    def load_defaults(self):
        """ Initializes default settings if none exist. """

        labelFont = self.value("default/labelFont" ).toString()
        if labelFont.isEmpty():
            self.setValue("default/labelFont",
                          DefaultSettings.DEFAULT_FONT)

        legendFont = self.value( "default/legendFont" ).toString()
        if legendFont.isEmpty():
            self.setValue("default/legendFont",
                          DefaultSettings.DEFAULT_FONT)

        labelInterval = self.value("default/labelInterval").toString()
        if labelInterval.isEmpty():
            self.setValue("default/labelInterval",
                          DefaultSettings.DEFAULT_INTERVAL)

        cellWidth = self.value("default/cellWidth").toString()
        if cellWidth.isEmpty():
            self.setValue("default/cellWidth",
                          DefaultSettings.DEFAULT_GRID_CELL_WIDTH)

        cellHeight = self.value("default/cellHeight").toString()
        if cellHeight.isEmpty():
            self.setValue("default/cellHeight", 
                          DefaultSettings.DEFAULT_GRID_CELL_HEIGHT)

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
            errorLogger.write("DefaultSettings.grid_cell_width: Failed to "
                              "retrieve grid cell width from settings.")

        return cellWidth



    @grid_cell_width.setter
    def grid_cell_width(self, width):
        """ Store the width of grid cells. """

        self.setValue("session/cellWidth", QString(unicode(width)))



    def set_default_grid_cell_width(self, width):
        """ Store the default width of grid cells. """

        self.setValue("default/cellWidth", QString(unicode(width)))



    @property
    def grid_cell_height(self):
        """ Return the grid cell height. """

        (cellHeight, heightStatus) = \
                    self.value("session/cellHeight").toString().toInt()

        if not heightStatus:
           errorLogger.write("DefaultSettings.grid_cell_height: Failed to "
                             "retrieve grid dimensions from settings.")

        return cellHeight



    @grid_cell_height.setter
    def grid_cell_height(self, height):
        """ Store the grid cell height. """

        self.setValue("session/cellHeight", QString(unicode(height)))


        
    def set_default_grid_cell_height(self, height):
        """ Store the default grid cell height. """

        self.setValue("default/cellHeight", QString(unicode(height)))



    @property
    def personal_symbol_path(self):
        """ Return path where custom symbols are located. """

        path = self.value("default/personalSymbolPath").toString()

        if not path:
            errorLogger.write("DefaultSettings.personal_symbol_path: "
                              "Failed to retrieve personal symbol path.")
            return("")

        return path


    
    @personal_symbol_path.setter
    def personal_symbol_path(self, newPath):
        """ Set the path where custom symbols are located. """

        self.setValue("default/personalSymbolPath", newPath)



    @property
    def text_font(self):
        """ Return the currently selected text font. """

        fontString = self.value("session/font").toString()

        font = QFont()
        if not font.fromString(fontString):
            errorLogger.write("DefaultSettings.text_font: Failed to "
                              "retrieve font from settings.")

        return font



    @property
    def label_font(self):
        """ Return the current label font. """

        labelFontString = self.value("session/labelFont").toString()

        font = QFont()
        if not font.fromString(labelFontString):
            errorLogger.write("DefaultSettings.label_font: Failed to "
                              "to retrieve label font from settings.")

        return font



    @label_font.setter
    def label_font(self, newLabelFont):
        """ Set the current label font. """

        if fontDatabase_has_font(newLabelFont):
            fontString = newLabelFont.toString()
            self.setValue("session/labelFont", fontString)



    def set_default_label_font(self, defaultLabelFont):
        """ Set the default label font. """

        if fontDatabase_has_font(defaultLabelFont):
            fontString = defaultLabelFont.toString()
            self.setValue("default/labelFont", fontString)



    @property
    def legend_font(self):
        """ Return the current legend font. """

        legendFontString = self.value("session/legendFont").toString()

        font = QFont()
        if not font.fromString(legendFontString):
            errorLogger.write("DefaultSettings.legend_font: Failed to "
                              "retrieve legend font from settings.")

        return font



    @legend_font.setter
    def legend_font(self, newLegendFont):
        """ Set the current legend font. """

        if fontDatabase_has_font(newLegendFont):
            fontString = newLegendFont.toString()
            self.setValue("session/legendFont", fontString)



    def set_default_legend_font(self, defaultLegendFont):
        """ Set the default legend font. """

        if fontDatabase_has_font(defaultLegendFont):
            fontString = defaultLegendFont.toString()
            self.setValue("default/legendFont", fontString)



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
        """ Store the current interval with which the labels are spaced. """

        self.setValue("session/labelInterval", QString(unicode(interval)))



    def set_default_label_interval(self, defaultInterval):
        """ Store the default interval with which the labels are spaced. """

        self.setValue("default/labelInterval",
                      QString(unicode(defaultInterval)))



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
