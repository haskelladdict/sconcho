# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/manageKnittingSymbolDialog.ui'
#
# Created: Tue Dec 14 23:34:23 2010
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
        ManageKnittingSymbolDialog.resize(702, 456)
        self.verticalLayout_3 = QtGui.QVBoxLayout(ManageKnittingSymbolDialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter = QtGui.QSplitter(ManageKnittingSymbolDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_7 = QtGui.QLabel(self.layoutWidget)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_2.addWidget(self.label_7)
        self.availableSymbolsWidget = QtGui.QTreeWidget(self.layoutWidget)
        self.availableSymbolsWidget.setColumnCount(1)
        self.availableSymbolsWidget.setObjectName(_fromUtf8("availableSymbolsWidget"))
        self.verticalLayout_2.addWidget(self.availableSymbolsWidget)
        self.groupBox = QtGui.QGroupBox(self.splitter)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.symbolPreviewFrame = QtGui.QFrame(self.groupBox)
        self.symbolPreviewFrame.setMinimumSize(QtCore.QSize(100, 60))
        self.symbolPreviewFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.symbolPreviewFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.symbolPreviewFrame.setObjectName(_fromUtf8("symbolPreviewFrame"))
        self.horizontalLayout.addWidget(self.symbolPreviewFrame)
        self.symbolPathEdit = QtGui.QLineEdit(self.groupBox)
        self.symbolPathEdit.setReadOnly(True)
        self.symbolPathEdit.setObjectName(_fromUtf8("symbolPathEdit"))
        self.horizontalLayout.addWidget(self.symbolPathEdit)
        self.browseSymbolButton = QtGui.QPushButton(self.groupBox)
        self.browseSymbolButton.setEnabled(False)
        self.browseSymbolButton.setObjectName(_fromUtf8("browseSymbolButton"))
        self.horizontalLayout.addWidget(self.browseSymbolButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(17, 28, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.symbolNameEntry = QtGui.QLineEdit(self.groupBox)
        self.symbolNameEntry.setReadOnly(True)
        self.symbolNameEntry.setObjectName(_fromUtf8("symbolNameEntry"))
        self.gridLayout.addWidget(self.symbolNameEntry, 0, 1, 1, 1)
        self.symbolCategoryLabel = QtGui.QLabel(self.groupBox)
        self.symbolCategoryLabel.setEnabled(False)
        self.symbolCategoryLabel.setObjectName(_fromUtf8("symbolCategoryLabel"))
        self.gridLayout.addWidget(self.symbolCategoryLabel, 1, 0, 1, 1)
        self.symbolCategoryEntry = QtGui.QLineEdit(self.groupBox)
        self.symbolCategoryEntry.setReadOnly(True)
        self.symbolCategoryEntry.setObjectName(_fromUtf8("symbolCategoryEntry"))
        self.gridLayout.addWidget(self.symbolCategoryEntry, 1, 1, 1, 1)
        self.symbolWidthLabel = QtGui.QLabel(self.groupBox)
        self.symbolWidthLabel.setEnabled(False)
        self.symbolWidthLabel.setObjectName(_fromUtf8("symbolWidthLabel"))
        self.gridLayout.addWidget(self.symbolWidthLabel, 2, 0, 1, 1)
        self.symbolWidthSpinner = QtGui.QSpinBox(self.groupBox)
        self.symbolWidthSpinner.setReadOnly(True)
        self.symbolWidthSpinner.setMinimum(1)
        self.symbolWidthSpinner.setObjectName(_fromUtf8("symbolWidthSpinner"))
        self.gridLayout.addWidget(self.symbolWidthSpinner, 2, 1, 1, 1)
        self.symbolDescriptionLabel = QtGui.QLabel(self.groupBox)
        self.symbolDescriptionLabel.setEnabled(False)
        self.symbolDescriptionLabel.setObjectName(_fromUtf8("symbolDescriptionLabel"))
        self.gridLayout.addWidget(self.symbolDescriptionLabel, 3, 0, 1, 1)
        self.symbolDescriptionEntry = QtGui.QTextEdit(self.groupBox)
        self.symbolDescriptionEntry.setReadOnly(True)
        self.symbolDescriptionEntry.setObjectName(_fromUtf8("symbolDescriptionEntry"))
        self.gridLayout.addWidget(self.symbolDescriptionEntry, 3, 1, 1, 1)
        self.symbolNameLabel = QtGui.QLabel(self.groupBox)
        self.symbolNameLabel.setEnabled(False)
        self.symbolNameLabel.setObjectName(_fromUtf8("symbolNameLabel"))
        self.gridLayout.addWidget(self.symbolNameLabel, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.updateSymbolButton = QtGui.QPushButton(self.groupBox)
        self.updateSymbolButton.setEnabled(False)
        self.updateSymbolButton.setObjectName(_fromUtf8("updateSymbolButton"))
        self.horizontalLayout_2.addWidget(self.updateSymbolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_3.addWidget(self.splitter)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.pushButton_3 = QtGui.QPushButton(ManageKnittingSymbolDialog)
        self.pushButton_3.setMinimumSize(QtCore.QSize(150, 0))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.horizontalLayout_4.addWidget(self.pushButton_3)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.retranslateUi(ManageKnittingSymbolDialog)
        QtCore.QObject.connect(self.pushButton_3, QtCore.SIGNAL(_fromUtf8("clicked()")), ManageKnittingSymbolDialog.close)
        QtCore.QMetaObject.connectSlotsByName(ManageKnittingSymbolDialog)

    def retranslateUi(self, ManageKnittingSymbolDialog):
        ManageKnittingSymbolDialog.setWindowTitle(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "sconcho: Manage Custom Knitting Symbols", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Available Symbols</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.availableSymbolsWidget.headerItem().setText(0, QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Category/Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Selected Symbol", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Image</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.browseSymbolButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Description</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolCategoryLabel.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol category", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolWidthLabel.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol width", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolDescriptionLabel.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol description", None, QtGui.QApplication.UnicodeUTF8))
        self.symbolNameLabel.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "symbol name", None, QtGui.QApplication.UnicodeUTF8))
        self.updateSymbolButton.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "Update", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("ManageKnittingSymbolDialog", "close", None, QtGui.QApplication.UnicodeUTF8))

