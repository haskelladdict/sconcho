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

from PyQt4.QtCore import (QStringList, SIGNAL, Qt, QDir, QByteArray)
from PyQt4.QtGui import (QDialog, QTreeWidgetItem, QFileDialog)
from PyQt4.QtSvg import (QSvgWidget)

from gui.ui_manageKnittingSymbolDialog import Ui_ManageKnittingSymbolDialog
import util.symbolParser as parser
import gui.symbolWidget as symbolWidget


##########################################################################
#
# This Dialog allows users to manage their own knitting symbols for
# use in sconcho (adding, deleting, updating, ...)
#
##########################################################################
class ManageKnittingSymbolDialog(QDialog, Ui_ManageKnittingSymbolDialog):


    def __init__(self, symbolPath, parent = None):
        """ Initialize the dialog. """

        super(ManageKnittingSymbolDialog, self).__init__(parent)
        self.setupUi(self)

        # grab all symbols allready present
        self._symbolDict = parser.parse_all_symbols([symbolPath])
        self._add_symbols_to_widget()
        self._set_up_update_symbol_tab()
        self._set_up_add_symbol_tab()

        # do some initialisation
        self._svgFilePath_A = None


        # add connections
        self.connect(self.availableSymbolsWidget, 
                     SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
                     self.update_selected_symbol_display)

        self.connect(self.clearEntryButton, SIGNAL("clicked()"),
                     self.clear_add_symbol_tab)

        self.connect(self.browseSymbolButton_A, SIGNAL("clicked()"),
                     self.load_svg_in_add_tab)



    def _add_symbols_to_widget(self):
        """ This function add all private knitting symbols to the list
        widget. Store the symbol id ("category::name") as UserDate so
        we can later more easily retrieve it from the database.
        """

        sortedSymbols = symbolWidget.sort_symbols_by_category(self._symbolDict)
        for entry in sortedSymbols:

            category = entry[0]
            categoryItem = QTreeWidgetItem(self.availableSymbolsWidget, 
                                           [category])
            categoryItem.setFlags(Qt.ItemIsEnabled)

            for symbol in entry[1]:
                name = symbol["name"]
                symbolItem = QTreeWidgetItem([name])
                symbolItem.setData(0, Qt.UserRole, category + "::" + name) 
                categoryItem.addChild(symbolItem)        
                symbolItem.setFlags(Qt.ItemIsSelectable | 
                                    Qt.ItemIsUserCheckable | 
                                    Qt.ItemIsEnabled)

        self.availableSymbolsWidget.resizeColumnToContents(0)
      


    def _set_up_update_symbol_tab(self):
        """ Do whatever additional initialization we need in the
        update symbol widget.
        """

        self.svgPathEdit_U.setText(QDir.homePath())



    def _set_up_add_symbol_tab(self):
        """ Do whatever additional initialization we need in the
        update symbol widget.
        """

        self.svgPathEdit_A.setText(QDir.homePath())


   
    def update_selected_symbol_display(self, widgetItem, col):
        """ Display the content of the currently selected symbol
        if one was selected (the user may have clicked on the category
        only). 
        """

        symbolId = widgetItem.data(col, Qt.UserRole).toString()
        if symbolId in self._symbolDict:

            symbol = self._symbolDict[symbolId]

            self.symbolNameLabel_U.setDisabled(False)
            self.symbolNameEntry_U.setReadOnly(False)
            self.symbolNameEntry_U.setText(symbol["name"])

            self.symbolCategoryLabel_U.setDisabled(False)
            self.symbolCategoryEntry_U.setReadOnly(False)
            self.symbolCategoryEntry_U.setText(symbol["category"])

            self.symbolWidthLabel_U.setDisabled(False)
            self.symbolWidthSpinner_U.setReadOnly(False)
            width, status = symbol["width"].toInt()
            self.symbolWidthSpinner_U.setDisabled(False)
            self.symbolWidthSpinner_U.setValue(width)

            self.symbolDescriptionLabel_U.setDisabled(False)
            self.symbolDescriptionEntry_U.setReadOnly(False)
            self.symbolDescriptionEntry_U.setText(symbol["description"])

            self.updateSymbolButton_U.setDisabled(False)
            self.browseSymbolButton_U.setDisabled(False)

        else:

            self.symbolNameLabel_U.setDisabled(True)
            self.symbolNameEntry_U.clear()
            self.symbolNameEntry_U.setReadOnly(True)

            self.symbolWidthLabel_U.setDisabled(True)
            self.symbolCategoryEntry_U.clear()
            self.symbolCategoryEntry_U.setReadOnly(True)
            self.symbolCategoryLabel_U.setDisabled(True)

            self.symbolWidthLabel_U.setDisabled(True)
            self.symbolWidthSpinner_U.clear()
            self.symbolWidthSpinner_U.setDisabled(True)
            self.symbolWidthSpinner_U.setReadOnly(True)

            self.symbolDescriptionLabel_U.setDisabled(True)
            self.symbolDescriptionEntry_U.clear()
            self.symbolDescriptionEntry_U.setReadOnly(True)

            self.updateSymbolButton_U.setDisabled(True)
            self.browseSymbolButton_U.setDisabled(True)



    def clear_add_symbol_tab(self):
        """ This slot clears all entries in the addSymbolTab """

        self.symbolNameEntry_A.clear()
        self.symbolCategoryEntry_A.clear()
        self.symbolWidthSpinner_A.setValue(1)
        self.symbolDescriptionEntry_A.clear()
        self.svgWidget_A.load(QByteArray())
        self.svgPathEdit_A.setText(QDir.homePath())
        self._svgFilePath_A = None

        

    def load_svg_in_add_tab(self):
        """ This methods loads an svg image from disk and 
        displays it inside the widget. 
        """

        filePath = QFileDialog.getOpenFileName(self, 
                                               "sconcho: Load svg image", 
                                               QDir.homePath(),
                                               "svg images (*.svg)") 

        if not filePath:
            return

        self._svgFilePath_A = filePath
        self.svgWidget_A.load(filePath)
        self.svgPathEdit_A.setText(filePath)

        


