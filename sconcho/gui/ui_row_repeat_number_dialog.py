# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/row_repeat_number_dialog.ui'
#
# Created: Sat Apr 14 13:58:32 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RowRepeatNumDialog(object):
    def setupUi(self, RowRepeatNumDialog):
        RowRepeatNumDialog.setObjectName(_fromUtf8("RowRepeatNumDialog"))
        RowRepeatNumDialog.resize(254, 117)
        self.verticalLayout = QtGui.QVBoxLayout(RowRepeatNumDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.numRepeatSpinner = QtGui.QSpinBox(RowRepeatNumDialog)
        self.numRepeatSpinner.setMinimum(2)
        self.numRepeatSpinner.setMaximum(1000)
        self.numRepeatSpinner.setObjectName(_fromUtf8("numRepeatSpinner"))
        self.horizontalLayout.addWidget(self.numRepeatSpinner)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(RowRepeatNumDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(RowRepeatNumDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(RowRepeatNumDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RowRepeatNumDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RowRepeatNumDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RowRepeatNumDialog)

    def retranslateUi(self, RowRepeatNumDialog):
        RowRepeatNumDialog.setWindowTitle(QtGui.QApplication.translate("RowRepeatNumDialog", "Row Repeat Selector", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("RowRepeatNumDialog", "select number of \n"
"row repeats", None, QtGui.QApplication.UnicodeUTF8))

