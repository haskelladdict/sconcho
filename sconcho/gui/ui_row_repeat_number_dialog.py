# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/row_repeat_number_dialog.ui'
#
# Created: Thu May  2 22:42:16 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

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
        RowRepeatNumDialog.setWindowTitle(_translate("RowRepeatNumDialog", "Row Repeat Selector", None))
        self.label.setText(_translate("RowRepeatNumDialog", "select number of \n"
"row repeats", None))

