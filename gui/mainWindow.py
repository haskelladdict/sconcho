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

from PyQt4.QtCore import SIGNAL, SLOT, QSettings, QDir, QFileInfo, \
                         QString, Qt
from PyQt4.QtGui import qApp, QMainWindow, QMessageBox, QFileDialog
from ui_mainWindow import Ui_MainWindow
import sconchoHelpers.text as text
import sconchoHelpers.settings as settings
import sconchoIO.io as io
import sconchoIO.symbolParser as parser
from symbolWidget import add_symbols_to_widget, SymbolSynchronizer
from colorWidget import ColorWidget, ColorSynchronizer
from patternCanvas import PatternCanvas



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
        
        # add connections
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
        """

        symbolTracker = SymbolSynchronizer()
        self.connect(symbolTracker, 
                     SIGNAL("synchronized_object_changed(PyQt_PyObject)"),
                     self.__canvas.set_active_symbol)
        
        add_symbols_to_widget(knittingSymbols, 
                              self.symbolWidgetBase, symbolTracker)




    def initialize_color_widget(self):
        """
        Proxy for adding all the color selectors to the color selector
        Widget and connecting the slots
        """

        colorTracker = ColorSynchronizer()
        self.connect(colorTracker, 
                     SIGNAL("synchronized_object_changed(PyQt_PyObject)"),
                     self.__canvas.set_active_color)

        colorList = [Qt.white, Qt.red, Qt.blue, Qt.black, Qt.darkGray, \
                     Qt.cyan, Qt.yellow, Qt.green, Qt.magenta]
        self.__colorWidget = ColorWidget(colorTracker, colorList)
        self.colorWidgetContainer.layout().addWidget(self.__colorWidget)
        


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



    def new_pattern_dialog(self):
        """
        Open a dialog asking users if they are sure that
        they want to open a new dialog and erase their
        current pattern.
        """

        answer = QMessageBox.question(self, "start new pattern",
                                      "Starting a new project will erase " \
                                      "your current pattern. Do you want to " \
                                      "proceed?",
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
                                                   "save as sconcho pattern file",
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
                QMessageBox.warning(self, "Warning",
                                    "Unknown extension " + extension +
                                    " - please save as .spf!",
                                    QMessageBox.Ok)
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
                                                   "open sconcho pattern file",
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
                                                     "Export pattern as image file",
                                                     QDir.homePath(),
                                                     "Image files (*.png *.tif)")

        if not exportFilePath:
            return

        # check the extension; if none is present add .spf
        extension = QFileInfo(exportFilePath).completeSuffix()
        if extension != "png" and extension != "tif":
            QMessageBox.warning(self, "Warning",
                                "Unknown image file format " + extension,
                                QMessageBox.Ok)
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
