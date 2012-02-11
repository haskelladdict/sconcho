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

import urllib
import re

from PyQt4.QtCore import (qVersion, SIGNAL, QThread)
from PyQt4.QtGui import (QDialog) 

from gui.ui_update_dialog import Ui_UpdateDialog
import util.messages as msg

LATEST_VERSION_FILE = "LATEST_VERSION.txt"
LATEST_VERSION_URL = ("http://sourceforge.net/projects/sconcho/files/" +
                      LATEST_VERSION_FILE + "/download")


##########################################################################
#
# This widget allows users to check for available updates to sconcho
#
##########################################################################
class UpdateDialog(QDialog, Ui_UpdateDialog):


    def __init__(self, version, date, parent = None):
        """ Initialize the dialog. """

        super(UpdateDialog, self).__init__(parent)
        self.setupUi(self)

        self.version = version
        self.date = date

        self.updateTextEdit.setReadOnly(True)

        self.add_current_version()
        self.urlchecker = UrlChecker()

        self.connect(self.urlchecker, SIGNAL("version_info"),
                     self.show_results)
        self.connect(self.closeButton, SIGNAL("pressed()"),
                     self.close)



    def add_current_version(self):
        """ Add a string with the current version to the interface """

        self.updateTextEdit.setText(msg.currentVersionText % self.version)

        

    def show_results(self, status, result):
        """ Show the result based on if there is a new version or 
        not.

        """

        if status:
            newVersion = result.split()[0]
            newDate = result.split()[1]
            # do some basic checks to make sure we actually received
            # a date string
            if not re.match("^(\d+)-(\d+)-(\d+)$", newDate):
                self.updateTextEdit.append(msg.versionFailureText)
            else:
                if self.date < newDate:
                    self.updateTextEdit.append(msg.notUpToDate %
                                               newVersion)
                else:
                    self.updateTextEdit.append(msg.upToDate)
        else:
            self.updateTextEdit.append(msg.versionFailureText)

    



############################################################
# 
# small thread that goes out and tries to retrieve the
# current sconcho version from LATEST_VERSION_URL
#
############################################################
class UrlChecker(QThread):

    def __init__(self, parent=None):
        """ Main initialization routine """

        super(UrlChecker, self).__init__(parent)

        # start the thread right away
        self.start()



    def run(self):
        """ Try to open the URL containing the current sconcho
        version and return it and the status.

        """

        try:
            handle = urllib.urlopen(LATEST_VERSION_URL, timeout=10)
            result = handle.read()

            # make sure we actually retrieved the correct file
            # since sourceforge seems to redirect us if the link
            # is incorrect
            if (handle.geturl().split("/")[-1] != LATEST_VERSION_FILE):
                self.emit(SIGNAL("version_info"), False, "")
            else:
                self.emit(SIGNAL("version_info"), True, result)

        # we catch any exception and simply abort 
        except:
            self.emit(SIGNAL("version_info"), False, "")

        



