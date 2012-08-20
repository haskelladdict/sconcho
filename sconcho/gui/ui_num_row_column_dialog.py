# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/num_row_column_dialog.ui'
#
# Created: Mon Aug 20 14:49:49 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_NumRowColumnDialog(object):
    def setupUi(self, NumRowColumnDialog):
        NumRowColumnDialog.setObjectName(_fromUtf8("NumRowColumnDialog"))
        NumRowColumnDialog.resize(254, 117)
        NumRowColumnDialog.setWindowTitle(_fromUtf8(""))
        self.verticalLayout = QtGui.QVBoxLayout(NumRowColumnDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.numSpinner = QtGui.QSpinBox(NumRowColumnDialog)
        self.numSpinner.setMinimum(1)
        self.numSpinner.setMaximum(1000)
        self.numSpinner.setObjectName(_fromUtf8("numSpinner"))
        self.gridLayout.addWidget(self.numSpinner, 0, 0, 1, 1)
        self.requestLabel = QtGui.QLabel(NumRowColumnDialog)
        self.requestLabel.setObjectName(_fromUtf8("requestLabel"))
        self.gridLayout.addWidget(self.requestLabel, 0, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 2)
        self.postLocationLabel = QtGui.QLabel(NumRowColumnDialog)
        self.postLocationLabel.setObjectName(_fromUtf8("postLocationLabel"))
        self.gridLayout.addWidget(self.postLocationLabel, 2, 3, 1, 1)
        self.locationChooser = QtGui.QComboBox(NumRowColumnDialog)
        self.locationChooser.setObjectName(_fromUtf8("locationChooser"))
        self.gridLayout.addWidget(self.locationChooser, 2, 2, 1, 1)
        self.preLocationLabel = QtGui.QLabel(NumRowColumnDialog)
        self.preLocationLabel.setObjectName(_fromUtf8("preLocationLabel"))
        self.gridLayout.addWidget(self.preLocationLabel, 2, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(NumRowColumnDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(NumRowColumnDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NumRowColumnDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NumRowColumnDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NumRowColumnDialog)

    def retranslateUi(self, NumRowColumnDialog):
        self.requestLabel.setText(QtGui.QApplication.translate("NumRowColumnDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.postLocationLabel.setText(QtGui.QApplication.translate("NumRowColumnDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.preLocationLabel.setText(QtGui.QApplication.translate("NumRowColumnDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

