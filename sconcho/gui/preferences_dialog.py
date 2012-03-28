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
 
from PyQt4.QtCore import (SIGNAL, QDir, QT_VERSION)
from PyQt4.QtGui import (QDialog, QFontDatabase, QFileDialog,
                         QColorDialog, QColor)

import sconcho.util.misc as misc
import sconcho.util.messages as msg
from sconcho.gui.ui_preferences_dialog import Ui_PreferencesDialog



##########################################################################
#
# This widget allows initiates the start of a new project/patter
# grid. Users can adjust the grid dimensions of the new pattern grid.
#
##########################################################################
class PreferencesDialog(QDialog, Ui_PreferencesDialog):


    def __init__(self, settings, parent = None):
        """ Initialize the dialog. """

        super(PreferencesDialog, self).__init__(parent)
        self.setupUi(self)

        self.settings = settings
        self.rowLabelsUnlocked = True
        self.populate_interface()
        self.establish_connections()

        self.connect(self.makeDefaultButton,
                     SIGNAL("pressed()"),
                     self.make_settings_the_default)


    def populate_interface(self):
        """ This function dispatches all members required
        to load the currently active session settings into the widget.

        """

        self.set_up_font_selectors()
        self.set_up_row_label_selectors()
        self.set_up_column_label_selectors()
        self.set_up_grid_properties()
        self.set_up_personal_symbol_path()
        self.set_up_logging()



    def establish_connections(self):
        """ This function dispatches all members required to establish
        widget connections.

        """

        self.set_up_font_selector_connections()
        self.set_up_row_label_selector_connections()
        self.set_up_column_label_selector_connections()
        self.set_up_grid_properties_connections()


        
    def set_up_font_selectors(self):
        """ Load widget with the currently active font. """

        legendFont = self.settings.legendFont.value
        self.legendFontComboBox.setCurrentFont(legendFont)
        self.legendExampleText.setText(misc.get_random_knitting_quote())
        self.legendExampleText.setFont(legendFont)
        self.update_legend_font_display(legendFont)

        labelFont = self.settings.labelFont.value
        self.labelFontComboBox.setCurrentFont(labelFont)
        self.labelExampleText.setText(misc.get_random_knitting_quote())
        self.labelExampleText.setFont(labelFont)
        self.update_label_font_display(labelFont)



    def set_up_font_selector_connections(self):
        """ Set up the connection for the font selectors. """

        self.connect(self.legendFontComboBox, 
                     SIGNAL("currentFontChanged(QFont)"),
                     self.update_legend_font_display)

        self.connect(self.labelFontComboBox, 
                     SIGNAL("currentFontChanged(QFont)"),
                     self.update_label_font_display)

        self.connect(self.legendFontComboBox, 
                     SIGNAL("currentIndexChanged(int)"),
                     self.update_current_legend_font)

        self.connect(self.legendStyleComboBox, 
                     SIGNAL("currentIndexChanged(int)"),
                     self.update_current_legend_font)

        self.connect(self.legendSizeComboBox, 
                     SIGNAL("currentIndexChanged(int)"),
                     self.update_current_legend_font)

        self.connect(self.labelFontComboBox, 
                     SIGNAL("currentIndexChanged(int)"),
                     self.update_current_label_font)

        self.connect(self.labelStyleComboBox, 
                     SIGNAL("currentIndexChanged(int)"),
                     self.update_current_label_font)

        self.connect(self.labelSizeComboBox, 
                     SIGNAL("currentIndexChanged(int)"),
                     self.update_current_label_font)



    def make_settings_the_default(self):
        """ Stores the currently selected properties as the default. """

        self.settings.legendFont.make_settings_default()
        self.settings.labelFont.make_settings_default()

        self.settings.showRowLabels.make_settings_default()
        self.settings.rowLabelMode.make_settings_default()
        self.settings.rowLabelsShowInterval.make_settings_default()
        self.settings.rowLabelsShowIntervalStart.make_settings_default()
        self.settings.rowLabelStart.make_settings_default()
        self.settings.evenRowLabelLocation.make_settings_default()
        self.settings.oddRowLabelLocation.make_settings_default()

        self.settings.showColumnLabels.make_settings_default()
        self.settings.columnLabelMode.make_settings_default()
        self.settings.columnLabelsShowInterval.make_settings_default()
        self.settings.columnLabelsShowIntervalStart.make_settings_default()

        self.settings.gridCellWidth.make_settings_default()
        self.settings.gridCellHeight.make_settings_default()
        self.settings.highlightRows.make_settings_default()
        self.settings.highlightRowsColor.make_settings_default()
        self.settings.highlightRowsOpacity.make_settings_default()
        self.settings.highlightRowsStart.make_settings_default()
        self.settings.snapPatternRepeatToGrid.make_settings_default()

        self.settings.personalSymbolPath.make_settings_default()
        self.settings.loggingPath.make_settings_default()
        self.settings.doLogging.make_settings_default()



    def update_legend_font_display(self, newLegendFont):
        """ Update the displayed font properties for a newly 
        selected legend font.
        
        Updated properties are font style, size, example text.
        
        """

        # block signals from to avoid that update_current_legend_font
        # is called multiple times. We'll call it once at the end
        self.legendStyleComboBox.blockSignals(True)
        self.legendSizeComboBox.blockSignals(True)

        fontFamily = newLegendFont.family()
        fontDatabase = QFontDatabase()

        availableStyles  = fontDatabase.styles(fontFamily)
        targetStyle      = fontDatabase.styleString(newLegendFont)
        targetStyleIndex = 0

        # FIXME: There seems to be a bug in Qt 4.8 
        # "Normal" styleStrings are "Regular" in styles leading to
        # a mismatch below
        if QT_VERSION >= 0x040800:
            if targetStyle == "Normal":
                targetStyle = "Regular"

        self.legendStyleComboBox.clear()
        for (index, style) in enumerate(availableStyles):
            self.legendStyleComboBox.addItem(style)
            
            if targetStyle == style:
                targetStyleIndex = index

        self.legendStyleComboBox.setCurrentIndex(targetStyleIndex)

        availableSizes  = fontDatabase.pointSizes(fontFamily)
        targetSize      = newLegendFont.pointSize()
        targetSizeIndex = 0
        self.legendSizeComboBox.clear()
        for (index, size) in enumerate(availableSizes):
            self.legendSizeComboBox.addItem(QString(unicode(size)))

            if targetSize == size:
                targetSizeIndex = index

        self.legendSizeComboBox.setCurrentIndex(targetSizeIndex)
       
        self.update_current_legend_font()

        # turn signals back on
        self.legendStyleComboBox.blockSignals(False)
        self.legendSizeComboBox.blockSignals(False)



    def _get_legend_font_from_widget(self):
        """ Helper function extracting the currently selected
        legend font info from the widget.

        """

        fontFamily = self.legendFontComboBox.currentFont().family()
        fontStyle  = self.legendStyleComboBox.currentText()
        if self.legendSizeComboBox.currentText():
            (fontSize, status) = self.legendSizeComboBox.currentText().toInt()
        else: 
            fontSize = 20

        fontDataBase  = QFontDatabase()
        newLegendFont = fontDataBase.font(fontFamily, fontStyle, fontSize)

        return newLegendFont



    def update_current_legend_font(self):
        """ This function updates the currently active legend font. """

        newLegendFont = self._get_legend_font_from_widget()
        self.settings.legendFont.value = newLegendFont
        self.legendExampleText.setFont(newLegendFont)

        self.emit(SIGNAL("legend_font_changed"))


 
    def update_label_font_display(self, newLabelFont):
        """ Update the displayed font properties for a newly 
        selected label font.
        
        Updated properties are font style, size, example text.
        
        """

        # block signals from to avoid that update_current_label_font
        # is called multiple times. We'll call it once at the end
        self.labelStyleComboBox.blockSignals(True)
        self.labelSizeComboBox.blockSignals(True)

        fontFamily = newLabelFont.family()
        fontDatabase = QFontDatabase()

        availableStyles  = fontDatabase.styles(fontFamily)
        targetStyle      = fontDatabase.styleString(newLabelFont)
        targetStyleIndex = 0

        # FIXME: There seems to be a bug in Qt 4.8 
        # "Normal" styleStrings are "Regular" in styles leading to
        # a mismatch below
        if QT_VERSION >= 0x040800:
            if targetStyle == "Normal":
                targetStyle = "Regular"

        self.labelStyleComboBox.clear()
        for (index, style) in enumerate(availableStyles):
            self.labelStyleComboBox.addItem(style)
            
            if targetStyle == style:
                targetStyleIndex = index

        self.labelStyleComboBox.setCurrentIndex(targetStyleIndex)

        availableSizes  = fontDatabase.pointSizes(fontFamily)
        targetSize      = newLabelFont.pointSize()
        targetSizeIndex = 0
        self.labelSizeComboBox.clear()
        for (index, size) in enumerate(availableSizes):
            self.labelSizeComboBox.addItem(QString(unicode(size)))

            if targetSize == size:
                targetSizeIndex = index

        self.labelSizeComboBox.setCurrentIndex(targetSizeIndex)
       
        self.update_current_label_font()

        # turn signals back on
        self.labelStyleComboBox.blockSignals(False)
        self.labelSizeComboBox.blockSignals(False)



    def _get_label_font_from_widget(self):
        """ Helper function extracting the currently selected
        labels font info from the widget.

        """

        fontFamily = self.labelFontComboBox.currentFont().family()
        fontStyle  = self.labelStyleComboBox.currentText()
        if self.labelSizeComboBox.currentText():
            (fontSize, status) = self.labelSizeComboBox.currentText().toInt()
        else:
            fontSize = 20

        fontDataBase  = QFontDatabase()
        newLabelFont = fontDataBase.font(fontFamily, fontStyle, fontSize)

        return newLabelFont

        

    def update_current_label_font(self):
        """ This function updates the currently active label font. """


        newLabelFont = self._get_label_font_from_widget()
        self.settings.labelFont.value = newLabelFont
        self.labelExampleText.setFont(newLabelFont)

        self.emit(SIGNAL("label_font_changed"))
    


    def allow_all_label_options(self, status):
        """ Toggle status of allowing all row label options """

        self.rowLabelsUnlocked = status

        self.rowLabelsIntervalSpinner.setEnabled(status)
        self.rowLabelsIntervalStartSpinner.setEnabled(status)
        self.rowLabelsStartLabel.setEnabled(status)
        self.showRowsWithIntervalButton.setEnabled(status)

        # since these are mutually exclusive we have to be 
        # a bit more careful here
        if status == False:
            self.showOddRowsButton.setEnabled(status)
            self.showEvenRowsButton.setEnabled(status)
            self.labelAllRowsButton.click()
        else:
            rowLabelStart = self.settings.rowLabelStart.value
            self._adjust_row_label_selectors(rowLabelStart)



    def set_up_row_label_selectors(self):
        """ Sets up the label interval selectors and 
        start of the row labels 

        """

        intervalType = self.settings.rowLabelMode.value
        self.labelAllRowsButton.setChecked(True)
        if intervalType == "SHOW_EVEN_ROWS":
            self.showEvenRowsButton.setChecked(True)
        elif intervalType == "SHOW_ODD_ROWS":
            self.showOddRowsButton.setChecked(True)
        elif intervalType == "SHOW_ROWS_WITH_INTERVAL":
            self.showRowsWithIntervalButton.setChecked(True)

        rowLabelStart = self.settings.rowLabelStart.value

        self.rowLabelStartSpinner.setValue(rowLabelStart)
        self._adjust_row_label_selectors(rowLabelStart)

        rowInterval = self.settings.rowLabelsShowInterval.value
        self.rowLabelsIntervalSpinner.blockSignals(True)
        self.rowLabelsIntervalSpinner.setValue(rowInterval)
        self.rowLabelsIntervalSpinner.blockSignals(False)
        
        rowShowInterval = self.settings.rowLabelsShowIntervalStart.value
        self.rowLabelsIntervalStartSpinner.setValue(rowShowInterval)

        evenRowLabelLocation = self.settings.evenRowLabelLocation.value
        if evenRowLabelLocation == "RIGHT_OF":
            self.evenRowLabelLocationComboBox.setCurrentIndex(0)
        else:
            self.evenRowLabelLocationComboBox.setCurrentIndex(1)
    
        oddRowLabelLocation = self.settings.oddRowLabelLocation.value
        if oddRowLabelLocation == "RIGHT_OF":
            self.oddRowLabelLocationComboBox.setCurrentIndex(0)
        else:
            self.oddRowLabelLocationComboBox.setCurrentIndex(1)
    


    def set_up_row_label_selector_connections(self):
        """ Set up connections for row labels. """

        self.connect(self.showRowLabelChecker, 
                     SIGNAL("clicked(bool)"),
                     self.change_row_label_visibility)

        self.connect(self.labelAllRowsButton,
                     SIGNAL("clicked(bool)"),
                     partial(self.change_row_label_interval, 
                             "LABEL_ALL_ROWS"))

        self.connect(self.showRowsWithIntervalButton,
                     SIGNAL("clicked(bool)"),
                     partial(self.change_row_label_interval, 
                             "SHOW_ROWS_WITH_INTERVAL"))

        self.connect(self.rowLabelsIntervalSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_row_label_interval_properties)

        self.connect(self.rowLabelsIntervalStartSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_row_label_interval_properties)

        self.connect(self.showEvenRowsButton,
                     SIGNAL("clicked(bool)"),
                     partial(self.change_row_label_interval, 
                             "SHOW_EVEN_ROWS"))

        self.connect(self.showOddRowsButton,
                     SIGNAL("clicked(bool)"),
                     partial(self.change_row_label_interval, 
                             "SHOW_ODD_ROWS"))

        self.connect(self.rowLabelStartSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_row_label_start) 

        self.connect(self.evenRowLabelLocationComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.change_even_row_label_location) 

        self.connect(self.oddRowLabelLocationComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.change_odd_row_label_location) 


    
    def change_row_label_visibility(self, status):
        """ Toggle the visibility of the row labels. """

        if status:
            self.settings.showRowLabels.value = 1
        else:
            self.settings.showRowLabels.value = 0
        self.emit(SIGNAL("toggle_rowLabel_visibility(bool)"), status)


    

    def change_row_label_interval(self, state, clicked):
        """ Sets the new row label state and lets the canvas know. """

        self.settings.rowLabelMode.value = state 
        if state == "SHOW_ROWS_WITH_INTERVAL":
            self.settings.rowLabelsShowInterval.value = \
                self.rowLabelsIntervalSpinner.value()
            self.settings.rowLabelsShowIntervalStart.value = \
                self.rowLabelsIntervalStartSpinner.value()

        self.emit(SIGNAL("row_label_interval_changed"))


    
    def change_row_label_interval_properties(self):
        """ Changes the values of the row label interval properties. """

        self.settings.rowLabelsShowInterval.value = \
            self.rowLabelsIntervalSpinner.value()
        self.settings.rowLabelsShowIntervalStart.value = \
            self.rowLabelsIntervalStartSpinner.value()

        self.emit(SIGNAL("row_label_interval_changed"))



    def change_row_label_start(self, start):
        """ Sets the new row label start and lets the canvas know. """

        if self.rowLabelsUnlocked:
            self._adjust_row_label_selectors(start)
        self.settings.rowLabelStart.value = start
        self.emit(SIGNAL("row_label_start_changed"), start)


    
    def _adjust_row_label_selectors(self, start):
        """ Adjust the row label property selectors. 

        If row labels start at an even number, the
        "odd row labels only" selection is invalid and has to be
        grayed out. If it was selected we unselect it and select
        the "even row labels only". The converse holds for an odd
        label start.

        """
       
        if ((start % 2) == 0): 
           self.showOddRowsButton.setEnabled(False)
           self.showEvenRowsButton.setEnabled(True)
           if (self.showOddRowsButton.isChecked()):
               self.showEvenRowsButton.click()
        elif ((start % 2) != 0):
           self.showOddRowsButton.setEnabled(True)
           self.showEvenRowsButton.setEnabled(False)
           if (self.showEvenRowsButton.isChecked()):
               self.showOddRowsButton.click()


    
    def change_even_row_label_location(self, value):
        """ Sets the location of the even row labels. """

        locationString = "RIGHT_OF"
        if value != 0:
            locationString = "LEFT_OF"

        self.settings.evenRowLabelLocation.value = locationString
        self.emit(SIGNAL("row_label_location_changed"))



    def change_odd_row_label_location(self, value):
        """ Sets the location of the odd row labels. """

        locationString = "RIGHT_OF"
        if value != 0:
            locationString = "LEFT_OF"

        self.settings.oddRowLabelLocation.value = locationString
        self.emit(SIGNAL("row_label_location_changed"))


    
    def set_up_column_label_selectors(self):
        """ Sets up the column label interval selectors. """
       
        intervalType = self.settings.columnLabelMode.value
        self.labelAllColumnsButton.setChecked(True)
        if intervalType == "SHOW_COLUMNS_WITH_INTERVAL":
            self.showColumnsWithIntervalButton.setChecked(True)

        columnInterval = \
            self.settings.columnLabelsShowInterval.value
        self.columnLabelsIntervalSpinner.blockSignals(True)
        self.columnLabelsIntervalSpinner.setValue(columnInterval)
        self.columnLabelsIntervalSpinner.blockSignals(False)

        columnShowInterval = \
            self.settings.columnLabelsShowIntervalStart.value
        self.columnLabelsIntervalStartSpinner.setValue(columnShowInterval)



    def set_up_column_label_selector_connections(self):
        """ Set up connections for column labels. """
        
        self.connect(self.showColumnLabelChecker, 
                     SIGNAL("clicked(bool)"),
                     self.change_column_label_visibility)

        self.connect(self.labelAllColumnsButton,
                     SIGNAL("clicked(bool)"),
                     partial(self.change_column_label_interval, 
                             "LABEL_ALL_COLUMNS"))

        self.connect(self.showColumnsWithIntervalButton,
                     SIGNAL("clicked(bool)"),
                     partial(self.change_column_label_interval, 
                             "SHOW_COLUMNS_WITH_INTERVAL"))

        self.connect(self.columnLabelsIntervalSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_column_label_interval_properties)

        self.connect(self.columnLabelsIntervalStartSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_column_label_interval_properties)


 
    def change_column_label_visibility(self, status):
        """ Toggle the visibility of the column labels. """

        if status:
            self.settings.showColumnLabels.value = 1
        else:
            self.settings.showColumnLabels.value = 0
        self.emit(SIGNAL("toggle_columnLabel_visibility(bool)"), status)



    def change_column_label_interval(self, state, clicked):
        """ Sets the new column label state and lets the canvas know. """

        self.settings.columnLabelMode.value = state 
        if state == "SHOW_COLUMNS_WITH_INTERVAL":
            self.settings.columnLabelsShowInterval.value = \
                self.columnLabelsIntervalSpinner.value()
            self.settings.columnLabelsShowIntervalStart.value = \
                self.columnLabelsIntervalStartSpinner.value()

        self.emit(SIGNAL("column_label_interval_changed"))


    
    def change_column_label_interval_properties(self):
        """ Changes the values of the column label interval properties. """

        self.settings.columnLabelsShowInterval.value = \
            self.columnLabelsIntervalSpinner.value()
        self.settings.columnLabelsShowIntervalStart.value = \
            self.columnLabelsIntervalStartSpinner.value()

        self.emit(SIGNAL("column_label_interval_changed"))



    def set_up_personal_symbol_path(self):
        """ Sets up the widget for changing the path where the
        user has stored her/his personal symbol paths.
        
        """

        symbolLocation = self.settings.personalSymbolPath.value
        self.customSymbolPathEdit.setText(symbolLocation)

        self.connect(self.customSymbolPathEdit,
                     SIGNAL("textChanged(QString)"),
                     self.update_personal_symbol_path)

        self.connect(self.customSymbolPathButton,
                     SIGNAL("clicked()"),
                     self.show_symbol_path_fileSelector)


        
    def update_personal_symbol_path(self, newPath):
        """ Update the path to a user's custom symbol location. """

        self.settings.personalSymbolPath.value = newPath



    def show_symbol_path_fileSelector(self):
        """ Open up a file selector dialog allowing a user to change
        the path to where the custom knitting symbols are.
        
        """

        customSymbolFilePath = QFileDialog.getExistingDirectory(self,
                                      msg.customSymbolPathDirectoryTitle,
                                      QDir.homePath())

        if customSymbolFilePath:
            self.settings.personalSymbolPath.value = customSymbolFilePath
            self.customSymbolPathEdit.setText(customSymbolFilePath)




    def set_up_logging(self):
        """ Sets up the widget items for enabling logging and setting
        the logging path.
        
        """

        loggingPath = self.settings.loggingPath.value
        self.loggingPathEdit.setText(loggingPath)

        self.connect(self.loggingPathEdit,
                     SIGNAL("textChanged(QString)"),
                     self.update_logging_path)

        self.connect(self.loggingPathButton,
                     SIGNAL("clicked()"),
                     self.show_logging_path_fileSelector)

        doLogging = self.settings.doLogging.value
        self.enableLoggingChecker.setChecked(doLogging)

        self.connect(self.enableLoggingChecker,
                    SIGNAL("clicked(bool)"),
                    self.update_logging_status)



    def update_logging_path(self, newPath):
        """ Update the path to where log files are stored. """

        self.settings.loggingPath.value = newPath



    def show_logging_path_fileSelector(self):
        """ Open up a file selector dialog allowing a user to change
        the path to where logfiles are stored.
        
        """

        loggingPath = QFileDialog.getExistingDirectory(self,
                                      msg.loggingPathDirectoryTitle,
                                      QDir.homePath())

        if loggingPath:
            self.settings.loggingPath.value = loggingPath
            self.loggingPathEdit.setText(loggingPath)



    def update_logging_status(self, status):
        """ Update the path to where log files are stored. """

        self.settings.doLogging.value = int(status)



    def set_up_grid_properties(self):
        """ Initialize the grid properties. """
        
        self.gridCellWidthSpinner.setValue(self.settings.gridCellWidth.value)
        self.gridCellHeightSpinner.setValue(self.settings.gridCellHeight.value)

        # set up highlight checkbox
        checkState = (False if self.settings.highlightRows.value == 0 \
            else True)
        self.rowHighlightChecker.setChecked(checkState)

        # set up highlight start row
        rowStart = self.settings.highlightRowsStart.value
        self.highlightRowStartComboBox.setCurrentIndex(rowStart)

        # set up opacity
        opacity = self.settings.highlightRowsOpacity.value
        self.highlightRowOpacitySpinner.setValue(opacity)

        self._update_highlight_button_color()

        # set up snap pattern repeat to grid
        snapValue = self.settings.snapPatternRepeatToGrid.value
        self.snapPatternRepeatChecker.setCheckState(snapValue)



    def change_row_highlight_color(self):
        """ Fire up a QColorDialog to change the color for
        hightlighting odd rows.

        """
        
        color = self.settings.highlightRowsColor.value
        newColor = QColorDialog.getColor(QColor(color), None,
                              "Select color for row highlighting")
        self.settings.highlightRowsColor.value = newColor.name()
        self._update_highlight_button_color()
        self.emit(SIGNAL("redraw_highlighted_rows"))


    def _update_highlight_button_color(self):
        """ Update the highlight button color with the currently
        active color.

        """

        color = self.settings.highlightRowsColor.value
        styleSheet = "background-color: " + color + ";"
        self.highlightRowColorButton.setStyleSheet(styleSheet)



    def change_row_highlight_opacity(self, newValue):
        """ Store new opacity setting request redrawing of
        chart.

        """
        
        self.settings.highlightRowsOpacity.value = newValue
        self.emit(SIGNAL("redraw_highlighted_rows"))



    def highlight_rows_toggled(self, state):
        """ This function propages checking/unchecking of the
        highlight odd rows selector.

        """
      
        if state:
            self.settings.highlightRows.value = 1
        else:
            self.settings.highlightRows.value = 0

        self.emit(SIGNAL("highlighted_row_visibility_changed"))



    def highlight_rows_start_toggled(self, state):
        """ This function propages the start row for highlighting """
      
        self.settings.highlightRowsStart.value = state
        self.emit(SIGNAL("redraw_highlighted_rows"))



    def change_snap_pattern_repeat_to_grid_state(self, newState):
        """ Set the new snap to grid value (on/off) """

        self.settings.snapPatternRepeatToGrid.value = newState



    def set_up_grid_properties_connections(self):
        """ Set up the connections for the grid properties tab. """
        
        self.connect(self.gridCellWidthSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.grid_cell_width_changed)

        self.connect(self.gridCellHeightSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.grid_cell_height_changed)

        self.connect(self.rowHighlightChecker,
                     SIGNAL("clicked(bool)"),
                     self.highlight_rows_toggled)

        self.connect(self.highlightRowStartComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.highlight_rows_start_toggled)

        self.connect(self.highlightRowColorButton,
                     SIGNAL("pressed()"),
                     self.change_row_highlight_color)

        self.connect(self.highlightRowOpacitySpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_row_highlight_opacity)

        self.connect(self.snapPatternRepeatChecker,
                     SIGNAL("stateChanged(int)"),
                     self.change_snap_pattern_repeat_to_grid_state)



    def grid_cell_width_changed(self, newWidth):
        """ Slot taking care of changes to the width of grid cells. """

        self.settings.gridCellWidth.value = newWidth
        self.emit(SIGNAL("grid_cell_dimensions_changed"))  



    def grid_cell_height_changed(self, newHeight):
        """ Slot taking care of changes to the width of grid cells. """

        self.settings.gridCellHeight.value = newHeight
        self.emit(SIGNAL("grid_cell_dimensions_changed"))


