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

    # options are LABEL_ALL_ROWS, LABEL_ODD_ROWS, LABEL_EVEN_ROWS,
    # SHOW_ODD_ROWS, SHOW_EVEN_ROWS
    DEFAULT_ROW_LABEL_MODE = "LABEL_ALL_ROWS"
    DEFAULT_ROW_LABEL_START = "1"
    DEFAULT_HIGHLIGHT_ODD_ROWS = "2"     # 2 corresponds to selected
    DEFAULT_HIGHLIGHT_ODD_ROWS_COLOR = "gray"
    DEFAULT_HIGHLIGHT_ODD_ROWS_OPACITY = "10"
    DEFAULT_PERSONAL_SYMBOL_PATH = QDir.convertSeparators(
            QDir.homePath() + "/sconcho_symbols")


    def __init__(self, organization, application, parent = None):

        super(DefaultSettings, self).__init__(organization,
                                              application,
                                              parent)

        # remove old "global" namespace
        self.remove("global")

        # create all settings objects we need
        self.gridCellWidth = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_GRID_CELL_WIDTH,
                "cellWidth", "Int")

        self.gridCellHeight = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_GRID_CELL_HEIGHT,
                "cellHeight", "Int")

        self.rowLabelInterval = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_ROW_LABEL_MODE,
                "rowLabelInterval", "QString")

        self.rowLabelStart = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_ROW_LABEL_START,
                "rowLabelStart", "Int")

        self.labelFont = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_FONT,
                "labelFont", "QFont")

        self.legendFont = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_FONT,
                "legendFont", "QFont")

        self.personalSymbolPath = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_PERSONAL_SYMBOL_PATH,
                "personalSymbolPath", "QString")

        self.highlightOddRows = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_HIGHLIGHT_ODD_ROWS,
                "highlightOddRows", "Int")

        self.highlightOddRowsColor = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_HIGHLIGHT_ODD_ROWS_COLOR,
                "highlightOddRowsColor", "QString")

        self.highlightOddRowsOpacity = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_HIGHLIGHT_ODD_ROWS_OPACITY,
                "highlightOddRowsOpacity", "Int")


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

   


####################################################################
#
# this class wraps individual settings and provides getters and
# setters for session and default values.
#
####################################################################
class PreferenceSetting(object):


    def __init__(self, settings, defaultValue, name, 
                 returnType = "String", errorMsg = ""):

        self.sessionName = "session/" + name
        self.defaultName = "default/" + name
        self.returnType = returnType
        self.errorMsg = errorMsg
        self.settings = settings

        # set defaults if necessary
        value = self.settings.value(self.defaultName).toString()
        if value.isEmpty():
            self.settings.setValue(self.defaultName, defaultValue)

        # set session values
        defaultVal = self.settings.value(self.defaultName).toString()
        self.settings.setValue(self.sessionName, defaultVal)


        

    @property
    def value(self):
        """ Return the property value. """

        value = self.settings.value(self.sessionName).toString()

        status = True
        if self.returnType == "Int":
            (value, status) = value.toInt()
        elif self.returnType == "QFont":
            newValue = QFont()
            if not newValue.fromString(value):
                status = False
            value = newValue

        if not status:
            if not self.errorMsg:
                self.errorMsg = "Settings Error: Failed to retrieve " \
                                "default values for " + self.defaultName
            errorLogger.write(self.errorMsg)

        return value



    @value.setter
    def value(self, setting):
        """ Store the value of property. """

        self._main_setter(self.sessionName, setting)


    
    def make_settings_default(self):
        """ Make the current session settings the default. """

        value = self.settings.value(self.sessionName).toString()
        self.settings.setValue(self.defaultName, value)



    def _main_setter(self, name, value):
        """ This function does the actual setting. """

        # for font settings we check that they exist
        if self.returnType == "QFont":
            if fontDatabase_has_font(value):
                fontString = value.toString()
                self.settings.setValue(name, fontString)
        else:
            self.settings.setValue(name, QString(unicode(value)))




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
