# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/manageKnittingSymbolDialog.ui'
#
# Created: Sun Jan  2 13:55:46 2011
#      by: PyQt4 UI code generator 4.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ManageKnittingSymbolDialog(object):
    def setupUi(self, ManageKnittingSymbolDialog):
        ManageKnittingSymbolDialog.setObjectName(_fromUtf8("ManageKnittingSymbolDialog"))
        ManageKnittingSymbolDialog.resize(814, 601)
        self.verticalLayout_4 = QtGui.QVBoxLayout(ManageKnittingSymbolDialog)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.splitter = QtGui.QSplitter(ManageKnittingSymbolDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_7 = QtGui.QLabel(self.layoutWidget)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_3.addWidget(self.label_7)
        self.availableSymbolsWidget = QtGui.QTreeWidget(self.layoutWidget)
        self.availableSymbolsWidget.setColumnCount(1)
        self.availableSymbolsWidget.setObjectName(_fromUtf8("availableSymbolsWidget"))
        self.verticalLayout_3.addWidget(self.availableSymbolsWidget)
        self.tabWidget = QtGui.QTabWidget(self.splitter)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.updateTab = QtGui.QWidget()
        self.updateTab.setObjectName(_fromUtf8("updateTab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.updateTab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_4 = QtGui.QLabel(self.updateTab)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.symbolPreviewFrame_update = QtGui.QFrame(self.updateTab)
        self.symbolPreviewFrame_update.setMinimumSize(QtCore.QSize(100, 60))
        self.symbolPreviewFrame_update.setFrameShape(QtGui.QFrame.StyledPanel)
        self.symbolPreviewFrame_update.setFrameShadow(QtGui.QFrame.Raised)
        self.symbolPreviewFrame_update.setObjectName(_fromUtf8("symbolPreviewFrame_update"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.symbolPreviewFrame_update)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.svgWidget_update = QSvgWidget(self.symbolPreviewFrame_update)
        self.svgWidget_update.setObjectName(_fromUtf8("svgWidget_update"))
        self.horizontalLayout_2.addWidget(self.svgWidget_update)
        self.horizontalLayout_8.addWidget(self.symbolPreviewFrame_update)
        self.svgPathEdit_update = QtGui.QLineEdit(self.updateTab)
        self.svgPathEdit_update.setReadOnly(True)
        self.svgPathEdit_update.setObjectName(_fromUtf8("svgPathEdit_update"))
        self.horizontalLayout_8.addWidget(self.svgPathEdit_update)
        self.browseSymbolButton_update = QtGui.QPushButton(self.updateTab)
        self.browseSymbolButton_update.setEnabled(True)
        self.browseSymbolButton_update.setAutoDefault(False)
        self.browseSymbolButton_update.setObjectName(_fromUtf8("browseSymbolButton_update"))
        self.horizontalLayout_8.addWidget(self.browseSymbolButton_update)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        spacerItem = QtGui.QSpacerItem(17, 13, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label_12 = QtGui.QLabel(self.updateTab)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.verticalLayout.addWidget(self.label_12)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.symbolNameLabel_update = QtGui.QLabel(self.updateTab)
        self.symbolNameLabel_update.setEnabled(True)
        self.symbolNameLabel_update.setObjectName(_fromUtf8("symbolNameLabel_update"))
        self.gridLayout_3.addWidget(self.symbolNameLabel_update, 0, 0, 1, 1)
        self.symbolNameEntry_update = QtGui.QLineEdit(self.updateTab)
        self.symbolNameEntry_update.setReadOnly(True)
        self.symbolNameEntry_update.setObjectName(_fromUtf8("symbolNameEntry_update"))
        self.gridLayout_3.addWidget(self.symbolNameEntry_update, 0, 1, 1, 1)
        self.symbolCategoryLabel_update = QtGui.QLabel(self.updateTab)
        self.symbolCategoryLabel_update.setEnabled(True)
        self.symbolCategoryLabel_update.setObjectName(_fromUtf8("symbolCategoryLabel_update"))
        self.gridLayout_3.addWidget(self.symbolCategoryLabel_update, 1, 0, 1, 1)
        self.symbolCategoryEntry_update = QtGui.QLineEdit(self.updateTab)
        self.symbolCategoryEntry_update.setReadOnly(True)
        self.symbolCategoryEntry_update.setObjectName(_fromUtf8("symbolCategoryEntry_update"))
        self.gridLayout_3.addWidget(self.symbolCategoryEntry_update, 1, 1, 1, 1)
        self.symbolWidthLabel_update = QtGui.QLabel(self.updateTab)
        self.symbolWidthLabel_update.setEnabled(True)
        self.symbolWidthLabel_update.setObjectName(_fromUtf8("symbolWidthLabel_update"))
        self.gridLayout_3.addWidget(self.symbolWidthLabel_update, 2, 0, 1, 1)
        self.symbolWidthSpinner_update = QtGui.QSpinBox(self.updateTab)
        self.symbolWidthSpinner_update.setEnabled(True)
        self.symbolWidthSpinner_update.setReadOnly(True)
        self.symbolWidthSpinner_update.setMinimum(1)
        self.symbolWidthSpinner_update.setObjectName(_fromUtf8("symbolWidthSpinner_update"))
        self.gridLayout_3.addWidget(self.symbolWidthSpinner_update, 2, 1, 1, 1)
        self.symbolDescriptionLabel_update = QtGui.QLabel(self.updateTab)
        self.symbolDescriptionLabel_update.setEnabled(True)
        self.symbolDescriptionLabel_update.setObjectName(_fromUtf8("symbolDescriptionLabel_update"))
        self.gridLayout_3.addWidget(self.symbolDescriptionLabel_update, 3, 0, 1, 1)
        self.symbolDescriptionEntry_update = QtGui.QTextEdit(self.updateTab)
        self.symbolDescriptionEntry_update.setReadOnly(True)
        self.symbolDescriptionEntry_update.setObjectName(_fromUtf8("symbolDescriptionEntry_update"))
        self.gridLayout_3.addWidget(self.symbolDescriptionEntry_update, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        spacerItem1 = QtGui.QSpacerItem(20, 18, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.updateSymbolButton = QtGui.QPushButton(self.updateTab)
        self.updateSymbolButton.setEnabled(True)
        self.updateSymbolButton.setAutoDefault(False)
        self.updateSymbolButton.setObjectName(_fromUtf8("updateSymbolButton"))
        self.horizontalLayout_9.addWidget(self.updateSymbolButton)
        self.deleteSymbolButton = QtGui.QPushButton(self.updateTab)
        self.deleteSymbolButton.setAutoDefault(False)
        self.deleteSymbolButton.setObjectName(_fromUtf8("deleteSymbolButton"))
        self.horizontalLayout_9.addWidget(self.deleteSymbolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.tabWidget.addTab(self.updateTab, _fromUtf8(""))
        self.newTab = QtGui.QWidget()
        self.newTab.setObjectName(_fromUtf8("newTab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.newTab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_3 = QtGui.QLabel(self.newTab)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_2.addWidget(self.label_3)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.symbolPreviewFrame_add = QtGui.QFrame(self.newTab)
        self.symbolPreviewFrame_add.setMinimumSize(QtCore.QSize(100, 60))
        self.symbolPreviewFrame_add.setFrameShape(QtGui.QFrame.StyledPanel)
        self.symbolPreviewFrame_add.setFrameShadow(QtGui.QFrame.Raised)
        self.symbolPreviewFrame_add.setObjectName(_fromUtf8("symbolPreviewFrame_add"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.symbolPreviewFrame_add)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.svgWidget_add = QSvgWidget(self.symbolPreviewFrame_add)
        self.svgWidget_add.setObjectName(_fromUtf8("svgWidget_add"))
        self.horizontalLayout.addWidget(self.svgWidget_add)
        self.horizontalLayout_7.addWidget(self.symbolPreviewFrame_add)
        self.svgPathEdit_add = QtGui.QLineEdit(self.newTab)
        self.svgPathEdit_add.setReadOnly(False)
        self.svgPathEdit_add.setObjectName(_fromUtf8("svgPathEdit_add"))
        self.horizontalLayout_7.addWidget(self.svgPathEdit_add)
        self.browseSymbolButton_add = QtGui.QPushButton(self.newTab)
        self.browseSymbolButton_add.setEnabled(True)
        self.browseSymbolButton_add.setAutoDefault(False)
        self.browseSymbolButton_add.setObjectName(_fromUtf8("browseSymbolButton_add"))
        self.horizontalLayout_7.addWidget(self.browseSymbolButton_add)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        spacerItem3 = QtGui.QSpacerItem(17, 28, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.label_11 = QtGui.QLabel(self.newTab)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.verticalLayout_2.addWidget(self.label_11)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.symbolNameLabel_add = QtGui.QLabel(self.newTab)
        self.symbolNameLabel_add.setEnabled(True)
        self.symbolNameLabel_add.setObjectName(_fromUtf8("symbolNameLabel_add"))
        self.gridLayout_2.addWidget(self.symbolNameLabel_add, 0, 0, 1, 1)
        self.symbolNameEntry_add = QtGui.QLineEdit(self.newTab)
        self.symbolNameEntry_add.setReadOnly(False)
        self.symbolNameEntry_add.setObjectName(_fromUtf8("symbolNameEntry_add"))
        self.gridLayout_2.addWidget(self.symbolNameEntry_add, 0, 1, 1, 1)
        self.symbolCategoryLabel_add = QtGui.QLabel(self.newTab)
        self.symbolCategoryLabel_add.setEnabled(True)
        self.symbolCategoryLabel_add.setObjectName(_fromUtf8("symbolCategoryLabel_add"))
        self.gridLayout_2.addWidget(self.symbolCategoryLabel_add, 1, 0, 1, 1)
        self.symbolCategoryEntry_add = QtGui.QLineEdit(self.newTab)
        self.symbolCategoryEntry_add.setReadOnly(False)
        self.symbolCategoryEntry_add.setObjectName(_fromUtf8("symbolCategoryEntry_add"))
        self.gridLayout_2.addWidget(self.symbolCategoryEntry_add, 1, 1, 1, 1)
        self.symbolWidthLabel_add = QtGui.QLabel(self.newTab)
        self.symbolWidthLabel_add.setEnabled(True)
        self.symbolWidthLabel_add.setObjectName(_fromUtf8("symbolWidthLabel_add"))
        self.gridLayout_2.addWidget(self.symbolWidthLabel_add, 2, 0, 1, 1)
        self.symbolWidthSpinner_add = QtGui.QSpinBox(self.newTab)
        self.symbolWidthSpinner_add.setEnabled(True)
        self.symbolWidthSpinner_add.setReadOnly(False)
        self.symbolWidthSpinner_add.setMinimum(1)
        self.symbolWidthSpinner_add.setObjectName(_fromUtf8("symbolWidthSpinner_add"))
        self.gridLayout_2.addWidget(self.symbolWidthSpinner_add, 2, 1, 1, 1)
        self.symbolDescriptionLabel_A = QtGui.QLabel(self.newTab)
        self.symbolDescriptionLabel_A.setEnabled(True)
        self.symbolDescriptionLabel_A.setObjectName(_fromUtf8("symbolDescriptionLabel_A"))
        self.gridLayout_2.addWidget(self.symbolDescriptionLabel_A, 3, 0, 1, 1)
        self.symbolDescriptionEntry_add = QtGui.QTextEdit(self.newTab)
        self.symbolDescriptionEntry_add.setReadOnly(False)
        self.symbolDescriptionEntry_add.setObjectName(_fromUtf8("symbolDescriptionEntry_add"))
        self.gridLayout_2.addWidget(self.symbolDescriptionEntry_add, 3, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        spacerItem4 = QtGui.QSpacerItem(20, 22, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem5)
        self.clearEntriesButton = QtGui.QPushButton(self.newTab)
        self.clearEntriesButton.setAutoDefault(False)
        self.clearEntriesButton.setObjectName(_fromUtf8("clearEntriesButton"))
        self.horizontalLayout_4.addWidget(self.clearEntriesButton)
        self.addSymbolButton = QtGui.QPushButton(self.newTab)
        self.addSymbolButton.setEnabled(True)
        self.addSymbolButton.setAutoDefault(False)
        self.addSymbolButton.setObjectName(_fromUtf8("addSymbolButton"))
        self.horizontalLayout_4.addWidget(self.addSymbolButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.tabWidget.addTab(self.newTab, _fromUtf8(""))
        self.verticalLayout_4.addWidget(self.splitter)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem6)
        self.pushButton_4 = QtGui.QPushButton(ManageKnittingSymbolDialog)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.horizontalLayout_6.addWidget(self.pushButton_4)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem7)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.symbolNameLabel_update.setBuddy(self.symbolNameEntry_update)
        self.symbolCategoryLabel_update.setBuddy(self.symbolCategoryEntry_update)
        self.symbolWidthLabel_update.setBuddy(self.symbolWidthSpinner_update)
        self.symbolDescriptionLabel_update.setBuddy(self.symbolDescriptionEntry_update)
        self.symbolNameLabel_add.setBuddy(self.symbolNameEntry_add)
        self.symbolCategoryLabel_add.setBuddy(self.symbolCategoryEntry_add)
        self.symbolWidthLabel_add.setBuddy(self.symbolWidthSpinner_add)
        self.symbolDescriptionLabel_A.setBuddy(self.symbolDescriptionEntry_add)

        self.retranslateUi(ManageKnittingSymbolDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.pushButton_4, QtCore.SIGNAL(_fromUtf8("clicked()")), ManageKnittingSymbolDialog.close)
        QtCore.QMetaObject.connectSlotsByName(ManageKnittingSymbolDialog)

    def retranslateUi(self, ManageKnittingSymbolDialog):
        ManageKnittingSymbolDialog.setWindowTitle(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "sconcho: Manage Custom Knitting Symbols", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Available Symbols</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.availableSymbolsWidget.headerItem().setText(0, QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Category/Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">SVG Image</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.browseSymbolButton_update.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "&Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Description</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolNameLabel_update.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol &name", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolCategoryLabel_update.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol &category", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolWidthLabel_update.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol &width", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolDescriptionLabel_update.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol &description", None, QtGui.QApplication.UnicodeUTF8))
        self.updateSymbolButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "&Update Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteSymbolButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "&Delete Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.updateTab), QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Update/Delete Existing Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">SVG Image</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.browseSymbolButton_add.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "&Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Description</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolNameLabel_add.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol &name", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolCategoryLabel_add.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol &category", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolWidthLabel_add.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol &width", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolDescriptionLabel_A.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol &description", None, QtGui.QApplication.UnicodeUTF8))
        self.clearEntriesButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "&Clear Entries", None, QtGui.QApplication.UnicodeUTF8))
        self.addSymbolButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "&Add Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.newTab), QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Add New Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4.QtSvg import QSvgWidget
