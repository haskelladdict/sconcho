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
sconchoDescription = (
    "<b>sconcho</b> v. %s"
    "<p>sconcho is a knitting chart "
    "design tool capable of producing print quality charts."
    "<p>Copyright &copy; 2009-2010 Markus Dittrich"
    "<p>Many thanks to Susan Dittrich for continued testing, advice, "
    "support, and generation of the SVG knitting symbols."
    "<p>This program is free software: you can redistribute it and/or "
    "modify it under the terms of the GNU General Public License "
    "as published by the Free Software Foundation, either version 3 "
    "of the License, or (at your option) any later version."
    "<p>This program is distributed in the hope that it will be useful, "
    "but WITHOUT ANY WARRANTY; without even the implied warranty of "
    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
    "GNU General Public License for more details.<br>"
    "You should have received a copy of the GNU General Public "
    "License along with this program. "
    "If not, see <a href=\"http://www.gnu.org/licenses/\">"
    "http://www.gnu.org/licenses</a>"
    "<p>Please contact the author via "
    "<a href=\"mailto:haskelladdict@users.sourceforge.org\">"
    "email</a> for suggestions, comments, or in case of problems"
    "<p>sconcho uses the following resources:"
    "<p>python %s  -  Qt %s  - PyQt %s on %s")


saveSconchoProjectTitle = "sconcho: Save project"
openSconchoProjectTitle = "sconcho: Open project"
exportPatternTitle      = "sconcho: Export pattern"


unknownImageFormatTitle = "sconcho: Unknown image format"
unknownImageFormatText  = ("Unknown image format for exporting as bitmap. "
                           "Please choose one of the supported image "
                           "formats.")

patternFileExistsTitle = "sconcho: Pattern File Exists"
patternFileExistsText = ("The pattern file %s already exists.\n"
                        "Do you want to overwrite it?")

noFilePathTitle = "sconcho: File Name Missing"
noFilePathText = ("No filename was given. Please enter one.")

wantToSavePatternTitle = "sconcho: Pattern File Not Saved"
wantToSavePatternText = ("Your pattern has unsaved changes. Please save or "
                         "discard these changes or press cancel to continue "
                         "with editing your pattern.")

numRowTooSmallTitle = "sconcho: Row Delete Error"
numRowTooSmallText = ("There has to be at least one row remaining.\n"
                      "Cannot delete the last row.")


numColTooSmallTitle = "sconcho: Column Delete Error"
numColTooSmallText = ("There has to be at least one column remaining.\n"
                      "Cannot delete the last column.")


noColInsertLayoutTitle = "sconcho: Cannot Insert Column"
noColInsertLayoutText = ("Cannot insert requested columns at the specified "
                         "location due to the current layout.")


noColDeleteLayoutTitle = "sconcho: Cannot Delete Column"
noColDeleteLayoutText = ("Cannot delete requested column at the specified "
                         "location due to the current layout.")


errorSavingProjectTitle = "sconcho: Error Saving Project"

errorOpeningProjectTitle = "sconcho: Error Opening Project"


errorMatchingLegendItemTitle = "sconcho: Error Loading Legend"
errorMatchingLegendItemText = ("A legend item found in the opened project "
                               "does not match any in the pattern.")


errorLoadingGridTitle = "sconcho: Error Loading Pattern Grid"
errorLoadingGridText = ("Could not load pattern grid from "
                        "opened project file. This indicates that "
                        "your file may be corrupted."
                        "<p>sconcho encountered the following "
                        "error: KeyError: %s.")

errorLoadingLegendTitle = "sconcho: Error Loading Legend"
errorLoadingLegendText = ("Could not load legend from "
                          "opened project file. This indicates that "
                          "your file may be corrupted."
                          "<p>sconcho encountered the following "
                          "error: KeyError: %s.")



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


patternColorParseErrorTitle = "sconcho: Failed to parse color information"
patternColorParseErrorText  = ("Failed to read project colors from "
                               "project file. The file may be damaged "
                               "and can not be read.")
