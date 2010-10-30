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

from PyQt4.QtCore import (QString, QSize, pyqtSignal, QObject, SIGNAL)
from PyQt4.QtGui import (QFrame, QGridLayout, QWidgetItem, QWidget, 
                         QHBoxLayout, QLabel, QScrollArea)
from PyQt4.QtSvg import QSvgWidget



def generate_symbolWidgets(symbols, chooser, symbolLayout,
                           synchronizer):
    """ Generate all symbolSelectorWidgets.

    For each category, we create a symbolSelectorWidget, add
    the category to the selector, and store the widget in a dictionary
    with the category name as key.
    The mainWindow then installs the proper widget based on the
    user selection.
    """

    selectorWidgets = {}
    symbolsByCategory = sort_symbols_by_category(symbols)
    for (symbolCategory, symbols) in symbolsByCategory:

        chooser.addItem(symbolCategory)

        # layout for current tab
        currentWidget = QWidget()
        layout        = QGridLayout()

        # sort symbols in requested order
        rawList = []
        for symbol in symbols:
            rawList.append((symbol["category_pos"].toInt()[0], symbol))

        rawList.sort(lambda x,y: cmp(x[0], y[0])) 
       
        # add them to the tab
        for (row, symbolEntry) in enumerate(rawList):
            symbol = symbolEntry[1]
            newItem = SymbolSelectorItem(symbol, synchronizer)
            layout.addWidget(newItem, row, 0)
            layout.addWidget(QLabel(symbol["name"]), row, 1)

        currentWidget.setLayout(layout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(currentWidget)
        selectorWidgets[symbolCategory] = scrollArea

    # make "basic" the top item if it exists, otherwise
    # we pick whatever happens to be top
    basicID = chooser.findText("basic")
    if basicID != -1:
        chooser.setCurrentIndex(basicID)
        activeWidget = selectorWidgets[QString("basic")]
    else:
        activeWidget = selectorWidgets[chooser.currentText()]

    symbolLayout.addWidget(activeWidget)

    return (activeWidget, selectorWidgets)

    

def add_symbols_to_widget(symbols, widget, synchronizer):
    """
    Adds all passed knitting symbols to the tab widget.
    """

    symbolsByCategory = sort_symbols_by_category(symbols)
    for (symbolCategory, symbols) in symbolsByCategory:

        # layout for current tab
        tab    = QWidget()
        layout = QGridLayout()

        # sort symbols in requested order
        rawList = []
        for symbol in symbols:
            rawList.append((symbol["category_pos"].toInt()[0], symbol))

        rawList.sort(lambda x,y: cmp(x[0], y[0])) 
       
        # add them to the tab
        for (row, symbolEntry) in enumerate(rawList):
            symbol = symbolEntry[1]
            newItem = SymbolSelectorItem(symbol, synchronizer)
            layout.addWidget(newItem, row, 0)
            layout.addWidget(QLabel(symbol["name"]), row, 1)

        tab.setLayout(layout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(tab)
        widget.addTab(scrollArea, symbolCategory)

        if symbolCategory == "basic":
            widget.setCurrentWidget(scrollArea)

    return synchronizer



def sort_symbols_by_category(symbols):
    """
    Given a dictionary of knitting symbols returns a list with
    tuples of category names and list of corresponding symbols.
    The category names are sorted with basic coming first.
    """

    # assemble the categories
    rawSortedSymbols = {}
    for symbol in symbols.values():
       
        symbolKey = symbol["category"]
        if symbolKey in rawSortedSymbols:
            rawSortedSymbols[symbolKey].append(symbol)
        else:
            rawSortedSymbols[symbolKey] = [symbol]

    # sort them
    sortedSymbols = []
    for (key, value) in rawSortedSymbols.items():
        sortedSymbols.append((key,value))

    sortedSymbols.sort(lambda x,y: cmp(x[0],y[0]))
    
    return sortedSymbols




#########################################################
## 
## class for managing a single symbol selector item
##
#########################################################
class SymbolSelectorItem(QFrame):

    def __init__(self, symbol, synchronizer, parent = None):

        QFrame.__init__(self, parent)
        self.__synchronizer = synchronizer
        self.__symbol = symbol

        # define and set stylesheets
        self.define_stylesheets() 
        self.setStyleSheet(self.__unselectedStyleSheet)
        self.setToolTip(symbol["description"])
        
        # add the symbol's svg
        svgWidget = QSvgWidget(symbol["svgPath"]) 
        svgWidth = symbol["width"].toInt()[0]
        svgWidget.setMaximumSize(QSize(svgWidth * 30, 30))

        self.setMinimumSize(30,30)
        self.setMaximumSize(svgWidth * 30, 30)

        # finalize the layout
        layout    = QHBoxLayout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        layout.addWidget(svgWidget)
        self.setLayout(layout)


    def get_content(self):
        """
        Returns the symbol controled by this widget.
        """

        return self.__symbol



    def define_stylesheets(self):
        """
        Defines the stylesheets used for active/inactive look
        of this widget.
        """

        self.__selectedStyleSheet = "border-width: 1px;" \
                                    "border-style: solid;" \
                                    "border-color: red;" \
                                    "background-color: lightblue;"

        if "backgroundColor" in self.__symbol:
            backColor = self.__symbol["backgroundColor"]
        else:
            backColor = "white"

        self.__unselectedStyleSheet = "border-width: 1px;" \
                                      "border-style: solid;" \
                                      "border-color: black;" \
                                      "background-color: " + backColor + ";"

    

    def mousePressEvent(self, event): 
        """
        Acts on mouse press events and uses the synchronizer
        for selecting.
        """

        self.__synchronizer.select(self)



    def activate_me(self):
        """
        This slot activates the item.
        """

        self.setStyleSheet(self.__selectedStyleSheet)



    def inactivate_me(self):
        """
        This slot inactivates the item.
        """

        self.setStyleSheet(self.__unselectedStyleSheet)




#########################################################
## 
## class for synchronizing all symbol selector widgets
##
#########################################################
class SymbolSynchronizer(QObject):

    # signal for notifying if active widget changes
    synchronized_object_changed = pyqtSignal("PyQt_PyObject")


    def __init__(self, parent = None):

        QObject.__init__(self, parent)
        self.__activeWidget = None

    
    
    def select(self, target):
        """
        This method "remembers" the newly activated
        widget and makes sure to deactivate
        the previous one.
        """

        if self.__activeWidget == target:
            self.__activeWidget.inactivate_me()
            self.__activeWidget = None
            self.synchronized_object_changed.emit(None)
        else:
            if self.__activeWidget:
                self.__activeWidget.inactivate_me()

            self.__activeWidget = target
            self.__activeWidget.activate_me()
            self.synchronized_object_changed.emit(self.__activeWidget.get_content())



    def get_active_widget(self):
        """
        Simply returns the active widget
        to anybody who cares to know.
        """

        return self.__activeWidget
