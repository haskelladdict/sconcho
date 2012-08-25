# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2009-2012 Markus Dittrich
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

from functools import partial

from PyQt4.QtCore import (QDir,
                          Qt,
                          SIGNAL)

from PyQt4.QtGui import (QColorDialog,
                         QDialog)

from sconcho.gui.ui_pattern_repeat_box_dialog import Ui_PatternRepeatDialog



##########################################################################
#
# This widget allows customization and deletion of pattern repeats on
# the canvas
#
##########################################################################
class PatternRepeatDialog(QDialog, Ui_PatternRepeatDialog):


    def __init__(self, width, color, hasLegend, parent = None):
        """ Initialize the dialog. """

        super(PatternRepeatDialog, self).__init__(parent)
        self.setupUi(self)

        self.lineWidthSpinner.setValue(width)
        self.width = width
        self.showInLegend = hasLegend
        self.legendChecker.setCheckState(hasLegend)
        self.color = color
        self.set_button_color()

        self.connect(self.acceptButton, SIGNAL("pressed()"),
                     partial(self.done, 1))
        self.connect(self.colorButton, SIGNAL("pressed()"),
                     self.change_color)
        self.connect(self.lineWidthSpinner, SIGNAL("valueChanged(int)"),
                     self.change_width)
        self.connect(self.legendChecker, SIGNAL("stateChanged(int)"),
                     self.change_legend_state)



    def set_button_color(self):
        """ Set the color of a button via a stylesheet. """

        styleSheet = "background-color: " + self.color.name() + ";"
        self.colorButton.setStyleSheet(styleSheet)



    def change_color(self):
        """ Fire up a QColorDialog to let the user change the
        color of the lines marking a pattern repeat box.

        """

        color = QColorDialog.getColor(self.color, None,
                                      "Select Line Color")

        self.color = color
        self.set_button_color()



    def change_width(self, newWidth):
        """ Adjust the line width after a user change to the
        width SpinBox.

        """

        self.width = newWidth



    def change_legend_state(self, legendState):
        """ Change the legend state of the repeat box, i.e.
        if a legend entry is shown or not.

        """

        self.showInLegend = legendState
