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
from tempfile import mkdtemp

from PyQt4.QtCore import (QStringList, SIGNAL, Qt, QDir, QByteArray,
                          QString, QRegExp)
from PyQt4.QtGui import (QDialog, QTreeWidgetItem, QFileDialog, 
                         QMessageBox)
from PyQt4.QtSvg import (QSvgWidget)

from sconcho.gui.ui_manageKnittingSymbolDialog import Ui_ManageKnittingSymbolDialog
from sconcho.util.symbolParser import (parse_all_symbols, create_new_symbol,
                                       remove_symbol, move_symbol, remove_directory)
import sconcho.util.messages as msg
import sconcho.gui.symbolWidget as symbolWidget


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

        self.symbolEntryFrame.setVisible(False)

        # grab all symbols allready present
        self._symbolPath = symbolPath
        self._symbolDict = parse_all_symbols([symbolPath])
        #self._set_up_update_symbol_tab()
        #self._set_up_add_symbol_tab()
        #self._add_symbols_to_widget()

        # do some initialisation
        self._svgFilePath_add = None
        
        # add connections
        """
        self.connect(self.availableSymbolsWidget, 
                     SIGNAL("currentItemChanged(QTreeWidgetItem*, \
                                                QTreeWidgetItem*)"),
                     self.update_selected_symbol_display)

        self.connect(self.clearEntriesButton, SIGNAL("clicked()"),
                     self.clear_add_symbol_tab)

        self.connect(self.addSymbolButton, SIGNAL("clicked()"),
                     self.add_symbol)

        self.connect(self.deleteSymbolButton, SIGNAL("clicked()"),
                     self.delete_symbol)

        self.connect(self.updateSymbolButton, SIGNAL("clicked()"),
                     self.update_symbol)

        self.connect(self.browseSymbolButton_add, SIGNAL("clicked()"),
                     self.load_svg_add)

        self.connect(self.browseSymbolButton_update, SIGNAL("clicked()"),
                     self.load_svg_update)

        self.connect(self.symbolWidthSpinner_add, SIGNAL("valueChanged(int)"),
                     partial(self.rescale_svg_item, self.svgWidget_add))

        self.connect(self.symbolWidthSpinner_update, SIGNAL("valueChanged(int)"),
                     partial(self.rescale_svg_item, self.svgWidget_update))
        """

        self.connect(self.addSymbolButton, SIGNAL("clicked()"),
                     self.add_new_symbol)


    def add_new_symbol(self):

        self.symbolEntryFrame.setVisible(True)



    def _add_symbols_to_widget(self):
        """ This function add all private knitting symbols to the list
        widget. Store the symbol id ("category::name") as UserDate so
        we can later more easily retrieve it from the database.
        """

        sortedSymbols = symbolWidget.sort_symbols_by_category(self._symbolDict)
        for entry in sortedSymbols:
            for symbol in entry[1]:
                self._add_symbol_to_tree_widget(symbol)



    def _set_up_update_symbol_tab(self):
        """ Do whatever additional initialization we need in the
        update symbol widget.
        """

        self.svgPathEdit_update.setText(QDir.homePath())



    def _set_up_add_symbol_tab(self):
        """ Do whatever additional initialization we need in the
        update symbol widget.
        """

        self.svgPathEdit_add.setText(QDir.homePath())


   
    def update_selected_symbol_display(self, newWidgetItem, 
                                       oldWidgetItem = None):
        """ Display the content of the currently selected symbol
        if one was selected (the user may have clicked on the category
        only). 
        """
        
        if not newWidgetItem:
            return

        symbolId = newWidgetItem.data(0, Qt.UserRole).toString()
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
        self.svgWidget_update.load(pathToSvgImage)
        self.svgPathEdit_update.setText(pathToSvgImage)

        self.symbolNameLabel_update.setDisabled(False)
        self.symbolNameEntry_update.setReadOnly(False)
        self.symbolNameEntry_update.setText(symbol["name"])

        self.symbolCategoryLabel_update.setDisabled(False)
        self.symbolCategoryEntry_update.setReadOnly(False)
        self.symbolCategoryEntry_update.setText(symbol["category"])

        self.symbolWidthLabel_update.setDisabled(False)
        self.symbolWidthSpinner_update.setReadOnly(False)
        width, status = symbol["width"].toInt()
        if status:
            self.symbolWidthSpinner_update.setDisabled(False)
            self.symbolWidthSpinner_update.setValue(width)
            self.rescale_svg_item(self.svgWidget_update, width)

        self.symbolDescriptionLabel_update.setDisabled(False)
        self.symbolDescriptionEntry_update.setReadOnly(False)
        self.symbolDescriptionEntry_update.setText(symbol["description"])

        self.updateSymbolButton.setDisabled(False)
        self.deleteSymbolButton.setDisabled(False)
        self.browseSymbolButton_update.setDisabled(False)



    def clear_symbol_info(self):
        """ Clear the the update/delete widget tab. """

        self.svgWidget_update.load(QByteArray())

        self.symbolNameLabel_update.setDisabled(True)
        self.symbolNameEntry_update.clear()
        self.symbolNameEntry_update.setReadOnly(True)

        self.symbolWidthLabel_update.setDisabled(True)
        self.symbolCategoryEntry_update.clear()
        self.symbolCategoryEntry_update.setReadOnly(True)
        self.symbolCategoryLabel_update.setDisabled(True)

        self.symbolWidthLabel_update.setDisabled(True)
        self.symbolWidthSpinner_update.clear()
        self.symbolWidthSpinner_update.setDisabled(True)
        self.symbolWidthSpinner_update.setReadOnly(True)

        self.symbolDescriptionLabel_update.setDisabled(True)
        self.symbolDescriptionEntry_update.clear()
        self.symbolDescriptionEntry_update.setReadOnly(True)

        self.updateSymbolButton.setDisabled(True)
        self.deleteSymbolButton.setDisabled(True)
        self.browseSymbolButton_update.setDisabled(True)



    def clear_add_symbol_tab(self):
        """ This slot clears all entries in the addSymbolTab """

        self.symbolNameEntry_add.clear()
        self.symbolCategoryEntry_add.clear()
        self.symbolWidthSpinner_add.setValue(1)
        self.symbolDescriptionEntry_add.clear()
        self.svgWidget_add.load(QByteArray())
        self.svgPathEdit_add.setText(QDir.homePath())
        self._svgFilePath_add = None



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

        # if we succeeded to remove the symbol from disk 
        # lets remove it from the interface and cached database as well
        if status:
            self._delete_symbol_from_database(self._selectedSymbol)
            self._delete_symbol_from_tree_widget(self._selectedSymbol)



    def _delete_symbol_from_database(self, symbol):
        """ Deletes the given symbol from the database. """

        category = self._selectedSymbol["category"]
        name     = self._selectedSymbol["name"]
        symbolID = create_symbol_id(category, name)
        del self._symbolDict[symbolID]



    def _delete_symbol_from_tree_widget(self, symbol):
        """ Delete the given symbol from the tree widget. If this
        was the last entry in a given category delete the whole
        category.
        """

        # find category
        category = symbol["category"]
        categoryItems = self.availableSymbolsWidget.findItems(category, 
                                                Qt.MatchExactly, 0)
        if len(categoryItems) != 1:
            print("Error: There are duplicate categories.")
        
        for categoryItem in categoryItems:

            # prune symbol itself
            name = symbol["name"]
        
            numChildren = categoryItem.childCount()
            for count in range(0, numChildren):
                child = categoryItem.child(count)

                if child.text(0) == name:
                    categoryItem.removeChild(child)
                    break
            
            if numChildren == 1:
                self.availableSymbolsWidget.removeItemWidget(categoryItem, 0)
                


    def update_symbol(self):
        """ This slot is implemented via delete and then add.
        When deleting we first check that we have valid data,
        then delete, then add.
        """

        if not self._selectedSymbol:
            return
        oldSymbol = self._selectedSymbol
        oldName = self._selectedSymbol["svgName"]

        svgImagePath = self.svgPathEdit_update.text()
        data = self._get_data_from_interface(svgImagePath,
                                       self.symbolNameEntry_update,
                                       self.symbolCategoryEntry_update,
                                       self.symbolDescriptionEntry_update,
                                       self.symbolWidthSpinner_update)

        if data:
            tempDir = mkdtemp(prefix=unicode(self._symbolPath))
            createOk = create_new_symbol(tempDir, 
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
                    if move_symbol(tempDir + "/" + data["svgName"], 
                                   self._symbolPath + "/" + data["svgName"]):
                        self._update_dict(data)
                        self._update_tree_widget(oldSymbol, data)
                        self._update_tab(data)
                        remove_directory(tempDir)
                        return
            else:
                # if we reach this point something went wrong during creation and
                # we try to at least remove the temp dir
                remove_directory(tempDir)




    def _update_dict(self, data):
        """ Syncs the dictionary with the just updated data. """

        # convert width value from int to string
        data["width"] = QString("%d" % data["width"])
        symbolId = create_symbol_id(data["category"], data["name"])
        self._symbolDict[symbolId] = data



    def _update_tree_widget(self, oldSymbol, newSymbol):
        """ Sync the available symbols widget with the just updated data. """

        self._add_symbol_to_tree_widget(newSymbol)
        self._delete_symbol_from_tree_widget(oldSymbol)



    def _update_tab(self, data):
        """ Update the contents of the tab based on a content
        change. For now this could at most be a change in the svg
        image path due to a symbol name change.
        """

        pathToSvgImage = generate_svg_path(self._symbolPath, data)
        self.svgPathEdit_update.setText(pathToSvgImage)
       


    def add_symbol(self):
        """ This is a simple wrapper calling the worker member function
        with the proper interface widgets.
        """
        
        self._add_symbol_worker(self._svgFilePath_add,
                                self.symbolNameEntry_add,
                                self.symbolCategoryEntry_add,
                                self.symbolDescriptionEntry_add,
                                self.symbolWidthSpinner_add)


    
    def _add_symbol_worker(self, svgPathName, nameWidget, categoryWidget,
                           descriptionWidget, widthWidget):
        """ This function checks that all widgets have valid entries
        and if so creates the symbol.
        """


        data = self._get_data_from_interface(svgPathName, nameWidget, 
                                             categoryWidget, descriptionWidget, 
                                             widthWidget)

        if not data:
            return

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
                self._update_dict(data)
                self._add_symbol_to_tree_widget(data)



    def _add_symbol_to_tree_widget(self, symbol):
        """ Add the given symbol to the tree widget. If this
        is a new category create it, otherwise append it
        to the already existing one.
        """

        # find category
        category = symbol["category"]
        categoryItems = self.availableSymbolsWidget.findItems(category, 
                                                Qt.MatchExactly, 0)

        name = symbol["name"]
        symbolItem = QTreeWidgetItem([name])
        symbolItem.setData(0, Qt.UserRole, 
                           create_symbol_id(category, name))
        symbolItem.setFlags(Qt.ItemIsSelectable | 
                            Qt.ItemIsUserCheckable | 
                            Qt.ItemIsEnabled)

        if categoryItems:
            categoryItems[0].addChild(symbolItem)        
        else:
            categoryItem = QTreeWidgetItem(self.availableSymbolsWidget, 
                                           [category])
            categoryItem.setFlags(Qt.ItemIsEnabled)
            categoryItem.addChild(symbolItem)

        self.availableSymbolsWidget.resizeColumnToContents(0)
        self.availableSymbolsWidget.sortItems(0, Qt.AscendingOrder)
        self.availableSymbolsWidget.setCurrentItem(symbolItem)
        self.update_selected_symbol_display(symbolItem)



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
            data["svgName"] = sanitize_name(QString(name))
       

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

        

    def load_svg_add(self):
        """ This methods loads an svg image from disk and 
        displays it in the add symbol tab.
        """

        filePath = QFileDialog.getOpenFileName(self, 
                                               "sconcho: Load svg image", 
                                               QDir.homePath(),
                                               "svg images (*.svg)") 

        if not filePath:
            return

        # add svg image and scale as requested by width spinbox
        # we have to check if loading of the svg succeeded
        self.svgWidget_add.load(filePath)
        if self.svgWidget_add.renderer().isValid():
            self._svgFilePath_add = filePath
            self.svgPathEdit_add.setText(filePath)
            width = self.symbolWidthSpinner_add.value()
            self.rescale_svg_item(self.svgWidget_add, width)



    def load_svg_update(self):
        """ This methods loads an svg image from disk and 
        displays it in the update symbol tab.
        """

        filePath = QFileDialog.getOpenFileName(self, 
                                               "sconcho: Load svg image", 
                                               QDir.homePath(),
                                               "svg images (*.svg)") 

        if not filePath:
            return


        # add svg image and scale as requested by width spinbox
        # we have to check if loading of the svg succeeded
        self.svgWidget_update.load(filePath)
        if self.svgWidget_update.renderer().isValid():
            self.svgPathEdit_update.setText(filePath)
            width = self.symbolWidthSpinner_update.value()
            self.rescale_svg_item(self.svgWidget_update, width)



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



def sanitize_name(name):
    """ This function sanitizes the knitting symbol name. The returned
    string will be used as the directory name where the symbol is located
    and will also be used for the filename of the svg image itself.
    """

    # replace all non word characters with underscores
    name.replace(QRegExp(r"\W"),"_")

    # replace consecutive stretches of underscores with a single one
    name.replace(QRegExp(r"[_]+"),"_")

    return name
