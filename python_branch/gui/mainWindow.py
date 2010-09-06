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

from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import qApp, QMainWindow, QMessageBox
import sconchoHelpers.text as text
import symbolWidget 
from ui_mainWindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, knittingSymbols, filename = None, parent = None):
        """
        Initialize the main window.
        """

        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.__knittingSymbols = knittingSymbols

        # add connections
        self.connect(self.actionQuit, SIGNAL("triggered()"),
            qApp, SLOT("quit()"))

        self.connect(self.actionAbout_sconcho, SIGNAL("triggered()"),
                self.show_about_sconcho)

        self.connect(self.actionAbout_Qt4, SIGNAL("triggered()"),
                self.show_about_qt4)


        # initialize the symbol tracker
        self.__symbolTracker = self.initialize_symbol_widget()
        self.connect(self.__symbolTracker, SIGNAL("selected_symbol_changed()"),
                     self.symbol_changed)


    def symbol_changed(self):
        print(self.__symbolTracker.get_active_symbol()["name"])


    def initialize_symbol_widget(self):
        """
        Proxy for adding all the knitting symbols to the symbolWidget.
        """

        return symbolWidget.add_symbols_to_widget(self.__knittingSymbols, 
                    self.symbolWidgetBase)



    def show_about_sconcho(self):
        """
        Show the about sconcho dialog.
        """
        QMessageBox.about(self, "sconcho", text.sconchoDescription)



    def show_about_qt4(self):
        """
        Show the about Qt dialog.
        """
        QMessageBox.aboutQt(self)




