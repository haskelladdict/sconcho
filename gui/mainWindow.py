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

from PyQt4.QtCore import (SIGNAL, SLOT, QSettings, QDir, QFileInfo, 
                          QString, Qt, QSize)
from PyQt4.QtGui import (qApp, QMainWindow, QMessageBox, QFileDialog,
                        QWidget, QGridLayout, QHBoxLayout, QLabel, 
                        QFrame, QColor)
from PyQt4.QtSvg import QSvgWidget
from gui.ui_mainWindow import Ui_MainWindow
import util.helpers.messages as msg
import util.helpers.settings as settings
import util.io.io as io
import util.io.symbolParser as parser
from gui.symbolWidget import (generate_symbolWidgets, SymbolSynchronizer)
from gui.colorWidget import (ColorWidget, ColorSynchronizer)
from gui.patternCanvas import PatternCanvas



#######################################################################
#
#
# top level window class
#
#
#######################################################################
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, symbolPaths, filename = None, parent = None):
        """
        Initialize the main window.
        """

        super(QMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.__settings = QSettings("sconcho", "settings")
        settings.initialize(self.__settings)

        self.__saveFilePath = None
        self.__colorWidget  = None

        # set up the statusBar
        self.activeSymbolWidget = ActiveSymbolWidget()
        self.statusBar().addPermanentWidget(self.activeSymbolWidget)
        
        self.__symbolPaths = symbolPaths
        knittingSymbols = parser.parse_all_symbols(self.__symbolPaths)
        self.__canvas = PatternCanvas(self.__settings, 
                                      knittingSymbols[QString("basic::knit")])
        self.initialize_symbol_widget(knittingSymbols)
        self.initialize_color_widget()

        # we set a manual scene rectangle for our view. we
        # should be a little smarter about this in the future
        self.graphicsView.setScene(self.__canvas)
        self.graphicsView.setSceneRect( -100, -100, 2000, 2000)

        # set up all the connections
        self.__set_up_connections()
        


    def __set_up_connections(self):
        """
        Set up all connections required by MainWindow.
        """
        
        self.connect(self.actionQuit, SIGNAL("triggered()"),
            qApp, SLOT("quit()"))

        self.connect(self.actionAbout_sconcho, SIGNAL("triggered()"),
                     self.show_about_sconcho)

        self.connect(self.actionAbout_Qt4, SIGNAL("triggered()"),
                     self.show_about_qt4)

        self.connect(self.actionNew, SIGNAL("triggered()"),
                     self.new_pattern_dialog)

        self.connect(self.actionSave, SIGNAL("triggered()"),
                     self.save_pattern_dialog)

        self.connect(self.actionSave_as, SIGNAL("triggered()"),
                     self.save_as_pattern_dialog)
        
        self.connect(self.actionOpen, SIGNAL("triggered()"),
                     self.read_pattern_dialog)

        self.connect(self.actionExport, SIGNAL("triggered()"),
                     self.export_pattern_dialog)

        self.connect(self.actionPrint, SIGNAL("triggered()"),
                     self.print_dialog)

        self.connect(self.actionShow_legend, SIGNAL("toggled(bool)"),
                     self.__canvas.toggle_legend_visibility)

        self.connect(self.actionShow_pattern_grid, SIGNAL("toggled(bool)"),
                     self.__canvas.toggle_pattern_grid_visibility)


        
    def initialize_symbol_widget(self, knittingSymbols):
        """
        Proxy for adding all the knitting symbols to the symbolWidget
        and connecting it to the symbol changed slot.

        NOTE: Unfortunately, the order of the connections below matters.
        Connect the patternCategoryChooser only after it has been fully
        set up. Otherwise we get spurious selector widget switches until
        the chooser has established the correct order.
        """

        symbolTracker = SymbolSynchronizer()
        self.connect(symbolTracker, 
                     SIGNAL("synchronized_object_changed(PyQt_PyObject)"),
                     self.__canvas.set_active_symbol)

        self.connect(symbolTracker, 
                     SIGNAL("synchronized_object_changed(PyQt_PyObject)"),
                     self.activeSymbolWidget.active_symbol_changed)
        
        (self.selectedSymbol, self.symbolSelectorWidgets) = \
                        generate_symbolWidgets(knittingSymbols,
                                               self.patternCategoryChooser,
                                               self.symbolSelectorLayout,
                                               symbolTracker)

        self.connect(self.patternCategoryChooser,
                     SIGNAL("currentIndexChanged(QString)"),
                     self.update_symbol_widget)
        


    def update_symbol_widget(self, categoryName):
        """ Update the currently visible symbolWidgetSelector

        Triggered by the user choosing a new symbol category removes
        the previous symbolSelectorWidget and installs the selected
        one.
        """

        self.symbolSelectorLayout.removeWidget(self.selectedSymbol)
        self.selectedSymbol.setParent(None)

        self.selectedSymbol = self.symbolSelectorWidgets[categoryName]
        self.symbolSelectorLayout.addWidget(self.selectedSymbol)
        
        


    def initialize_color_widget(self):
        """
        Proxy for adding all the color selectors to the color selector
        Widget and connecting the slots
        """

        colorTracker = ColorSynchronizer()
        self.connect(colorTracker, 
                     SIGNAL("synchronized_object_changed(PyQt_PyObject)"),
                     self.__canvas.set_active_color)

        self.connect(colorTracker, 
                     SIGNAL("synchronized_object_changed(PyQt_PyObject)"),
                     self.activeSymbolWidget.active_color_changed)

        colorList = [Qt.white, Qt.red, Qt.blue, Qt.black, Qt.darkGray, \
                     Qt.cyan, Qt.yellow, Qt.green, Qt.magenta]
        self.__colorWidget = ColorWidget(colorTracker, colorList)
        self.colorWidgetContainer.layout().addWidget(self.__colorWidget)
        


    def show_about_sconcho(self):
        """
        Show the about sconcho dialog.
        """
        QMessageBox.about(self, "sconcho", msg.sconchoDescription)



    def show_about_qt4(self):
        """
        Show the about Qt dialog.
        """
        QMessageBox.aboutQt(self)



    def new_pattern_dialog(self):
        """
        Open a dialog asking users if they are sure that
        they want to open a new dialog and erase their
        current pattern.
        """

        answer = QMessageBox.question(self, msg.startNewPatternTitle,
                                      msg.startNewPatternText,
                                      QMessageBox.Ok, QMessageBox.Cancel)

        if answer == QMessageBox.Ok:
            self.__canvas.create_new_canvas()



    def save_as_pattern_dialog(self):
        """
        This function opens a save pattern dialog.
        """

        if not self.__saveFilePath:
            self.save_pattern_dialog()

        io.save_project(self.__canvas, None, self.__settings,
                        self.__saveFilePath)
        
        saveFileName = QFileInfo(self.__saveFilePath).fileName()
        self.statusBar().showMessage("successfully saved " + saveFileName, 3000)



    def save_pattern_dialog(self):
        """
        This function opens a save as pattern dialog.
        """

        location = self.__saveFilePath if self.__saveFilePath else QDir.homePath()
        saveFilePath = QFileDialog.getSaveFileName(self,
                                                   msg.saveSconchoProjectTitle,
                                                   location,
                                                   "sconcho pattern files (*.spf)")

        if not saveFilePath:
            return

        # check the extension; if none is present add .spf
        extension = QFileInfo(saveFilePath).completeSuffix()
        if extension != "spf":
            if not extension:
                saveFilePath = saveFilePath + ".spf"
            else:
                QMessageBox.warning(self, msg.unknownSpfExtensionTitle,
                                    msg.unknownSpfExtensionText,
                                    QMessageBox.Close)
                return

        self.set_project_save_file(saveFilePath)
        io.save_project(self.__canvas, self.__colorWidget.get_all_colors(),
                        self.__settings, saveFilePath)
        saveFileName = QFileInfo(saveFilePath).fileName()
        self.statusBar().showMessage("successfully saved " + saveFileName, 3000)



    def read_pattern_dialog(self):
        """
        This function opens a read pattern dialog.
        """

        readFilePath = QFileDialog.getOpenFileName(self,
                                                   msg.openSconchoProjectTitle,
                                                   QDir.currentPath(),
                                                   "sconcho pattern files (*.spf)")

        if not readFilePath:
            return

        (patternGridItems, legendItems, colors) = io.read_project(readFilePath)
        knittingSymbols = parser.parse_all_symbols(self.__symbolPaths)
        self.__canvas.load_previous_canvas(knittingSymbols, patternGridItems,
                                           legendItems)
        set_up_colors(self.__colorWidget, colors)
        readFileName = QFileInfo(readFilePath).fileName()
        self.statusBar().showMessage("successfully opened " + readFileName, 3000)
        self.set_project_save_file(readFilePath)



    def export_pattern_dialog(self):
        """
        This function opens and export pattern dialog.
        """

        exportFilePath = QFileDialog.getSaveFileName(self,
                                                     msg.exportPatternTitle,
                                                     QDir.homePath(),
                                                     "Image files (*.png *.tif)")

        if not exportFilePath:
            return

        # check the extension; if none is present add .spf
        extension = QFileInfo(exportFilePath).completeSuffix()
        if extension != "png" and extension != "tif":
            QMessageBox.warning(self, msg.unknownImageFormatTitle,
                                msg.unknownImageFormatText,
                                QMessageBox.Close)
            return

        io.export_scene(self.__canvas, exportFilePath)
        exportFileName = QFileInfo(exportFilePath).fileName()
        self.statusBar().showMessage("successfully exported " + exportFileName,
                                     3000)



    def print_dialog(self):
        """
        This member function calls print routine.
        """

        io.print_scene(self.__canvas)
        


    def set_project_save_file(self, fileName):
        """
        Stores the name of the currently operated on file.
        """

        self.__saveFilePath = fileName
        self.setWindowTitle(QFileInfo(fileName).fileName())




def set_up_colors(widget, colors):
    """
    Sets the colors of ColorSelectorItems in the widget to
    the requested colors.
    """

    assert (len(widget.colorWidgets) == len(colors))

    for (i, item) in enumerate(widget.colorWidgets):
        item.set_content(colors[i])
        item.repaint()





###############################################################
#
# this simple class provides a view of the currently
# active widget in the status bar
#
###############################################################
class ActiveSymbolWidget(QWidget):
    """ Container Widget for currently active symbol """ 


    def __init__(self, parent = None):

        super(QWidget, self).__init__(parent)

        self.layout = QGridLayout()
        self.color  = QColor(Qt.white)
        self.layout.setSizeConstraint(5)
        
        self.activeSymbolLabel     = QLabel("Active Symbol")
        self.inactiveSymbolLabel   = QLabel("No Active Symbol")
        
        self.widget = None
        self.label  = self.inactiveSymbolLabel
        self.layout.addWidget(self.label,0,0)
        self.setLayout(self.layout)



    def active_symbol_changed(self, symbol):
        """
        Update the displayed active Widget after
        the user selected a new one.
        """

        if self.widget:
            self.layout.removeWidget(self.widget)
            self.widget.setParent(None)

        if symbol:
            self.widget = SymbolDisplayItem(symbol, self.color)
            self.layout.addWidget(self.widget,0,1)

            if self.label is self.inactiveSymbolLabel:
                self.layout.removeWidget(self.label)
                self.label.setParent(None)
                self.label = self.activeSymbolLabel
                self.layout.addWidget(self.label,0,0)       
                
        else:
            if self.label is self.activeSymbolLabel:
                self.layout.removeWidget(self.label)
                self.label.setParent(None)
                self.label = self.inactiveSymbolLabel
                self.layout.addWidget(self.label,0,0)       
            


    def active_color_changed(self, color):
        """
        Update the background of the displayed active
        widget (if there is one) after a user color change.
        """

        self.color = color
        
        if self.widget:
            self.widget.set_backcolor(color)
        

            
        
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
        self.__symbol = symbol
        self.backColor = color

        # define and set stylesheets
        self.setup_stylesheets()
        self.setMinimumSize(20,20)
        self.setStyleSheet(self.__theStyleSheet)

        # layout
        layout    = QHBoxLayout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        self.setToolTip(symbol["description"])

        # add the symbol's svg
        svgWidget = QSvgWidget(symbol["svgPath"]) 
        svgWidth = symbol["width"].toInt()[0]
        svgWidget.setMaximumSize(QSize(svgWidth * 20, 20))
        layout.addWidget(svgWidget)
            
        self.setLayout(layout)



    def set_backcolor(self, color):
        """
        Sets the background color.
        """

        self.backColor = color
        self.setup_stylesheets()
        self.setStyleSheet(self.__theStyleSheet)
        


    def setup_stylesheets(self):
        """
        Defines the stylesheets used for display.
        """

        self.__theStyleSheet = "border-width: 1px;" \
                               "border-style: solid;" \
                               "border-color: black;" \
                               "background-color: " + self.backColor.name() + ";"

    
