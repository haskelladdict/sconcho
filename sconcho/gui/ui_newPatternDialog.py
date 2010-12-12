# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/newPatternDialog.ui'
#
# Created: Sun Dec 12 18:23:52 2010
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_NewPatternDialog(object):
    def setupUi(self, NewPatternDialog):
        NewPatternDialog.setObjectName("NewPatternDialog")
        NewPatternDialog.resize(288, 178)
        self.verticalLayout = QtGui.QVBoxLayout(NewPatternDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(NewPatternDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(NewPatternDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.rowSpinner = QtGui.QSpinBox(NewPatternDialog)
        self.rowSpinner.setMaximum(10000)
        self.rowSpinner.setProperty("value", 10)
        self.rowSpinner.setObjectName("rowSpinner")
        self.gridLayout.addWidget(self.rowSpinner, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(NewPatternDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.columnSpinner = QtGui.QSpinBox(NewPatternDialog)
        self.columnSpinner.setMaximum(1000)
        self.columnSpinner.setProperty("value", 10)
        self.columnSpinner.setObjectName("columnSpinner")
        self.gridLayout.addWidget(self.columnSpinner, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(NewPatternDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.label_2.setBuddy(self.rowSpinner)
        self.label_3.setBuddy(self.columnSpinner)

        self.retranslateUi(NewPatternDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), NewPatternDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), NewPatternDialog.close)
        QtCore.QMetaObject.connectSlotsByName(NewPatternDialog)

    def retranslateUi(self, NewPatternDialog):
        NewPatternDialog.setWindowTitle(QtGui.QApplication.translate("NewPatternDialog", "sconcho: New Pattern Grid", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("NewPatternDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Pattern Grid Dimensions</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("NewPatternDialog", "number of rows", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("NewPatternDialog", "number of columns", None, QtGui.QApplication.UnicodeUTF8))

