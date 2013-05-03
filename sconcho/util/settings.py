# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2009-2013 Markus Dittrich
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

import logging 

from PyQt4.QtCore import (QByteArray,
                          QDir,
                          QPoint,
                          QSettings, 
                          QSize)

from PyQt4.QtGui import (QFont, 
                         QFontDatabase)


# module level logger:
logger = logging.getLogger(__name__)


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

    DEFAULT_SHOW_COLUMN_LABELS = "1"
    DEFAULT_SHOW_ROW_LABELS = "1"
    DEFAULT_ROW_LABELS_EDITABLE = "0"
    DEFAULT_COLUMN_LABELS_EDITABLE = "0"

    # options are LABEL_ALL_ROWS, SHOW_ROWS_WITH_INTERVAL,
    # SHOW_ODD_ROWS, SHOW_EVEN_ROWS
    DEFAULT_ROW_LABEL_MODE = "LABEL_ALL_ROWS"
    DEFAULT_ROW_LABEL_START = "1"
    DEFAULT_EVEN_ROW_LABEL_LOCATION = "RIGHT_OF"
    DEFAULT_ODD_ROW_LABEL_LOCATION = "RIGHT_OF"
    DEFAULT_ROW_LABELS_SHOW_INTERVAL = "1"
    DEFAULT_ROW_LABELS_SHOW_INTERVAL_START = "1"
    DEFAULT_ALIGN_ROW_LABELS_TO_VISIBLE_CELLS = "0"

    # options are LABEL_ALL_COLUMNS, SHOW_COLUMNS_WITH_INTERVAL,
    DEFAULT_COLUMN_LABEL_MODE = "LABEL_ALL_COLUMNS"
    DEFAULT_COLUMN_LABELS_SHOW_INTERVAL = "1"
    DEFAULT_COLUMN_LABELS_SHOW_INTERVAL_START = "1"

    DEFAULT_HIGHLIGHT_ROWS = "1"     # 1 corresponds to selected
    DEFAULT_HIGHLIGHT_ROWS_COLOR = "gray"
    DEFAULT_HIGHLIGHT_ROWS_OPACITY = "10"
    DEFAULT_HIGHLIGHT_ROWS_START = "0" # 0 corresponds to bottom row
    DEFAULT_SNAP_PATTERN_REPEAT_TO_GRID = "2"
    DEFAULT_PERSONAL_SYMBOL_PATH = QDir.convertSeparators(
            QDir.homePath() + "/.sconcho_symbols")
    DEFAULT_LOGGING_PATH = QDir.convertSeparators(
            QDir.homePath() + "/.sconcho_logs")
    DEFAULT_DO_LOGGING = "0"
    DEFAULT_EXPORT_PATH = QDir.homePath()
    
    DEFAULT_NUM_RECENT_SYMBOLS = "5"



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

        self.showColumnLabels = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_SHOW_COLUMN_LABELS,
                "showColumnLabels", "Int")

        self.showRowLabels = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_SHOW_ROW_LABELS,
                "showRowLabels", "Int")

        self.rowLabelsEditable = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_ROW_LABELS_EDITABLE,
                "rowLabelsEditable", "Int")

        self.columnLabelsEditable = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_COLUMN_LABELS_EDITABLE,
                "columnLabelsEditable", "Int")

        self.rowLabelsShowInterval = PreferenceSetting(self,
                DefaultSettings.DEFAULT_ROW_LABELS_SHOW_INTERVAL,
                "rowLabelsShowInterval", "Int")

        self.rowLabelsShowIntervalStart = PreferenceSetting(self,
                DefaultSettings.DEFAULT_ROW_LABELS_SHOW_INTERVAL_START,
                "rowLabelsShowIntervalStart", "Int")

        self.rowLabelMode = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_ROW_LABEL_MODE,
                "rowLabelMode", "QString")

        self.rowLabelStart = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_ROW_LABEL_START,
                "rowLabelStart", "Int")

        self.evenRowLabelLocation = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_EVEN_ROW_LABEL_LOCATION,
                "evenRowLabelLocation", "QString")

        self.oddRowLabelLocation = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_ODD_ROW_LABEL_LOCATION,
                "oddRowLabelLocation", "QString")

        self.alignRowLabelsToVisibleCells = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_ALIGN_ROW_LABELS_TO_VISIBLE_CELLS,
                "alignRowLabelsToVisibleCells", "Int")

        self.columnLabelsShowInterval = PreferenceSetting(self,
                DefaultSettings.DEFAULT_COLUMN_LABELS_SHOW_INTERVAL,
                "columnLabelsShowInterval", "Int")

        self.columnLabelsShowIntervalStart = PreferenceSetting(self,
                DefaultSettings.DEFAULT_COLUMN_LABELS_SHOW_INTERVAL_START,
                "columnLabelsShowIntervalStart", "Int")

        self.columnLabelMode = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_COLUMN_LABEL_MODE,
                "columnLabelMode", "QString")

        self.labelFont = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_FONT,
                "labelFont", "QFont")

        self.legendFont = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_FONT,
                "legendFont", "QFont")

        self.personalSymbolPath = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_PERSONAL_SYMBOL_PATH,
                "personalSymbolPath", "QString")

        self.highlightRows = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_HIGHLIGHT_ROWS,
                "highlightRows", "Int")

        self.highlightRowsColor = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_HIGHLIGHT_ROWS_COLOR,
                "highlightRowsColor", "QString")

        self.highlightRowsOpacity = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_HIGHLIGHT_ROWS_OPACITY,
                "highlightRowsOpacity", "Int")

        self.highlightRowsStart = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_HIGHLIGHT_ROWS_START,
                "highlightRowsStart", "Int")

        self.snapPatternRepeatToGrid = PreferenceSetting(self,
                DefaultSettings.DEFAULT_SNAP_PATTERN_REPEAT_TO_GRID,
                "snapPatternRepeatToGrid", "Int")

        self.loggingPath = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_LOGGING_PATH,
                "loggingPath", "QString")

        self.doLogging = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_DO_LOGGING,
                "doLogging", "Int")

        self.numRecentSymbols = PreferenceSetting(self, 
                DefaultSettings.DEFAULT_NUM_RECENT_SYMBOLS,
                "numRecentSymbols", "Int")


    @property
    def main_window_size(self):
        """ Return the size of the main window. """

        return self.value("MainWindow/Size", QSize(1200, 800))



    @main_window_size.setter
    def main_window_size(self, size):
        """ Set the size of the main window. """

        self.setValue("MainWindow/Size", size)
                          


    @property
    def main_window_position(self):
        """ Return the position of the main window. """
        
        return self.value("MainWindow/Position", QPoint(0,0))



    @main_window_position.setter
    def main_window_position(self, position):
        """ Set the size of the main window. """

        self.setValue("MainWindow/Position", position)



    @property
    def main_window_state(self):
        """ Return the saved state of the main window. """

        return self.value("MainWindow/State", QByteArray())



    @main_window_state.setter
    def main_window_state(self, state):
        """ Set the state of the main window. """

        self.setValue("MainWindow/State", state)



    @property
    def symbol_selector_state(self):
        """ Return the saved state of the symbol selector splitter. """

        return self.value("SymbolSelector/State", QByteArray())



    @symbol_selector_state.setter
    def symbol_selector_state(self, state):
        """ Set the state of the symbol selector splitter. """

        self.setValue("SymbolSelector/State", state)



    @property
    def recently_used_files(self):
        """ Return the list of recently used files. """

        # handle empty entries
        if not self.value("RecentlyUsedFiles/List"):
            self.recently_used_files = ""

        return self.value("RecentlyUsedFiles/List")



    @recently_used_files.setter
    def recently_used_files(self, values):
        """ Set the list of recently used files. """

        self.setValue("RecentlyUsedFiles/List", values)



    @property
    def export_path(self):
        """ Return the current export path for spf and 
        bitmap files. 

        """

        # handle empty entry
        if not self.value("ExportPath/Path"):
            self.export_path = DefaultSettings.DEFAULT_EXPORT_PATH

        return self.value("ExportPath/Path")



    @export_path.setter
    def export_path(self, path):
        """ Set the new export path for spf and bitmap
        files. 

        """

        self.setValue("ExportPath/Path", path)




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
        value = self.settings.value(self.defaultName)
        if not value:
            self.settings.setValue(self.defaultName, defaultValue)

        # set session values
        defaultVal = self.settings.value(self.defaultName)
        self.settings.setValue(self.sessionName, defaultVal)


        

    @property
    def value(self):
        """ Return the property value. """

        value = self.settings.value(self.sessionName)

        status = True
        if self.returnType == "Int":
            value = int(value)
        elif self.returnType == "QFont":
            value = QFont(value)
        elif self.returnType == "QString":
            pass
        else:
            logger.error("Unknown return type %s encountered when "
                          "retrieving settings." % self.returnType)

        if not status:
            if not self.errorMsg:
                self.errorMsg = "Settings Error: Failed to retrieve " \
                                "default values for " + self.defaultName
            logger.error(self.errorMsg)

        return value



    @value.setter
    def value(self, setting):
        """ Store the value of property. """

        self._main_setter(self.sessionName, setting)


    
    def make_settings_default(self):
        """ Make the current session settings the default. """

        value = self.settings.value(self.sessionName)
        self.settings.setValue(self.defaultName, value)



    def _main_setter(self, name, value):
        """ This function does the actual setting. """

        # for font settings we check that they exist
        if self.returnType == "QFont":
            if fontDatabase_has_font(value):
                fontString = value
                self.settings.setValue(name, fontString)
        else:
            self.settings.setValue(name, value)




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
    
    return (font.family() in families)
