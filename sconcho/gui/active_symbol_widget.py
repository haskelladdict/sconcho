# -*- coding: utf-8 -*-
######################################################################## #
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

from PyQt4.QtCore import (Qt, QSize) 
from PyQt4.QtGui import (QWidget, QFrame, QGridLayout, QColor,
                         QLabel, QHBoxLayout)
from PyQt4.QtSvg import QSvgWidget


###############################################################
#
# this simple class provides a view of the currently
# active widget in the status bar
#
###############################################################
class ActiveSymbolWidget(QWidget):
    """ Container Widget for currently active symbol """ 


    def __init__(self, parent = None):

        super(ActiveSymbolWidget, self).__init__(parent)

        self.layout = QGridLayout()
        self.color  = QColor(Qt.white)
        
        self.activeSymbolLabel     = QLabel("Active Symbol")
        self.inactiveSymbolLabel   = QLabel("No Active Symbol")

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        
        self.widget = None
        self.label  = self.inactiveSymbolLabel
        self.layout.addWidget(self.label,0,0, Qt.AlignVCenter)
        self.setLayout(self.layout)



    def get_symbol(self):
        """ Returns the current active symbol. """

        return self.widget.get_symbol() if self.widget else None
        


    def active_symbol_changed(self, symbolObject):
        """ Update the displayed active Widget after
        the user selected a new one.
        
        """

        if self.widget:
            self.layout.removeWidget(self.widget)
            self.widget.setParent(None)

        if symbolObject:
            symbol = symbolObject.get_content()

            # for nostitch we use its default color
            if symbolObject.name == "nostitch":
                color = symbolObject.color
            else:
                color = self.color
            
            self.widget = SymbolDisplayItem(symbol, color)
            self.layout.addWidget(self.widget,0,1, Qt.AlignVCenter)

            if self.label is self.inactiveSymbolLabel:
                self.layout.removeWidget(self.label)
                self.label.setParent(None)
                self.label = self.activeSymbolLabel
                self.layout.addWidget(self.label,0,0, Qt.AlignVCenter)       
                
        else:
            self.widget = None
            
            if self.label is self.activeSymbolLabel:
                self.layout.removeWidget(self.label)
                self.label.setParent(None)
                self.label = self.inactiveSymbolLabel
                self.layout.addWidget(self.label,0,0, Qt.AlignVCenter)       
            


    def active_colorObject_changed(self, newColorObject):
        """ Update the background of the displayed active
        widget (if there is one) after a user color change.
        
        """

        self.color = newColorObject.get_content()
        
        if self.widget and not self.widget.name == "nostitch":
            self.widget.set_backcolor(self.color)
        

            
        
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


