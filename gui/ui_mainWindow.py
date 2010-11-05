# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/mainWindow.ui'
#
# Created: Thu Nov  4 21:46:12 2010
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1137, 777)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/sconcho_icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.graphicsView = PatternView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setMinimumSize(QtCore.QSize(0, 0))
        self.graphicsView.setDragMode(QtGui.QGraphicsView.NoDrag)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.verticalLayout.addWidget(self.graphicsView)
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 80))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.colorWidgetContainer = QtGui.QWidget(self.scrollArea)
        self.colorWidgetContainer.setGeometry(QtCore.QRect(0, 0, 757, 76))
        self.colorWidgetContainer.setObjectName(_fromUtf8("colorWidgetContainer"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.colorWidgetContainer)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.scrollArea.setWidget(self.colorWidgetContainer)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1137, 28))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuGrid = QtGui.QMenu(self.menubar)
        self.menuGrid.setObjectName(_fromUtf8("menuGrid"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.symbolDockWidget = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.symbolDockWidget.sizePolicy().hasHeightForWidth())
        self.symbolDockWidget.setSizePolicy(sizePolicy)
        self.symbolDockWidget.setMinimumSize(QtCore.QSize(350, 154))
        self.symbolDockWidget.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.symbolDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.symbolDockWidget.setObjectName(_fromUtf8("symbolDockWidget"))
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName(_fromUtf8("dockWidgetContents_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.patternCategoryChooser = QtGui.QComboBox(self.dockWidgetContents_3)
        self.patternCategoryChooser.setObjectName(_fromUtf8("patternCategoryChooser"))
        self.verticalLayout_2.addWidget(self.patternCategoryChooser)
        self.symbolSelectorLayout = QtGui.QVBoxLayout()
        self.symbolSelectorLayout.setObjectName(_fromUtf8("symbolSelectorLayout"))
        self.verticalLayout_2.addLayout(self.symbolSelectorLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.symbolDockWidget.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.symbolDockWidget)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionAbout_sconcho = QtGui.QAction(MainWindow)
        self.actionAbout_sconcho.setIcon(icon)
        self.actionAbout_sconcho.setObjectName(_fromUtf8("actionAbout_sconcho"))
        self.actionAbout_Qt4 = QtGui.QAction(MainWindow)
        self.actionAbout_Qt4.setObjectName(_fromUtf8("actionAbout_Qt4"))
        self.actionPreferences = QtGui.QAction(MainWindow)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.actionNew = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/filenew.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNew.setIcon(icon1)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionOpen = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/fileopen.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon2)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QtGui.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/filesave.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon3)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionSave_as = QtGui.QAction(MainWindow)
        self.actionSave_as.setIcon(icon3)
        self.actionSave_as.setObjectName(_fromUtf8("actionSave_as"))
        self.actionExport = QtGui.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/fileexport.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExport.setIcon(icon4)
        self.actionExport.setObjectName(_fromUtf8("actionExport"))
        self.actionQuit = QtGui.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionQuit.setIcon(icon5)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionPrint = QtGui.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/fileprint.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPrint.setIcon(icon6)
        self.actionPrint.setObjectName(_fromUtf8("actionPrint"))
        self.actionShow_pattern_grid = QtGui.QAction(MainWindow)
        self.actionShow_pattern_grid.setCheckable(True)
        self.actionShow_pattern_grid.setChecked(True)
        self.actionShow_pattern_grid.setObjectName(_fromUtf8("actionShow_pattern_grid"))
        self.actionShow_legend = QtGui.QAction(MainWindow)
        self.actionShow_legend.setCheckable(True)
        self.actionShow_legend.setChecked(True)
        self.actionShow_legend.setObjectName(_fromUtf8("actionShow_legend"))
        self.actionShow_grid_labels = QtGui.QAction(MainWindow)
        self.actionShow_grid_labels.setCheckable(True)
        self.actionShow_grid_labels.setChecked(True)
        self.actionShow_grid_labels.setObjectName(_fromUtf8("actionShow_grid_labels"))
        self.actionInsert_delete_rows_and_columns = QtGui.QAction(MainWindow)
        self.actionInsert_delete_rows_and_columns.setObjectName(_fromUtf8("actionInsert_delete_rows_and_columns"))
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPrint)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuView.addAction(self.actionShow_pattern_grid)
        self.menuView.addAction(self.actionShow_grid_labels)
        self.menuView.addAction(self.actionShow_legend)
        self.menuHelp.addAction(self.actionAbout_sconcho)
        self.menuHelp.addAction(self.actionAbout_Qt4)
        self.menuGrid.addAction(self.actionInsert_delete_rows_and_columns)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuGrid.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionNew)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionExport)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPrint)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "sconcho: create your own pattern charts", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setTitle(QtGui.QApplication.translate("MainWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menuView.setTitle(QtGui.QApplication.translate("MainWindow", "&View", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuGrid.setTitle(QtGui.QApplication.translate("MainWindow", "&Grid", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolDockWidget.setWindowTitle(QtGui.QApplication.translate("MainWindow", "sconcho: available knitting symbols", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_sconcho.setText(QtGui.QApplication.translate("MainWindow", "About sconcho", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_Qt4.setText(QtGui.QApplication.translate("MainWindow", "About Qt4", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate("MainWindow", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setText(QtGui.QApplication.translate("MainWindow", "&New...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "&Open...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_as.setText(QtGui.QApplication.translate("MainWindow", "Save  &as...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExport.setText(QtGui.QApplication.translate("MainWindow", "&Export...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExport.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+E", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPrint.setText(QtGui.QApplication.translate("MainWindow", "&Print...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPrint.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+P", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_pattern_grid.setText(QtGui.QApplication.translate("MainWindow", "show pattern grid", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_legend.setText(QtGui.QApplication.translate("MainWindow", "show legend", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_grid_labels.setText(QtGui.QApplication.translate("MainWindow", "show grid labels", None, QtGui.QApplication.UnicodeUTF8))
        self.actionInsert_delete_rows_and_columns.setText(QtGui.QApplication.translate("MainWindow", "insert/delete rows and columns", None, QtGui.QApplication.UnicodeUTF8))

from patternView import PatternView
import icons_rc
