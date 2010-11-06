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


startNewPatternTitle = "sconcho: Start new project"
startNewPatternText  = ("Would you like to save your current project "
                        "before continuing.")

saveSconchoProjectTitle = "sconcho: Save project"
openSconchoProjectTitle = "sconcho: Open project"
exportPatternTitle      = "sconcho: Export pattern"


unknownImageFormatTitle = "sconcho: Unknown image format"
unknownImageFormatText  = ("Unknown image format to export to. "
                           "Please choose one of the supported image "
                           "formats.")

patternFileExistsTitle = "sconcho: Pattern file exists"
patternFileExistsText = ("The pattern file %s already exists.\n"
                        "Do you want to overwrite it?")

wantToSavePatternTitle = "sconcho: Pattern file not saved"
wantToSavePatternText = ("Your pattern has unsaved changes. Please save or "
                         "discard these changes or press cancel to continue "
                         "with editing your pattern.")

numRowTooSmallTitle = "sconcho: Row delete error"
numRowTooSmallText = ("There has to be at least one row remaining.\n"
                      "Cannot delete the last row.")


numColTooSmallTitle = "sconcho: Column delete error"
numColTooSmallText = ("There has to be at least one column remaining.\n"
                      "Cannot delete the last column.")


noColInsertLayoutTitle = "sconcho: Cannot insert column"
noColInsertLayoutText = ("Cannot insert requested columns at the specified "
                         "location due to the current layout.")


noColDeleteLayoutTitle = "sconcho: Cannot delete column"
noColDeleteLayoutText = ("Cannot delete requested column at the specified "
                         "location due to the current layout.")


########################################################################
##
## sconchoIO/io.py messages
##
########################################################################
domParserErrorTitle = "sconcho: DOM parser error"
domParserErrorText  = ("Error parsing\n %s \nat line %d column %d; %s")

patternGridItemParseErrorTitle = "sconcho: Failed to parse pattern grid"
patternGridItemParseErrorText  = ("Failed to read pattern grid from "
                                  "project file. The file may be damaged "
                                  "and can not be read.")

patternLegendItemParseErrorTitle = "sconcho: Failed to parse legend"
patternLegendItemParseErrorText  = ("Failed to read legend from "
                                    "project file. The file may be damaged "
                                    "and can not be read.")
