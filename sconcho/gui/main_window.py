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


__version__ = "0.1.0_a9"


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

from sconcho.gui.ui_main_window import Ui_MainWindow
import sconcho.util.messages as msg
import sconcho.util.settings as settings
import sconcho.util.misc as misc
import sconcho.util.io as io
import sconcho.util.symbol_parser as parser
from sconcho.gui.symbol_widget import (generate_symbolWidgets, SymbolSynchronizer,
                                      symbols_by_category)
from sconcho.gui.color_widget import (ColorWidget, ColorSynchronizer)
from sconcho.gui.pattern_canvas import PatternCanvas
from sconcho.gui.export_bitmap_dialog import ExportBitmapDialog
from sconcho.gui.new_pattern_dialog import NewPatternDialog
from sconcho.gui.preferences_dialog import PreferencesDialog
from sconcho.gui.sconcho_manual import SconchoManual
from sconcho.gui.manage_symbol_dialog import ManageSymbolDialog
from sconcho.util.exceptions import PatternReadError



#######################################################################
#
# top level window class
#
#######################################################################
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, topLevelPath, settings, knittingSymbols, 
                 fileName = None, parent = None):
        """ Initialize the main window. """

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.settings = settings
        self._restore_window_settings()
        self.colorWidget = None
        self.preferencesDialog = None
        self.manualDialog = None

        self.clear_project_save_file()

        # set up the statusBar
        self.activeSymbolWidget = ActiveSymbolWidget()
        self.statusBar().addPermanentWidget(self.activeSymbolWidget)

        self._topLevelPath = topLevelPath
        self._knittingSymbols = knittingSymbols
        self.canvas = PatternCanvas(self.settings, 
                                    knittingSymbols[QString("knit")],
                                    self)
        self.initialize_symbol_widget(knittingSymbols)
        self.initialize_color_widget()

        # we set a manual scene rectangle for our view. we
        # should be a little smarter about this in the future
        self.graphicsView.setScene(self.canvas)
        self.connect(self.canvas, SIGNAL("adjust_view"),
                     self.graphicsView.adjust_scene)
        self.graphicsView.adjust_scene()

        # set up all the connections
        self._set_up_connections()

        # nothing happened so far
        self._projectIsDirty = False

        # read project if we received a filename but first check
        # if we have a recovery file.
        if fileName:
            (was_recovered, readFileName) = check_for_recovery_file(fileName)
            self._read_project(readFileName)
            self.set_project_save_file(fileName)
            self.canvas.clear_undo_stack()
            if not was_recovered:
                self.mark_project_clean()

        # set up timers
        # NOTE: Needs to be last, otherwise some signals may not
        # connect properly
        self._set_up_timers()



    def _restore_window_settings(self):
        """ Restore the previously saved settings. """

        self.resize(self.settings.main_window_size)
        self.move(self.settings.main_window_position)
        self.restoreState(self.settings.main_window_state)



    def _save_settings(self):
        """ Save all settings. """
        
        self.settings.main_window_size = self.size()
        self.settings.main_window_position = self.pos()
        self.settings.main_window_state = self.saveState()



    def _set_up_connections(self):
        """ Set up all connections for MainWindow. """
        
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

        self.connect(self.action_Manage_Knitting_Symbols,
                     SIGNAL("triggered()"),
                     self.open_manage_knitting_symbols_dialog)

        self.connect(self.actionShow_grid_labels, SIGNAL("toggled(bool)"),
                     self.canvas.toggle_label_visibility)
        
        self.connect(self.actionShow_legend, SIGNAL("toggled(bool)"),
                     self.canvas.toggle_legend_visibility)

        self.connect(self.actionShow_pattern_grid, SIGNAL("toggled(bool)"),
                     self.canvas.toggle_pattern_grid_visibility)

        self.connect(self.canvas, SIGNAL("scene_changed"),
                     self.set_project_dirty)

        self.connect(self.action_Insert_delete_rows_and_columns, 
                     SIGNAL("triggered()"),
                     partial(self.canvas.insert_delete_rows_columns, 1, 1))

        self.connect(self.actionZoom_In, SIGNAL("triggered()"),
                     self.graphicsView.zoom_in)

        self.connect(self.actionZoom_Out, SIGNAL("triggered()"),
                     self.graphicsView.zoom_out)

        self.connect(self.actionFit, SIGNAL("triggered()"),
                     self.graphicsView.fit_scene)

        self.connect(self.action_Normal, SIGNAL("triggered()"),
                     self.graphicsView.normal_view)

        self.connect(self.actionUnselect_All, SIGNAL("triggered()"),
                     self.canvas.clear_all_selected_cells)

        self.connect(self.actionCreate_Pattern_Repeat, SIGNAL("triggered()"),
                     self.canvas.add_pattern_repeat)

        self.connect(self.action_Undo, SIGNAL("triggered()"),
                     self.canvas.undo)

        self.connect(self.action_Redo, SIGNAL("triggered()"),
                     self.canvas.redo)



    def keyPressEvent(self, event):
        """ Catch some key press events. """

        if event.key() == Qt.Key_G:
            if (event.modifiers() & Qt.ControlModifier) and \
               (event.modifiers() & Qt.ShiftModifier):
                   self.check_pattern_grid()
        else:
            QMainWindow.keyPressEvent(self, event)



    def check_pattern_grid(self):
        """ NOTE: this is a temporary function which will be removed
        in the production version. It is mainly indended for the 
        maintiner and this hidden. It can be invoked
        by pressing CONTROL + SHIFT + G. It allows to query the pattern grid
        to make sure there are no overlapping PatternGridItems as has
        happened in the past after copy and past actions.
        If such items are detected they are removed (but one).

        """

        result = self.canvas.check_pattern_grid()

        if result:
            message = ("The canvas had duplicate symbols. \n"
                      "The following items were removed from the canvas:\n")
            for item in result:
                message += str(item)
                message += "\n"
        else:
            message = "Canvas is clean - no changes neccessary!"

        QMessageBox.information(self, "sconcho: Check Pattern", message)



    def _set_up_timers(self):
        """ Set up timers.

        NOTE: We can't use functools.partial to bind the recoveryFilePath
        since it might change during the life time of the program.

        """

        saveTimer = QTimer(self)
        self.connect(saveTimer, SIGNAL("timeout()"),
                     self._save_timed_recovery_file)
        saveTimer.start(10000)



    def _save_timed_recovery_file(self):
        """ Simple function that calls the saving routine. """

        if self._recoveryFilePath:
            self._save_pattern(self._recoveryFilePath, False)



    def set_project_dirty(self):
        """ This function marks the canvas as dirty, aka it needs
        to be saved.
        
        """

        self._projectIsDirty = True
        self.setWindowModified(True)



    def mark_project_clean(self):
        """ This function marks the project as clean, aka it does not need
        to be saved.
        
        """

        self._projectIsDirty = False
        self.setWindowModified(False)



    def closeEvent(self, event):
        """ Quit sconcho. If the canvas is currently dirty, we ask the
        user if she wants to save it.
         
        """

        if not self._ok_to_continue_without_saving():
            event.ignore()
        else:
            # before we exit save our settings
            self._save_settings()

            # remove recovery file
            if self._recoveryFilePath:
                recoveryFileHandle = QFile(self._recoveryFilePath)
                recoveryFileHandle.remove()
            
            event.accept()



    def initialize_symbol_widget(self, knittingSymbols):
        """ Proxy for adding all the knitting symbols to the symbolWidget
        and connecting it to the symbol changed slot.

        NOTE: Unfortunately, the order of the connections below matters.
        Connect the symbolCategoryChooser only after it has been fully
        set up. Otherwise we get spurious selector widget switches until
        the chooser has established the correct order.
        
        """

        symbolTracker = SymbolSynchronizer()
        self.connect(self.canvas, 
                     SIGNAL("activate_symbol"),
                     self.activeSymbolWidget.active_symbol_changed)
        
        self.connect(self.canvas, 
                     SIGNAL("unactivate_symbol"),
                     partial(self.activeSymbolWidget.active_symbol_changed,
                             None))
        
        self.connect(self.canvas,
                     SIGNAL("activate_symbol"),
                     self.set_project_dirty)

        self.connect(self.canvas,
                     SIGNAL("unactivate_symbol"),
                     self.set_project_dirty)

        # the connection between canvas and symbolTracker has
        # to be bi-directional so the canvas can properly 
        # undo/redo selections
        self.connect(symbolTracker, 
                     SIGNAL("synchronized_object_changed"),
                     self.canvas.set_active_symbol)

        self.connect(self.canvas,
                     SIGNAL("activate_symbol"),
                     symbolTracker.select_plain)

        self.connect(self.canvas,
                     SIGNAL("unactivate_symbol"),
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
        """ Proxy for adding all the color selectors to the color selector
        Widget and connecting the slots
        
        """

        colorTracker = ColorSynchronizer()
        self.connect(self.canvas,
                     SIGNAL("activate_color_selector"),
                     self.activeSymbolWidget.active_colorObject_changed)
        
        self.connect(self.canvas,
                     SIGNAL("activate_color_selector"),
                     self.set_project_dirty)

        # the connection between canvas and colorTracker has
        # to be bi-directional so the canvas can properly 
        # undo/redo selections
        self.connect(colorTracker, 
                     SIGNAL("synchronized_object_changed"),
                     self.canvas.set_active_colorObject)

        self.connect(self.canvas,
                     SIGNAL("activate_color_selector"),
                     colorTracker.select_plain)

        self.connect(colorTracker,
                     SIGNAL("active_color_changed"),
                     self.canvas.change_active_color)


        colorList = [QColor(name) for name in [Qt.white, Qt.red, Qt.blue, \
                        Qt.black, Qt.darkGray, Qt.cyan, Qt.yellow, Qt.green, 
                        Qt.magenta]]
        self.colorWidget = ColorWidget(colorTracker, colorList)
        self.colorWidgetContainer.layout().addWidget(self.colorWidget)
        


    def show_sconcho_manual(self):
        """ Show the sconcho manual. """

        manualPath = os.path.join(self._topLevelPath, "doc/manual.html")
        self.manualDialog = SconchoManual(manualPath)
        self.manualDialog.setAttribute(Qt.WA_DeleteOnClose)
        self.manualDialog.open()



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
        """ Open a dialog giving users an opportunity to save
        their previous pattern or cancel.
        
        """

        if not self._ok_to_continue_without_saving():
            return


        newPattern = NewPatternDialog(self)
        if newPattern.exec_():
            
            # start new canvas
            self.clear_project_save_file()
            self.set_project_dirty()
            self.canvas.create_new_canvas(newPattern.num_rows,
                                            newPattern.num_columns)




    def save_pattern_dialog(self, mode):
        """ If necessary, fire up a save pattern dialog and then save.

        Returns True on successful saving of the file and False
        otherwise.
        
        """

        if (mode == "save as") or (not self._saveFilePath): 
            location = self._saveFilePath if self._saveFilePath \
                       else QDir.homePath() + "/.spf"
            saveFilePath = QFileDialog.getSaveFileName(self,
                                                msg.saveSconchoProjectTitle,
                                                location,
                                                "sconcho pattern files (*.spf)")

            # with "save as" we always want to save so
            self._projectIsDirty = True

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

        # write recovery file
        self._save_pattern(self._recoveryFilePath, markProjectClean = False)

        # ready to save
        return self._save_pattern(self._saveFilePath)
    


    def _save_pattern(self, filePath, markProjectClean = True):
        """ Main save routine.

        If there is no filepath we return (e.g. when called by the saveTimer).
        
        """
        
        if not filePath or not self._projectIsDirty:
            return False

        saveFileName = QFileInfo(filePath).fileName()
        self.statusBar().showMessage("saving " + saveFileName)

        (status, errMsg) = io.save_project(self.canvas, 
                                           self.colorWidget.get_all_colors(),
                                           self.activeSymbolWidget.get_symbol(),
                                           self.settings, filePath)

        if not status:
            QMessageBox.critical(self, msg.errorSavingProjectTitle,
                                 errMsg, QMessageBox.Close)
            return False
        
        self.statusBar().showMessage("successfully saved " + \
                                     saveFileName, 2000)

        if markProjectClean:
            self.mark_project_clean()
            
        return True



    def read_project_dialog(self):
        """ This function opens a read pattern dialog. """

        if not self._ok_to_continue_without_saving():
            return

        readFilePath = \
             QFileDialog.getOpenFileName(self,
                                         msg.openSconchoProjectTitle,
                                         QDir.homePath(),
                                         "sconcho pattern files (*.spf)")

        if not readFilePath:
            return

        self._read_project(readFilePath)
        self.set_project_save_file(readFilePath)
        self.mark_project_clean()

        

    def _read_project(self, readFilePath):
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
        if not self.canvas.load_previous_pattern(self._knittingSymbols, 
                                                 patternGridItems,
                                                 legendItems):
            return

        set_up_colors(self.colorWidget, colors)
        self.activate_symbolSelectorItem(self.symbolSelectorWidgets, activeItem)
        readFileName = QFileInfo(readFilePath).fileName()
        self.emit(SIGNAL("update_preferences"))
        self.statusBar().showMessage("successfully opened " + readFileName, 3000)



    def export_pattern_dialog(self):
        """ This function opens and export pattern dialog. """

        canvasSize = self.canvas.itemsBoundingRect()
        exportDialog = ExportBitmapDialog(canvasSize, self)
        if exportDialog.exec_():
            io.export_scene(self.canvas,
                            exportDialog.width,
                            exportDialog.height,
                            exportDialog.hideNostitchSymbols,
                            exportDialog.filePath)
            exportFileName = QFileInfo(exportDialog.filePath).fileName()
            self.statusBar().showMessage("successfully exported " + 
                                         exportFileName, 3000)



    def open_print_dialog(self):
        """ This member function calls print routine. """

        io.print_scene(self.canvas)
        


    def open_preferences_dialog(self):
        """ Open the preferences dialog. """

        
        if not self.preferencesDialog:
            self.preferencesDialog = PreferencesDialog(self.settings, self)
            
            self.connect(self.preferencesDialog, 
                         SIGNAL("label_font_changed"),
                         self.canvas.label_font_changed)

            self.connect(self.preferencesDialog, 
                         SIGNAL("label_font_changed"),
                         self.set_project_dirty)

            self.connect(self.preferencesDialog, 
                         SIGNAL("legend_font_changed"),
                         self.canvas.legend_font_changed)

            self.connect(self.preferencesDialog, 
                         SIGNAL("legend_font_changed"),
                         self.set_project_dirty)

            self.connect(self.preferencesDialog, 
                         SIGNAL("label_interval_changed"),
                         self.canvas.set_up_labels)

            self.connect(self.preferencesDialog, 
                         SIGNAL("label_interval_changed"),
                         self.set_project_dirty)

            self.connect(self.preferencesDialog,
                         SIGNAL("grid_cell_dimensions_changed"),
                         self.canvas.change_grid_cell_dimensions)

            self.connect(self.preferencesDialog,
                         SIGNAL("grid_cell_dimensions_changed"),
                         self.set_project_dirty)

            self.connect(self,
                         SIGNAL("update_preferences"),
                         self.preferencesDialog.populate_interface)


        self.preferencesDialog.raise_()
        self.preferencesDialog.show()




    def open_manage_knitting_symbols_dialog(self):
        """ Open dialog allowing users to manage their own
        symbols (as opposed to the ones which come with sconcho).
        
        """

        sortedSymbols = symbols_by_category(self._knittingSymbols)
        symbolCategories = sortedSymbols.keys()
        personalSymbolPath = self.settings.personal_symbol_path
        manager = ManageSymbolDialog(personalSymbolPath, 
                                             symbolCategories, self)
        manager.exec_()




    def set_project_save_file(self, fileName):
        """ Stores the name of the currently operated on file. """

        self._saveFilePath = fileName
        self.setWindowTitle(QApplication.applicationName() + ": " \
                            + QFileInfo(fileName).fileName() + "[*]")

        # generate recovery file path
        self._recoveryFilePath = generate_recovery_filepath(fileName)



    def clear_project_save_file(self):
        """ Resets the save file name and window title. """


        self._saveFilePath = None
        self._recoveryFilePath = None
        self.setWindowTitle(QApplication.applicationName() + ": "\
                            + misc.get_random_knitting_quote() + "[*]")



    def _ok_to_continue_without_saving(self):
        """ This function checks if the user would like to
        save the current pattern. Returns True if the pattern
        was save or the user discarded changes, and False if
        the user canceled.
        
        """

        status = True
        if self._projectIsDirty:
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
        self.setMinimumSize(20,20)
        self.setStyleSheet(self._theStyleSheet)

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





################################################################
##
## Helper functions
##
################################################################

def set_up_colors(widget, colors):
    """ Sets the colors of ColorSelectorItems in the widget to
    the requested colors. Also activates the previously
    active item.
    
    """

    assert (len(widget.colorWidgets) >= len(colors))

    for (i, item) in enumerate(widget.colorWidgets):
        (color, state) = colors[i]
        item.set_content(color)
        if state == 1:
            widget._synchronizer.select(item)
            
        item.repaint()



def generate_recovery_filepath(filePath):
    """ Based on a filePath generate the name for the recovery File. """

    recoveryFileInfo = QFileInfo(filePath)
    recoveryFilePath = recoveryFileInfo.path() + "/." + \
                           recoveryFileInfo.fileName() + ".swp"

    return recoveryFilePath



def check_for_recovery_file(filePath):
    """ Check for presence of recovery file. If we have
    one, ask we if should open if and return a tuple
    (status, filename of file to open).

    """
    
    returnPath = (False, filePath)
    recoveryFilePath = generate_recovery_filepath(filePath)
    recoveryFile = QFile(recoveryFilePath)
    fileName = QFileInfo(filePath).fileName()
    if recoveryFile.exists():
        answer = QMessageBox.question(None,
                                 msg.recoveryFilePresentTitle, 
                                 msg.recoveryFilePresentText.format(fileName),
                                 QMessageBox.Ok | QMessageBox.Cancel)

        if (answer == QMessageBox.Ok):
            returnPath = (True, recoveryFilePath)

    return returnPath