# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/newPatternWidget.ui'
#
# Created: Thu Nov 25 08:23:20 2010
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_NewPatternWidget(object):
    def setupUi(self, NewPatternWidget):
        NewPatternWidget.setObjectName(_fromUtf8("NewPatternWidget"))
        NewPatternWidget.resize(288, 178)
        self.verticalLayout = QtGui.QVBoxLayout(NewPatternWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(NewPatternWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(NewPatternWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.rowSpinner = QtGui.QSpinBox(NewPatternWidget)
        self.rowSpinner.setMaximum(10000)
        self.rowSpinner.setProperty(_fromUtf8("value"), 10)
        self.rowSpinner.setObjectName(_fromUtf8("rowSpinner"))
        self.gridLayout.addWidget(self.rowSpinner, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(NewPatternWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.columnSpinner = QtGui.QSpinBox(NewPatternWidget)
        self.columnSpinner.setMaximum(1000)
        self.columnSpinner.setProperty(_fromUtf8("value"), 10)
        self.columnSpinner.setObjectName(_fromUtf8("columnSpinner"))
        self.gridLayout.addWidget(self.columnSpinner, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(NewPatternWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.label_2.setBuddy(self.rowSpinner)
        self.label_3.setBuddy(self.columnSpinner)

        self.retranslateUi(NewPatternWidget)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewPatternWidget.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewPatternWidget.close)
        QtCore.QMetaObject.connectSlotsByName(NewPatternWidget)

    def retranslateUi(self, NewPatternWidget):
        NewPatternWidget.setWindowTitle(QtGui.QApplication.translate("NewPatternWidget", "sconcho: New Pattern Grid", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("NewPatternWidget", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Pattern Grid Dimensions</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("NewPatternWidget", "number of rows", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("NewPatternWidget", "number of columns", None, QtGui.QApplication.UnicodeUTF8))

