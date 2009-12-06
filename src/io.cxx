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
#include <QDir>
#include <QFile>
#include <QFileDialog>
#include <QFileInfo>
#include <QMessageBox>
#include <QPainter>
#include <QPrinter>
#include <QPrintDialog>
#include <QTextStream>

/* local includes */
#include "config.h"
#include "basicDefs.h"
#include "graphicsScene.h"
#include "legendItem.h"
#include "legendLabel.h"
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
// this functions a file export dialog and returns the selected
// filename or an empty string if nothing was selected
//---------------------------------------------------------------
QString show_file_export_dialog()
{
  QString currentDirectory = QDir::currentPath();
  QString saveFileName = QFileDialog::getSaveFileName(0,
    QObject::tr("Export"), currentDirectory,
    QObject::tr("Image Files (*.png *.tif *.jpg *.gif)"));

  if ( saveFileName.isEmpty() )
  {
    return QString("");
  }

  /* extract file extension and make sure it corresponds to
   * a supported format */
  QFileInfo saveFileInfo(saveFileName);
  QString extension = saveFileInfo.completeSuffix();

  if ( extension != "png" && extension != "tif"
       && extension != "jpg" && extension != "gif" )
  {
    QMessageBox::warning(0, QObject::tr("Warning"),
      QObject::tr("Unknown file format ") + extension,
      QMessageBox::Ok);
    return QString("");
  }

  return saveFileName;
}



//---------------------------------------------------------------
// this functions export the content of a QGraphicsScene to
// a file
//---------------------------------------------------------------
void export_scene(const QString& fileName, GraphicsScene* scene)
{
  /* for now print the image in a fixed resolution 
   * NOTE: We seem to need the 1px buffer region to avoid
   *       the image being cut off */
  QRectF theScene = scene->get_visible_area();
  theScene.adjust(-10,-10,10,10);  // need this to avoid cropping

  QImage finalImage(theScene.width()*3, theScene.height() *3,
      QImage::Format_ARGB32_Premultiplied);
  QPainter painter(&finalImage);
  painter.setRenderHints(QPainter::SmoothPixmapTransform);
  painter.setRenderHints(QPainter::HighQualityAntialiasing);
  painter.setRenderHints(QPainter::TextAntialiasing);

  scene->render(&painter, QRectF(), theScene);
  painter.end();
  finalImage.save(fileName);
}



//---------------------------------------------------------------
// this function prints the content of a QGraphicsScene
//---------------------------------------------------------------
void print_scene(GraphicsScene* scene)
{
  QPrinter aPrinter(QPrinter::HighResolution);
  QPrintDialog printDialog(&aPrinter);
  if ( printDialog.exec() == QDialog::Accepted )
  {
    /* get size to be rendered */
    QRectF theScene = scene->get_visible_area();
    theScene.adjust(-10,-10,10,10);  // need this to avoid cropping  

    /* tell our canvas that we want to print its */
    QPainter painter(&aPrinter);
    painter.setRenderHints(QPainter::SmoothPixmapTransform);
    painter.setRenderHints(QPainter::HighQualityAntialiasing);
    painter.setRenderHints(QPainter::TextAntialiasing);
    scene->render(&painter, QRectF(), theScene);
    painter.end();
  }
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
  bool statusLegendEntryPos = save_legendInfo_(root);

  /* write it to stream */
  writeDoc_.save(*writeStream_, 4);

  return (statusPatternGridItems && statusLegendEntryPos);
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
         writeDoc_.createTextNode(cell->get_knitting_symbol_name()));
   }
  }

  return true;
} 


//-------------------------------------------------------------
// save the positions of all items in the legend
//-------------------------------------------------------------
bool CanvasIOWriter::save_legendInfo_(QDomElement& root)
{
  qDebug() << "save legend items";

  /* retrieve all legend items from canvas */
  QString helper;
  QMap<QString,LegendEntry> allEntries(
    ourScene_->get_legend_entries());

  QMapIterator<QString,LegendEntry> iter(allEntries);
  while (iter.hasNext()) 
  {
    iter.next();

    QString labelID = iter.key();
    LegendItem* item  = iter.value().first;
    LegendLabel* label = iter.value().second;

    QDomElement mainTag = writeDoc_.createElement("canvasItem");
    root.appendChild(mainTag);

    QDomElement itemTag = writeDoc_.createElement("legendEntry");
    mainTag.appendChild(itemTag);

    /* write ID tag */
    QDomElement idTag = writeDoc_.createElement("IDTag");
    itemTag.appendChild(idTag);
    idTag.appendChild(writeDoc_.createTextNode(labelID));
    
    /* write position of legend item */
    QDomElement itemXPosTag = writeDoc_.createElement("itemXPos");
    itemTag.appendChild(itemXPosTag);
    helper.setNum(item->pos().x());
    itemXPosTag.appendChild(writeDoc_.createTextNode(helper));
    
    QDomElement itemYPosTag = writeDoc_.createElement("itemYPos");
    itemTag.appendChild(itemYPosTag);
    helper.setNum(item->pos().y());
    itemYPosTag.appendChild(writeDoc_.createTextNode(helper));
 
    /* write position of legend label */
    QDomElement labelXPosTag = writeDoc_.createElement("labelXPos");
    itemTag.appendChild(labelXPosTag);
    helper.setNum(label->pos().x());
    labelXPosTag.appendChild(writeDoc_.createTextNode(helper));
 
    QDomElement labelYPosTag = writeDoc_.createElement("labelYPos");
    itemTag.appendChild(labelYPosTag);
    helper.setNum(label->pos().y());
    labelYPosTag.appendChild(writeDoc_.createTextNode(helper));
    
    /* write text of label */
    QDomElement labelTextTag = writeDoc_.createElement("labelText");
    itemTag.appendChild(labelTextTag);
    labelTextTag.appendChild(writeDoc_.createTextNode(
          label->toPlainText()));
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
// read content of canvas; 
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
        parse_patternGridItems_(theItem);
      }
      else if (theItem.toElement().tagName() == "legendEntry")
      {
        parse_legendItems_(theItem);
      }
    }

    node = node.nextSibling();
  }

  /* as the canvas to reset itself and recreate the 
   * scene specified in the file just read 
   * (as specified in newPatternGridItems_) */
  if (!newPatternGridItems_.isEmpty())
  {
    ourScene_->load_new_canvas(newPatternGridItems_);
    ourScene_->place_legend_items(newLegendEntryDescriptors_);
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
bool CanvasIOReader::parse_patternGridItems_(const QDomNode& itemNode)
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


//-------------------------------------------------------------
// read a single legend entry from our input stream
//-------------------------------------------------------------
bool CanvasIOReader::parse_legendItems_(const QDomNode& itemNode)
{
  qDebug() << "read legend entries";

  /* loop over all the properties we expect for the pattern */
  QString entryID("");
  int itemXPos = 0;
  int itemYPos = 0;
  int labelXPos = 0;
  int labelYPos = 0;
  QString labelText("");

  QDomNode node = itemNode.firstChild();
  while (!node.isNull())
  {
    if (node.toElement().tagName() == "IDTag")
    {
      QDomNode childNode(node.firstChild());
      entryID = childNode.toText().data();
    }

    if (node.toElement().tagName() == "itemXPos")
    {
      QDomNode childNode(node.firstChild());
      itemXPos = childNode.toText().data().toInt();
    }

    if (node.toElement().tagName() == "itemYPos")
    {
      QDomNode childNode(node.firstChild());
      itemYPos = childNode.toText().data().toInt();
    }

    if (node.toElement().tagName() == "labelXPos")
    {
      QDomNode childNode(node.firstChild());
      labelXPos = childNode.toText().data().toInt();
    }

    if (node.toElement().tagName() == "labelYPos")
    {
      QDomNode childNode(node.firstChild());
      labelYPos = childNode.toText().data().toInt();
    }

    if (node.toElement().tagName() == "labelText")
    {
      QDomNode childNode(node.firstChild());
      labelText = childNode.toText().data();
    }

    node = node.nextSibling();
  }


  /* store parsed item in list of new LegendEntryDescriptors */
  LegendEntryDescriptor currentEntry;
  currentEntry.entryID = entryID;
  currentEntry.itemLocation = QPoint(itemXPos, itemYPos);
  currentEntry.labelLocation = QPoint(labelXPos, labelYPos);
  currentEntry.labelText = labelText;
  newLegendEntryDescriptors_.push_back(currentEntry);

  qDebug() << entryID << " " << itemXPos << " " << itemYPos << " " <<
    labelXPos << "  " << labelYPos << " " << labelText;

  return true;
}



QT_END_NAMESPACE
