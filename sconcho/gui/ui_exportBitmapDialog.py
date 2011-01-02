# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/exportBitmapDialog.ui'
#
# Created: Sun Jan  2 13:01:28 2011
#      by: PyQt4 UI code generator 4.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportBitmapDialog(object):
    def setupUi(self, ExportBitmapDialog):
        ExportBitmapDialog.setObjectName(_fromUtf8("ExportBitmapDialog"))
        ExportBitmapDialog.resize(423, 323)
        self.verticalLayout_4 = QtGui.QVBoxLayout(ExportBitmapDialog)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(ExportBitmapDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ExportBitmapDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.widthSpinner = QtGui.QSpinBox(ExportBitmapDialog)
        self.widthSpinner.setMaximum(10000)
        self.widthSpinner.setObjectName(_fromUtf8("widthSpinner"))
        self.gridLayout.addWidget(self.widthSpinner, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ExportBitmapDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.heightSpinner = QtGui.QSpinBox(ExportBitmapDialog)
        self.heightSpinner.setMaximum(10000)
        self.heightSpinner.setObjectName(_fromUtf8("heightSpinner"))
        self.gridLayout.addWidget(self.heightSpinner, 4, 1, 1, 1)
        self.label_4 = QtGui.QLabel(ExportBitmapDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 2, 1, 1)
        self.label_6 = QtGui.QLabel(ExportBitmapDialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 4, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_7 = QtGui.QLabel(ExportBitmapDialog)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_2.addWidget(self.label_7)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.scalingSpinner = QtGui.QSpinBox(ExportBitmapDialog)
        self.scalingSpinner.setMaximum(10000)
        self.scalingSpinner.setObjectName(_fromUtf8("scalingSpinner"))
        self.horizontalLayout.addWidget(self.scalingSpinner)
        self.label_8 = QtGui.QLabel(ExportBitmapDialog)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout.addWidget(self.label_8)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_5 = QtGui.QLabel(ExportBitmapDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_3.addWidget(self.label_5)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.fileNameEdit = QtGui.QLineEdit(ExportBitmapDialog)
        self.fileNameEdit.setObjectName(_fromUtf8("fileNameEdit"))
        self.horizontalLayout_2.addWidget(self.fileNameEdit)
        self.browseButton = QtGui.QPushButton(ExportBitmapDialog)
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.horizontalLayout_2.addWidget(self.browseButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        spacerItem3 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem3)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.cancelButton = QtGui.QPushButton(ExportBitmapDialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.exportButton = QtGui.QPushButton(ExportBitmapDialog)
        self.exportButton.setObjectName(_fromUtf8("exportButton"))
        self.horizontalLayout_3.addWidget(self.exportButton)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.label.setBuddy(self.widthSpinner)
        self.label_2.setBuddy(self.heightSpinner)
        self.label_8.setBuddy(self.scalingSpinner)

        self.retranslateUi(ExportBitmapDialog)
        QtCore.QMetaObject.connectSlotsByName(ExportBitmapDialog)
        ExportBitmapDialog.setTabOrder(self.widthSpinner, self.heightSpinner)
        ExportBitmapDialog.setTabOrder(self.heightSpinner, self.scalingSpinner)
        ExportBitmapDialog.setTabOrder(self.scalingSpinner, self.fileNameEdit)
        ExportBitmapDialog.setTabOrder(self.fileNameEdit, self.browseButton)

    def retranslateUi(self, ExportBitmapDialog):
        ExportBitmapDialog.setWindowTitle(QtGui.QApplication.translate("ExportBitmapDialog", "sconcho: Export as Bitmap", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ExportBitmapDialog", "<b>Image Size</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExportBitmapDialog", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ExportBitmapDialog", "Height", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ExportBitmapDialog", "pixels", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("ExportBitmapDialog", "pixels", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("ExportBitmapDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Scaling</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("ExportBitmapDialog", "%", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ExportBitmapDialog", "< b>File Name</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.browseButton.setText(QtGui.QApplication.translate("ExportBitmapDialog", "&Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("ExportBitmapDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.exportButton.setText(QtGui.QApplication.translate("ExportBitmapDialog", "&Export", None, QtGui.QApplication.UnicodeUTF8))

