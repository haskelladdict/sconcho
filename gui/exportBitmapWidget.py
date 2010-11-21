# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2010 Markus Dittrich
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License Version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License Version 3 for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
#######################################################################

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import math

from PyQt4.QtCore import (Qt, SIGNAL, QString, QDir, QFileInfo)
from PyQt4.QtGui import (QDialog, QMessageBox, QFileDialog,
                         QImageReader)
from gui.ui_exportBitmapWidget import Ui_ExportBitmapWidget

import util.helpers.messages as msg


##########################################################################
#
# This widget allows users to adjust to control exporting of the
# canvas to a bitmap
#
##########################################################################
class ExportBitmapWidget(QDialog, Ui_ExportBitmapWidget):


    def __init__(self, size, parent = None):
        """
        Initialize the dialog.
        """

        super(ExportBitmapWidget, self).__init__(parent)
        self.setupUi(self)

        self.width = math.floor(size.width())
        self.height = math.floor(size.height())
        self.fileName = None
        self.__aspectRatio = size.width()/size.height()
        
        self.widthSpinner.setValue(self.width)
        self.heightSpinner.setValue(self.height)

        # synchronize spin boxes
        self.connect(self.widthSpinner, SIGNAL("valueChanged(int)"),
                     self.update_height_spinner)

        self.connect(self.heightSpinner, SIGNAL("valueChanged(int)"),
                     self.update_width_spinner)

        self.connect(self.browseButton, SIGNAL("pressed()"),
                     self.open_file_selector)



    def update_height_spinner(self, newWidth):
        """ Update height spinner after width change.

        Update according to the correct aspect ratio.
        """

        if newWidth <= 0:
            self.heightSpinner.setValue(0)

        self.width = newWidth
        self.height = newWidth/self.__aspectRatio

        # need to block signals during updating to avoid
        # infinite loop
        self.heightSpinner.blockSignals(True)
        self.heightSpinner.setValue(self.height)
        self.heightSpinner.blockSignals(False)



    def update_width_spinner(self, newHeight):
        """ Update width spinner after height change.

        Update according to the correct aspect ratio.
        """

        self.width = newHeight * self.__aspectRatio
        self.height = newHeight

        # need to block signals during updating to avoid
        # infinite loop
        self.widthSpinner.blockSignals(True)
        self.widthSpinner.setValue(self.width)
        self.widthSpinner.blockSignals(False)



    def open_file_selector(self):
        """ Open a file selector and ask for the name """

        #formats = ["*.%s" % unicode(format).lower() for \
        #           format in QImageReader.supportedImageFormats()]
        #formatsAsString = " ".join(formats)


        exportFilePath = QFileDialog.getSaveFileName(self,
                                                     msg.exportPatternTitle,
                                                     QDir.homePath(),
                                                     "Image files (*.png *.tif)") 

        if exportFilePath:
            self.fileNameEdit.setText(exportFilePath)



    def accept(self):
        """ Checks that we have a path and reminds the user to
        enter one if not. """

        exportFilePath = self.fileNameEdit.text()

        if not exportFilePath:
            QMessageBox.warning(self, msg.noFilePathTitle,
                                msg.noFilePathText,
                                QMessageBox.Close)
            return


        # check the extension; if none is present add .spf
        extension = QFileInfo(exportFilePath).completeSuffix()
        if extension != "png" and extension != "tif":
            QMessageBox.warning(self, msg.unknownImageFormatTitle,
                                msg.unknownImageFormatText,
                                QMessageBox.Close)
            return


        self.filePath = exportFilePath

        QDialog.accept(self)
