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


from PyQt4.QtCore import QFile, QTextStream, QIODevice, QString, \
                         Qt, QRectF
from PyQt4.QtGui import QColor, QMessageBox, QImage, QPainter, \
                        QPrinter, QPrintDialog, QDialog
from PyQt4.QtXml import QDomDocument, QDomNode, QDomElement
from gui.patternCanvas import PatternGridItem, PatternLegendItem, \
                              legendItem_symbol, legendItem_text



def save_project(canvas, colors, settings, saveFileName):
    """
    Toplevel writer routine.
    """

    writeFile = QFile(saveFileName)
    if not writeFile.open(QIODevice.WriteOnly | QIODevice.Truncate):
        return

    writeStream = QTextStream(writeFile)
    writeDoc    = QDomDocument()

    # write all the content
    root = initialize_DOM(writeDoc)
    write_patternGridItems(writeDoc, root, canvas)
    write_patternLegendItems(writeDoc, root, canvas)
    write_colors(writeDoc, root, colors)

    # save it
    writeDoc.save(writeStream, 4)
    writeFile.close()



def initialize_DOM(writeDoc):
    """
    Write the header.
    """
    
    xmlNode = writeDoc.createProcessingInstruction("xml",
                                                   "version=\"1.0\" "
                                                   "encoding=\"UTF-8\"" )
    writeDoc.insertBefore(xmlNode, writeDoc.firstChild())

    apiEntry = writeDoc.createElement("sconchoAPI")
    apiEntry.appendChild(writeDoc.createTextNode("1.0"))

    root = writeDoc.createElement("sconcho")
    writeDoc.appendChild(root)

    # add an api version so we can handle changes in the
    # future
    apiTag = writeDoc.createElement("api")
    root.appendChild(apiTag)
    apiTag.appendChild(writeDoc.createTextNode("1.0"))

    return root

    

def write_patternGridItems(writeDoc, root, canvas):
    """
    Write all the patternGridItems to the sconcho file.
    """
    
    helper = QString()

    for item in canvas.items():
        if isinstance(item, PatternGridItem):
            mainTag = writeDoc.createElement("canvasItem")
            root.appendChild(mainTag)

            itemTag = writeDoc.createElement("patternGridItem")
            mainTag.appendChild(itemTag)
                        
            colTag = writeDoc.createElement("colIndex")
            itemTag.appendChild(colTag)
            helper.setNum(item.column)
            colTag.appendChild(writeDoc.createTextNode(helper))
                                    
            rowTag = writeDoc.createElement("rowIndex")
            itemTag.appendChild(rowTag)
            helper.setNum(item.row)
            rowTag.appendChild(writeDoc.createTextNode(helper))

            widthTag = writeDoc.createElement("width")
            itemTag.appendChild(widthTag)
            helper.setNum(item.width)
            widthTag.appendChild(writeDoc.createTextNode(helper))

            heightTag = writeDoc.createElement("height")
            itemTag.appendChild(heightTag)
            helper.setNum(item.height)
            heightTag.appendChild(writeDoc.createTextNode(helper))

            colorTag = writeDoc.createElement("backgroundColor")
            itemTag.appendChild(colorTag)
            colorString = QColor(item.color).name()
            colorTag.appendChild(writeDoc.createTextNode(colorString))

            symbol = item.symbol
            catTag = writeDoc.createElement("patternCategory")
            itemTag.appendChild(catTag)
            catTag.appendChild(writeDoc.createTextNode(symbol["category"]))

            nameTag = writeDoc.createElement("patternName")
            itemTag.appendChild(nameTag)
            nameTag.appendChild(writeDoc.createTextNode(symbol["name"]))



def write_patternLegendItems(writeDoc, root, canvas):
    """
    Write all the PatternLegendItems to the sconcho file.
    """
    
    helper = QString()

    for item in canvas.legend.values():

        symbolItem = legendItem_symbol(item)
        textItem   = legendItem_text(item)

        mainTag = writeDoc.createElement("canvasItem")
        root.appendChild(mainTag)

        itemTag = writeDoc.createElement("legendEntry")
        mainTag.appendChild(itemTag)

        idTag = writeDoc.createElement("patternName")
        itemTag.appendChild(idTag)
        idTag.appendChild(writeDoc.createTextNode(symbolItem.symbol["name"]))

        idTag = writeDoc.createElement("patternCategory")
        itemTag.appendChild(idTag)
        idTag.appendChild(writeDoc.createTextNode(symbolItem.symbol["category"]))
                        
        colorTag = writeDoc.createElement("backgroundColor")
        itemTag.appendChild(colorTag)
        colorString = QColor(symbolItem.color).name()
        colorTag.appendChild(writeDoc.createTextNode(colorString))

        itemXPosTag = writeDoc.createElement("itemXPos")
        itemTag.appendChild(itemXPosTag)
        helper.setNum(symbolItem.pos().x())
        itemXPosTag.appendChild(writeDoc.createTextNode(helper))
                                    
        itemYPosTag = writeDoc.createElement("itemYPos")
        itemTag.appendChild(itemYPosTag)
        helper.setNum(symbolItem.pos().y())
        itemYPosTag.appendChild(writeDoc.createTextNode(helper))

        labelXPosTag = writeDoc.createElement("labelXPos")
        itemTag.appendChild(labelXPosTag)
        helper.setNum(textItem.pos().x())
        labelXPosTag.appendChild(writeDoc.createTextNode(helper))
                                    
        labelYPosTag = writeDoc.createElement("labelYPos")
        itemTag.appendChild(labelYPosTag)
        helper.setNum(textItem.pos().y())
        labelYPosTag.appendChild(writeDoc.createTextNode(helper))

        labelDescriptionTag = writeDoc.createElement("description")
        itemTag.appendChild(labelDescriptionTag)
        text = textItem.toPlainText()
        labelDescriptionTag.appendChild(writeDoc.createTextNode(text))


            
def write_colors(writeDoc, root, colors):
    """
    Write all colors currently selected in colorSelectorItems
    """
    
    mainTag = writeDoc.createElement("projectColors")
    root.appendChild(mainTag)
    
    for item in colors:
        colorTag = writeDoc.createElement("color")
        mainTag.appendChild(colorTag)
        colorTag.appendChild(writeDoc.createTextNode(item.name()))




def read_project(readFileName):
    """
    Toplevel reader routine.
    """

    readFile = QFile(readFileName)
    if not readFile.open(QIODevice.ReadOnly):
        return


    readDoc = QDomDocument()
    (status, errMsg, errLine, errCol) = readDoc.setContent(readFile, True)
    print(errMsg)
    if not status:
        QMessageBox.critical(None, "sconcho DOM Parser",
                             "Error parsing\n %s \nat line %d column %d; %s"
                             % (str(readFileName), errLine, errCol, str(errMsg)))

    root = readDoc.documentElement()
    if root.tagName() != "sconcho":
        print("Error: This doesn't look like a sconncho file")
        return 


    # list of parsed patternGridItems
    patternGridItems = []
    legendItems      = []
    projectColors    = None
    
    node = root.firstChild()
    while not node.isNull():
        if node.toElement().tagName() == "canvasItem":
            item = node.firstChild()

            if item.toElement().tagName() == "patternGridItem":
                newEntry = parse_patternGridItem(item)
                if newEntry:
                    patternGridItems.append(newEntry)

            if item.toElement().tagName() == "legendEntry":
                newEntry = parse_legendItem(item)
                if newEntry:
                    legendItems.append(newEntry)

        elif node.toElement().tagName() == "projectColors":
            item = node.firstChild()
            projectColors = parse_colors(item)
            print(projectColors)

        node = node.nextSibling()

    return (patternGridItems, legendItems, projectColors)



def parse_patternGridItem(item):
    """
    Parse a patternGridItem.
    """

    node = item.firstChild()
    while not node.isNull():

        if node.toElement().tagName() == "colIndex":
            (colIndex, status) = node.firstChild().toText().data().toInt()

        if node.toElement().tagName() == "rowIndex":
            (rowIndex, status) = node.firstChild().toText().data().toInt()

        if node.toElement().tagName() == "width":
            (width, status) = node.firstChild().toText().data().toInt()

        if node.toElement().tagName() == "height":
            (height, status) = node.firstChild().toText().data().toInt()

        if node.toElement().tagName() == "backgroundColor":
            color = node.firstChild().toText().data()

        if node.toElement().tagName() == "patternCategory":
            category = node.firstChild().toText().data()

        if node.toElement().tagName() == "patternName":
            name = node.firstChild().toText().data()

        node = node.nextSibling()

    try:
        newItem = { "column"   : colIndex,
                    "row"      : rowIndex,
                    "width"    : width,
                    "height"   : height,
                    "color"    : color,
                    "category" : category,
                    "name"     : name }
    except:
        QMessageBox.critical(None, "Error", "Failed to parse pattern. " + \
                            "Please check the file for an incomplete patternEntry.",
                            QMessageBox.Ok)
        return None

    return newItem



def parse_legendItem(item):
    """
    Parse a patternGridItem.
    """

    node = item.firstChild()
    while not node.isNull():

        if node.toElement().tagName() == "patternCategory":
            category = node.firstChild().toText().data()

        if node.toElement().tagName() == "patternName":
            name = node.firstChild().toText().data()
            
        if node.toElement().tagName() == "itemXPos":
            (itemXPos, status) = node.firstChild().toText().data().toInt()

        if node.toElement().tagName() == "itemYPos":
            (itemYPos, status) = node.firstChild().toText().data().toInt()

        if node.toElement().tagName() == "labelXPos":
            (labelXPos, status) = node.firstChild().toText().data().toInt()

        if node.toElement().tagName() == "labelYPos":
            (labelYPos, status) = node.firstChild().toText().data().toInt()

        if node.toElement().tagName() == "backgroundColor":
            color = node.firstChild().toText().data()
            
        if node.toElement().tagName() == "description":
            description = node.firstChild().toText().data()

        node = node.nextSibling()

    try:
        newItem = { "category"  : category,
                    "name"      : name,
                    "itemXPos"  : itemXPos,
                    "itemYPos"  : itemYPos,
                    "labelXPos" : labelXPos,
                    "labelYPos" : labelYPos, 
                    "color"     : color }
    except:
        QMessageBox.critical(None, "Error", "Failed to parse legend. " + \
                            "Please check the file for an incomplete legend entry.",
                            QMessageBox.Ok)
        return None

    return newItem



def parse_colors(node):
    """
    Parse a projectColor entry
    """

    colors = []
    while not node.isNull():
        if node.toElement().tagName() == "color":
            colors.append(QColor(node.firstChild().toText().data()))

        node = node.nextSibling()

    return colors


            
def export_scene(canvas, exportFileName):
    """
    This function exports the scene to a file.
    """

    # NOTE: We seem to need the 1px buffer region to avoid
    # the image being cut off
    theScene = canvas.itemsBoundingRect()
    theScene.adjust(-10, -10, 10, 10)

    finalImage = QImage(theScene.width()*3, theScene.height()*3,
                        QImage.Format_ARGB32_Premultiplied )
    painter = QPainter(finalImage)
    painter.setRenderHints(QPainter.SmoothPixmapTransform )
    painter.setRenderHints(QPainter.HighQualityAntialiasing )
    painter.setRenderHints(QPainter.TextAntialiasing )
    painter.setBackgroundMode(Qt.TransparentMode )

    canvas.render(painter, QRectF(), theScene )
    painter.end()
    finalImage.save(exportFileName)



def print_scene(canvas):
    """
    This function prints the content of the canvas.
    """

    aPrinter = QPrinter(QPrinter.HighResolution)
    printDialog = QPrintDialog(aPrinter)
    
    if printDialog.exec_() == QDialog.Accepted:
        
        theScene = canvas.itemsBoundingRect()
        theScene.adjust(-10, -10, 10, 10)

        painter = QPainter(aPrinter)
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)
        painter.setRenderHints(QPainter.TextAntialiasing)
        canvas.render(painter, QRectF(), theScene)
        painter.end()



