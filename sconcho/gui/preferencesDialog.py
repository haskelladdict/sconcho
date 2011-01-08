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

from PyQt4.QtCore import (SIGNAL, QString, QDir)
from PyQt4.QtGui import (QDialog, QFontDatabase, QFileDialog)

import sconcho.util.misc as misc
import sconcho.util.messages as msg
from sconcho.util.settings import (get_label_font, get_legend_font, 
                                   set_legend_font, set_label_font,
                                   get_label_interval, set_label_interval,
                                   get_grid_dimensions, set_grid_cell_width,
                                   set_grid_cell_height,
                                   get_personal_symbol_path,
                                   set_personal_symbol_path)
from sconcho.gui.ui_preferencesDialog import Ui_PreferencesDialog



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
        self.set_up_font_selectors()
        self.set_up_label_interval_selector()
        self.set_up_grid_dimension_selector()
        self.set_up_personal_symbol_path()



    def set_up_font_selectors(self):
        """ Extract the currently active font.

        Extract the font for labels and legend and set up
        the font selectors correspondingly.
        """

        legendFont = get_legend_font(self.settings)
        self.legendFontComboBox.setCurrentFont(legendFont)
        self.legendExampleText.setText(misc.get_random_knitting_quote())
        self.legendExampleText.setFont(legendFont)
        self.update_legend_font_display(legendFont)

        labelFont = get_label_font(self.settings)
        self.labelFontComboBox.setCurrentFont(labelFont)
        self.labelExampleText.setText(misc.get_random_knitting_quote())
        self.labelExampleText.setFont(labelFont)
        self.update_label_font_display(labelFont)

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



    def update_current_legend_font(self, index = None):
        """ This function updates the currently active legend font."""

        fontFamily = self.legendFontComboBox.currentFont().family()
        fontStyle  = self.legendStyleComboBox.currentText()
        (fontSize, status) = self.legendSizeComboBox.currentText().toInt()

        fontDataBase  = QFontDatabase()
        newLegendFont = fontDataBase.font(fontFamily, fontStyle, fontSize)
        set_legend_font(self.settings, newLegendFont)
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



    def update_current_label_font(self, index = None):
        """ This function updates the currently active label font."""

        fontFamily = self.labelFontComboBox.currentFont().family()
        fontStyle  = self.labelStyleComboBox.currentText()
        (fontSize, status) = self.labelSizeComboBox.currentText().toInt()

        fontDataBase  = QFontDatabase()
        newLabelFont = fontDataBase.font(fontFamily, fontStyle, fontSize)
        set_label_font(self.settings, newLabelFont)
        self.labelExampleText.setFont(newLabelFont)

        self.emit(SIGNAL("label_font_changed"))



    def set_up_label_interval_selector(self):
        """ Sets up the label interval selector. """
       
        interval = get_label_interval(self.settings)
        self.labelIntervalSpinner.setValue(interval)
        self.connect(self.labelIntervalSpinner,
                     SIGNAL("valueChanged(int)"),
                     self.change_label_interval)



    def change_label_interval(self, interval):
        """ Sets the new label interval and lets the canvas know. """

        set_label_interval(self.settings, interval)
        self.emit(SIGNAL("label_interval_changed"))




    def set_up_personal_symbol_path(self):
        """ Sets up the widget for changing the path where the
        user has stored her/his personal symbol paths.
        """

        symbolLocation = get_personal_symbol_path(self.settings)
        self.customSymbolPathEdit.setText(symbolLocation)

        self.connect(self.customSymbolPathEdit,
                     SIGNAL("textChanged(QString)"),
                     self.update_personal_symbol_path)

        self.connect(self.customSymbolPathButton,
                     SIGNAL("clicked()"),
                     self.show_symbol_path_fileSelector)



    def update_personal_symbol_path(self, newPath):
        """ Update the path to a user's custom symbol location. """

        set_personal_symbol_path(self.settings, newPath)



    def show_symbol_path_fileSelector(self):
        """ Open up a file selector dialog allowing a user to change
        the path to where the custom knitting symbols are.
        """

        customSymbolFilePath = QFileDialog.getExistingDirectory(self,
                                            msg.customSymbolPathDirectoryTitle,
                                            QDir.homePath())

        if customSymbolFilePath:
            set_personal_symbol_path(self.settings, customSymbolFilePath)
            self.customSymbolPathEdit.setText(customSymbolFilePath)


    def set_up_grid_dimension_selector(self):
        """ Initialize the selectors for grid cell height and width
        with the current value and connect the selectors to the
        proper slots.
        """

        cellDim = get_grid_dimensions(self.settings)

        self.gridCellWidthSpinner.setValue(cellDim.width())
        self.gridCellHeightSpinner.setValue(cellDim.height())


        self.connect(self.gridCellWidthSpinner,
                     SIGNAL("valueChanged(int)"),
                     self._grid_cell_width_changed)

        self.connect(self.gridCellHeightSpinner,
                     SIGNAL("valueChanged(int)"),
                     self._grid_cell_height_changed)

   

    def _grid_cell_width_changed(self, newWidth):
        """ Slot taking care of changes to the width of grid cells. """

        set_grid_cell_width(self.settings, newWidth)
        self.emit(SIGNAL("grid_cell_width_changed"), newWidth)  



    def _grid_cell_height_changed(self, newHeight):
        """ Slot taking care of changes to the width of grid cells. """

        set_grid_cell_height(self.settings, newHeight)
        self.emit(SIGNAL("grid_cell_height_changed"), newHeight)  
