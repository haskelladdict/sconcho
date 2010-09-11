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

from PyQt4.QtCore import SIGNAL, SLOT, QSettings
from PyQt4.QtGui import qApp, QMainWindow, QMessageBox
from ui_mainWindow import Ui_MainWindow
import sconchoHelpers.text as text
import sconchoHelpers.settings as settings
import symbolWidget
from patternCanvas import PatternCanvas


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, knittingSymbols, filename = None, parent = None):
        """
        Initialize the main window.
        """

        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.__settings = QSettings("sconcho", "settings")
        settings.initialize(self.__settings)

        self.__canvas = PatternCanvas(self.__settings)
        self.initialize_symbol_widget(knittingSymbols)
        self.graphicsView.setScene(self.__canvas)
        
        # add connections
        self.connect(self.actionQuit, SIGNAL("triggered()"),
            qApp, SLOT("quit()"))

        self.connect(self.actionAbout_sconcho, SIGNAL("triggered()"),
                self.show_about_sconcho)

        self.connect(self.actionAbout_Qt4, SIGNAL("triggered()"),
                self.show_about_qt4)


   
    def initialize_symbol_widget(self, knittingSymbols):
        """
        Proxy for adding all the knitting symbols to the symbolWidget
        and connecting it to the symbol changed slot.
        """

        symbolTracker = symbolWidget.add_symbols_to_widget(knittingSymbols, 
                            self.symbolWidgetBase)

        # we connect the symbol tracker directly to the canvas
        self.connect(symbolTracker, 
                     SIGNAL("selected_symbol_changed(PyQt_PyObject)"),
                     self.__canvas.set_active_symbol)



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




