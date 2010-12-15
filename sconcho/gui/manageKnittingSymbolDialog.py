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

from PyQt4.QtCore import (QStringList, SIGNAL, Qt)
from PyQt4.QtGui import (QDialog, QTreeWidgetItem)

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

        # add connections
        self.connect(self.availableSymbolsWidget, 
                     SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
                     self.update_selected_symbol_display)



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
            for symbol in entry[1]:
                name = symbol["name"]
                symbolItem = QTreeWidgetItem([name])
                symbolItem.setData(0, Qt.UserRole, category + "::" + name) 
                categoryItem.addChild(symbolItem)        

        self.availableSymbolsWidget.resizeColumnToContents(0)
       

    
    def update_selected_symbol_display(self, widgetItem, col):
        """ Display the content of the currently selected symbol
        if one was selected (the user may have clicked on the category
        only). 
        """

        symbolId = widgetItem.data(col, Qt.UserRole).toString()
        if symbolId in self._symbolDict:

            symbol = self._symbolDict[symbolId]

            self.symbolNameLabel.setDisabled(False)
            self.symbolNameEntry.setReadOnly(False)
            self.symbolNameEntry.setText(symbol["name"])

            self.symbolCategoryLabel.setDisabled(False)
            self.symbolCategoryEntry.setReadOnly(False)
            self.symbolCategoryEntry.setText(symbol["category"])

            self.symbolWidthLabel.setDisabled(False)
            self.symbolWidthSpinner.setReadOnly(False)
            width, status = symbol["width"].toInt()
            self.symbolWidthSpinner.setValue(width)

            self.symbolDescriptionLabel.setDisabled(False)
            self.symbolDescriptionEntry.setReadOnly(False)
            self.symbolDescriptionEntry.setText(symbol["description"])

            self.updateSymbolButton.setDisabled(False)
            self.browseSymbolButton.setDisabled(False)

        else:

            self.symbolNameLabel.setDisabled(True)
            self.symbolNameEntry.clear()
            self.symbolNameEntry.setReadOnly(True)

            self.symbolWidthLabel.setDisabled(True)
            self.symbolCategoryEntry.clear()
            self.symbolCategoryEntry.setReadOnly(True)
            self.symbolCategoryLabel.setDisabled(True)

            self.symbolWidthLabel.setDisabled(True)
            self.symbolWidthSpinner.setValue(1)
            self.symbolWidthSpinner.setReadOnly(True)

            self.symbolDescriptionLabel.setDisabled(True)
            self.symbolDescriptionEntry.clear()
            self.symbolDescriptionEntry.setReadOnly(True)

            self.updateSymbolButton.setDisabled(True)
            self.browseSymbolButton.setDisabled(True)
