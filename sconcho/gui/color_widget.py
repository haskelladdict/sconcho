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

from PyQt4.QtCore import (QString, QObject, Qt, SIGNAL)
from PyQt4.QtGui import (QFrame, QWidget, QColor, QPushButton, 
                         QHBoxLayout, QColorDialog)



#########################################################
## 
## class for managing the color selection widget
##
#########################################################
class ColorWidget(QWidget):

    def __init__(self, parent = None):

        super(ColorWidget, self).__init__(parent)


    def initialize(self, synchronizer, colors):

        self._synchronizer = synchronizer
   
        # set up layout
        layout = QHBoxLayout()

        # we need to keep a list of all ColorSelectorItems so we can
        # parse them later for their colors when saving as spf
        # or set their color when loading an spf.
        self.colorWidgets = []
        for color in colors:
            newItem = ColorSelectorItem(color, synchronizer)
            layout.addWidget(newItem)
            self.colorWidgets.append(newItem)
            if color == QColor(Qt.white):
                synchronizer.select(newItem)

        colorButton = QPushButton("customize color")
        QObject.connect(colorButton, SIGNAL("pressed()"),
                        self.customized_color_button_pressed)
        layout.addWidget(colorButton)
        layout.addStretch()
        
        self.setLayout(layout)


    def customized_color_button_pressed(self):
        """ 
        Deal with user requests to customize colors.
        """

        color = QColorDialog.getColor(Qt.white, None,
                                      "Select Custom Color")

        self._synchronizer.change_active_color(color)



    def get_all_colors(self):
        """ Returns a list with of (color, state) tuples currently available
        as ColorSelectorItems.

        The state it 1 if the item is active and 0 for the inactive rest.
        """

        activeWidget = self._synchronizer.get_active_widget()
        allColors = []
        for item in self.colorWidgets:
            state = 1 if item == activeWidget else 0
            allColors.append((item.color, state))

        return allColors
            



#########################################################
## 
## class for managing a single symbol selector item
##
#########################################################
class ColorSelectorItem(QFrame):

    def __init__(self, color, synchronizer, parent = None):

        super(ColorSelectorItem, self).__init__(parent)

        self._synchronizer = synchronizer
        self.itemColor = QColor(color)

        # define and set stylesheets
        self.define_stylesheets() 
        self.setStyleSheet(self._unselectedStyleSheet)
        self._currentStyleSheet = self._unselectedStyleSheet

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        self.setMinimumWidth(40)
        self.setMaximumWidth(40)

        
    @property
    def color(self):
        """ Returns the color content controled by this widget. """

        return self.itemColor



    @color.setter
    def color(self, color):
        """ Sets the current color of the selector. """

        self.itemColor = color
        self.define_stylesheets()



    def define_stylesheets(self):
        """
        Defines the stylesheets used for active/inactive look
        of this widget.
        """

        buttonColor = QColor(self.itemColor).name()
        self._selectedStyleSheet = "border-width: 2px;" \
                                    "margin: 0px;" \
                                    "padding: 6px;" \
                                    "border-style: solid;" \
                                    "border-color: black;" \
                                    "background-color: " + \
                                    buttonColor + ";" 

        self._unselectedStyleSheet = "border-width: 1px;" \
                                      "margin: 7px;" \
                                      "border-style: solid;" \
                                      "border-color: black;" \
                                      "background-color: " + \
                                      buttonColor + ";" 

    

    def mousePressEvent(self, event): 
        """
        Acts on mouse press events and uses the synchronizer
        for selecting.
        """

        self._synchronizer.select(self)



    def activate_me(self):
        """
        This slot activates the item.
        """

        self.setStyleSheet(self._selectedStyleSheet)
        self._currentStyleSheet = self._selectedStyleSheet



    def inactivate_me(self):
        """
        This slot inactivates the item.
        """

        self.setStyleSheet(self._unselectedStyleSheet)
        self._currentStyleSheet = self._unselectedStyleSheet




#########################################################
## 
## class for synchronizing color selector widgets
##
## NOTE: In contrast to the symbol selector synchronizer,
## this one does not allow to deselect a color button,
## i.e., some color has to be selected at all times
##
#########################################################
class ColorSynchronizer(QObject):


    def __init__(self, parent = None):

        QObject.__init__(self, parent)
        self._activeWidget = None
        self._activeColor = None



    def select(self, target):
        """ This method notifies the canvas that the color selector
        has changed.

        NOTE: We need to go via the canvas since it needs to keep
        track for the undo/redo framework.
        
        """

        self.emit(SIGNAL("synchronized_object_changed"), target) 



    def change_active_color(self, newColor):
        """ This method notifies the canvas that the color of
        the currently active selector has changed.

        NOTE: We need to go via the canvas since it needs to keep
        track for the undo/redo framework.
        
        """
    
        self.emit(SIGNAL("active_color_changed"), newColor)

        

    def select_plain(self, target):
        """ This function does most of the work and is also
        called by the canvas redo/undo machinery after we emit
        synchronized_color_selector.

        """

        if self._activeWidget != target:
            if self._activeWidget:
                self._activeWidget.inactivate_me()

        self._activeWidget = target
        self._activeWidget.activate_me()

        

    def get_active_widget(self):
        """ Simply returns the active widget to anybody who cares to know. """

        return self._activeWidget



        
