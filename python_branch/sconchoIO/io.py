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


from PyQt4.QtCore import QFile, QTextStream, QIODevice, QString
from PyQt4.QtGui import QColor
from PyQt4.QtXml import QDomDocument, QDomNode, QDomElement
from gui.patternCanvas import PatternCanvasItem



def save_canvas(canvas, colors, settings, fileName):
    """
    Toplevel writer routine.
    """

    writeFile = QFile(fileName)
    if not writeFile.open(QIODevice.WriteOnly | QIODevice.Truncate):
        return

    writeStream = QTextStream(writeFile)
    writeDoc    = QDomDocument()

    # write all the content
    root = initialize_DOM(writeDoc)
    write_patternGridItems(writeDoc, root, canvas)


    # save it
    writeDoc.save(writeStream, 4)
    writeFile.close()



    
def initialize_DOM(writeDoc):
    """
    Write the header.
    """
    
    xmlNode = writeDoc.createProcessingInstruction("xml",
                                                   "version=\"1.0\" encoding=\"UTF-8\"" )
    writeDoc.insertBefore(xmlNode, writeDoc.firstChild())
    root = writeDoc.createElement("sconcho")
    writeDoc.appendChild(root)

    return root

    


def write_patternGridItems(writeDoc, root, canvas):
    """
    Write all the patternGridItems to the sconcho file.
    """
    
    helper = QString()

    for item in canvas.items():
        if isinstance(item, PatternCanvasItem):
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
            helper.setNum(QColor(item.color).rgb())
            colorTag.appendChild(writeDoc.createTextNode(helper))

            symbol = item.symbol
            catTag = writeDoc.createElement("patternCategory")
            itemTag.appendChild(catTag)
            catTag.appendChild(writeDoc.createTextNode(symbol["category"]))

            nameTag = writeDoc.createElement("patternName")
            itemTag.appendChild(nameTag)
            nameTag.appendChild(writeDoc.createTextNode(symbol["name"]))



            
            

            
                              

            

            
