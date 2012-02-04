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
from tempfile import mkdtemp

try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str

# QStringlist

from PyQt4.QtCore import (SIGNAL, Qt, QDir, QByteArray, QRegExp, QVariant)
from PyQt4.QtGui import (QDialog, QTreeWidgetItem, QFileDialog, 
                         QMessageBox, QInputDialog, QLineEdit)
from PyQt4.QtSvg import (QSvgWidget)

from sconcho.gui.ui_manage_symbol_dialog import Ui_ManageKnittingSymbolDialog
from sconcho.util.symbol_parser import (parse_all_symbols, 
                                        create_new_symbol,
                                        remove_symbol, move_symbol, 
                                        SymbolTempDir)
import sconcho.util.messages as msg
import sconcho.gui.symbol_widget as symbolWidget


##########################################################################
#
# This Dialog allows users to manage their own knitting symbols for
# use in sconcho (adding, deleting, updating, ...)
#
##########################################################################
class ManageSymbolDialog(QDialog, Ui_ManageKnittingSymbolDialog):

    SYMBOL_SIZE   = 30
    ADD_ACTION    = 1
    UPDATE_ACTION = 2


    def __init__(self, symbolPath, symbolCategories, parent = None):
        """ Initialize the dialog. """

        super(ManageSymbolDialog, self).__init__(parent)
        self.setupUi(self)

        self.symbolEntryFrame.setVisible(False)

        # do some initialisation
        self._svgFilePath      = None
        self._activeAction     = None
        self._selectedSymbol   = None
        self._symbolCategories = symbolCategories
        self._symbolCategories.sort()

        # main setup
        self._add_connections()
        self._symbolPath = symbolPath
        self._symbolDict = parse_all_symbols([symbolPath])
        self._set_up_symbols_frame()
        self._add_symbols_to_widget()
        self._populate_category_chooser()
        


    def add_new_symbol(self):
        """ This slot make the symbolEntryFrame visible and marks it
        as an 'add-symbol-frame'.
        
        """

        self.symbolEntryFrame.setVisible(True)
        self.actionButton.setText("Add Symbol")
        self._activeAction = ManageSymbolDialog.ADD_ACTION
        self.disable_selection_buttons()



    def done_with_input(self):
        """ This slot cancels the current input action. """

        self.symbolEntryFrame.setVisible(False)
        self.clear_symbol_info()
        self.enable_selection_buttons()
        self.availableSymbolsWidget.setDisabled(False)



    def disable_selection_buttons(self):
        """ Disables all selection buttons. """

        self.addSymbolButton.setEnabled(False)
        self.updateSymbolButton.setEnabled(False)
        self.deleteSymbolButton.setEnabled(False)



    def enable_selection_buttons(self):
        """ Enables all selection buttons that should be enabled. 
        Definitely the 'Add New Symbol' button and the update/delete
        button depending if a symbol is currently selected.
        
        """

        self.addSymbolButton.setEnabled(True)
        if self._selectedSymbol:
            self.updateSymbolButton.setEnabled(True)
            self.deleteSymbolButton.setEnabled(True)



    def _add_connections(self):
        """ Add all main gui connections. """

        self.connect(self.availableSymbolsWidget, 
                     SIGNAL("currentItemChanged(QTreeWidgetItem*, \
                                                QTreeWidgetItem*)"),
                     self.selected_symbol_changed)

        self.connect(self.symbolWidthSpinner, SIGNAL("valueChanged(int)"),
                     partial(self.rescale_svg_item, self.svgWidget))

        self.connect(self.cancelButton, SIGNAL("clicked()"),
                     self.done_with_input)

        self.connect(self.addSymbolButton, SIGNAL("clicked()"),
                     self.add_new_symbol)

        self.connect(self.actionButton, SIGNAL("clicked()"),
                     self.take_action)

        self.connect(self.browseSymbolButton, SIGNAL("clicked()"),
                     self.load_svg)

        self.connect(self.updateSymbolButton, SIGNAL("clicked()"),
                     self.show_selected_symbol_info)

        self.connect(self.deleteSymbolButton, SIGNAL("clicked()"),
                     self.delete_symbol)

        self.connect(self.categoryChooser, SIGNAL("currentIndexChanged(int)"),
                     self.category_changed)



    def _add_symbols_to_widget(self):
        """ This function add all private knitting symbols to the list
        widget. Store the symbol id ('category::name') as UserDate so
        we can later more easily retrieve it from the database.
        
        """

        sortedSymbols = symbolWidget.sort_symbols_by_category(self._symbolDict)
        for entry in sortedSymbols:
            for symbol in entry[1]:
                self._add_symbol_to_tree_widget(symbol)



    def _populate_category_chooser(self):
        """ Adds all categories we know of to the combo box. """

        self.categoryChooser.clear()
        for name in self._symbolCategories:
            self.categoryChooser.addItem(name)

        self.categoryChooser.addItem("other...", QVariant(1))


    
    def category_changed(self, index):
        """ This slot deals with changes to the selected category """

        itemText = self.categoryChooser.itemText(index)
        (itemData, dummy) = self.categoryChooser.itemData(index).toInt()

        if itemText == QString("other...") and itemData == 1:
              
            (newCategory, status) = \
                    QInputDialog.getText(self, 
                                "sconcho: New category",
                                "Please enter the name of the new category")

            if status and newCategory:
                self._symbolCategories.append(newCategory)
                self._symbolCategories.sort()
                self._populate_category_chooser()
                newCategoryIndex = self.categoryChooser.findText(newCategory)
                self.categoryChooser.setCurrentIndex(newCategoryIndex)
    



    def take_action(self):
        """ Dispatches the proper function depending if the
        user is adding or updating a symbol.
        
        """

        if self._activeAction == ManageSymbolDialog.ADD_ACTION:
            self.add_symbol()
        elif self._activeAction == ManageSymbolDialog.UPDATE_ACTION:
            self.update_symbol()



    def _set_up_symbols_frame(self):
        """ Do whatever additional initialization we need in the
        update symbol widget.

        """

        self.svgPathEdit.setText(QDir.homePath())


   
    def selected_symbol_changed(self, newWidgetItem, 
                                oldWidgetItem = None):
        """ Display the content of the currently selected symbol
        if one was selected (the user may have clicked on the category
        only). 

        """
        
        if not newWidgetItem:
            return

        symbolID = newWidgetItem.data(0, Qt.UserRole).toString()
        if symbolID in self._symbolDict:
            symbol = self._symbolDict[symbolID]
            self._selectedSymbol = symbol
            self.updateSymbolButton.setEnabled(True)
            self.deleteSymbolButton.setEnabled(True)
        else:
            self._selectedSymbol = None
            self.updateSymbolButton.setEnabled(False)
            self.deleteSymbolButton.setEnabled(False)



    def show_selected_symbol_info(self):
        """ Show info for symbol so user can update it."""

        if not self._selectedSymbol:
            return

        self.availableSymbolsWidget.setDisabled(True)
        self.disable_selection_buttons()
        symbol = self._selectedSymbol

        pathToSvgImage = generate_svg_path(self._symbolPath, symbol)
        self.svgWidget.load(pathToSvgImage)
        self.svgPathEdit.setText(pathToSvgImage)

        self.symbolNameEntry.setText(symbol["name"])

        categoryIndex = self.categoryChooser.findText(symbol["category"])
        self.categoryChooser.setCurrentIndex(categoryIndex)
        
        width = int(symbol["width"])
        self.symbolWidthSpinner.setValue(width)
        self.rescale_svg_item(self.svgWidget, width)

        self.symbolDescriptionEntry.setText(symbol["description"])

        self.symbolEntryFrame.setVisible(True)
        self.actionButton.setText("Update Symbol")
        self._activeAction = ManageSymbolDialog.UPDATE_ACTION



    def clear_symbol_info(self):
        """ This slot clears all entries in the addSymbolTab """

        self.symbolNameEntry.clear()
        self.symbolWidthSpinner.setValue(1)
        self.symbolDescriptionEntry.clear()
        self.svgWidget.load(QByteArray())
        self.svgPathEdit.setText(QDir.homePath())
        self._svgFilePath = None



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
        del self._symbolDict[name]



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
            message = ("ManageSymbolDialog._delete_symbol_from_tree_widget:"
                       " there are duplicate categories.")
            errorLogger.write(message)
            return
        
        item = categoryItems[0]

        # prune symbol itself
        name = symbol["name"]

        numChildren = item.childCount()
        for count in range(0, numChildren):
            child = item.child(count)

            if child.text(0) == name:
                item.removeChild(child)
                break

        if numChildren == 1:
            index = self.availableSymbolsWidget.indexOfTopLevelItem(item)
            self.availableSymbolsWidget.takeTopLevelItem(index)



    def update_symbol(self):
        """ Updated the information for a custom symbol.

        For robustnes, this slot is implemented via creating
        a completely new symbol definition directory that is
        then replacing the original one.
        
        """

        if not self._selectedSymbol:
            return

        oldSymbol = self._selectedSymbol
        oldName = self._selectedSymbol["svgName"]

        data = self._get_data_from_interface()
        if data:
            with SymbolTempDir(self._symbolPath) as tempDir:
                if (create_new_symbol(tempDir, data) 
                    and remove_symbol(self._symbolPath, oldName)
                    and move_symbol(tempDir + "/" + data["svgName"], 
                                    self._symbolPath + "/" 
                                    + data["svgName"])):
                    self._update_dict(data)
                    self._update_tree_widget(oldSymbol, data)
                    self._update_frame_data(data)

        self.done_with_input()



    def _update_dict(self, data):
        """ Syncs the dictionary with the just updated data. """

        # convert width value from int to string
        data["width"] = QString("%d" % data["width"])
        symbolID = data["name"]
        self._symbolDict[symbolID] = data



    def _update_tree_widget(self, oldSymbol, newSymbol):
        """ Sync the available symbols widget with the just updated data. """

        self._add_symbol_to_tree_widget(newSymbol)
        self._delete_symbol_from_tree_widget(oldSymbol)



    def _update_frame_data(self, data):
        """ Update the contents of the tab based on a content
        change. For now this could at most be a change in the svg
        image path due to a symbol name change.
        
        """

        pathToSvgImage = generate_svg_path(self._symbolPath, data)
        self.svgPathEdit.setText(pathToSvgImage)
       


    def add_symbol(self):
        """ This is a simple wrapper calling the worker member function
        with the proper interface widgets.
        
        """
        
        self._add_symbol_worker(self._svgFilePath,
                                self.symbolNameEntry,
                                self.categoryChooser,
                                self.symbolDescriptionEntry,
                                self.symbolWidthSpinner)


    
    def _add_symbol_worker(self, svgPathName, nameWidget, categoryWidget,
                           descriptionWidget, widthWidget):
        """ This function checks that all widgets have valid entries
        and if so creates the symbol.
        
        """


        data = self._get_data_from_interface()
        if not data:
            return

        # check that symbol is unique and new
        if data["name"] in self._symbolDict:
            QMessageBox.critical(None, msg.symbolExistsTitle,
                                 msg.symbolExistsText % (name, category),
                                 QMessageBox.Close)
            return 

        if data:
            if create_new_symbol(self._symbolPath, data):
                self._update_dict(data)
                self._add_symbol_to_tree_widget(data)

        self.done_with_input()



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
        symbolItem.setData(0, Qt.UserRole, name)
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



    def _get_data_from_interface(self): 
        """ This function extracts the data from the interface and checks
        that all is well and present.
        
        """

        data = {}

        svgPathName = self.svgPathEdit.text()
        if not svgPathName:
            QMessageBox.critical(None, msg.noSvgFileErrorTitle,
                                 msg.noSvgFileErrorText,
                                 QMessageBox.Close)
            return None
        else:
            data["svgPath"] = svgPathName

        name = self.symbolNameEntry.text()
        if not name:
            QMessageBox.critical(None, msg.noNameErrorTitle,
                                 msg.noNameErrorText,
                                 QMessageBox.Close)
            return None
        else:
            data["name"] = name
            
            # since we use this as a file path get rid of whitespace
            data["svgName"] = sanitize_name(QString(name))
       

        category = self.categoryChooser.currentText()
        if not category:
            QMessageBox.critical(None, msg.noCategoryErrorTitle,
                                 msg.noCategoryErrorText,
                                 QMessageBox.Close)
            return None
        else:
            data["category"] = category


        data["description"]  = self.symbolDescriptionEntry.toPlainText()
        data["width"]        = self.symbolWidthSpinner.value()
        data["category_pos"] = QString("100000")

        return data

        

    def load_svg(self):
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
        self.svgWidget.load(filePath)
        if self.svgWidget.renderer().isValid():
            self._svgFilePath = filePath
            self.svgPathEdit.setText(filePath)
            width = self.symbolWidthSpinner.value()
            self.rescale_svg_item(self.svgWidget, width)



    def rescale_svg_item(self, item, width):
        """ Rescales the svg image if a user changes the symbol width. """

        item.setFixedSize(ManageSymbolDialog.SYMBOL_SIZE * width,
                          ManageSymbolDialog.SYMBOL_SIZE)

       



###########################################################################
#
# some helper functions
#
###########################################################################

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
