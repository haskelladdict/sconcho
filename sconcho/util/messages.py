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

    
########################################################################
##
## gui/mainWindow.py messages
##
########################################################################
sconchoDescription = (
    "<b>sconcho</b> v. %s"
    "<p>sconcho is a professional tool for designing knitting charts."
    "<p>Copyright &copy; 2009-2012 Markus Dittrich"
    "<p>Special thanks go to Susan Dittrich for continued testing, advice, "
    "support, and generation of the SVG knitting symbols. Many thanks "
    "also to all users who have provided feedback, reported problems "
    "and shared their knitting symbols."
    "<p>Please help make sconcho better by reporting problems or "
    "suggesting enhancements to the author. Thanks!"
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


patternFileExistsTitle = "sconcho: Pattern File Exists"
patternFileExistsText = ("The pattern file %s already exists.\n"
                        "Do you want to overwrite it?")


patternFileDoesNotExistTitle = "sconcho: Pattern File Does Not Exists"
patternFileDoesNotExistText = ("The pattern file %s does not exist.\n")


imageFileExistsTitle = "sconcho: Image File Exists"
imageFileExistsText = ("The image file %s already exists.\n"
                        "Do you want to overwrite it?")


wantToSavePatternTitle = "sconcho: Pattern File Not Saved"
wantToSavePatternText = ("Your pattern has unsaved changes. You can either "
                         "save or ignore these changes or press cancel to "
                         "continue with editing your pattern.")


recoveryFilePresentTitle = "sconcho: Pattern File Recovery"
recoveryFilePresentText = ("A recovery file for pattern <b>{0}</b> has "
                           "been detected.<p>"
                           "This could have been caused by a system crash."
                           "Would you like to recover this file now? " 
                           "Selecting Cancel will deleted the recovery "
                           "file and continue with loading {0}.")


errorSavingProjectTitle = "sconcho: Error Saving Project"


errorOpeningProjectTitle = "sconcho: Error Opening Project"


########################################################################
##
## exportBitmapDialog messages
##
########################################################################
noFilePathTitle = "sconcho: File Name Missing"
noFilePathText = ("No filename was given. Please enter one.")



########################################################################
##
## patternCanvas messages
##
########################################################################
noColInsertLayoutTitle = "sconcho: Cannot Insert Column"
noColInsertLayoutText = ("Sorry, cannot insert requested columns at the "
                         "specified location due to the current layout.")


noColDeleteLayoutTitle = "sconcho: Cannot Delete Columns"
noColDeleteLayoutText = ("Sorry, cannot delete requested columns. To "
                         "delete columns, please select complete columns "
                         "only (i.e. there can be no partially "
                         "selected ones).")


selectCompleteRowsTitle = "sconcho: Cannot Delete Rows"
selectCompleteRowsText = ("Sorry, cannot delete rows. To delete rows, "
                         "please select complete rows only"
                         "(i.e. there can be no partially selected ones).")


selectSingleColumnTitle = "sconcho: Cannot Insert Columns"
selectSingleColumnText = ("Sorry, cannot insert columns. To insert new "
                          "columns, please select a single and complete "
                          "column as pivot first.")


selectSingleRowTitle = "sconcho: Cannot Insert Rows"
selectSingleRowText = ("Sorry, cannot insert rows. To insert new rows, "
                       "please select a single row as pivot first.")


noSelectionTitle = "sconcho: No Cells Selected"
noSelectionText = ("Sorry, nothing to do. Please select some cells first.")


noCopySelectionTitle = "sconcho: Cannot Paste Selection"
noCopySelectionText = ("Sorry, there is no selection to be pasted. " 
                        "Please copy a rectangular selection first, "
                        "then paste.")


noPasteSelectionTitle = "sconcho: Cannot Paste Selection"
noPasteSelectionText = ("Sorry, can not paste. Either select a region "
                        "which fits your copied selection exactly (or a "
                        "multiple of it for rectangular selections) "
                        "or directly right click on the pattern "
                        "grid and then paste.")


noPasteGeometryTitle = "sconcho: Cannot Paste Selection"
noPasteGeometryText = ("Sorry, can not paste. Your region selected for "
                       "pasting into does not fit your copied selection or "
                       "a multiple of it.")


noPasteGeometryTitle1 = "sconcho: Cannot Paste Selection"
noPasteGeometryText1 = ("Sorry, can not paste. Your region selected for "
                       "pasting into does not fit your copied selection.")


badPasteSelectionTitle = "sconcho: Cannot Paste Selection"
badPasteSelectionText = ("Sorry, your copied selection can not be pasted. "
                         "Make sure your copied selection fits into the "
                         "current chart (the cell you clicked on when "
                         "pasting will be the upper left hand corner) and "
                         "does not cover an existing symbol partially (e.g. "
                         "cover half a 2 stitch cable).")


cannotAddRowRepeatTitle = "sconcho: Cannot Add Row Repeat"
cannotAddRowRepeatText = ("Sorry, cannot add row repeat. To insert a "
                          "row repeat please select complete rows which "
                          "form a contiguous block, and do not overlap with "
                          "with already existing row repeats.")


cannotDeleteRowRepeatTitle = "sconcho: Cannot Delete Row Repeat"
cannotDeleteRowRepeatText = ("Sorry, cannot delete row repeat. To delete a "
                          "row repeat please make sure that complete rows "
                          "are selected and are all inside the row repeat "
                          "you would like to delete.")



errorLoadingTextItemsTitle = "sconcho: Error Loading Text Items"
errorLoadingTextItemsText = ("Could not load text item from "
                             "opened project file. This indicates that "
                             "your file may be corrupted."
                             "<p>sconcho encountered the following "
                             "error: KeyError: %s.")



########################################################################
#
# messages for preferencesDialog
#
########################################################################
customSymbolPathDirectoryTitle = ("sconcho: Please Enter Location of Custom "
                                  "Symbol database.")


loggingPathDirectoryTitle = ("sconcho: Please Enter Location of Path for "
                             "storing log files.")



########################################################################
#
# messages for sconcho_gui
#
########################################################################
errorOpeningKnittingSymbols = ("sconcho: Failed to open knitting symbol "
                               "database.\n"
                               "Please check that you have valid symbols "
                               "at\n%s.\nExiting ....")



########################################################################
#
# messages for canvas
#
########################################################################
errorMatchingLegendItemTitle = "sconcho: Error Loading Legend"
errorMatchingLegendItemText = ("A legend item found in the opened project "
                               "does not match any in the pattern.")


errorLoadingGridTitle = "sconcho: Error Loading Pattern Grid"
errorLoadingGridText = ("Could not load pattern grid from "
                        "opened project file. Often this is caused "
                        "by a missing symbol. Maybe you are trying "
                        "to open a project file with a custom symbol "
                        "which is not installed on your computer.\n"
                        "sconcho encountered the following "
                        "error: KeyError: %s.")

errorLoadingLegendTitle = "sconcho: Error Loading Legend"
errorLoadingLegendText = ("Could not load legend from "
                          "opened project file. This indicates that "
                          "your file may be corrupted."
                          "<p>sconcho encountered the following "
                          "error: KeyError: %s.")


errorLoadingRepeatBoxTitle = "sconcho: Error Loading Repeat Box"
errorLoadingRepeatBoxText = ("Could not load repeat box from "
                             "opened project file. This indicates that "
                             "your file may be corrupted."
                             "<p>sconcho encountered the following "
                             "error: KeyError: %s.")


errorLoadingRepeatBoxLegendTitle = "sconcho: Error Loading Repeat Box Legend"
errorLoadingRepeatBoxLegendText = ("Could not load repeat box legend from "
                                   "opened project file. This indicates "
                                   "that your file may be corrupted."
                                   "<p>sconcho encountered the following "
                                   "error: KeyError: %s.")


########################################################################
#
# messages for io
#
########################################################################
symbolAlreadyExistsText = ("Symbol %s already exists. Refused to import "
                           "new symbol.")


failedToImportSymbolError = ("Failed to import custom symbols due to % ")



directoryLayoutIncorrect = ("Directory layout of new symbol %s is incorrect."
                            " Skipping import of symbol.")


failedToUnpackZipFile = ("Failed to unpack zip archive with custom symbols "
                         "due to %s.")
 


########################################################################
#
# messages for symbolParser
#
########################################################################
failedToCopySvgTitle = "sconcho: Add Symbol Error"
failedToCopySvgText  = ("Error: Failed to copy SVG image %s into sconcho "
                        "database." )


failedCreateDescriptionFileTitle = "sconcho: Add Symbol Error"
failedCreateDescriptionFileText  = ("Error: Failed to create the "
        "description file for the symbol %s in category %s.")


failedToCreateDirectoryTitle = "sconcho: Failed to create directory"
failedToCreateDirectoryText = "Error: Failed to create directory %s."



########################################################################
#
# messages for manageKnittingSymbolDialog
#
########################################################################
noSvgFileErrorTitle  = "sconcho: Add Symbol Error"
noSvgFileErrorText   = "Error: Please add an svg image for your symbol."


noCategoryErrorTitle = "sconcho: Add Symbol Error"
noCategoryErrorText  = "Error: Please enter a category for your symbol."


symbolExistsTitle    = "sconcho: Add Symbol Error"
symbolExistsText     = ("Error: The symbol with name %s you "
                        "entered already exists.")

noNameErrorTitle     = "sconcho: Add Symbol Error"
noNameErrorText      = "Error: Please enter a name for your symbol."


deleteSymbolTitle    = "sconcho: Delete Symbol"
deleteSymbolText     = ("Are you sure you would like to delete symbol "
                        "<b>%s</b>?\n"
                        "Warning: This will clear your undo history.")


cannotDeleteSymbolTitle = "sconcho: Can Not Delete Symbol"
cannotDeleteSymbolText = ("You cannot delete symbol <b>%s</b> since your "
                          "char currently contains this symbol.")


updateSymbolTitle    = "sconcho: Update Symbol"
updateSymbolText     = ("Are you sure you would like to update symbol "
                        "<b>%s</b>?\n"
                        "Warning: This will clear your undo history.")


cannotUpdateSymbolTitle = "sconcho: Cannot Update Symbol"
cannotUpdateSymbolText = ("You cannot change the name, width, or svg image "
                          "of symbol <b>%s</b> since your chart currently "
                          "contains this symbol. To change, open a new "
                          "blank sconcho session and then modify.")


cannotExportSymbolsTitle = "sconcho: Cannot Export Custom Symbols"
cannotExportSymbolsText = ("Sorry, I could not export your symbols for "
                           "some reason.")


cannotImportSymbolsTitle = "sconcho: Cannot Import Custom Symbols"
cannotImportSymbolsText = ("Sorry, some or all of the symbols from the "
                           "symbol archive could not be imported (please "
                           "check logs for more detail)")


restartAfterImportTitle = "sconcho: Please restart sconcho"
restartAfterImportText = ("Please restart sconcho to make your newly "
                          "imported symbols available within sconcho.")



########################################################################
#
# messages for patternRepeatRowEditor dialog 
#
########################################################################
badRepeatRowRangeTitle = "sconcho: Range Error"
badRepeatRowRangeText = ("Error: The range of your new pattern row repeat "
                         "overlaps with an already existing one. "
                         "Please change!")



########################################################################
# 
# messages for update checking dialog
#
########################################################################
currentVersionText = ("<b>Installed Version:</b> sconcho-%s"
                      "<p><i>... Checking for updates ...</i></p>")


versionFailureText = ("<font color=\"red\">ERROR: Failed to retrieve "
                      "version information.<\font>")


upToDate = ("<b>Congratulations!</b> You are up to date.")
notUpToDate = ("Your version of sconcho is <b>out of date</b>. "
               "sconcho-%s is available. Please go to the "
               "sconcho download site and update to the most "
               "recent version.")



########################################################################
##
## list of possible main window titles
##
########################################################################
knittingQuotes = ["Oops, I charted ....",
                  "Chart this!",
                  "Happy knitting!",
                  "Purls before swine",
                  "Knit happens",
                  "Knit or die!"]

