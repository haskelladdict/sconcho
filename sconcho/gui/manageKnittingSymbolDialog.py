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

from PyQt4.QtCore import (QStringList, SIGNAL, Qt, QDir, QByteArray,
                          QString)
from PyQt4.QtGui import (QDialog, QTreeWidgetItem, QFileDialog, 
                         QMessageBox)
from PyQt4.QtSvg import (QSvgWidget)

from gui.ui_manageKnittingSymbolDialog import Ui_ManageKnittingSymbolDialog
from util.symbolParser import (parse_all_symbols, create_new_symbol)
import util.messages as msg
import gui.symbolWidget as symbolWidget


##########################################################################
#
# This Dialog allows users to manage their own knitting symbols for
# use in sconcho (adding, deleting, updating, ...)
#
##########################################################################
class ManageKnittingSymbolDialog(QDialog, Ui_ManageKnittingSymbolDialog):

    SYMBOL_SIZE = 30


    def __init__(self, symbolPath, parent = None):
        """ Initialize the dialog. """

        super(ManageKnittingSymbolDialog, self).__init__(parent)
        self.setupUi(self)

        # grab all symbols allready present
        self._symbolPath = symbolPath
        self._symbolDict = parse_all_symbols([symbolPath])
        self._add_symbols_to_widget()
        self._set_up_update_symbol_tab()
        self._set_up_add_symbol_tab()

        # do some initialisation
        self._svgFilePath_A = None


        # add connections
        self.connect(self.availableSymbolsWidget, 
                     SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
                     self.update_selected_symbol_display)

        self.connect(self.clearEntriesButton, SIGNAL("clicked()"),
                     self.clear_add_symbol_tab)

        self.connect(self.addSymbolButton, SIGNAL("clicked()"),
                     self.add_symbol)

        self.connect(self.browseSymbolButton_A, SIGNAL("clicked()"),
                     self.load_svg_in_add_tab)

        self.connect(self.symbolWidthSpinner_A, SIGNAL("valueChanged(int)"),
                     self.rescale_svg_item_A)



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
                symbolItem.setData(0, Qt.UserRole, 
                                   create_symbol_id(category, name))
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


    
    def add_symbol(self):
        """ This slot checks that the interface contains a valid
        symbol (all fields have some data and an svg image has been
        selected.
        """

        if not self._svgFilePath_A:
            QMessageBox.critical(None, msg.noSvgFileErrorTitle,
                                 msg.noSvgFileErrorText,
                                 QMessageBox.Close)
            return


        name = self.symbolNameEntry_A.text()
        if not name:
            QMessageBox.critical(None, msg.noNameErrorTitle,
                                 msg.noNameErrorText,
                                 QMessageBox.Close)
            return

        # we name the svg with the symbol name
        svgName = name
        
        category = self.symbolCategoryEntry_A.text()
        if not category:
            QMessageBox.critical(None, msg.noCategoryErrorTitle,
                                 msg.noCategoryErrorText,
                                 QMessageBox.Close)
            return

        # check that symbol is unique and new
        if create_symbol_id(category, name) in self._symbolDict:
            QMessageBox.critical(None, msg.symbolExistsTitle,
                                 msg.symbolExistsText % (name, category),
                                 QMessageBox.Close)
            #return

        description = self.symbolDescriptionEntry_A.toPlainText()
        width       = self.symbolWidthSpinner_A.value()

        status = create_new_symbol(self._symbolPath, self._svgFilePath_A, 
                                   svgName, category, name, description, 
                                   width)
        
        # clear the tab if we saved successfully
        if status:
            self.clear_add_symbol_tab()

        

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


        # add svg image and scale as requested by width spinbox
        # we have to check if loading of the svg succeeded
        self.svgWidget_A.load(filePath)
        if self.svgWidget_A.renderer().isValid():
            self._svgFilePath_A = filePath
            self.svgPathEdit_A.setText(filePath)
            width = self.symbolWidthSpinner_A.value()
            self.rescale_svg_item_A(width)

        

    def rescale_svg_item_A(self, width):
        """ Rescales the svg image if a user changes the symbol width. """

        self.svgWidget_A.setFixedSize(ManageKnittingSymbolDialog.SYMBOL_SIZE * width,
                                      ManageKnittingSymbolDialog.SYMBOL_SIZE)

       



###########################################################################
#
# some helper functions
#
###########################################################################

def create_symbol_id(category, name):
    """ Creates the ID corresponding to a symbol name and category
    for look up in the symbol dictionary.
    """

    return QString(category + "::" + name) 
