# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/manageKnittingSymbolDialog.ui'
#
# Created: Sat Dec 18 22:41:39 2010
#      by: PyQt4 UI code generator 4.8.1
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
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_7 = QtGui.QLabel(self.widget)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_3.addWidget(self.label_7)
        self.availableSymbolsWidget = QtGui.QTreeWidget(self.widget)
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
        self.symbolPreviewFrame_U = QtGui.QFrame(self.updateTab)
        self.symbolPreviewFrame_U.setMinimumSize(QtCore.QSize(100, 60))
        self.symbolPreviewFrame_U.setFrameShape(QtGui.QFrame.StyledPanel)
        self.symbolPreviewFrame_U.setFrameShadow(QtGui.QFrame.Raised)
        self.symbolPreviewFrame_U.setObjectName(_fromUtf8("symbolPreviewFrame_U"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.symbolPreviewFrame_U)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.svgWidget_U = QSvgWidget(self.symbolPreviewFrame_U)
        self.svgWidget_U.setObjectName(_fromUtf8("svgWidget_U"))
        self.horizontalLayout_2.addWidget(self.svgWidget_U)
        self.horizontalLayout_8.addWidget(self.symbolPreviewFrame_U)
        self.svgPathEdit_U = QtGui.QLineEdit(self.updateTab)
        self.svgPathEdit_U.setReadOnly(True)
        self.svgPathEdit_U.setObjectName(_fromUtf8("svgPathEdit_U"))
        self.horizontalLayout_8.addWidget(self.svgPathEdit_U)
        self.browseSymbolButton_U = QtGui.QPushButton(self.updateTab)
        self.browseSymbolButton_U.setEnabled(True)
        self.browseSymbolButton_U.setObjectName(_fromUtf8("browseSymbolButton_U"))
        self.horizontalLayout_8.addWidget(self.browseSymbolButton_U)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        spacerItem = QtGui.QSpacerItem(17, 13, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label_12 = QtGui.QLabel(self.updateTab)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.verticalLayout.addWidget(self.label_12)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.symbolNameLabel_U = QtGui.QLabel(self.updateTab)
        self.symbolNameLabel_U.setEnabled(True)
        self.symbolNameLabel_U.setObjectName(_fromUtf8("symbolNameLabel_U"))
        self.gridLayout_3.addWidget(self.symbolNameLabel_U, 0, 0, 1, 1)
        self.symbolNameEntry_U = QtGui.QLineEdit(self.updateTab)
        self.symbolNameEntry_U.setReadOnly(True)
        self.symbolNameEntry_U.setObjectName(_fromUtf8("symbolNameEntry_U"))
        self.gridLayout_3.addWidget(self.symbolNameEntry_U, 0, 1, 1, 1)
        self.symbolCategoryLabel_U = QtGui.QLabel(self.updateTab)
        self.symbolCategoryLabel_U.setEnabled(True)
        self.symbolCategoryLabel_U.setObjectName(_fromUtf8("symbolCategoryLabel_U"))
        self.gridLayout_3.addWidget(self.symbolCategoryLabel_U, 1, 0, 1, 1)
        self.symbolCategoryEntry_U = QtGui.QLineEdit(self.updateTab)
        self.symbolCategoryEntry_U.setReadOnly(True)
        self.symbolCategoryEntry_U.setObjectName(_fromUtf8("symbolCategoryEntry_U"))
        self.gridLayout_3.addWidget(self.symbolCategoryEntry_U, 1, 1, 1, 1)
        self.symbolWidthLabel_U = QtGui.QLabel(self.updateTab)
        self.symbolWidthLabel_U.setEnabled(True)
        self.symbolWidthLabel_U.setObjectName(_fromUtf8("symbolWidthLabel_U"))
        self.gridLayout_3.addWidget(self.symbolWidthLabel_U, 2, 0, 1, 1)
        self.symbolWidthSpinner_U = QtGui.QSpinBox(self.updateTab)
        self.symbolWidthSpinner_U.setEnabled(True)
        self.symbolWidthSpinner_U.setReadOnly(True)
        self.symbolWidthSpinner_U.setMinimum(1)
        self.symbolWidthSpinner_U.setObjectName(_fromUtf8("symbolWidthSpinner_U"))
        self.gridLayout_3.addWidget(self.symbolWidthSpinner_U, 2, 1, 1, 1)
        self.symbolDescriptionLabel_U = QtGui.QLabel(self.updateTab)
        self.symbolDescriptionLabel_U.setEnabled(True)
        self.symbolDescriptionLabel_U.setObjectName(_fromUtf8("symbolDescriptionLabel_U"))
        self.gridLayout_3.addWidget(self.symbolDescriptionLabel_U, 3, 0, 1, 1)
        self.symbolDescriptionEntry_U = QtGui.QTextEdit(self.updateTab)
        self.symbolDescriptionEntry_U.setReadOnly(True)
        self.symbolDescriptionEntry_U.setObjectName(_fromUtf8("symbolDescriptionEntry_U"))
        self.gridLayout_3.addWidget(self.symbolDescriptionEntry_U, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        spacerItem1 = QtGui.QSpacerItem(20, 18, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.updateSymbolButton = QtGui.QPushButton(self.updateTab)
        self.updateSymbolButton.setEnabled(True)
        self.updateSymbolButton.setObjectName(_fromUtf8("updateSymbolButton"))
        self.horizontalLayout_9.addWidget(self.updateSymbolButton)
        self.deleteSymbolButton = QtGui.QPushButton(self.updateTab)
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
        self.symbolPreviewFrame_A = QtGui.QFrame(self.newTab)
        self.symbolPreviewFrame_A.setMinimumSize(QtCore.QSize(100, 60))
        self.symbolPreviewFrame_A.setFrameShape(QtGui.QFrame.StyledPanel)
        self.symbolPreviewFrame_A.setFrameShadow(QtGui.QFrame.Raised)
        self.symbolPreviewFrame_A.setObjectName(_fromUtf8("symbolPreviewFrame_A"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.symbolPreviewFrame_A)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.svgWidget_A = QSvgWidget(self.symbolPreviewFrame_A)
        self.svgWidget_A.setObjectName(_fromUtf8("svgWidget_A"))
        self.horizontalLayout.addWidget(self.svgWidget_A)
        self.horizontalLayout_7.addWidget(self.symbolPreviewFrame_A)
        self.svgPathEdit_A = QtGui.QLineEdit(self.newTab)
        self.svgPathEdit_A.setReadOnly(False)
        self.svgPathEdit_A.setObjectName(_fromUtf8("svgPathEdit_A"))
        self.horizontalLayout_7.addWidget(self.svgPathEdit_A)
        self.browseSymbolButton_A = QtGui.QPushButton(self.newTab)
        self.browseSymbolButton_A.setEnabled(True)
        self.browseSymbolButton_A.setObjectName(_fromUtf8("browseSymbolButton_A"))
        self.horizontalLayout_7.addWidget(self.browseSymbolButton_A)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        spacerItem3 = QtGui.QSpacerItem(17, 28, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.label_11 = QtGui.QLabel(self.newTab)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.verticalLayout_2.addWidget(self.label_11)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.symbolNameLabel_A = QtGui.QLabel(self.newTab)
        self.symbolNameLabel_A.setEnabled(True)
        self.symbolNameLabel_A.setObjectName(_fromUtf8("symbolNameLabel_A"))
        self.gridLayout_2.addWidget(self.symbolNameLabel_A, 0, 0, 1, 1)
        self.symbolNameEntry_A = QtGui.QLineEdit(self.newTab)
        self.symbolNameEntry_A.setReadOnly(False)
        self.symbolNameEntry_A.setObjectName(_fromUtf8("symbolNameEntry_A"))
        self.gridLayout_2.addWidget(self.symbolNameEntry_A, 0, 1, 1, 1)
        self.symbolCategoryLabel_A = QtGui.QLabel(self.newTab)
        self.symbolCategoryLabel_A.setEnabled(True)
        self.symbolCategoryLabel_A.setObjectName(_fromUtf8("symbolCategoryLabel_A"))
        self.gridLayout_2.addWidget(self.symbolCategoryLabel_A, 1, 0, 1, 1)
        self.symbolCategoryEntry_A = QtGui.QLineEdit(self.newTab)
        self.symbolCategoryEntry_A.setReadOnly(False)
        self.symbolCategoryEntry_A.setObjectName(_fromUtf8("symbolCategoryEntry_A"))
        self.gridLayout_2.addWidget(self.symbolCategoryEntry_A, 1, 1, 1, 1)
        self.symbolWidthLabel_A = QtGui.QLabel(self.newTab)
        self.symbolWidthLabel_A.setEnabled(True)
        self.symbolWidthLabel_A.setObjectName(_fromUtf8("symbolWidthLabel_A"))
        self.gridLayout_2.addWidget(self.symbolWidthLabel_A, 2, 0, 1, 1)
        self.symbolWidthSpinner_A = QtGui.QSpinBox(self.newTab)
        self.symbolWidthSpinner_A.setEnabled(True)
        self.symbolWidthSpinner_A.setReadOnly(False)
        self.symbolWidthSpinner_A.setMinimum(1)
        self.symbolWidthSpinner_A.setObjectName(_fromUtf8("symbolWidthSpinner_A"))
        self.gridLayout_2.addWidget(self.symbolWidthSpinner_A, 2, 1, 1, 1)
        self.symbolDescriptionLabel_A = QtGui.QLabel(self.newTab)
        self.symbolDescriptionLabel_A.setEnabled(True)
        self.symbolDescriptionLabel_A.setObjectName(_fromUtf8("symbolDescriptionLabel_A"))
        self.gridLayout_2.addWidget(self.symbolDescriptionLabel_A, 3, 0, 1, 1)
        self.symbolDescriptionEntry_A = QtGui.QTextEdit(self.newTab)
        self.symbolDescriptionEntry_A.setReadOnly(False)
        self.symbolDescriptionEntry_A.setObjectName(_fromUtf8("symbolDescriptionEntry_A"))
        self.gridLayout_2.addWidget(self.symbolDescriptionEntry_A, 3, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        spacerItem4 = QtGui.QSpacerItem(20, 22, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem5)
        self.clearEntriesButton = QtGui.QPushButton(self.newTab)
        self.clearEntriesButton.setObjectName(_fromUtf8("clearEntriesButton"))
        self.horizontalLayout_4.addWidget(self.clearEntriesButton)
        self.addSymbolButton = QtGui.QPushButton(self.newTab)
        self.addSymbolButton.setEnabled(True)
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
        self.browseSymbolButton_U.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Description</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolNameLabel_U.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol name", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolCategoryLabel_U.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol category", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolWidthLabel_U.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol width", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolDescriptionLabel_U.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol description", None, QtGui.QApplication.UnicodeUTF8))
        self.updateSymbolButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Update Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteSymbolButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Delete Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.updateTab), QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Update/Delete Existing Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">SVG Image</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.browseSymbolButton_A.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Description</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolNameLabel_A.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol name", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolCategoryLabel_A.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol category", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolWidthLabel_A.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol width", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolDescriptionLabel_A.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol description", None, QtGui.QApplication.UnicodeUTF8))
        self.clearEntriesButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Clear Entries", None, QtGui.QApplication.UnicodeUTF8))
        self.addSymbolButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Add Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.newTab), QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Add New Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4.QtSvg import QSvgWidget
