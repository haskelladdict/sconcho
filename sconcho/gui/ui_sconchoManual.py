# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/sconchoManual.ui'
#
# Created: Tue Feb  8 21:14:01 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SconchoManual(object):
    def setupUi(self, SconchoManual):
        SconchoManual.setObjectName(_fromUtf8("SconchoManual"))
        SconchoManual.setWindowModality(QtCore.Qt.NonModal)
        SconchoManual.resize(925, 550)
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
        SconchoManual.setWindowTitle(QtGui.QApplication.translate("SconchoManual", "Sconcho Manual", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("SconchoManual", "&Close", None, QtGui.QApplication.UnicodeUTF8))

