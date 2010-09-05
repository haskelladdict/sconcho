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

    symbolsByCategory = sort_symbols_by_category(symbols)
    for (symbolCategory, symbols) in symbolsByCategory.items():

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
            newItem = SymbolSelectorItem(symbol)
            layout.addWidget(newItem, row, 0)
            layout.addWidget(QLabel(symbol["patternName"]), row, 1)

        tab.setLayout(layout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(tab)
        widget.addTab(scrollArea, symbolCategory)



def sort_symbols_by_category(symbols):
    """
    Given a dictionary of knitting symbols returns a dictionary
    with key category and value a list of corresponding symbols
    """

    sortedSymbols = {}
    for symbol in symbols.values():
       
        symbolKey = symbol["category"]
        if symbolKey in sortedSymbols:
            sortedSymbols[symbolKey].append(symbol)
        else:
            sortedSymbols[symbolKey] = [symbol]


    return sortedSymbols




class SymbolSelectorItem(QFrame):

    def __init__(self, symbol, parent = None):

        QFrame.__init__(self, parent)
        self.__name = symbol["patternName"]

       
        
        selectedStyleSheet = "border-width: 1px;" \
                             "border-style: solid;" \
                             "border-color: red;" \
                             "background-color: lightblue;"

        unselectedStyleSheet = "border-width: 1px;" \
                               "border-style: solid;" \
                               "border-color: black;" \
                               "background-color: white;"

        self.setStyleSheet(unselectedStyleSheet)


        svgWidget = QSvgWidget(symbol["svgPath"]) 

        svgWidth = symbol["patternWidth"].toInt()[0]
        svgWidget.setMaximumSize(QSize(svgWidth * 30, 30))


        layout    = QHBoxLayout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        layout.addWidget(svgWidget)

        self.setLayout(layout)








