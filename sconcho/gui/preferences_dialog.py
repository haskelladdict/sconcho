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

from PyQt4.QtCore import (SIGNAL, QString, QDir)
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
        self.populate_interface()
        self.establish_connections()
        self.set_up_personal_symbol_path()

        self.connect(self.makeDefaultButton,
                     SIGNAL("pressed()"),
                     self.make_settings_the_default)


    def populate_interface(self):
        """ This function dispatches all members required
        to load the currently active session settings into the widget.

        """

        self.set_up_font_selectors()
        self.set_up_label_interval_selector()
        self.set_up_grid_properties()



    def establish_connections(self):
        """ This function dispatches all members required to establish
        widget connections.

        """

        self.set_up_font_selector_connections()
        self.set_up_label_interval_selector_connections()
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
        self.settings.labelInterval.make_settings_default()
        self.settings.gridCellWidth.make_settings_default()
        self.settings.gridCellHeight.make_settings_default()
        self.settings.highlightOddRows.make_settings_default()
        self.settings.highlightOddRowsColor.make_settings_default()
        self.settings.highlightOddRowsOpacity.make_settings_default()
        self.settings.personalSymbolPath.make_settings_default()



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
        (fontSize, status) = self.legendSizeComboBox.currentText().toInt()

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
        (fontSize, status) = self.labelSizeComboBox.currentText().toInt()

        fontDataBase  = QFontDatabase()
        newLabelFont = fontDataBase.font(fontFamily, fontStyle, fontSize)

        return newLabelFont

        

    def update_current_label_font(self):
        """ This function updates the currently active label font. """


        newLabelFont = self._get_label_font_from_widget()
        self.settings.labelFont.value = newLabelFont
        self.labelExampleText.setFont(newLabelFont)

        self.emit(SIGNAL("label_font_changed"))



    def set_up_label_interval_selector(self):
        """ Sets up the label interval selector. """
       
        interval = self.settings.labelInterval.value
        self.labelIntervalSpinner.setValue(interval)



    def set_up_label_interval_selector_connections(self):
        """ Set up connection for label interval selector. """
        
        self.connect(self.labelIntervalSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_label_interval)



    def change_label_interval(self, interval):
        """ Sets the new label interval and lets the canvas know. """

        self.settings.labelInterval.value = interval
        self.emit(SIGNAL("label_interval_changed"))




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



    def set_up_grid_properties(self):
        """ Initialize the grid properties. """
        
        self.gridCellWidthSpinner.setValue(self.settings.gridCellWidth.value)
        self.gridCellHeightSpinner.setValue(self.settings.gridCellHeight.value)

        # set up highlight checkbox
        checkState = self.settings.highlightOddRows.value
        self.oddRowHighlightCheck.setCheckState(checkState)

        # set up opacity
        opacity = self.settings.highlightOddRowsOpacity.value
        self.oddRowHighlightOpacitySpinner.setValue(opacity)

        self._update_highlight_button_color()



    def change_odd_row_highlight_color(self):
        """ Fire up a QColorDialog to change the color for
        hightlighting odd rows.

        """
        
        color = self.settings.highlightOddRowsColor.value
        newColor = QColorDialog.getColor(QColor(color), None,
                              "Select Highlight Color for Odd Rows")
        self.settings.highlightOddRowsColor.value = newColor.name()
        self._update_highlight_button_color()
        self.emit(SIGNAL("redraw_highlight_odd_rows"))


    def _update_highlight_button_color(self):
        """ Update the highlight button color with the currently
        active color.

        """

        color = self.settings.highlightOddRowsColor.value
        styleSheet = "background-color: " + color + ";"
        self.oddRowHighlightColorButton.setStyleSheet(styleSheet)



    def change_odd_row_highlight_opacity(self, newValue):
        """ Store new opacity setting request redrawing of
        chart.

        """
        
        self.settings.highlightOddRowsOpacity.value = newValue
        self.emit(SIGNAL("redraw_highlight_odd_rows"))



    def set_up_grid_properties_connections(self):
        """ Set up the connections for the grid properties tab. """
        
        self.connect(self.gridCellWidthSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.grid_cell_width_changed)

        self.connect(self.gridCellHeightSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.grid_cell_height_changed)

        self.connect(self.oddRowHighlightCheck,
                     SIGNAL("stateChanged(int)"),
                     self.highlight_odd_rows_toggled)

        self.connect(self.oddRowHighlightColorButton,
                     SIGNAL("pressed()"),
                     self.change_odd_row_highlight_color)

        self.connect(self.oddRowHighlightOpacitySpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_odd_row_highlight_opacity)


    def grid_cell_width_changed(self, newWidth):
        """ Slot taking care of changes to the width of grid cells. """

        self.settings.gridCellWidth.value = newWidth
        self.emit(SIGNAL("grid_cell_dimensions_changed"))  



    def grid_cell_height_changed(self, newHeight):
        """ Slot taking care of changes to the width of grid cells. """

        self.settings.gridCellHeight.value = newHeight
        self.emit(SIGNAL("grid_cell_dimensions_changed"))



    def highlight_odd_rows_toggled(self, state):
        """ This function propages checking/unchecking of the
        highlight odd rows selector.

        """
      
        self.settings.highlightOddRows.value = state
        self.emit(SIGNAL("highlight_odd_rows_changed"))
