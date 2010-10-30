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

from PyQt4.QtCore import QString


########################################################################
##
## gui/mainWindow.py messages
##
########################################################################
sconchoDescription = QString(
    "<b>sconcho</b> is a knitting chart "
    "design tool capable of producing print quality charts.<br><br>"
    "Copyright (C) 2009-2010 Markus Dittrich<br><br>"
    "This is a complete rewrite of the original C++/Qt4 version of sconcho "
    "ported to python/PyQt4.<br><br>"
    "Many thanks to Susan Dittrich for continued testing, advice, "
    "support, and generation of the SVG knitting symbols.<br><br>"
    "This program is free software: you can redistribute it and/or "
    "modify it under the terms of the GNU General Public License "
    "as published by the Free Software Foundation, either version 3 "
    "of the License, or (at your option) any later version.<br><br>"
    "This program is distributed in the hope that it will be useful, "
    "but WITHOUT ANY WARRANTY; without even the implied warranty of "
    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
    "GNU General Public License for more details.<br>"
    "You should have received a copy of the GNU General Public "
    "License along with this program. "
    "If not, see <a href=\"http://www.gnu.org/licenses/\">"
    "http://www.gnu.org/licenses</a><br><br>"
    "Please contact the author via <a href=\"mailto:haskelladdict@users.sourceforge.org\">"
    "email</a> for suggestions, comments, or in case of problems")


startNewPatternTitle = QString("sconcho: Start new project")
startNewPatternText  = QString("Starting a new project will erase your current "
                               "one. Would you like to proceed?")

saveSconchoProjectTitle = QString("sconcho: Save project")
openSconchoProjectTitle = QString("sconcho: Open project")
exportPatternTitle      = QString("sconcho: Export pattern")

unknownSpfExtensionTitle = QString("sconcho: Unknown extension")
unknownSpfExtensionText  = QString("Unknown extension for sconcho project file. "
                                   "Please save a sconcho patter file with a "
                                   ".spf extenstion.")

unknownImageFormatTitle = QString("sconcho: Unknown image format")
unknownImageFormatText  = QString("Unknown image format to export to. "
                                  "Please choose one of the supported image "
                                  "formats.")

patternFileExistsTitle = QString("sconcho: Pattern file exists")
patternFileExistsText = ("The pattern file %s already exists.\n"
                        "Do you want to overwrite it?")

########################################################################
##
## sconchoIO/io.py messages
##
########################################################################
domParserErrorTitle = QString("sconcho: DOM parser error")
domParserErrorText  = ("Error parsing\n %s \nat line %d column %d; %s")

patternGridItemParseErrorTitle = QString("sconcho: Failed to parse pattern grid")
patternGridItemParseErrorText  = QString("Failed to read pattern grid from "
                                         "project file. The file may be damaged.")

patternLegendItemParseErrorTitle = QString("sconcho: Failed to parse legend")
patternLegendItemParseErrorText  = QString("Failed to read legend from "
                                           "project file. The file may be damaged.")
