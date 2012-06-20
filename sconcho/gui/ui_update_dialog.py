# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/update_dialog.ui'
#
# Created: Wed Jun 20 10:10:21 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_UpdateDialog(object):
    def setupUi(self, UpdateDialog):
        UpdateDialog.setObjectName(_fromUtf8("UpdateDialog"))
        UpdateDialog.resize(507, 165)
        UpdateDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(UpdateDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.updateTextEdit = QtGui.QTextEdit(UpdateDialog)
        self.updateTextEdit.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.updateTextEdit.setObjectName(_fromUtf8("updateTextEdit"))
        self.verticalLayout.addWidget(self.updateTextEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.closeButton = QtGui.QPushButton(UpdateDialog)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(UpdateDialog)
        QtCore.QMetaObject.connectSlotsByName(UpdateDialog)

    def retranslateUi(self, UpdateDialog):
        UpdateDialog.setWindowTitle(QtGui.QApplication.translate("UpdateDialog", "Check For Updates", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("UpdateDialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

