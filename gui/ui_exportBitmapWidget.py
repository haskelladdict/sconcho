# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/exportBitmapWidget.ui'
#
# Created: Sat Nov 20 17:48:11 2010
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportBitmapWidget(object):
    def setupUi(self, ExportBitmapWidget):
        ExportBitmapWidget.setObjectName(_fromUtf8("ExportBitmapWidget"))
        ExportBitmapWidget.resize(365, 225)
        self.verticalLayout_3 = QtGui.QVBoxLayout(ExportBitmapWidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(ExportBitmapWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ExportBitmapWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.widthSpinner = QtGui.QSpinBox(ExportBitmapWidget)
        self.widthSpinner.setMaximum(10000)
        self.widthSpinner.setObjectName(_fromUtf8("widthSpinner"))
        self.gridLayout.addWidget(self.widthSpinner, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ExportBitmapWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.heightSpinner = QtGui.QSpinBox(ExportBitmapWidget)
        self.heightSpinner.setMaximum(10000)
        self.heightSpinner.setObjectName(_fromUtf8("heightSpinner"))
        self.gridLayout.addWidget(self.heightSpinner, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(ExportBitmapWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_5 = QtGui.QLabel(ExportBitmapWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_2.addWidget(self.label_5)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.fileNameEdit = QtGui.QLineEdit(ExportBitmapWidget)
        self.fileNameEdit.setObjectName(_fromUtf8("fileNameEdit"))
        self.horizontalLayout.addWidget(self.fileNameEdit)
        self.browseButton = QtGui.QPushButton(ExportBitmapWidget)
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.horizontalLayout.addWidget(self.browseButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        spacerItem = QtGui.QSpacerItem(20, 6, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ExportBitmapWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(ExportBitmapWidget)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ExportBitmapWidget.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ExportBitmapWidget.reject)
        QtCore.QMetaObject.connectSlotsByName(ExportBitmapWidget)

    def retranslateUi(self, ExportBitmapWidget):
        ExportBitmapWidget.setWindowTitle(QtGui.QApplication.translate("ExportBitmapWidget", "Export as Bitmap", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ExportBitmapWidget", "<b>Image Size</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExportBitmapWidget", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ExportBitmapWidget", "Height", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ExportBitmapWidget", "pixels", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ExportBitmapWidget", "< b>File Name</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.browseButton.setText(QtGui.QApplication.translate("ExportBitmapWidget", "Browse", None, QtGui.QApplication.UnicodeUTF8))

