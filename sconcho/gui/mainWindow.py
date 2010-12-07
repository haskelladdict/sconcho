# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2009 Markus Dittrich
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

import platform, os
from functools import partial

from PyQt4.QtCore import (SIGNAL, SLOT, QSettings, QDir, QFileInfo, 
                          QString, Qt, QSize, QFile, QTimer, QVariant,
                          QPoint, PYQT_VERSION_STR, QT_VERSION_STR,
                          QObject)
from PyQt4.QtGui import (QMainWindow, QMessageBox, QFileDialog,
                         QWidget, QGridLayout, QHBoxLayout, QLabel, 
                         QFrame, QColor, QApplication)
from PyQt4.QtSvg import QSvgWidget

from gui.ui_mainWindow import Ui_MainWindow
import util.messages as msg
import util.settings as settings
import util.misc as misc
import util.io as io
import util.symbolParser as parser
from gui.symbolWidget import (generate_symbolWidgets, SymbolSynchronizer)
from gui.colorWidget import (ColorWidget, ColorSynchronizer)
from gui.patternCanvas import PatternCanvas
from gui.exportBitmapWidget import ExportBitmapWidget
from gui.newPatternWidget import NewPatternWidget
from gui.preferencesDialog import PreferencesDialog
from gui.sconchoManual import SconchoManual
from util.exceptions import PatternReadError


__version__ = "0.1.0_a5"


#######################################################################
#
#
# top level window class
#
#
#######################################################################
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, topLevelPath, fileName = None, parent = None):
        """
        Initialize the main window.
        """

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.settings = self.__restore_settings()
        self.__colorWidget  = None
        self.__preferencesDialog = None

        self.clear_project_save_file()

        # set up the statusBar
        self.activeSymbolWidget = ActiveSymbolWidget()
        self.statusBar().addPermanentWidget(self.activeSymbolWidget)

        self.__topLevelPath = topLevelPath
        self.__symbolPaths = [os.path.join(topLevelPath, "symbols")]
        knittingSymbols = parser.parse_all_symbols(self.__symbolPaths)
        self.__canvas = PatternCanvas(self.settings, 
                                      knittingSymbols[QString("basic::knit")],
                                      self)
        self.initialize_symbol_widget(knittingSymbols)
        self.initialize_color_widget()

        # we set a manual scene rectangle for our view. we
        # should be a little smarter about this in the future
        self.graphicsView.setScene(self.__canvas)
        self.connect(self.__canvas, SIGNAL("adjust_view"),
                     self.graphicsView.adjust_scene)
        self.connect(self.__canvas, SIGNAL("active_color_changed"),
                     self.__colorWidget.set_active_color)
        self.graphicsView.adjust_scene()

        # set up all the connections
        self.__set_up_connections()

        # set up timers
        self.__set_up_timers()

        # nothing happened so far
        self.__projectIsDirty = False

        # read project if we received a filename
        if fileName:
            self.__read_project(fileName)
        


    def __restore_settings(self):
        """ Restore the previously saved settings """
        
        newSettings = QSettings()
        newSize = newSettings.value("MainWindow/Size",
                                    QVariant(QSize(1200, 800))).toSize()
        self.resize(newSize)

        newPosition = newSettings.value("MainWindow/Position",
                                        QVariant(QPoint(0,0))).toPoint()
        self.move(newPosition)
        
        self.restoreState(newSettings.value("MainWindow/State").toByteArray())
        settings.initialize(newSettings)

        return newSettings



    def __save_settings(self):
        """ Save all settings. """
        
        self.settings.setValue("MainWindow/Size", QVariant(self.size()))
        self.settings.setValue("MainWindow/Position", QVariant(self.pos()))
        self.settings.setValue("MainWindow/State", QVariant(self.saveState()))


                          
    def __set_up_connections(self):
        """
        Set up all connections required by MainWindow.
        """
        
        self.connect(self.actionQuit, SIGNAL("triggered()"),
                     self.close)

        self.connect(self.actionAbout_sconcho, SIGNAL("triggered()"),
                     self.show_about_sconcho)

        self.connect(self.actionAbout_Qt4, SIGNAL("triggered()"),
                     self.show_about_qt4)

        self.connect(self.actionSconcho_Manual, SIGNAL("triggered()"),
                     self.show_sconcho_manual)

        self.connect(self.actionNew, SIGNAL("triggered()"),
                     self.new_pattern_dialog)

        self.connect(self.actionPrefs, SIGNAL("triggered()"),
                     self.open_preferences_dialog)

        self.connect(self.actionSave, SIGNAL("triggered()"),
                     partial(self.save_pattern_dialog, "save"))

        self.connect(self.actionSave_as, SIGNAL("triggered()"),
                     partial(self.save_pattern_dialog, "save as"))
        
        self.connect(self.actionOpen, SIGNAL("triggered()"),
                     self.read_project_dialog)

        self.connect(self.actionExport, SIGNAL("triggered()"),
                     self.export_pattern_dialog)

        self.connect(self.actionPrint, SIGNAL("triggered()"),
                     self.open_print_dialog)

        self.connect(self.actionShow_grid_labels, SIGNAL("toggled(bool)"),
                     self.__canvas.toggle_label_visibility)
        
        self.connect(self.actionShow_legend, SIGNAL("toggled(bool)"),
                     self.__canvas.toggle_legend_visibility)

        self.connect(self.actionShow_pattern_grid, SIGNAL("toggled(bool)"),
                     self.__canvas.toggle_pattern_grid_visibility)
        
        self.connect(self.__canvas, SIGNAL("scene_changed"),
                     self.set_project_dirty)

        self.connect(self.actionInsert_delete_rows_and_columns, 
                     SIGNAL("triggered()"),
                     partial(self.__canvas.insert_delete_rows_columns, 1, 1))

        self.connect(self.actionZoom_In, SIGNAL("triggered()"),
                     self.graphicsView.zoom_in)

        self.connect(self.actionZoom_Out, SIGNAL("triggered()"),
                     self.graphicsView.zoom_out)

        self.connect(self.actionFit, SIGNAL("triggered()"),
                     self.graphicsView.fit_scene)



    def __set_up_timers(self):
        """
        Set up timers.
        """

        saveTimer = QTimer(self)
        self.connect(saveTimer, SIGNAL("timeout()"), self.__save_pattern)
        saveTimer.start(10000)



    def set_project_dirty(self):
        """
        This function marks the canvas as dirty, aka it needs
        to be saved.
        """

        self.__projectIsDirty = True
        self.setWindowModified(True)



    def set_project_clean(self):
        """
        This function marks the project as clean, aka it does not need
        to be saved.
        """

        self.__projectIsDirty = False
        self.setWindowModified(False)



    def closeEvent(self, event):
        """
        Quit sconcho. If the canvas is currently dirty, we ask the
        user if she wants to save it.
        """

        if not self.__ok_to_continue_without_saving():
            return

        # before we exit save our settings
        self.__save_settings()
        



    def initialize_symbol_widget(self, knittingSymbols):
        """
        Proxy for adding all the knitting symbols to the symbolWidget
        and connecting it to the symbol changed slot.

        NOTE: Unfortunately, the order of the connections below matters.
        Connect the symbolCategoryChooser only after it has been fully
        set up. Otherwise we get spurious selector widget switches until
        the chooser has established the correct order.
        """

        symbolTracker = SymbolSynchronizer()
        self.connect(symbolTracker, 
                     SIGNAL("synchronized_object_changed"),
                     self.__canvas.set_active_symbol)

        self.connect(symbolTracker, 
                     SIGNAL("synchronized_object_changed"),
                     self.activeSymbolWidget.active_symbol_changed)
        
        self.connect(symbolTracker, 
                     SIGNAL("synchronized_object_changed"),
                     self.set_project_dirty)

        self.connect(self,
                     SIGNAL("unselect_active_symbol"),
                     symbolTracker.unselect)
       
        
        (self.selectedSymbol, self.symbolSelector,
         self.symbolSelectorWidgets) = \
                        generate_symbolWidgets(knittingSymbols,
                                               self.symbolCategoryChooser,
                                               self.symbolSelectorLayout,
                                               symbolTracker)

        self.connect(self.symbolCategoryChooser,
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

        self.selectedSymbol = self.symbolSelector[categoryName]
        self.symbolSelectorLayout.addWidget(self.selectedSymbol)
        
        

    def initialize_color_widget(self):
        """
        Proxy for adding all the color selectors to the color selector
        Widget and connecting the slots
        """

        colorTracker = ColorSynchronizer()
        self.connect(colorTracker, 
                     SIGNAL("synchronized_object_changed"),
                     self.__canvas.set_active_color)

        self.connect(colorTracker, 
                     SIGNAL("synchronized_object_changed"),
                     self.activeSymbolWidget.active_color_changed)

        self.connect(colorTracker, 
                     SIGNAL("synchronized_object_changed"),
                     self.set_project_dirty)

        colorList = [QColor(name) for name in [Qt.white, Qt.red, Qt.blue, \
                        Qt.black, Qt.darkGray, Qt.cyan, Qt.yellow, Qt.green, 
                        Qt.magenta]]
        self.__colorWidget = ColorWidget(colorTracker, colorList)
        self.colorWidgetContainer.layout().addWidget(self.__colorWidget)
        


    def show_sconcho_manual(self):
        """ Show the sconcho manual. """

        manualPath = os.path.join(self.__topLevelPath, "doc/manual.html")
        manual = SconchoManual(manualPath, self)
        manual.exec_()



    def show_about_sconcho(self):
        """ Show the about sconcho dialog. """
        
        QMessageBox.about(self, QApplication.applicationName(),
                          msg.sconchoDescription % (__version__,
                                                    platform.python_version(),
                                                    QT_VERSION_STR,
                                                    PYQT_VERSION_STR,
                                                    platform.system()))



    def show_about_qt4(self):
        """ Show the about Qt dialog. """
        
        QMessageBox.aboutQt(self)



    def new_pattern_dialog(self):
        """ 
        Open a dialog giving users an opportunity to save
        their previous pattern or cancel.
        """

        if not self.__ok_to_continue_without_saving():
            return


        newPattern = NewPatternWidget(self)
        if newPattern.exec_():
            
            # start new canvas
            self.clear_project_save_file()
            self.set_project_dirty()
            self.__canvas.create_new_canvas(newPattern.num_rows,
                                            newPattern.num_columns)




    def save_pattern_dialog(self, mode):
        """
        If necessary, fire up a save pattern dialog and then save.

        Returns True on successful saving of the file and False
        otherwise.
        """

        if (mode == "save as") or (not self.__saveFilePath): 
            location = self.__saveFilePath if self.__saveFilePath \
                       else QDir.homePath() + "/.spf"
            saveFilePath = QFileDialog.getSaveFileName(self,
                                                msg.saveSconchoProjectTitle,
                                                location,
                                                "sconcho pattern files (*.spf)")

            if not saveFilePath:
                return False

            # check the extension; if none is present add .spf
            extension = QFileInfo(saveFilePath).completeSuffix()
            if extension != "spf":
                saveFilePath = saveFilePath + ".spf"

                # since we added the extension QFileDialog might not
                # have detected a file collision
                if QFile(saveFilePath).exists():
                    saveFileName = QFileInfo(saveFilePath).fileName()
                    messageBox = QMessageBox.question(self,
                                    msg.patternFileExistsTitle, 
                                    msg.patternFileExistsText % saveFileName,
                                    QMessageBox.Ok | QMessageBox.Cancel)

                    if (messageBox == QMessageBox.Cancel):
                            return False

            self.set_project_save_file(saveFilePath)

        # ready to save
        return self.__save_pattern()
    


    def __save_pattern(self):
        """ Main save routine.

        If there is no filepath we return (e.g. when called by the saveTimer).
        """
        
        if not self.__saveFilePath or not self.__projectIsDirty:
            return False

        saveFileName = QFileInfo(self.__saveFilePath).fileName()
        self.statusBar().showMessage("saving " + saveFileName)

        (status, errMsg) = io.save_project(self.__canvas, 
                                           self.__colorWidget.get_all_colors(),
                                           self.activeSymbolWidget.get_symbol(),
                                           self.settings, self.__saveFilePath)

        if not status:
            QMessageBox.critical(self, msg.errorSavingProjectTitle,
                                 errMsg, QMessageBox.Close)
            return False
        
        self.statusBar().showMessage("successfully saved " + saveFileName, 2000)
        self.set_project_clean()
        return True



    def read_project_dialog(self):
        """ This function opens a read pattern dialog. """

        if not self.__ok_to_continue_without_saving():
            return

        readFilePath = \
             QFileDialog.getOpenFileName(self,
                                         msg.openSconchoProjectTitle,
                                         QDir.homePath(),
                                         "sconcho pattern files (*.spf)")

        if not readFilePath:
            return

        self.__read_project(readFilePath)

        

    def __read_project(self, readFilePath):
        """ This function does the hard work for opening a 
        sconcho project file.
        """

        (status, errMsg, patternGridItems, legendItems, colors, activeItem) = \
                               io.read_project(self.settings, readFilePath)
           
        if not status:
            QMessageBox.critical(self, msg.errorOpeningProjectTitle,
                                 errMsg, QMessageBox.Close)
            return

        # add newly loaded project
        knittingSymbols = parser.parse_all_symbols(self.__symbolPaths)
        if not self.__canvas.load_previous_pattern(knittingSymbols, 
                                                   patternGridItems,
                                                   legendItems):
            return

        set_up_colors(self.__colorWidget, colors)
        self.activate_symbolSelectorItem(self.symbolSelectorWidgets, activeItem)
        readFileName = QFileInfo(readFilePath).fileName()
        self.statusBar().showMessage("successfully opened " + readFileName, 3000)
        self.set_project_save_file(readFilePath)
        self.set_project_clean()



    def export_pattern_dialog(self):
        """
        This function opens and export pattern dialog.
        """

        canvasSize = self.__canvas.itemsBoundingRect()
        exportDialog = ExportBitmapWidget(canvasSize, self)
        if exportDialog.exec_():
            width = exportDialog.width
            height = exportDialog.height
            exportFilePath = exportDialog.filePath
            
            io.export_scene(self.__canvas, width, height, exportFilePath)
            exportFileName = QFileInfo(exportFilePath).fileName()
            self.statusBar().showMessage("successfully exported " + 
                                         exportFileName, 3000)



    def open_print_dialog(self):
        """
        This member function calls print routine.
        """

        io.print_scene(self.__canvas)
        


    def open_preferences_dialog(self):
        """ Open the preferences dialog. """

        
        if not self.__preferencesDialog:
            self.__preferencesDialog = PreferencesDialog(self.settings, self)
            
            self.connect(self.__preferencesDialog, 
                         SIGNAL("label_font_changed"),
                         self.__canvas.label_font_changed)

            self.connect(self.__preferencesDialog, 
                         SIGNAL("label_font_changed"),
                         self.set_project_dirty)

            self.connect(self.__preferencesDialog, 
                         SIGNAL("legend_font_changed"),
                         self.__canvas.legend_font_changed)

            self.connect(self.__preferencesDialog, 
                         SIGNAL("legend_font_changed"),
                         self.set_project_dirty)

            self.connect(self.__preferencesDialog, 
                         SIGNAL("label_interval_changed"),
                         self.__canvas.set_up_labels)

            self.connect(self.__preferencesDialog, 
                         SIGNAL("label_interval_changed"),
                         self.set_project_dirty)

       
        self.__preferencesDialog.raise_()
        self.__preferencesDialog.show()



    def set_project_save_file(self, fileName):
        """ Stores the name of the currently operated on file. """

        self.__saveFilePath = fileName
        self.setWindowTitle(QApplication.applicationName() + ": " \
                            + QFileInfo(fileName).fileName() + "[*]")



    def clear_project_save_file(self):
        """ Resets the save file name and window title. """


        self.__saveFilePath = None
        self.setWindowTitle(QApplication.applicationName() + ": "\
                            + misc.get_random_knitting_quote() + "[*]")



    def __ok_to_continue_without_saving(self):
        """ This function checks if the user would like to
        save the current pattern. Returns True if the pattern
        was save or the user discarded changes, and False if
        the user canceled.
        """

        status = True
        if self.__projectIsDirty:
            answer = QMessageBox.question(self, msg.wantToSavePatternTitle,
                                          msg.wantToSavePatternText,
                                          QMessageBox.Save |
                                          QMessageBox.Discard |
                                          QMessageBox.Cancel)

            if answer == QMessageBox.Save:
                savedOk = self.save_pattern_dialog("save")
                if not savedOk:
                    status = False
            elif answer == QMessageBox.Cancel:
                status = False

        return status
        


    def activate_symbolSelectorItem(self, symbolWidgets, activeItem):
        """ Activate the requested item.

        If activeItem is None we inactivate whatever symbolSelectorWidget
        is currently selected. Otherwise activate the proper widget.
        The activeItem comes directly from the parser so we have to
        be careful.
        """

        try:
            name = activeItem["name"]
        except:
            return

        if name == "None":
            self.emit(SIGNAL("unselect_active_symbol"))

        try:
            category = activeItem["category"]
        except:
            return

        if (name, category) in symbolWidgets:
            symbolWidgets[(name, category)].click_me()
        


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
        self.layout.setSizeConstraint(5)
        
        self.activeSymbolLabel     = QLabel("Active Symbol")
        self.inactiveSymbolLabel   = QLabel("No Active Symbol")
        
        self.widget = None
        self.label  = self.inactiveSymbolLabel
        self.layout.addWidget(self.label,0,0)
        self.setLayout(self.layout)



    def get_symbol(self):
        """ Returns the current active symbol. """

        return self.widget.get_symbol() if self.widget \
               else None
        


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
            self.widget = None
            
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



    def get_symbol(self):
        """ Return our symbol. """

        return self.__symbol

    


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





################################################################
##
## Helper functions
##
################################################################

def set_up_colors(widget, colors):
    """
    Sets the colors of ColorSelectorItems in the widget to
    the requested colors. Also activates the previously
    active item.
    """

    assert (len(widget.colorWidgets) >= len(colors))

    for (i, item) in enumerate(widget.colorWidgets):
        (color, state) = colors[i]
        item.set_content(color)
        if state == 1:
            item.activate()
            
        item.repaint()


