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


from PyQt4.QtCore import QString, pyqtSignal, QObject, Qt, SIGNAL
from PyQt4.QtGui import QFrame, QWidget, QColor, QPushButton, \
                        QHBoxLayout, QColorDialog



#########################################################
## 
## class for managing the color selection widget
##
#########################################################
class ColorWidget(QWidget):

    def __init__(self, synchronizer, colors, parent = None):

        super(QWidget, self).__init__(parent)

        self.__synchronizer = synchronizer

        # set up layout
        layout = QHBoxLayout()
        colorButton = QPushButton("customize color")
        QObject.connect(colorButton, SIGNAL("pressed()"),
                        self.customized_color_button_pressed)
        layout.addWidget(colorButton)
        layout.addStretch()

        # we need to keep a list of all ColorSelectorItems so we can
        # parse them later for their colors when saving as spf
        # or set their color when loading an spf.
        self.colorWidgets = []
        for color in colors:
            newItem = ColorSelectorItem(color, synchronizer)
            layout.addWidget(newItem)
            self.colorWidgets.append(newItem)
            if color == Qt.white:
                synchronizer.select(newItem)

        self.setLayout(layout)



    def customized_color_button_pressed(self):
        """ 
        Deal with user requests to customize colors.
        """

        color = QColorDialog.getColor(Qt.white, None,
                                      "Select custom color")

        activeColorWidget = self.__synchronizer.get_active_widget()
        activeColorWidget.set_content(color)
        self.__synchronizer.select(activeColorWidget)



    def get_all_colors(self):
        """
        Returns a list with all colors currently available in
        the ColorSelectorItems.
        """

        allColors = []
        for item in self.colorWidgets:
            allColors.append(item.get_content())

        return allColors
            



#########################################################
## 
## class for managing a single symbol selector item
##
#########################################################
class ColorSelectorItem(QFrame):

    def __init__(self, color, synchronizer, parent = None):

        super(QFrame, self).__init__(parent)

        self.__synchronizer = synchronizer
        self.color = QColor(color)

        # define and set stylesheets
        self.define_stylesheets() 
        self.setStyleSheet(self.__unselectedStyleSheet)

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        self.setMinimumWidth(40)
        self.setMaximumWidth(40)

        

    def get_content(self):
        """
        Returns the color content controled by this widget.
        """

        return self.color


    def set_content(self, color):
        """
        Sets the current color of the selector.
        """

        self.color = color
        self.define_stylesheets()



    def define_stylesheets(self):
        """
        Defines the stylesheets used for active/inactive look
        of this widget.
        """

        buttonColor = QColor(self.color).name()
        self.__selectedStyleSheet = "border-width: 2px;" \
                                    "margin: 0px;" \
                                    "padding: 6px;" \
                                    "border-style: solid;" \
                                    "border-color: black;" \
                                    "background-color: " + \
                                    buttonColor + ";" 

        self.__unselectedStyleSheet = "border-width: 1px;" \
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
## class for synchronizing color selector widgets
##
## NOTE: In contrast to the symbol selector synchronizer,
## this one does not allow to deselect a color button,
## i.e., some color has to be selected at all times
##
#########################################################
class ColorSynchronizer(QObject):

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
            self.__activeWidget.activate_me()
            self.synchronized_object_changed.emit(self.__activeWidget.get_content())
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
