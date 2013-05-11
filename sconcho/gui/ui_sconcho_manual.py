# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/sconcho_manual.ui'
#
# Created: Thu May  9 22:35:56 2013
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

class Ui_SconchoManual(object):
    def setupUi(self, SconchoManual):
        SconchoManual.setObjectName(_fromUtf8("SconchoManual"))
        SconchoManual.setWindowModality(QtCore.Qt.NonModal)
        SconchoManual.resize(925, 550)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../icons/sconcho_icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SconchoManual.setWindowIcon(icon)
        SconchoManual.setSizeGripEnabled(True)
        SconchoManual.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(SconchoManual)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.helpBrowser = QtGui.QTextBrowser(SconchoManual)
        self.helpBrowser.setObjectName(_fromUtf8("helpBrowser"))
        self.verticalLayout.addWidget(self.helpBrowser)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtGui.QPushButton(SconchoManual)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SconchoManual)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), SconchoManual.accept)
        QtCore.QMetaObject.connectSlotsByName(SconchoManual)

    def retranslateUi(self, SconchoManual):
        SconchoManual.setWindowTitle(_translate("SconchoManual", "Sconcho Manual", None))
        self.pushButton.setText(_translate("SconchoManual", "&Close", None))

