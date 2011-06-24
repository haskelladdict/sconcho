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

from PyQt4.QtCore import (Qt, QSize) 
from PyQt4.QtGui import (QWidget, QFrame, QGridLayout, QColor,
                         QLabel, QHBoxLayout)
from PyQt4.QtSvg import QSvgWidget


MAX_RECENT_SYMBOLS = 3


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

        self.recentSymbolsDict = {}

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
       
        labelWidget = QLabel("None");
        self.layout.addWidget(labelWidget, 0, 0, Qt.AlignVCenter)
        self.recentSymbols = [labelWidget]
        self.setLayout(self.layout)



    def get_symbol(self):
        """ Returns the current active symbol. """

        return self.widget.get_symbol() if self.widget else None



    def insert_new_symbol(self, symbol):

        if not symbol:
            return

        # add symbol name to dictionary
        if symbol in self.recentSymbolsDict:
            self.recentSymbolsDict[symbol] += 1
        else:
            # if we have more than 3 symbols evict 
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

            # remove previous symbols
            for widget in self.recentSymbols:
                self.layout.removeWidget(widget)
                widget.setParent(None)
            self.recentSymbols = []

            # add new ones
            for (index, item) in enumerate(self.recentSymbolsDict.keys()):
                widget = SymbolDisplayItem(item.get_content(), self.color)
                self.layout.addWidget(widget, 0, index, Qt.AlignVCenter)
                self.recentSymbols.append(widget)


        
#########################################################
## 
## class for displaying the currently active symbol
## and color
##
#########################################################
class SymbolDisplayItem(QFrame):
    """ Widget displaying currently active symbol and color """

    def __init__(self, symbol, color, parent = None):

        QFrame.__init__(self, parent)
        self._symbol = symbol
        self.backColor = color

        # define and set stylesheets
        self.setup_stylesheets()
        self.setStyleSheet(self._theStyleSheet)

        # layout
        layout    = QHBoxLayout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        self.setToolTip(symbol["description"])

        # add the symbol's svg
        svgWidget = QSvgWidget(symbol["svgPath"]) 
        svgWidth = symbol["width"].toInt()[0]
        self.setMinimumWidth(svgWidth * 25)
        self.setMaximumWidth(svgWidth * 25)
        self.setMinimumHeight(25)
        self.setMaximumHeight(25)

        layout.addWidget(svgWidget)
        self.setLayout(layout)



    def get_symbol(self):
        """ Return our symbol. """

        return self._symbol

    

    @property
    def name(self):
        """ Return the name of the underlying symbol. """

        return self._symbol["name"]
        
    

    def set_backcolor(self, color):
        """ Sets the background color. """

        self.backColor = color
        self.setup_stylesheets()
        self.setStyleSheet(self._theStyleSheet)
        


    def setup_stylesheets(self):
        """ Defines the stylesheets used for display. """

        self._theStyleSheet = "border-width: 1px;" \
                               "border-style: solid;" \
                               "border-color: black;" \
                               "background-color: " + \
                               self.backColor.name() + ";"


