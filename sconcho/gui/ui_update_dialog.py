# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/update_dialog.ui'
#
# Created: Thu May  2 23:53:44 2013
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
        UpdateDialog.setWindowTitle(_translate("UpdateDialog", "Check For Updates", None))
        self.closeButton.setText(_translate("UpdateDialog", "Close", None))

