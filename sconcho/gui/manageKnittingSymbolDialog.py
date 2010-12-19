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

from functools import partial

from PyQt4.QtCore import (QStringList, SIGNAL, Qt, QDir, QByteArray,
                          QString, QRegExp)
from PyQt4.QtGui import (QDialog, QTreeWidgetItem, QFileDialog, 
                         QMessageBox)
from PyQt4.QtSvg import (QSvgWidget)

from gui.ui_manageKnittingSymbolDialog import Ui_ManageKnittingSymbolDialog
from util.symbolParser import (parse_all_symbols, create_new_symbol,
                               remove_symbol, move_symbol, remove_directory)
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
        self._selectedSymbol = None


        # add connections
        self.connect(self.availableSymbolsWidget, 
                     SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
                     self.update_selected_symbol_display)

        self.connect(self.clearEntriesButton, SIGNAL("clicked()"),
                     self.clear_add_symbol_tab)

        self.connect(self.addSymbolButton, SIGNAL("clicked()"),
                     self.add_symbol)

        self.connect(self.deleteSymbolButton, SIGNAL("clicked()"),
                     self.delete_symbol)

        self.connect(self.updateSymbolButton, SIGNAL("clicked()"),
                     self.update_symbol)

        self.connect(self.browseSymbolButton_A, SIGNAL("clicked()"),
                     self.load_svg_in_add_tab)

        self.connect(self.symbolWidthSpinner_A, SIGNAL("valueChanged(int)"),
                     partial(self.rescale_svg_item, self.svgWidget_A))

        self.connect(self.symbolWidthSpinner_U, SIGNAL("valueChanged(int)"),
                     partial(self.rescale_svg_item, self.svgWidget_U))



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
            self._selectedSymbol = symbol
            self.show_selected_symbol_info(symbol)
        else:
            self._selectedSymbol = None
            self.clear_symbol_info()



    def show_selected_symbol_info(self, symbol):
        """ Show info for symbol on update/delete widget tab."""

        pathToSvgImage = generate_svg_path(self._symbolPath, symbol)
        self.svgWidget_U.load(pathToSvgImage)
        self.svgPathEdit_U.setText(pathToSvgImage)

        self.symbolNameLabel_U.setDisabled(False)
        self.symbolNameEntry_U.setReadOnly(False)
        self.symbolNameEntry_U.setText(symbol["name"])

        self.symbolCategoryLabel_U.setDisabled(False)
        self.symbolCategoryEntry_U.setReadOnly(False)
        self.symbolCategoryEntry_U.setText(symbol["category"])

        self.symbolWidthLabel_U.setDisabled(False)
        self.symbolWidthSpinner_U.setReadOnly(False)
        width, status = symbol["width"].toInt()
        if status:
            self.symbolWidthSpinner_U.setDisabled(False)
            self.symbolWidthSpinner_U.setValue(width)
            self.rescale_svg_item(self.svgWidget_U, width)

        self.symbolDescriptionLabel_U.setDisabled(False)
        self.symbolDescriptionEntry_U.setReadOnly(False)
        self.symbolDescriptionEntry_U.setText(symbol["description"])

        self.updateSymbolButton.setDisabled(False)
        self.deleteSymbolButton.setDisabled(False)
        self.browseSymbolButton_U.setDisabled(False)



    def clear_symbol_info(self):
        """ Clear the the update/delete widget tab. """

        self.svgWidget_U.load(QByteArray())

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

        self.updateSymbolButton.setDisabled(True)
        self.deleteSymbolButton.setDisabled(True)
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



    def delete_symbol(self):
        """ This slot deletes the currently selected symbol.
        We pop up a confirmation dialog just to make sure ;)
        """
      
        # should never occur, but what the heck
        if not self._selectedSymbol:
            return

        name = self._selectedSymbol["name"]
        answer = QMessageBox.question(self,
                                      msg.deleteSymbolTitle, 
                                      msg.deleteSymbolText % name,
                                      QMessageBox.Ok | QMessageBox.Cancel)

        if answer == QMessageBox.Cancel:
            return

        svgName = self._selectedSymbol["svgName"]
        status = remove_symbol(self._symbolPath, svgName)

        if status:
            print("all went well")



    def update_symbol(self):
        """ This slot is implemented via delete and then add.
        When deleting we first check that we have valid data,
        then delete, then add.
        """

        if not self._selectedSymbol:
            return
        oldName = self._selectedSymbol["name"]

        svgImagePath = self.svgPathEdit_U.text()
        data = self._get_data_from_interface(svgImagePath,
                                       self.symbolNameEntry_U,
                                       self.symbolCategoryEntry_U,
                                       self.symbolDescriptionEntry_U,
                                       self.symbolWidthSpinner_U)

        if data:
            createOk = create_new_symbol(self._symbolPath + "/tmp/", 
                                         data["svgPath"],
                                         data["svgName"], 
                                         data["category"], 
                                         data["name"], 
                                         data["description"], 
                                         data["width"])
        
            # if creation of the new symbol succeeded we remove the old
            # data, otherwise we move it back in place
            if createOk:
                if remove_symbol(self._symbolPath, oldName):
                    if move_symbol(self._symbolPath, "/tmp/" + data["svgName"],
                            data["svgName"]):
                        if remove_directory(self._symbolPath + "/tmp/"):
                            self._update_dict(data)
                            self._update_symbols_widget(data)
                            self._update_tab(data)
                            return

        print("there was a problem updating")
            


    def _update_dict(self, data):
        """ Syncs the dictionary with the just updated data. """

        # convert width value from int to string
        data["width"] = QString("%d" % data["width"])
        symbolId = create_symbol_id(data["category"], data["name"])
        self._symbolDict[symbolId] = data



    def _update_symbols_widget(self, data):
        """ Synce the available symbols widget with the just updated data. """

        category = data["category"]
        name     = data["name"]

        item = self.availableSymbolsWidget.currentItem()
        item.setText(0, name)
        item.parent().setText(0, category)
        item.setData(0, Qt.UserRole, create_symbol_id(category, name))


    def _update_tab(self, data):
        """ Update the contents of the tab based on a content
        change. For now this could at most be a change in the svg
        image path due to a symbol name change.
        """

        pathToSvgImage = generate_svg_path(self._symbolPath, data)
        self.svgPathEdit_U.setText(pathToSvgImage)
       


    def add_symbol(self):
        """ This is a simple wrapper calling the worker member function
        with the proper interface widgets.
        """
        
        self._add_symbol_worker(self._svgFilePath_A,
                                self.symbolNameEntry_A,
                                self.symbolCategoryEntry_A,
                                self.symbolDescriptionEntry_A,
                                self.symbolWidthSpinner_A)


    
    def _add_symbol_worker(self, svgPathName, nameWidget, categoryWidget,
                           descriptionWidget, widthWidget):
        """ This function checks that all widgets have valid entries
        and if so creates the symbol.
        """


        data = self._get_data_from_interface(svgPathName, nameWidget, 
                                             categoryWidget, descriptionWidget, 
                                             widthWidget)

        # check that symbol is unique and new
        if create_symbol_id(data["category"], data["name"]) in self._symbolDict:
            QMessageBox.critical(None, msg.symbolExistsTitle,
                                 msg.symbolExistsText % (name, category),
                                 QMessageBox.Close)
            return 

        if data:
            createdOk = create_new_symbol(self._symbolPath, 
                                          data["svgPath"], 
                                          data["svgName"], 
                                          data["category"], 
                                          data["name"], 
                                          data["description"], 
                                          data["width"])
            if createdOk:
                self.clear_add_symbol_tab()



    def _get_data_from_interface(self, svgPathName, nameWidget, categoryWidget,
                                 descriptionWidget, widthWidget):
        """ This function extracts the data from the interface and checks
        that all is wel and present.
        """

        data = {}
        if not svgPathName:
            QMessageBox.critical(None, msg.noSvgFileErrorTitle,
                                 msg.noSvgFileErrorText,
                                 QMessageBox.Close)
            return None
        else:
            data["svgPath"] = svgPathName


        name = nameWidget.text()
        if not name:
            QMessageBox.critical(None, msg.noNameErrorTitle,
                                 msg.noNameErrorText,
                                 QMessageBox.Close)
            return None
        else:
            data["name"] = name
            
            # since we use this as a file path get rid of whitespace
            data["svgName"] = name.replace(QRegExp("\s"),"_")
       

        category = categoryWidget.text()
        if not category:
            QMessageBox.critical(None, msg.noCategoryErrorTitle,
                                 msg.noCategoryErrorText,
                                 QMessageBox.Close)
            return None
        else:
            data["category"] = category


        data["description"]  = descriptionWidget.toPlainText()
        data["width"]        = widthWidget.value()
        data["category_pos"] = QString("100000")

        return data

        

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
            self.rescale_svg_item(self.svgWidget_A, width)

        

    def rescale_svg_item(self, item, width):
        """ Rescales the svg image if a user changes the symbol width. """

        item.setFixedSize(ManageKnittingSymbolDialog.SYMBOL_SIZE * width,
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



def generate_svg_path(symbolTopDir, symbol):
    """ Generates the path to the svg image for the given symbol."""

    svgName = symbol["svgName"]
    path = symbolTopDir + "/" + svgName + "/" + svgName + ".svg"

    return path
