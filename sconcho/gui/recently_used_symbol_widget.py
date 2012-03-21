# -*- coding: utf-8 -*-
######################################################################## #
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

from PyQt4.QtCore import (Qt, QSize, SIGNAL) 
from PyQt4.QtGui import (QWidget, QFrame, QGridLayout, QColor,
                         QLabel, QHBoxLayout)
from PyQt4.QtSvg import QSvgWidget


from sconcho.gui.symbol_widget import (SymbolSelectorItem,
                               SymbolSynchronizer)


MAX_RECENT_SYMBOLS = 5


###############################################################
#
# this simple class provides a view of the most recently
# used symbols
#
###############################################################
class RecentlyUsedSymbolWidget(QWidget):
    """ Container Widget for most recently used symbols symbol """ 


    def __init__(self, parent = None):

        super(RecentlyUsedSymbolWidget, self).__init__(parent)

        self.layout = QGridLayout()
        self.color  = QColor(Qt.white)

        self._synchronizer = SymbolSynchronizer()
        self.recentSymbolsDict = {}
        self.widgetToSymbol = {}

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
       
        labelWidget = QLabel("None");
        self.layout.addWidget(labelWidget, 0, 0, Qt.AlignVCenter)
        self.recentSymbols = [labelWidget]
        self.setLayout(self.layout)



    def clear(self):
        """ Removes all widgets and re-inializes the widget. """

        for widget in self.recentSymbols:
            self.layout.removeWidget(widget)
            widget.setParent(None)

        self._synchronizer.unselect()
        self.recentSymbols = []
        self.recentSymbolsDict = {}
        self.widgetToSymbol = {}



    def widget_clicked(self, widget):
        """ What happens when one of the widgets is clicked """

        # make sure that we count clicks on widgets as well
        symbol = self.widgetToSymbol[widget]
        self.recentSymbolsDict[symbol] += 1

        self.widgetToSymbol[widget].click_me()



    def insert_new_symbol(self, symbol):
        """ Insert new symbol into recently used symbols widget """

        if not symbol:
            self._synchronizer.unselect()
            return

        # add symbol name to dictionary
        if symbol in self.recentSymbolsDict:
            self.recentSymbolsDict[symbol] += 1
            self.click_on_a_symbols_widget(symbol)

        else:
            # if we have more than MAX_RECENT_SYMBOLS symbols evict 
            # the one with the lowest count
            if len(self.recentSymbolsDict) > MAX_RECENT_SYMBOLS-1:
                minKey = min(self.recentSymbolsDict.values())
                keyDict = self.recentSymbolsDict.copy()
                for (key, val) in keyDict.items():
                    if val == minKey:
                        del self.recentSymbolsDict[key]
                        break

            # adding it after evicting a previous one 
            # makes sure we always keep the most recent item
            self.recentSymbolsDict[symbol] = 1

            self.update_widget(symbol)



    def update_widget(self, symbol):
        """ Update the widget, e.g. after adding/deleting a symbol. """

        # remove previous symbols
        for widget in self.recentSymbols:
            self.layout.removeWidget(widget)
            widget.setParent(None)
        self.recentSymbols = []

        # add new ones
        self.widgetToSymbol = {}
        for (index, item) in enumerate(self.recentSymbolsDict.keys()):
            widget = SymbolDisplayItem(item.get_content(), 
                                       self._synchronizer)
            self.connect(widget, SIGNAL("widget_pressed"), 
                         self.widget_clicked)
            self.widgetToSymbol[widget] = item 
            self.layout.addWidget(widget, 0, index, Qt.AlignVCenter)
            self.recentSymbols.append(widget)

        self.click_on_a_symbols_widget(symbol)



    def click_on_a_symbols_widget(self, symbol):
        """ Clicks the widget corresponding to symbol. """

        for (widget, widgetSymbol) in self.widgetToSymbol.items():
            if widgetSymbol == symbol:
                widget.click_me()




        
#########################################################
## 
## class for displaying the most recently used symbols
##
#########################################################
class SymbolDisplayItem(SymbolSelectorItem):
    """ Widget displaying currently active symbol and color.
   
    This is a very close specialization of SymbolSelectorItem
    for use in the recently used widget display.
    
    """

    def __init__(self, symbol, synchronizer, parent = None):

        super(SymbolDisplayItem, self).__init__(symbol, synchronizer, 
                                                parent)

        # adjust the size according to the symbol's svg
        svgWidget = QSvgWidget(symbol["svgPath"]) 
        svgWidth = int(symbol["width"])
        self.setMinimumWidth(svgWidth * 25)
        self.setMaximumWidth(svgWidth * 25)
        self.setMinimumHeight(25)
        self.setMaximumHeight(25)



    def mousePressEvent(self, event): 
        """ Acts on mouse press events """

        self.emit(SIGNAL("widget_pressed"), self)

