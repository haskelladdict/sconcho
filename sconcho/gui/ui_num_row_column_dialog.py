# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/num_row_column_dialog.ui'
#
# Created: Sat Dec 17 20:56:52 2011
#      by: PyQt4 UI code generator 4.8.6
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
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.numSpinner = QtGui.QSpinBox(NumRowColumnDialog)
        self.numSpinner.setMinimum(1)
        self.numSpinner.setMaximum(1000)
        self.numSpinner.setObjectName(_fromUtf8("numSpinner"))
        self.horizontalLayout.addWidget(self.numSpinner)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.requestLabel = QtGui.QLabel(NumRowColumnDialog)
        self.requestLabel.setText(_fromUtf8(""))
        self.requestLabel.setObjectName(_fromUtf8("requestLabel"))
        self.horizontalLayout.addWidget(self.requestLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
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
        pass

