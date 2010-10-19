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
                        QHBoxLayout
from symbolWidget import Synchronizer



def add_color_buttons_to_widget(colors, colorWidgetContainer, synchronizer):
    """
    Adds all passed color widget to the color widget.
    """

    myColorWidget = ColorWidget(synchronizer, colors)

    # add it to our color widget container
    colorWidgetContainer.layout().addWidget(myColorWidget)




#########################################################
## 
## class for managing the color selection widget
##
#########################################################
class ColorWidget(QWidget):

    def __init__(self, synchronizer, colors, parent = None):

        super(QWidget, self).__init__(parent)

        self.__synchronizer = synchronizer

        layout = QHBoxLayout()
        colorButton = QPushButton("customize color")
        QObject.connect(colorButton, SIGNAL("pressed()"),
                        self.customized_color_button_pressed)

        layout.addWidget(colorButton)
        layout.addStretch()

        for color in colors:
            newItem = ColorSelectorItem(color, synchronizer)
            layout.addWidget(newItem)
            if color == Qt.white:
                synchronizer.select(newItem)

        self.setLayout(layout)


    def customized_color_button_pressed(self):
        """ 
        Deal with user requests to customize colors.
        """

        print("pressed it")



#########################################################
## 
## class for managing a single symbol selector item
##
#########################################################
class ColorSelectorItem(QFrame):

    def __init__(self, color, synchronizer, parent = None):

        super(QFrame, self).__init__(parent)

        self.__synchronizer = synchronizer
        self.__color = color

        # define and set stylesheets
        self.define_stylesheets() 
        self.setStyleSheet(self.__unselectedStyleSheet)

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        self.setMinimumWidth(40)
        self.setMaximumWidth(40)
        
        # finalize the layout
        layout    = QHBoxLayout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        self.setLayout(layout)


    def get_content(self):
        """
        Returns the color content controled by this widget.
        """

        return self.__color



    def define_stylesheets(self):
        """
        Defines the stylesheets used for active/inactive look
        of this widget.
        """

        buttonColor = QColor(self.__color).name()
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

