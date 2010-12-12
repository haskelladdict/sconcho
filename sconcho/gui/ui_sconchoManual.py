# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/sconchoManual.ui'
#
# Created: Sun Dec 12 14:29:30 2010
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SconchoManual(object):
    def setupUi(self, SconchoManual):
        SconchoManual.setObjectName("SconchoManual")
        SconchoManual.resize(554, 545)
        self.verticalLayout = QtGui.QVBoxLayout(SconchoManual)
        self.verticalLayout.setObjectName("verticalLayout")
        self.helpBrowser = QtGui.QTextBrowser(SconchoManual)
        self.helpBrowser.setObjectName("helpBrowser")
        self.verticalLayout.addWidget(self.helpBrowser)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtGui.QPushButton(SconchoManual)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SconchoManual)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), SconchoManual.accept)
        QtCore.QMetaObject.connectSlotsByName(SconchoManual)

    def retranslateUi(self, SconchoManual):
        SconchoManual.setWindowTitle(QtGui.QApplication.translate("SconchoManual", "Sconcho Manual", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("SconchoManual", "Ok", None, QtGui.QApplication.UnicodeUTF8))

