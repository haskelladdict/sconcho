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

from PyQt4.QtCore import (QString, QSize, QObject, SIGNAL, Qt)
from PyQt4.QtGui import (QFrame, QGridLayout, QWidgetItem, QWidget, 
                         QHBoxLayout, QLabel, QScrollArea, QMenu,
                         QColor)
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
    widgetList = {}
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
            newLabel = SymbolSelectorLabel(symbol)
            layout.addWidget(newItem, row, 0)
            layout.addWidget(newLabel, row, 1)

            QObject.connect(newLabel, SIGNAL("label_clicked()"),
                            newItem.click_me)

            widgetList[(symbol["name"], symbol["category"])] = newItem

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

    return (activeWidget, selectorWidgets, widgetList)

    

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



def symbols_by_category(symbols):
    """ Given a dictionary of knitting symbols returns another
    dictionary with the category as key and value a list of
    all symbols with that category.

    """

    # assemble the categories
    rawSortedSymbols = {}
    for symbol in symbols.values():
       
        symbolKey = symbol["category"]
        if symbolKey in rawSortedSymbols:
            rawSortedSymbols[symbolKey].append(symbol)
        else:
            rawSortedSymbols[symbolKey] = [symbol]

    return rawSortedSymbols



def sort_symbols_by_category(symbols):
    """ Given a dictionary of knitting symbols returns a list with
    tuples of category names and list of corresponding symbols.
    The category names are sorted with basic coming first.

    """

    rawSortedSymbols = symbols_by_category(symbols)

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

        super(SymbolSelectorItem, self).__init__(parent)
        self._synchronizer = synchronizer
        self._symbol = symbol

        # define and set stylesheets
        self.define_stylesheets() 
        self.setStyleSheet(self._unselectedStyleSheet)
        self.setToolTip(symbol["description"])
        
        # add the symbol's svg
        svgWidget = QSvgWidget(symbol["svgPath"]) 
        svgWidth = symbol["width"].toInt()[0]
        svgWidget.setMaximumSize(QSize(svgWidth * 30, 30))

        self.setMinimumSize(30,30)
        self.setMaximumSize(svgWidth * 30, 30)

        # finalize the layout
        layout = QHBoxLayout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        layout.addWidget(svgWidget)
        self.setLayout(layout)


    def get_content(self):
        """
        Returns the symbol controled by this widget.
        """

        return self._symbol



    @property
    def name(self):
        """ Returns the name of the underlying symbol. """

        return self._symbol["name"]



    @property
    def color(self):
        """ Returns the background color of the underlying symbol if
        it has one or white otherwise

        """

        if "backgroundColor" in self._symbol:
            backColor = self._symbol["backgroundColor"]
        else:
            backColor = "white"
            
        return QColor(backColor)



    def define_stylesheets(self):
        """
        Defines the stylesheets used for active/inactive look
        of this widget.
        """

        self._selectedStyleSheet = "border-width: 1px;" \
                                    "border-style: solid;" \
                                    "border-color: red;" \
                                    "background-color: lightblue;"

        if "backgroundColor" in self._symbol:
            backColor = self._symbol["backgroundColor"]
        else:
            backColor = "white"

        self._unselectedStyleSheet = "border-width: 1px;" \
                                      "border-style: solid;" \
                                      "border-color: black;" \
                                      "background-color: " + backColor + ";"



    def click_me(self):
        """
        Encapsulates all events when somebody clicks on us.
        """
        
        self._synchronizer.select(self)



    def mousePressEvent(self, event): 
        """
        Acts on mouse press events and uses the synchronizer
        for selecting.
        """

        self.click_me()



    def set_active_look(self):
        """
        This slot activates the item.
        """

        self.setStyleSheet(self._selectedStyleSheet)



    def set_inactive_look(self):
        """
        This slot inactivates the item.
        """

        self.setStyleSheet(self._unselectedStyleSheet)




#########################################################
## 
## class for managing a single symbol label
##
#########################################################
class SymbolSelectorLabel(QLabel):


    def __init__(self, symbol, parent = None):

        super(SymbolSelectorLabel, self).__init__(symbol["name"], parent)

        # define and set stylesheets
        self.setToolTip(symbol["description"])
        


    def mousePressEvent(self, event): 
        """
        Acts on mouse press events and uses the synchronizer
        for selecting.
        """

        self.emit(SIGNAL("label_clicked"))




#########################################################
## 
## class for synchronizing all symbol selector widgets
##
#########################################################
class SymbolSynchronizer(QObject):


    def __init__(self, parent = None):

        QObject.__init__(self, parent)
        self._activeWidget = None


    def select(self, target):
        """ This method 'remembers' the newly activated
        widget and makes sure to deactivate the previous one.

        """

        if self._activeWidget == target:
            self.unselect()
            self.emit(SIGNAL("synchronized_object_changed"), None)
        else:
            self.select_plain(target)
            self.emit(SIGNAL("synchronized_object_changed"),
                      self._activeWidget) 



    def select_plain(self, target):
        """ Select the target symbol selector. """

        # this function is called back by the canvas redo/undo
        # machinery after we emit synchronized_object_changed
        # and this test avoids duplication
        if self._activeWidget == target:
            return

        if self._activeWidget:
            self._activeWidget.set_inactive_look()

        self._activeWidget = target
        self._activeWidget.set_active_look()



    def unselect(self):
        """ Unselect the currently active widget. """

        if not self._activeWidget:
            return

        self._activeWidget.set_inactive_look()
        self._activeWidget = None



    def get_active_widget(self):
        """ Return the active widget to anybody who cares to know. """

        return self._activeWidget