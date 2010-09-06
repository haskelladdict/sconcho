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


from PyQt4.QtCore import QString, QSize
from PyQt4.QtGui import QFrame, QGridLayout, QWidgetItem, QWidget, \
                        QHBoxLayout, QLabel, QScrollArea
from PyQt4.QtSvg import QSvgWidget



def add_symbols_to_widget(symbols, widget):
    """
    Adds all passed knitting symbols to the tab widget.
    """

    # the synchronizer object makes sure one object is selected
    # at a time and keeps track of which one
    synchronizer = Synchronizer()

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
            layout.addWidget(QLabel(symbol["patternName"]), row, 1)

        tab.setLayout(layout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(tab)
        widget.addTab(scrollArea, symbolCategory)

        if symbolCategory == "basic":
            widget.setCurrentWidget(scrollArea)



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
        self.name = symbol["patternName"]
        self.__synchronizer = synchronizer

        # define and set stylesheets
        self.define_stylesheets() 
        self.setStyleSheet(self.__unselectedStyleSheet)

        # add the symbol's svg
        svgWidget = QSvgWidget(symbol["svgPath"]) 
        svgWidth = symbol["patternWidth"].toInt()[0]
        svgWidget.setMaximumSize(QSize(svgWidth * 30, 30))

        # finalize the layout
        layout    = QHBoxLayout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        layout.addWidget(svgWidget)
        self.setLayout(layout)



    def define_stylesheets(self):
        """
        Defines the stylesheets used for active/inactive look
        of this widget.
        """

        self.__selectedStyleSheet = "border-width: 1px;" \
                                    "border-style: solid;" \
                                    "border-color: red;" \
                                    "background-color: lightblue;"

        self.__unselectedStyleSheet = "border-width: 1px;" \
                                      "border-style: solid;" \
                                      "border-color: black;" \
                                      "background-color: white;"

       
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
## class for synchronizing all SymbolSelectorItems
##
#########################################################
class Synchronizer(object):


    def __init__(self):

        self.__activeWidget = None


    def select(self, target):

        if self.__activeWidget == target:
            self.__activeWidget.inactivate_me()
            self.__activeWidget = None
        else:
            if self.__activeWidget:
                self.__activeWidget.inactivate_me()

            self.__activeWidget = target
            self.__activeWidget.activate_me()

        if self.__activeWidget:
            print(self.__activeWidget.name)


