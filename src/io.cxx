/***************************************************************
 *
 * (c) 2009 Markus Dittrich 
 *
 * This program is free software; you can redistribute it 
 * and/or modify it under the terms of the GNU General Public 
 * License Version 3 as published by the Free Software Foundation. 
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License Version 3 for more details.
 *
 * You should have received a copy of the GNU General Public 
 * License along with this program; if not, write to the Free 
 * Software Foundation, Inc., 59 Temple Place - Suite 330, 
 * Boston, MA 02111-1307, USA.
 *
 ****************************************************************/

/* Qt include */
#include <QDebug>
#include <QFile>
#include <QMessageBox>
#include <QTextStream>

/* local includes */
#include "config.h"
#include "basicDefs.h"
#include "graphicsScene.h"
#include "patternGridItem.h"
#include "io.h"

QT_BEGIN_NAMESPACE

//----------------------------------------------------------------
// given the name of a knitting pattern, return the path
// it can be found at 
//----------------------------------------------------------------
QString get_pattern_path(const QString& name)
{
  return SVG_ROOT_PATH + "/" + name + ".svg";
}




//---------------------------------------------------------------
//
//
// class CanvasIOWriter
//
//
//---------------------------------------------------------------


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
CanvasIOWriter::CanvasIOWriter(const GraphicsScene* scene,
    const QString& theName)
  :
    ourScene_(scene),
    fileName_(theName)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
  qDebug() << "canvasIOWriter constructed";
}


//-------------------------------------------------------------
// destructor 
//-------------------------------------------------------------
CanvasIOWriter::~CanvasIOWriter()
{
  if (filePtr_ != 0)
  {
    filePtr_->close();
    delete filePtr_;

    writeStream_->flush();
    delete writeStream_;
  }

  qDebug() << "canvasIOWriter destroyed";
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool CanvasIOWriter::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  
  /* open file */
  filePtr_ = new QFile(fileName_);
  if (!filePtr_->open(QFile::WriteOnly | QFile::Truncate))
  {
    delete filePtr_;
    filePtr_ = 0;
    return false;
  }

  writeStream_ = new QTextStream(filePtr_);

  return true;
}


//--------------------------------------------------------------
// save content of canvas; 
// returns true on success or false on failure
//--------------------------------------------------------------
bool CanvasIOWriter::save()
{
  /* add header */
  QDomNode xmlNode = writeDoc_.createProcessingInstruction("xml",
      "version=\"1.0\" encoding=\"UTF-8\"");
  writeDoc_.insertBefore(xmlNode, writeDoc_.firstChild());
  QDomElement root = writeDoc_.createElement("sconcho");
  writeDoc_.appendChild(root);

  /* add actual canvas items */
  bool statusPatternGridItems = save_patternGridItems_(root);

  /* write it to stream */
  writeDoc_.save(*writeStream_, 4);

  return statusPatternGridItems;
}


/**************************************************************
 *
 * PRIVATE FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// save all PatternGridItems to our write stream
//-------------------------------------------------------------
bool CanvasIOWriter::save_patternGridItems_(QDomElement& root)
{
  qDebug() << "save patternGridItems";

  /* retrieve all patternGridItems from canvas */
  QString helper;
  QList<QGraphicsItem*> allItems(ourScene_->items());
  foreach(QGraphicsItem* anItem, allItems)
  {
    PatternGridItem* cell = 
      qgraphicsitem_cast<PatternGridItem*>(anItem);

   if ( cell != 0 )
   {
     QDomElement mainTag = writeDoc_.createElement("canvasItem");
     root.appendChild(mainTag);

     QDomElement itemTag = writeDoc_.createElement("patternGridItem");
     mainTag.appendChild(itemTag);

     /* write column and row info */
     QDomElement colTag = writeDoc_.createElement("colIndex");
     itemTag.appendChild(colTag);
     helper.setNum(cell->col());
     colTag.appendChild(writeDoc_.createTextNode(helper));
     
     QDomElement rowTag = writeDoc_.createElement("rowIndex");
     itemTag.appendChild(rowTag);
     helper.setNum(cell->row());
     rowTag.appendChild(writeDoc_.createTextNode(helper));
    
     /* cell width and height */
     QDomElement widthTag = writeDoc_.createElement("width");
     itemTag.appendChild(widthTag);
     helper.setNum(cell->dim().width());
     widthTag.appendChild(writeDoc_.createTextNode(helper));
     
     QDomElement heightTag = writeDoc_.createElement("height");
     itemTag.appendChild(heightTag);
     helper.setNum(cell->dim().height());
     heightTag.appendChild(writeDoc_.createTextNode(helper));

     /* background color */
     QDomElement colorTag = writeDoc_.createElement("backgroundColor");
     itemTag.appendChild(colorTag);
     helper.setNum(cell->color().rgb());
     colorTag.appendChild(writeDoc_.createTextNode(helper));

     /* knitting symbol name */
     QDomElement svgTag = writeDoc_.createElement("SVGSymbolName");
     itemTag.appendChild(svgTag);
     svgTag.appendChild(
         writeDoc_.createTextNode(cell->knittingSymbolName()));
   }
  }

  return true;
} 



//---------------------------------------------------------------
//
//
// class CanvasIOReader
//
//
//---------------------------------------------------------------


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
CanvasIOReader::CanvasIOReader(GraphicsScene* scene,
    const QString& theName)
  :
    ourScene_(scene),
    fileName_(theName)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
  qDebug() << "canvasIOReader constructed";
}


//-------------------------------------------------------------
// destructor 
//-------------------------------------------------------------
CanvasIOReader::~CanvasIOReader()
{
  if (filePtr_ != 0)
  {
    filePtr_->close();
    delete filePtr_;
  }

  qDebug() << "canvasIOReader destroyed";
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool CanvasIOReader::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* open write stream */
  filePtr_ = new QFile(fileName_);
  if (!filePtr_->open(QFile::ReadOnly))
  {
    delete filePtr_;
    filePtr_ = 0;
    return false;
  }

  return true;
}


//--------------------------------------------------------------
// save content of canvas; 
// returns true on success or false on failure
//--------------------------------------------------------------
bool CanvasIOReader::read()
{
  /* parse file and make sure we can read it */
  QString errStr;
  int errLine;
  int errCol;
  if (!readDoc_.setContent(filePtr_, true, &errStr, &errLine, &errCol))
  {
    QMessageBox::critical(0,"sconcho DOM Parser",
      QString("Error parsing\n%1\nat line %2 column %3; %4")
      .arg(fileName_) .arg(errLine) .arg(errCol) .arg(errStr));

    return false;
  }

  /* make sure we're reading a sconcho file */
  QDomElement root = readDoc_.documentElement();
  if ( root.tagName() != "sconcho" ) return false;

  /** parse all events */
  QDomNode node = root.firstChild();
  while ( !node.isNull() )
  {
    if (node.toElement().tagName() == "canvasItem")
    {
      QDomNode theItem = node.firstChild();
      if (theItem.toElement().tagName() == "patternGridItem")
      {
        parse_patternGridItem_(theItem);
      }
    }

    node = node.nextSibling();
  }

  /* as the canvas to reset itself and recreate the old scene
   * as specified in newPatternGridItems_ */
  if (!newPatternGridItems_.isEmpty())
  {
    ourScene_->reset_canvas(newPatternGridItems_);
  }

  return true;
}



/**************************************************************
 *
 * PRIVATE FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// read a single PatternGridItem from our input stream
//-------------------------------------------------------------
bool CanvasIOReader::parse_patternGridItem_(const QDomNode& itemNode)
{
  qDebug() << "read patternGridItems";

  /* loop over all the properties we expect for the pattern */
  int colIndex = 0;
  int rowIndex = 0;
  int width    = 0;
  int height   = 0;
  uint color   = 0;
  QString name("");

  QDomNode node = itemNode.firstChild();
  while (!node.isNull())
  {

    if (node.toElement().tagName() == "colIndex")
    {
      QDomNode childNode(node.firstChild());
      colIndex = childNode.toText().data().toInt();
    }

    if (node.toElement().tagName() == "rowIndex")
    {
      QDomNode childNode(node.firstChild());
      rowIndex = childNode.toText().data().toInt();
    }

    if (node.toElement().tagName() == "width")
    {
      QDomNode childNode(node.firstChild());
      width = childNode.toText().data().toInt();
    }

    if (node.toElement().tagName() == "height")
    {
      QDomNode childNode(node.firstChild());
      height = childNode.toText().data().toInt();
    }

    if (node.toElement().tagName() == "backgroundColor")
    {
      QDomNode childNode(node.firstChild());
      color = childNode.toText().data().toUInt();
    }

    if (node.toElement().tagName() == "SVGSymbolName")
    {
      QDomNode childNode(node.firstChild());
      name = childNode.toText().data();
    }

    node = node.nextSibling();
  }

  /* store parsed item in list of new patternGridItems */
  PatternGridItemDescriptor currentItem;
  currentItem.location = QPoint(colIndex, rowIndex);
  currentItem.dimension = QSize(width,height);
  currentItem.backgroundColor = QColor(color);
  currentItem.knittingSymbolName = name;
  newPatternGridItems_.push_back(currentItem);

  qDebug() << colIndex << " " << rowIndex << " " << width << " " <<
    height << "  " << color << " " << name;

  return true;
}

QT_END_NAMESPACE
