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


##########################################################################
#
# This widget allows users to adjust to control exporting of the
# canvas to a bitmap
#
##########################################################################
class ExportBitmapDialog(QDialog, Ui_ExportBitmapDialog):


    def __init__(self, size, filePath, hideNoStitch, parent = None):
        """ Initialize the dialog. """

        super(ExportBitmapDialog, self).__init__(parent)
        self.setupUi(self)
        self.determine_image_formats()
        self.add_image_formats_to_gui()
        self.hideNostitchCheckBox.setChecked(hideNoStitch)

        self.hideNostitchSymbols = False
        self.width = math.floor(size.width())
        self.height = math.floor(size.height())
        self._originalWidth = self.width
        self.scaling = 100.0
        if filePath:
            self.fileNameEdit.setText(filePath)
        else:
            self.fileNameEdit.setText(QDir.homePath() + "/")

        self._aspectRatio = size.width()/size.height()
        
        self.widthSpinner.setValue(self.width)
        self.heightSpinner.setValue(self.height)
        self.scalingSpinner.setValue(self.scaling)

        # synchronize spin boxes
        self.connect(self.widthSpinner, SIGNAL("editingFinished()"),
                     self.width_update)

        self.connect(self.heightSpinner, SIGNAL("editingFinished()"),
                     self.height_update)

        self.connect(self.scalingSpinner, SIGNAL("editingFinished()"),
                     self.scaling_update)

        self.connect(self.hideNostitchCheckBox, SIGNAL("stateChanged(int)"),
                     self.hide_nostitch_update)
        
        self.connect(self.browseButton, SIGNAL("pressed()"),
                     self.open_file_selector)

        self.connect(self.cancelButton, SIGNAL("pressed()"),
                     self.close)

        self.connect(self.exportButton, SIGNAL("pressed()"),
                     self.accept)


    
    def determine_image_formats(self):
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



    def add_image_formats_to_gui(self):
        """ This function lists all available formats on the gui """

        self.availableFormatsLabel.setText("available formats: " +
                                           "; ".join(self.formats))



    def width_update(self):
        """ Update height spinner after width change.

        Update according to the correct aspect ratio.
        
        """

        newWidth = self.widthSpinner.value()

        self.width = newWidth
        self.height = self.width/self._aspectRatio
        self.scaling = self.width/self._originalWidth * 100.0

        self.heightSpinner.setValue(self.height)
        self.scalingSpinner.setValue(self.scaling)



    def height_update(self):
        """ Update width spinner after height change.

        Update according to the correct aspect ratio.
        
        """

        newHeight = self.heightSpinner.value()
        
        self.width = newHeight * self._aspectRatio
        self.height = newHeight
        self.scaling = self.width/self._originalWidth * 100.0

        self.widthSpinner.setValue(self.width)
        self.scalingSpinner.setValue(self.scaling)



    def scaling_update(self):
        """ Update scaling spinner after height change.

        Update according to the correct aspect ratio.
        
        """

        newScale = self.scalingSpinner.value()

        self.scaling = newScale
        self.width = self._originalWidth * self.scaling / 100.0
        self.height = self.width/self._aspectRatio

        self.widthSpinner.setValue(self.width)
        self.heightSpinner.setValue(self.height)



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
                                        "Image files (%s)" % formatsString) 

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


        self.filePath = exportFilePath

        QDialog.accept(self)



    def keyPressEvent(self, event):
        """ We catch the return key so we don't open
        up the browse menu.

        """

        if event.key() == Qt.Key_Return:
            return

        QDialog.keyPressEvent(self, event)
