# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/pattern_repeat_dialog.ui'
#
# Created: Tue Jun  7 22:08:09 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PatternRepeatDialog(object):
    def setupUi(self, PatternRepeatDialog):
        PatternRepeatDialog.setObjectName(_fromUtf8("PatternRepeatDialog"))
        PatternRepeatDialog.resize(419, 204)
        self.verticalLayout_2 = QtGui.QVBoxLayout(PatternRepeatDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(PatternRepeatDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineWidthSpinner = QtGui.QSpinBox(self.groupBox)
        self.lineWidthSpinner.setMinimum(1)
        self.lineWidthSpinner.setObjectName(_fromUtf8("lineWidthSpinner"))
        self.gridLayout.addWidget(self.lineWidthSpinner, 0, 1, 1, 1)
        self.colorButton = QtGui.QPushButton(self.groupBox)
        self.colorButton.setText(_fromUtf8(""))
        self.colorButton.setObjectName(_fromUtf8("colorButton"))
        self.gridLayout.addWidget(self.colorButton, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.groupBox)
        spacerItem = QtGui.QSpacerItem(20, 64, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.deleteButton = QtGui.QPushButton(PatternRepeatDialog)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout_2.addWidget(self.deleteButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.acceptButton = QtGui.QPushButton(PatternRepeatDialog)
        self.acceptButton.setObjectName(_fromUtf8("acceptButton"))
        self.horizontalLayout_2.addWidget(self.acceptButton)
        self.pushButton_3 = QtGui.QPushButton(PatternRepeatDialog)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.label.setBuddy(self.lineWidthSpinner)
        self.label_2.setBuddy(self.colorButton)

        self.retranslateUi(PatternRepeatDialog)
        QtCore.QObject.connect(self.pushButton_3, QtCore.SIGNAL(_fromUtf8("clicked()")), PatternRepeatDialog.close)
        QtCore.QMetaObject.connectSlotsByName(PatternRepeatDialog)

    def retranslateUi(self, PatternRepeatDialog):
        PatternRepeatDialog.setWindowTitle(QtGui.QApplication.translate("PatternRepeatDialog", "sconcho: Pattern Repeat Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("PatternRepeatDialog", "Line Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PatternRepeatDialog", "Line &Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PatternRepeatDialog", "Line &Color", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteButton.setText(QtGui.QApplication.translate("PatternRepeatDialog", "&Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.acceptButton.setText(QtGui.QApplication.translate("PatternRepeatDialog", "&Accept Changes", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("PatternRepeatDialog", "&Close", None, QtGui.QApplication.UnicodeUTF8))

