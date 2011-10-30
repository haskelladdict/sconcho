# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2009-2011 Markus Dittrich
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

from PyQt4.QtCore import (Qt, SIGNAL, QString, QDir, QFileInfo, QFile)
from PyQt4.QtGui import (QDialog, QMessageBox, QFileDialog,
                         QImageReader, QDialogButtonBox)

from sconcho.gui.ui_export_bitmap_dialog import Ui_ExportBitmapDialog
import sconcho.util.messages as msg


# global conversion
inToCm = 1/0.393700787


##########################################################################
#
# This widget allows users to adjust to control exporting of the
# canvas to a bitmap
#
##########################################################################
class ExportBitmapDialog(QDialog, Ui_ExportBitmapDialog):


    def __init__(self, canvas, parent = None):
        """ Initialize the dialog. """

        super(ExportBitmapDialog, self).__init__(parent)
        self.setupUi(self)

        self.canvas = canvas

        self._determine_image_formats()
        self._add_image_formats_to_gui()
        self._update_dimensions()

        self.hideNostitchSymbols = False

        self.currentUnit = 0
        self.unitSelector.setCurrentIndex(self.currentUnit)
        self.defaultDPI = 90
        self.dpi = self.defaultDPI
        self.dpiSpinner.setValue(self.dpi)

        self.fileNameEdit.setText(QDir.homePath() + "/")

        # synchronize spin boxes
        self.connect(self.imageWidthSpinner, SIGNAL("valueChanged(double)"),
                     self.imageWidth_update)

        self.connect(self.imageHeightSpinner, 
                     SIGNAL("valueChanged(double)"),
                     self.imageHeight_update)

        self.connect(self.widthSpinner, SIGNAL("valueChanged(int)"),
                     self.width_update)

        self.connect(self.heightSpinner, SIGNAL("valueChanged(int)"),
                     self.height_update)

        self.connect(self.dpiSpinner, SIGNAL("valueChanged(int)"),
                     self.dpi_update)

        self.connect(self.hideNostitchCheckBox, SIGNAL("stateChanged(int)"),
                     self.hide_nostitch_update)

        self.connect(self.unitSelector, SIGNAL("currentIndexChanged(int)"),
                     self.unit_update)
        
        self.connect(self.browseButton, SIGNAL("pressed()"),
                     self.open_file_selector)

        self.connect(self.cancelButton, SIGNAL("pressed()"),
                     self.close)

        self.connect(self.exportButton, SIGNAL("pressed()"),
                     self.accept)



    def showEvent(self, event):
        """ We derive showEvent so we can make update
        the current canvas dimensions.

        """

        self._update_dimensions()
        return QDialog.showEvent(self, event)



    def _update_dimensions(self):
        """ Update values with the current canvas dimensions """

        
        size = self.canvas.itemsBoundingRect()

        self.width = math.floor(size.width())
        self.height = math.floor(size.height())
        self.imageWidth = self.width
        self.imageHeight = self.height

        self._aspectRatio = size.width()/size.height()
        self.imageWidthSpinner.setValue(self.imageWidth)
        self.imageHeightSpinner.setValue(self.imageHeight)
        self.widthSpinner.setValue(self.width)
        self.heightSpinner.setValue(self.height)


    
    def _determine_image_formats(self):
        """ Determine and store all image formats we can
        support. 

        NOTE: qt-4.7 seems to offer gif format even if it
        doesn't support it always so we manually punt it.
        
        """

        self.formats = ["*.%s" % unicode(format).lower() for \
                            format in QImageReader.supportedImageFormats()]

        self.formats.remove("*.gif")

        # we support svg format as well
        self.formats.append("*.svg")



    def _add_image_formats_to_gui(self):
        """ This function lists all available formats on the gui """

        self.availableFormatsLabel.setText("available formats: " +
                                           "; ".join(self.formats))



    def imageWidth_update(self, newWidth):
        """ Update after image width change. """

        self.imageWidth = self._convert_length_to_pixels(newWidth)
        self.imageHeight = self.imageWidth/self._aspectRatio
        height = self._convert_pixels_to_length(self.imageHeight)
        
        self._set_blocking_value(self.imageHeightSpinner, height)
        self._set_blocking_value(self.widthSpinner, 
                                 self.imageWidth * self.dpi/self.defaultDPI)
        self._set_blocking_value(self.heightSpinner, 
                                 self.imageHeight * self.dpi/self.defaultDPI)



    def imageHeight_update(self, newHeight):
        """ Update after image width change. """

        self.imageHeight = self._convert_length_to_pixels(newHeight)
        self.imageWidth = self.imageHeight * self._aspectRatio
        width = self._convert_pixels_to_length(self.imageWidth)

        self._set_blocking_value(self.imageWidthSpinner, width)
        self._set_blocking_value(self.widthSpinner, 
                                 self.imageWidth * self.dpi/self.defaultDPI)
        self._set_blocking_value(self.heightSpinner, 
                                 self.imageHeight * self.dpi/self.defaultDPI)



    def _convert_length_to_pixels(self, length):
        """ Converts a length value in currentUnit to pixels """

        # pixels
        if self.currentUnit == 1:
            length *= self.defaultDPI
        elif self.currentUnit == 2:
            length = length/inToCm * self.defaultDPI

        return length



    def _convert_pixels_to_length(self, length):
        """ Converts a pixel value to length in currentUnit """

        # pixels
        if self.currentUnit == 1:
            length /= self.defaultDPI
        elif self.currentUnit == 2:
            length = length/self.defaultDPI * inToCm

        return length



    def width_update(self, newWidth):
        """ Update after width change. """

        self.width = newWidth
        self.height = self.width/self._aspectRatio
        self.dpi = self.width/self.imageWidth * self.defaultDPI
        self._set_blocking_value(self.heightSpinner, self.height)
        self._set_blocking_value(self.dpiSpinner, self.dpi)



    def height_update(self, newHeight):
        """ Update after height change. """

        self.width = newHeight * self._aspectRatio
        self.height = newHeight
        self.dpi = self.width/self.imageWidth * self.defaultDPI
        self._set_blocking_value(self.widthSpinner, self.width)
        self._set_blocking_value(self.dpiSpinner, self.dpi)


    
    def dpi_update(self, newDPI):
        """ Update after dpi change. """

        self.dpi = newDPI
        self.width = self.dpi/self.defaultDPI * self.imageWidth
        self.height = self.width/self._aspectRatio
        self._set_blocking_value(self.heightSpinner, self.height)
        self._set_blocking_value(self.widthSpinner, self.width)


    def unit_update(self, newUnit):
        """ Update after unit change. """

        self.currentUnit = newUnit
        
        # pixels
        if newUnit == 0:    
            self._set_blocking_value(self.imageWidthSpinner, 
                                     self.imageWidth)
            self._set_blocking_value(self.imageHeightSpinner, 
                                     self.imageHeight)
        # inches
        elif newUnit == 1:
            self._set_blocking_value(self.imageWidthSpinner, 
                                     self.imageWidth/self.defaultDPI)
            self._set_blocking_value(self.imageHeightSpinner, 
                                     self.imageHeight/self.defaultDPI)
        # cm
        elif newUnit == 2:
            self._set_blocking_value(self.imageWidthSpinner, 
                                     self.imageWidth/self.defaultDPI*inToCm)
            self._set_blocking_value(self.imageHeightSpinner, 
                                     self.imageHeight/self.defaultDPI*inToCm)



    def _set_blocking_value(self, theObject, value):
        """ Helper function for setting selector values.

        Blocks signals to avoid infinite loop.

        """

        theObject.blockSignals(True)
        theObject.setValue(value)
        theObject.blockSignals(False)



    def hide_nostitch_update(self, state):
        """ Update the current hide nostitch state """

        if state == 0:
            self.hideNostitchSymbols = False
        else:
            self.hideNostitchSymbols = True
            

        
    def open_file_selector(self):
        """ Open a file selector and ask for the name """

        formatsString = " ".join(self.formats)
        exportFilePath = QFileDialog.getSaveFileName(self,
                                        msg.exportPatternTitle,
                                        QDir.homePath(),
                                        "Image files (%s)" % formatsString,
                                        None,
                                        QFileDialog.DontConfirmOverwrite) 

        if exportFilePath:
            self.fileNameEdit.setText(exportFilePath)



    def accept(self):
        """ Checks that we have a path and reminds the user to
        enter one if not.

        """

        exportFilePath = self.fileNameEdit.text()

        if not exportFilePath:
            QMessageBox.warning(self, msg.noFilePathTitle,
                                msg.noFilePathText,
                                QMessageBox.Close)
            return


        # check the extension; if none is present fire up warnint
        extension = "*.%s" % QFileInfo(exportFilePath).completeSuffix()
        if extension not in self.formats:
            QMessageBox.warning(self, msg.unknownImageFormatTitle,
                                msg.unknownImageFormatText,
                                QMessageBox.Close)
            return


        # if file exists issue a warning as well
        if QFile(exportFilePath).exists():
            saveFileName = QFileInfo(exportFilePath).fileName()
            messageBox = QMessageBox.question(self,
                                msg.imageFileExistsTitle, 
                                msg.imageFileExistsText % saveFileName,
                                QMessageBox.Ok | QMessageBox.Cancel)

            if (messageBox == QMessageBox.Cancel):
                return 


        # provide the io subroutines with the relevant info
        self.emit(SIGNAL("export_pattern"), self.width, self.height,
                  self.dpi, self.hideNostitchSymbols, exportFilePath)

        QDialog.accept(self)



    def keyPressEvent(self, event):
        """ We catch the return key so we don't open
        up the browse menu.

        """

        if event.key() == Qt.Key_Return:
            return

        QDialog.keyPressEvent(self, event)
