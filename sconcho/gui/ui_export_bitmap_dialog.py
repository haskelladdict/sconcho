# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/export_bitmap_dialog.ui'
#
# Created: Sat Nov  5 12:39:17 2011
#      by: PyQt4 UI code generator 4.8.6
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
        ExportBitmapDialog.resize(414, 497)
        ExportBitmapDialog.setWindowTitle(QtGui.QApplication.translate("ExportBitmapDialog", "sconcho: Export as Bitmap or Svg", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(ExportBitmapDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_10 = QtGui.QLabel(ExportBitmapDialog)
        self.label_10.setText(QtGui.QApplication.translate("ExportBitmapDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:600;\">Image Size</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.verticalLayout.addWidget(self.label_10)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_11 = QtGui.QLabel(ExportBitmapDialog)
        self.label_11.setText(QtGui.QApplication.translate("ExportBitmapDialog", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 2, 1, 1)
        self.label_14 = QtGui.QLabel(ExportBitmapDialog)
        self.label_14.setText(QtGui.QApplication.translate("ExportBitmapDialog", "Height", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_2.addWidget(self.label_14, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 2, 1, 1, 1)
        self.label_15 = QtGui.QLabel(ExportBitmapDialog)
        self.label_15.setText(QtGui.QApplication.translate("ExportBitmapDialog", "Units", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_2.addWidget(self.label_15, 2, 2, 1, 1)
        self.unitSelector = QtGui.QComboBox(ExportBitmapDialog)
        self.unitSelector.setObjectName(_fromUtf8("unitSelector"))
        self.unitSelector.addItem(_fromUtf8(""))
        self.unitSelector.setItemText(0, QtGui.QApplication.translate("ExportBitmapDialog", "px", None, QtGui.QApplication.UnicodeUTF8))
        self.unitSelector.addItem(_fromUtf8(""))
        self.unitSelector.setItemText(1, QtGui.QApplication.translate("ExportBitmapDialog", "in", None, QtGui.QApplication.UnicodeUTF8))
        self.unitSelector.addItem(_fromUtf8(""))
        self.unitSelector.setItemText(2, QtGui.QApplication.translate("ExportBitmapDialog", "cm", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout_2.addWidget(self.unitSelector, 2, 3, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 2, 4, 1, 1)
        self.imageWidthSpinner = QtGui.QDoubleSpinBox(ExportBitmapDialog)
        self.imageWidthSpinner.setMaximum(10000.0)
        self.imageWidthSpinner.setObjectName(_fromUtf8("imageWidthSpinner"))
        self.gridLayout_2.addWidget(self.imageWidthSpinner, 0, 1, 1, 1)
        self.imageHeightSpinner = QtGui.QDoubleSpinBox(ExportBitmapDialog)
        self.imageHeightSpinner.setMaximum(10000.0)
        self.imageHeightSpinner.setObjectName(_fromUtf8("imageHeightSpinner"))
        self.gridLayout_2.addWidget(self.imageHeightSpinner, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        spacerItem4 = QtGui.QSpacerItem(20, 37, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem4)
        self.label_3 = QtGui.QLabel(ExportBitmapDialog)
        self.label_3.setText(QtGui.QApplication.translate("ExportBitmapDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:600;\">Bitmap Size</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ExportBitmapDialog)
        self.label.setText(QtGui.QApplication.translate("ExportBitmapDialog", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.widthSpinner = QtGui.QSpinBox(ExportBitmapDialog)
        self.widthSpinner.setMaximum(50000)
        self.widthSpinner.setObjectName(_fromUtf8("widthSpinner"))
        self.gridLayout.addWidget(self.widthSpinner, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(ExportBitmapDialog)
        self.label_6.setText(QtGui.QApplication.translate("ExportBitmapDialog", "pixels at", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 0, 2, 1, 1)
        self.dpiSpinner = QtGui.QSpinBox(ExportBitmapDialog)
        self.dpiSpinner.setMaximum(1200)
        self.dpiSpinner.setObjectName(_fromUtf8("dpiSpinner"))
        self.gridLayout.addWidget(self.dpiSpinner, 0, 3, 1, 1)
        self.label_9 = QtGui.QLabel(ExportBitmapDialog)
        self.label_9.setText(QtGui.QApplication.translate("ExportBitmapDialog", "dpi", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 0, 4, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 0, 5, 1, 1)
        self.label_2 = QtGui.QLabel(ExportBitmapDialog)
        self.label_2.setText(QtGui.QApplication.translate("ExportBitmapDialog", "Height", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.heightSpinner = QtGui.QSpinBox(ExportBitmapDialog)
        self.heightSpinner.setMaximum(50000)
        self.heightSpinner.setObjectName(_fromUtf8("heightSpinner"))
        self.gridLayout.addWidget(self.heightSpinner, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(ExportBitmapDialog)
        self.label_4.setText(QtGui.QApplication.translate("ExportBitmapDialog", "pixels at", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem6, 1, 3, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem7 = QtGui.QSpacerItem(20, 27, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem7)
        self.label_7 = QtGui.QLabel(ExportBitmapDialog)
        self.label_7.setText(QtGui.QApplication.translate("ExportBitmapDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:600;\">Nostich Symbols</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout.addWidget(self.label_7)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.hideNostitchCheckBox = QtGui.QCheckBox(ExportBitmapDialog)
        self.hideNostitchCheckBox.setToolTip(QtGui.QApplication.translate("ExportBitmapDialog", "Checking this option will hide all <i>nostitch</i> symbols in the exported image of your pattern. This can be used to generate non-rectangular patterns.", None, QtGui.QApplication.UnicodeUTF8))
        self.hideNostitchCheckBox.setText(QtGui.QApplication.translate("ExportBitmapDialog", "Hide nostitch symbols", None, QtGui.QApplication.UnicodeUTF8))
        self.hideNostitchCheckBox.setObjectName(_fromUtf8("hideNostitchCheckBox"))
        self.horizontalLayout.addWidget(self.hideNostitchCheckBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem8 = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem8)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_5 = QtGui.QLabel(ExportBitmapDialog)
        self.label_5.setText(QtGui.QApplication.translate("ExportBitmapDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:600;\">File Name </span>(by extension)</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_3.addWidget(self.label_5)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.fileNameEdit = QtGui.QLineEdit(ExportBitmapDialog)
        self.fileNameEdit.setObjectName(_fromUtf8("fileNameEdit"))
        self.horizontalLayout_2.addWidget(self.fileNameEdit)
        self.browseButton = QtGui.QPushButton(ExportBitmapDialog)
        self.browseButton.setText(QtGui.QApplication.translate("ExportBitmapDialog", "&Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.horizontalLayout_2.addWidget(self.browseButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.availableFormatsLabel = QtGui.QLabel(ExportBitmapDialog)
        self.availableFormatsLabel.setText(QtGui.QApplication.translate("ExportBitmapDialog", "available formats", None, QtGui.QApplication.UnicodeUTF8))
        self.availableFormatsLabel.setWordWrap(True)
        self.availableFormatsLabel.setObjectName(_fromUtf8("availableFormatsLabel"))
        self.verticalLayout_3.addWidget(self.availableFormatsLabel)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        spacerItem9 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem9)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem10 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem10)
        self.cancelButton = QtGui.QPushButton(ExportBitmapDialog)
        self.cancelButton.setText(QtGui.QApplication.translate("ExportBitmapDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.exportButton = QtGui.QPushButton(ExportBitmapDialog)
        self.exportButton.setText(QtGui.QApplication.translate("ExportBitmapDialog", "&Export", None, QtGui.QApplication.UnicodeUTF8))
        self.exportButton.setObjectName(_fromUtf8("exportButton"))
        self.horizontalLayout_3.addWidget(self.exportButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label_11.setBuddy(self.widthSpinner)
        self.label_14.setBuddy(self.heightSpinner)
        self.label.setBuddy(self.widthSpinner)
        self.label_2.setBuddy(self.heightSpinner)

        self.retranslateUi(ExportBitmapDialog)
        QtCore.QMetaObject.connectSlotsByName(ExportBitmapDialog)
        ExportBitmapDialog.setTabOrder(self.widthSpinner, self.heightSpinner)
        ExportBitmapDialog.setTabOrder(self.heightSpinner, self.fileNameEdit)
        ExportBitmapDialog.setTabOrder(self.fileNameEdit, self.browseButton)

    def retranslateUi(self, ExportBitmapDialog):
        pass

