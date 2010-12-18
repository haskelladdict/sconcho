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

from PyQt4.QtCore import (QDir, QFile, QString, QStringList, QIODevice,
                          QTextStream)
from PyQt4.QtGui import QMessageBox
from PyQt4.QtXml import QDomDocument

import util.messages as msg


# need this for sorting symbol entries
# at the end of the category list
__LARGE_INT__ = 100000



def parse_all_symbols(symbolTopLevelPaths):
    """ 
    This function reads all available knitting symbols and
    returns a dictionary with them all.
    """

    symbolPaths = get_list_of_symbol_paths(symbolTopLevelPaths)

    allSymbolDesc = {}
    for path in symbolPaths:
        symbolDesc = parse_knitting_symbol(path)
        
        # if there was a problem we simply skip
        # with a short warning
        if not symbolDesc:
            print("Warning: Could not read symbol " + path)
            continue

        # try to add symbol to symbol database
        try:
            symbolID = symbolDesc["category"] + "::" + symbolDesc["name"]
            allSymbolDesc[symbolID] = symbolDesc
        except KeyError:
            continue

    return allSymbolDesc



def get_list_of_symbol_paths(symbolTopLevelPaths):
    """
    Given a list of top level paths to directories containting
    sconcho kitting symbols returns a QStringList of all paths to 
    individual sconcho patterns.
    """

    symbolPaths = []
    for path in symbolTopLevelPaths:
        aDir = QDir(path)
        for entry in aDir.entryList(QDir.AllDirs | QDir.NoDotAndDotDot):
            symbolPaths.append(aDir.absolutePath() + "/" + entry)

    return symbolPaths
        


def parse_knitting_symbol(symbolPath):
    """
    Parse the knitting symbol located at path symbolPath.
    """

    descriptionFile = QFile(symbolPath + "/description")
    if (not descriptionFile.exists()) or descriptionFile.error():
        return None

    # parse XML
    dom = QDomDocument()
    (status, msg, line, col) = dom.setContent(descriptionFile)
    if not status:
        print("Warning: in file %s\n%s at line %d column %d" % \
              (descriptionFile.fileName(), msg, line, col))

    # make sure we're reading a sconcho pattern description 
    root = dom.documentElement()
    if root.tagName() != "sconcho":
        return None

    # parse the actual content
    node = root.firstChild()
    if node.toElement().tagName() != "knittingSymbol":
        return None
  
    content = parse_symbol_description(node)

    # add the absolute path
    content["svgPath"] = symbolPath + "/" + content["svgName"] + ".svg"

    return content



def parse_symbol_description(node):
    """
    Parses the main content of a sconcho pattern description
    file. 
    FIXME: This function currently does not much checking 
           and probably should do more.
    """

    content = {}

    item = node.firstChild()
    while not item.isNull():

        entry = item.firstChild().toText().data()

        if item.toElement().tagName() == "svgName":
            content["svgName"] = entry

        # looks like we explicitly have to copy the QStringList
        # elements into a QString otherwise the code seg faults
        if item.toElement().tagName() == "category":
            splitEntry = entry.split(":")
            if len(splitEntry) == 1:
                content["category"] = QString(splitEntry.first())
                content["category_pos"] = QString("%d" % __LARGE_INT__)
            elif len(splitEntry) == 2:
                content["category"] = QString(splitEntry.first())
                content["category_pos"] = QString(splitEntry.last())
            else:
                return None


        if item.toElement().tagName() == "symbolName":
            content["name"] = entry

        if item.toElement().tagName() == "symbolDescription":
            content["description"] = entry

        if item.toElement().tagName() == "symbolWidth":
            content["width"] = entry

        if item.toElement().tagName() == "backgroundColor":
            content["backgroundColor"] = entry

        item = item.nextSibling();

    return content



def create_new_symbol(symbolPath, svgPath, svgName, category, name, 
                      description, width):
    """ This function creates a new knitting symbol as specified by
    the user. 
    """

    # make sure the user's symbol directory exists. If not we
    # create it
    symbolTopDir = QDir(symbolPath)
    if not symbolTopDir.exists():
        if not symbolTopDir.mkdir(symbolPath):
            QMessageBox.critical(None, msg.failedToCreateDirectoryTitle,
                                 msg.failedToCreateDirectoryText % symbolPath,
                                 QMessageBox.Close)
            return False

    # this should never happen since the manageKnittingSymbolDialog is
    # supposed to check. We'll check anyways.
    symbolDirPath = symbolPath + "/" + svgName
    symbolDir = QDir(symbolDirPath)
    if symbolDir.exists():
        QMessageBox.critical(None, msg.symbolExistsTitle,
                             msg.symbolExistsText % (category, name),
                             QMessageBox.Close)
        return False

    symbolDir.mkdir(symbolDirPath)

    # copy the svg file
    symbolTargetFilePath = symbolDirPath + "/" + svgName + ".svg"
    if not QFile(svgPath).copy(symbolTargetFilePath):
        QMessageBox.critical(None, msg.failedToCopySvgTitle,
                             msg.failedToCopySvgText % svgPath,
                             QMessageBox.Close)
        
        # remove symbolDir again, otherwise we have an orphan
        symbolDir.rmdir(symbolDirPath)
        return False

    # write the description file
    descriptionFileHandle = QFile(symbolDirPath + "/" + "description")
    if not descriptionFileHandle.open(QIODevice.WriteOnly):
        QMessageBox.critical(None, msg.failedToCreateDescriptionFIleTitle,
                             msg.failedToCreateDescriptionFileText % (category,
                             name), QMessageBox.Close)

        # remove the copied svg file and directory
        symbolDir.remove(descriptionFileHandle)
        symbolDir.remove(symbolTargetFilePath)
        symbolDir.remove(symbolDirPath)

    # finally write the content of the file
    write_description_content(descriptionFileHandle, svgName, category, 
                              name, description, width)

    return True



def write_description_content(handle, svgName, category, name, description,
                              width):
    """ This function generates the xml content of the description 
    file.
    """
    
    stream = QTextStream(handle)
    stream << ("<?xml version='1.0' encoding='UTF-8'?>\n"
               "<sconcho>\n"
               "  <knittingSymbol>\n"
               "    <svgName>%s</svgName>\n"
               "    <category>%s</category>\n"
               "    <symbolName>%s</symbolName>\n"
               "    <symbolDescription>%s</symbolDescription>\n"
               "    <symbolWidth>%d</symbolWidth>\n"
               "  </knittingSymbol>\n"
               "</sconcho>\n"
               % (svgName, category, name, description, width))


