#-*- coding: utf-8 -*-
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


# version and release date of current sconcho
__version__ = "0.1.0_b9"
__releaseDate__ = "2012-01-02"


import platform, os
from functools import partial

try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str

# QStringlist

from PyQt4.QtCore import (SIGNAL, SLOT, QSettings, QDir, QFileInfo, 
                          Qt, QSize, QFile, QTimer, QVariant,
                          QPoint, PYQT_VERSION_STR, qVersion, 
                          QObject, QFileInfo)
from PyQt4.QtGui import (QMainWindow, QMessageBox, QFileDialog,
                         QWidget, QGridLayout, QHBoxLayout, QLabel, 
                         QFrame, QColor, QApplication, QDialog, QAction,
                         QPrinter, QPrintDialog, QPrintPreviewDialog,)
from PyQt4.QtSvg import QSvgWidget

from sconcho.gui.ui_main_window import Ui_MainWindow
import sconcho.util.messages as msg
import sconcho.util.settings as settings
import sconcho.util.misc as misc
import sconcho.util.io as io
import sconcho.util.symbol_parser as parser
from sconcho.gui.symbol_widget import (generate_symbolWidgets, 
                                       SymbolSynchronizer,
                                       symbols_by_category)
from sconcho.gui.color_widget import (ColorWidget, ColorSynchronizer)
from sconcho.gui.pattern_canvas import PatternCanvas
from sconcho.gui.export_bitmap_dialog import ExportBitmapDialog
from sconcho.gui.new_pattern_dialog import NewPatternDialog
from sconcho.gui.preferences_dialog import PreferencesDialog
from sconcho.gui.sconcho_manual import SconchoManual
from sconcho.gui.update_dialog import UpdateDialog
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
        self.preferencesDialog = PreferencesDialog(self.settings, self)
        self.exportBitmapDialog = None
        self.manualDialog = None

        self.clear_project_save_file()

        self._topLevelPath = topLevelPath
        self._knittingSymbols = knittingSymbols
        self.canvas = PatternCanvas(self.settings, 
                                    knittingSymbols[QString("knit")], self)
        self.initialize_symbol_widget(knittingSymbols)
        self.initialize_color_widget()
        self.initialize_row_col_widget()

        # we set a manual scene rectangle for our view. we
        # should be a little smarter about this in the future
        self.graphicsView.setScene(self.canvas)

        self._readFileDialogPath = QDir.homePath()
        self._set_up_recently_used_files_menu()

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
            self.update_recently_used_files(fileName)
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



    def _set_up_recently_used_files_menu(self):
        """ Set up the recently used files menu """

        # load stored previously used files
        self.update_recently_used_files()

        self.connect(self.action_Clear_Recently_Used_Files,
                     SIGNAL("triggered(bool)"),
                     self.clear_recently_used_files_list)



    def _set_up_connections(self):
        """ Set up all connections for MainWindow. """

        self.connect(self.actionQuit, SIGNAL("triggered()"),
                     self.close)

        self.connect(self.actionAbout_sconcho, SIGNAL("triggered()"),
                     self.show_about_sconcho)

        self.connect(self.actionCheck_for_updates, SIGNAL("triggered()"),
                     self.show_update_check)

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

        self.connect(self.menuRecent_Files, SIGNAL("triggered(QAction*)"),
                     self.open_recent_file)

        self.connect(self.actionExport, SIGNAL("triggered()"),
                     self.export_pattern_dialog)

        self.connect(self.actionPrint, SIGNAL("triggered()"),
                     self.open_print_dialog)

        self.connect(self.actionPrint_Preview, SIGNAL("triggered()"),
                     self.open_print_preview_dialog)

        self.connect(self.action_Manage_Knitting_Symbols,
                     SIGNAL("triggered()"),
                     self.open_manage_knitting_symbols_dialog)

        self.connect(self.actionShow_legend, SIGNAL("toggled(bool)"),
                     self.canvas.toggle_legend_visibility)

        self.connect(self.actionShow_pattern_grid, SIGNAL("toggled(bool)"),
                     self.canvas.toggle_pattern_grid_visibility)

        self.connect(self.canvas, SIGNAL("scene_changed"),
                     self.set_project_dirty)

        self.connect(self.canvas, SIGNAL("row_repeat_added"),
                     partial(self.preferencesDialog.allow_all_label_options, False))

        self.connect(self.canvas, SIGNAL("no_more_row_labels"),
                     partial(self.preferencesDialog.allow_all_label_options, True))

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

        self.connect(self.actionCreate_Pattern_Repeat, 
                     SIGNAL("triggered()"),
                     self.canvas.add_pattern_repeat)

        self.connect(self.actionApply_Color_to_Selection, 
                     SIGNAL("triggered()"),
                     self.canvas.apply_color_to_selection)

        self.connect(self.actionAdd_Text, SIGNAL("triggered()"),
                     self.canvas.add_text_item)

        self.connect(self.action_Undo, SIGNAL("triggered()"),
                     self.canvas.undo)

        self.connect(self.action_Redo, SIGNAL("triggered()"),
                     self.canvas.redo)

        # connections for preferences dialog
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
                     SIGNAL("toggle_rowLabel_visibility(bool)"),
                     self.canvas.toggle_rowLabel_visibility)

        self.connect(self.preferencesDialog, 
                     SIGNAL("toggle_columnLabel_visibility(bool)"),
                     self.canvas.toggle_columnLabel_visibility)

        self.connect(self.preferencesDialog, 
                     SIGNAL("row_label_interval_changed"),
                     self.canvas.set_up_labels)

        self.connect(self.preferencesDialog, 
                     SIGNAL("row_label_interval_changed"),
                     self.set_project_dirty)

        self.connect(self.preferencesDialog, 
                     SIGNAL("column_label_interval_changed"),
                     self.canvas.set_up_labels)

        self.connect(self.preferencesDialog, 
                     SIGNAL("column_label_interval_changed"),
                     self.set_project_dirty)

        self.connect(self.preferencesDialog, 
                     SIGNAL("row_label_start_changed"),
                     self.canvas.set_up_labels)

        self.connect(self.preferencesDialog, 
                     SIGNAL("row_label_start_changed"),
                     self.set_project_dirty)

        self.connect(self.preferencesDialog, 
                     SIGNAL("row_label_location_changed"),
                     self.canvas.set_up_labels)

        self.connect(self.preferencesDialog, 
                     SIGNAL("row_label_location_changed"),
                     self.set_project_dirty)

        self.connect(self.preferencesDialog,
                     SIGNAL("grid_cell_dimensions_changed"),
                     self.canvas.change_grid_cell_dimensions)

        self.connect(self.preferencesDialog,
                     SIGNAL("grid_cell_dimensions_changed"),
                     self.set_project_dirty)

        self.connect(self.preferencesDialog,
                     SIGNAL("highlighted_row_visibility_changed"),
                     self.canvas.toggle_row_highlighting)

        self.connect(self.preferencesDialog,
                     SIGNAL("redraw_highlighted_rows"),
                     self.canvas.set_up_highlighted_rows)

        self.connect(self.preferencesDialog,
                     SIGNAL("redraw_highlighted_rows"),
                     self.set_project_dirty)

        self.connect(self,
                     SIGNAL("update_preferences"),
                     self.preferencesDialog.populate_interface)


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
        saveTimer.start(120000)



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
                     self.recentlyUsedSymbolWidget.insert_new_symbol)
 
        self.connect(self.canvas, 
                     SIGNAL("unactivate_symbol"),
                     partial(
                       self.recentlyUsedSymbolWidget.insert_new_symbol,
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


        # this makes sure that the currently active symbol is unselected
        # when the users chooses a new category
        self.connect(self.symbolCategoryChooser,
                     SIGNAL("currentIndexChanged(QString)"),
                     partial(self.canvas.set_active_symbol, None))
        


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
                        Qt.black, Qt.darkGray, Qt.cyan, Qt.yellow, \
                        Qt.green, Qt.magenta]]
        self.colorWidget.initialize(colorTracker, colorList)
        


    def initialize_row_col_widget(self):
        """ Initialize widget showing the current row col index. """

        colLabel = QLabel("col:")
        rowLabel = QLabel("row:")
        
        self.columnCounter = QLabel("NA")
        self.connect(self.canvas, SIGNAL("col_count_changed"),
                     (lambda x: self.columnCounter.setText(str(x))))

        self.rowCounter = QLabel("NA")
        self.connect(self.canvas, SIGNAL("row_count_changed"),
                     (lambda x: self.rowCounter.setText(str(x))))
        
        layout = QHBoxLayout()
        layout.addWidget(colLabel)
        layout.addWidget(self.columnCounter)
        layout.addWidget(rowLabel)
        layout.addWidget(self.rowCounter)
        rowColWidget = QWidget()
        rowColWidget.setLayout(layout)

        self.infoLayout.addWidget(rowColWidget)



    def show_sconcho_manual(self):
        """ Show the sconcho manual. """

        manualPath = os.path.join(self._topLevelPath, "doc/manual.html")
        self.manualDialog = SconchoManual(manualPath)
        self.manualDialog.setAttribute(Qt.WA_DeleteOnClose)
        self.manualDialog.open()



    def show_update_check(self):
        """ Show dialog that checks and displays any updates 
        for sconcho.
        """

        updater = UpdateDialog(__version__, __releaseDate__)
        updater.exec_()



    def show_about_sconcho(self):
        """ Show the about sconcho dialog. """
        
        QMessageBox.about(self, QApplication.applicationName(),
                          msg.sconchoDescription % (__version__,
                                                    platform.python_version(),
                                                    qVersion(),
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
            self.recentlyUsedSymbolWidget.clear()
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
            extension = QFileInfo(saveFilePath).suffix()
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

        # write recovery file so we are up to date
        self._save_pattern(self._recoveryFilePath, markProjectClean = False)

        # ready to save main project file
        (status, thread) = self._save_pattern(self._saveFilePath)
        if status:
            thread.wait()

        # update recent files
        self.update_recently_used_files(self._saveFilePath)

        return True
    

    
    def update_recently_used_files(self, path = None):
        """ Update the list of recently used files.

        We update both the menu as well as the stored
        value in settings.

        """

        fileString = self.settings.recently_used_files

        # need this check to avoid interpreting a nonexisting entry
        # as an empty filename
        if len(fileString) == 0:
            files = list()
        else:
            files = fileString.split("%")

        # whithout a path we simply update the menu without
        # adding any filename
        if path:
            fullPath = QFileInfo(path).absoluteFilePath()
            if fullPath in files:
                return
            else:
                files.append(fullPath)
                while len(files) > 10:
                    files.pop(0)

        self.settings.recently_used_files = files.join("%")
        self.clear_recently_used_files_menu()

        # the actual path is stored as data since the text
        # of the Action also provides numbering and accelerators
        for (index, path) in enumerate(files):
            fileName = QFileInfo(path).fileName()
            newPathAction = \
                QAction(QString("&%d.  %s" % (index+1, fileName)),
                        self.menuRecent_Files)
            newPathAction.setData(path)
            self.menuRecent_Files.addAction(newPathAction)



    def clear_recently_used_files_menu(self):
        """ Clear the list of files in QMenu.

        NOTE: We can't just call clear, otherwise we'd
        nuke the Clear action and separator as well.
        """

        allPaths = self.menuRecent_Files.actions()
        for path in allPaths:
            dontKeep = path.data()
            if dontKeep:
                self.menuRecent_Files.removeAction(path)



    def clear_recently_used_files_list(self):
        """ Clear the list of recently used files. """

        self.settings.recently_used_files = QString("")
        self.clear_recently_used_files_menu()



    def _save_pattern(self, filePath, markProjectClean = True):
        """ Main save routine.

        If there is no filepath we return (e.g. when called by the 
        saveTimer).

        NOTE: This function returns the SaveThread so callers have the
        opportunity to call wait() to make sure that saving is all
        done. 
        
        """
        
        if not filePath or not self._projectIsDirty:
            return (False, None)

        saveFileName = QFileInfo(filePath).fileName()
        self.statusBar().showMessage("saving " + saveFileName)

        saveThread = io.SaveThread(self.canvas, 
                                   self.colorWidget.get_all_colors(),
                                   self.activeSymbolWidget.get_symbol(),
                                   self.settings, filePath,
                                   markProjectClean)
        self.connect(saveThread, SIGNAL("finished()"),
                     saveThread, SLOT("deleteLater()"))
        self.connect(saveThread, SIGNAL("saving_done"),
                     self._save_pattern_epilog)
        saveThread.start()

        return (True, saveThread)



    def _save_pattern_epilog(self, status, errorMessage, saveFileName,
                             markProjectClean):
        """ This method is called after the SaveThread is finished. """
        
        if not status:
            QMessageBox.critical(self, msg.errorSavingProjectTitle,
                                 errorMsg, QMessageBox.Close)
            return 
        
        self.statusBar().showMessage("successfully saved " + \
                                     saveFileName, 2000)

        if markProjectClean:
            self.mark_project_clean()

            

    def open_recent_file(self, action):
        """ This function opens a recently opened pattern."""

        # make sure we ignore menu clicks on non-filename
        # items (like the clear button)
        isFile = action.data()
        if not isFile:
            return

        # the actual filename is in the data *not* the
        # text of the item
        readFilePath = action.data().toString()
        
        if not self._ok_to_continue_without_saving():
            return

        self._read_project(readFilePath)
        self.set_project_save_file(readFilePath)
        self.mark_project_clean()



    def read_project_dialog(self):
        """ This function opens a read pattern dialog. """

        if not self._ok_to_continue_without_saving():
            return

        readFilePath = \
             QFileDialog.getOpenFileName(self,
                                         msg.openSconchoProjectTitle,
                                         self._readFileDialogPath,
                                         ("sconcho pattern files (*.spf);;"
                                          "all files (*.*)"))

        if not readFilePath:
            return

        self._readFileDialogPath = QFileInfo(readFilePath).absoluteFilePath()
        self._read_project(readFilePath)
        self.set_project_save_file(readFilePath)
        self.update_recently_used_files(readFilePath)
        self.mark_project_clean()

        

    def _read_project(self, readFilePath):
        """ This function does the hard work for opening a 
        sconcho project file.
        
        """

        (status, errMsg, patternGridItems, legendItems, colors,
         activeItem, patternRepeats, repeatLegends, rowRepeats,
         textItems) = io.read_project(self.settings, readFilePath)
        

        if not status:
            QMessageBox.critical(self, msg.errorOpeningProjectTitle,
                                 errMsg, QMessageBox.Close)
            return

        # add newly loaded project
        if not self.canvas.load_previous_pattern(self._knittingSymbols, 
                                                 patternGridItems,
                                                 legendItems,
                                                 patternRepeats,
                                                 repeatLegends,
                                                 rowRepeats,
                                                 textItems):
            return

        set_up_colors(self.colorWidget, colors)
        self.recentlyUsedSymbolWidget.clear()
        self.select_symbolSelectorItem(self.symbolSelectorWidgets, 
                                       activeItem)

        # provide feedback in statusbar
        readFileName = QFileInfo(readFilePath).fileName()
        self.emit(SIGNAL("update_preferences"))
        self.statusBar().showMessage("successfully opened " + readFileName,
                                     3000)



    def export_pattern_dialog(self):
        """ This function opens and export pattern dialog. """

        if not self.exportBitmapDialog:
            self.exportBitmapDialog = ExportBitmapDialog(self.canvas, self)

            self.connect(self.exportBitmapDialog, SIGNAL("export_pattern"),
                         partial(io.export_scene, self.canvas),
                         Qt.QueuedConnection)

        self.exportBitmapDialog.raise_()
        self.exportBitmapDialog.show()



    def open_print_dialog(self):
        """ This member function calls print routine. """

        aPrinter = QPrinter(QPrinter.HighResolution)
        printDialog = QPrintDialog(aPrinter)

        # need this to make sure we take away focus from
        # any currently selected legend items
        self.canvas.clearFocus()
    
        if printDialog.exec_() == QDialog.Accepted:
            io.printer(self.canvas, aPrinter)



    def open_print_preview_dialog(self):
        """ This member function calls print preview routine. """

        aPrinter = QPrinter(QPrinter.HighResolution)
        printPrevDialog = QPrintPreviewDialog(aPrinter)
        self.connect(printPrevDialog, SIGNAL("paintRequested(QPrinter*)"),
                     partial(io.printer, self.canvas))

        # need this to make sure we take away focus from
        # any currently selected legend items
        self.canvas.clearFocus()

        printPrevDialog.exec_()



    def open_preferences_dialog(self):
        """ Open the preferences dialog. """

        self.preferencesDialog.raise_()
        self.preferencesDialog.show()



    def open_manage_knitting_symbols_dialog(self):
        """ Open dialog allowing users to manage their own
        symbols (as opposed to the ones which come with sconcho).
        
        """

        sortedSymbols = symbols_by_category(self._knittingSymbols)
        symbolCategories = sortedSymbols.keys()
        personalSymbolPath = self.settings.personalSymbolPath.value
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
                # we save and make sure that we wait until the
                # thread is finished and the project was saved
                status = self.save_pattern_dialog("save")
            elif answer == QMessageBox.Cancel:
                status = False

        return status
 


    def select_symbolSelectorItem(self, symbolWidgets, activeItem):
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

        try:
            category = activeItem["category"]
        except:
            return

        if (name, category) in symbolWidgets:

            # select the proper category widget
            index = self.symbolCategoryChooser.findText(category)
            self.symbolCategoryChooser.setCurrentIndex(index)

            # then select the proper item in the category
            symbolWidgets[(name, category)].click_me()
        



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
        (aColor, state) = colors[i]
        item.color = aColor
        item.repaint()
        if state == 1:
            widget._synchronizer.select(item)
            




def generate_recovery_filepath(filePath):
    """ Based on a filePath generate the name for the recovery File. """

    # check if sconcho directory in user's home directory exists
    sconchoDirName = QDir.homePath() + "/.sconcho"
    sconchoDir = QDir(sconchoDirName)
    if not sconchoDir.exists():
        status = sconchoDir.mkdir(sconchoDirName)

    recoveryFileInfo = QFileInfo(filePath)
    recoveryFilePath = sconchoDirName + "/" + \
            recoveryFileInfo.fileName() + ".recovery"

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

