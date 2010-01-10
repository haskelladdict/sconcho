/***************************************************************
 *
 * (c) 2009-2010 Markus Dittrich 
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

/* C++ includes */
#include <cmath>

/* Qt include */
#include <QDebug>
#include <QColor>
#include <QDir>
#include <QFile>
#include <QFileDialog>
#include <QFileInfo>
#include <QMessageBox>
#include <QPainter>
#include <QPrinter>
#include <QProcess>
#include <QPrintDialog>
#include <QRegExp>
#include <QString>
#include <QStringList>
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


namespace
{
  /* name of environmental variable that points to
   *  * sconcho knitting symbols */
  const QString SCONCHO_ENV("SCONCHO_SYMBOL_PATH");

  /* name of file that holds the description of knitting
   *  * symbols */
  const QString KNITTING_SYMBOL_DESC("description");
};
  

//--------------------------------------------------------------
// this function attempts to load all knitting symbols it can
// find (at the default and user defined paths), creates
// the corresponding KnittingSymbolPtrs and returns them
// all in a QList
//--------------------------------------------------------------
QList<KnittingSymbolPtr> load_all_symbols()
{
  QList<KnittingSymbolPtr> allSymbols;
  QStringList symbolPaths(get_all_symbol_paths());
  foreach(QString path, symbolPaths)
  {
    allSymbols.append(load_symbols_from_path(path));
  }

  return allSymbols;
}



//--------------------------------------------------------------
// this function takes a path and looks for directories
// containing instructions for knitting symbols
// NOTE: We have to expect that some of the directories
// the we examine won't contain actual symbol information
//--------------------------------------------------------------
QList<KnittingSymbolPtr> load_symbols_from_path(const QString& path)
{
  QList<KnittingSymbolPtr> allSymbols;
  
  QDir symbolDir(path);
  QStringList allFiles(
    symbolDir.entryList(QDir::AllDirs | QDir::NoDotAndDotDot));
  foreach(QString directory, allFiles)
  {
    KnittingSymbolReader symbolReader(path + "/" + directory);
    if (symbolReader.Init())
    {
      if (symbolReader.read())
      {
        allSymbols.push_back(symbolReader.get_symbol());
      }
    }
  }
  
  return allSymbols;
}



//---------------------------------------------------------------
// given the list of all available knitting symbols and the
// category+name of a symbol retrieve the proper
// KnittingSymbolPtr. Returns true on success and false otherwise
//---------------------------------------------------------------
bool retrieve_knitting_symbol(
  const QList<KnittingSymbolPtr>& allSymbols,
  const QString& cat,
  const QString& name,
  KnittingSymbolPtr& symbolPtr)
{
  foreach(KnittingSymbolPtr aSym, allSymbols)
  {
    if ((aSym->category() == cat) && (aSym->patternName() == name))
    {
      symbolPtr = aSym;
      return true;
    }
  }

  return false;
}
    



//--------------------------------------------------------------
// this function collects all paths where knitting pattern
// symbols might be located
//--------------------------------------------------------------
QStringList get_all_symbol_paths()
{
  QStringList symbolPaths;
  symbolPaths << SVG_ROOT_PATH;

  // check if the environmental variable SCONCHO_SYMBOL_PATH
  // is defined
  QString sconchoPath =
    search_for_environmental_variable(SCONCHO_ENV);
  if (!sconchoPath.isEmpty())
  {
    symbolPaths << sconchoPath;
  }

  return symbolPaths;
}

  


//----------------------------------------------------------------
// given the name of a knitting pattern, return the path
// it can be found at. For now, we try two locations. First,
// the one defined at compile time via SVG_ROOT_PATH. If this
// doesn't work we try the path given by SCONCHO_SYMBOL_PATH
// if it exists. If both methods fail we print an error message
// and continue.
//----------------------------------------------------------------
QString get_pattern_path(const QString& name)
{
  /* try the default path */
  QString firstPath = SVG_ROOT_PATH + "/" + name + ".svg";
  QFile firstFile(firstPath);
  if (firstFile.exists())
  {
    return firstPath;
  }

  /* try the path set by SCONCO_SYMBOL_PATH */
  QString sconchoPath =
    search_for_environmental_variable(SCONCHO_ENV);
  QString secondPath = sconchoPath + "/" + name + ".svg";
  QFile secondFile(secondPath);
  if (!secondFile.exists())
  {
    qDebug() << "ERROR: Failed to load svg file " << name << ".svg";
    return QString("");
  }

  return secondPath;
}



//---------------------------------------------------------------
// looks for a particular environmental variable in a StringList
// of the full environment and returns its value as a QString
// if present
//---------------------------------------------------------------
QString search_for_environmental_variable(const QString& item)
{
  QStringList fullEnvironment = QProcess::systemEnvironment();
  QString value("");
  QStringList filteredResults = fullEnvironment.filter(QRegExp(item));
  foreach(QString entry, filteredResults)
  {
    QStringList separated = entry.split("=");
    if (separated.length() == 2 && separated[0] == item)
    {
      value = separated[1];
      break;
    }
  }

  return value;
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
                               const QList<QColor>& colors,
                               const QString& theName)
  :
    ourScene_(scene),
    projectColors_(colors),
    fileName_(theName)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
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
  bool statusColors = save_colorInfo_(root);

  /* write it to stream */
  writeDoc_.save(*writeStream_, 4);

  return (statusPatternGridItems && statusLegendEntryPos
          && statusColors);
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

     /* write knitting symbol related info */
     KnittingSymbolPtr symbol = cell->get_knitting_symbol();
     
     /* knitting symbol category */
     QDomElement catTag = writeDoc_.createElement("patternCategory");
     itemTag.appendChild(catTag);
     catTag.appendChild(
         writeDoc_.createTextNode(symbol->category()));
     
     /* knitting symbol name */
     QDomElement nameTag = writeDoc_.createElement("patternName");
     itemTag.appendChild(nameTag);
     nameTag.appendChild(
         writeDoc_.createTextNode(symbol->patternName()));
   }
  }

  return true;
} 


//-------------------------------------------------------------
// save the positions of all items in the legend
//-------------------------------------------------------------
bool CanvasIOWriter::save_legendInfo_(QDomElement& root)
{
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


//-------------------------------------------------------------
// save the currently defined custom colors
//-------------------------------------------------------------
bool CanvasIOWriter::save_colorInfo_(QDomElement& root)
{
  QDomElement mainTag = writeDoc_.createElement("projectColors");
  root.appendChild(mainTag);

  foreach(QColor aColor, projectColors_)
  {
    /* write column and row info */
    QDomElement colorTag = writeDoc_.createElement("color");
    mainTag.appendChild(colorTag);
    colorTag.appendChild(writeDoc_.createTextNode(aColor.name()));
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
CanvasIOReader::CanvasIOReader(const QString& theName,
                               const QList<KnittingSymbolPtr>& syms)
  :
    fileName_(theName),
    allSymbols_(syms)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
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

  /* parse all events */
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
  /* loop over all the properties we expect for the pattern */
  int colIndex = 0;
  int rowIndex = 0;
  int width    = 0;
  int height   = 0;
  uint color   = 0;
  QString category("");
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

    if (node.toElement().tagName() == "patternCategory")
    {
      QDomNode childNode(node.firstChild());
      category = childNode.toText().data();
    }
    
    if (node.toElement().tagName() == "patternName")
    {
      QDomNode childNode(node.firstChild());
      name = childNode.toText().data();
    }

    node = node.nextSibling();
  }

  /* find proper knitting symbol */
  KnittingSymbolPtr symbolPtr;
  bool status =
    retrieve_knitting_symbol(allSymbols_, category, name, symbolPtr);
  if (!status)
  {
    qDebug() << "ERROR: failed to load symbol " << "category"
             << "/" << name;
    return false;
  }
  
  /* store parsed item in list of new patternGridItems */
  PatternGridItemDescriptorPtr 
    currentItem(new PatternGridItemDescriptor);
  currentItem->location = QPoint(colIndex, rowIndex);
  currentItem->dimension = QSize(width,height);
  currentItem->backgroundColor = QColor(color);
  currentItem->patternSymbolPtr = symbolPtr;
  newPatternGridItems_.push_back(currentItem);

  return true;
}


//-------------------------------------------------------------
// read a single legend entry from our input stream
//-------------------------------------------------------------
bool CanvasIOReader::parse_legendItems_(const QDomNode& itemNode)
{
  /* loop over all the properties we expect for the pattern */
  QString entryID("");
  double itemXPos = 0.0;
  double itemYPos = 0.0;
  double labelXPos = 0.0;
  double labelYPos = 0.0;
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
      itemXPos = childNode.toText().data().toDouble();
    }

    if (node.toElement().tagName() == "itemYPos")
    {
      QDomNode childNode(node.firstChild());
      itemYPos = childNode.toText().data().toDouble();
    }

    if (node.toElement().tagName() == "labelXPos")
    {
      QDomNode childNode(node.firstChild());
      labelXPos = childNode.toText().data().toDouble();
    }

    if (node.toElement().tagName() == "labelYPos")
    {
      QDomNode childNode(node.firstChild());
      labelYPos = childNode.toText().data().toDouble();
    }

    if (node.toElement().tagName() == "labelText")
    {
      QDomNode childNode(node.firstChild());
      labelText = childNode.toText().data();
    }

    node = node.nextSibling();
  }


  /* store parsed item in list of new LegendEntryDescriptors */
  LegendEntryDescriptorPtr currentEntry(new LegendEntryDescriptor);
  currentEntry->entryID = entryID;
  currentEntry->itemLocation = QPointF(itemXPos, itemYPos);
  currentEntry->labelLocation = QPointF(labelXPos, labelYPos);
  currentEntry->labelText = labelText;
  newLegendEntryDescriptors_.push_back(currentEntry);

  return true;
}



//---------------------------------------------------------------
//
//
// class KnittingSymbolReader
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
KnittingSymbolReader::KnittingSymbolReader(const QString& pathName)
  :
    pathName_(pathName)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//-------------------------------------------------------------
// destructor 
//-------------------------------------------------------------
KnittingSymbolReader::~KnittingSymbolReader()
{
  if (filePtr_ != 0)
  {
    filePtr_->close();
    delete filePtr_;
  }
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool KnittingSymbolReader::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* open read stream */
  descriptionFileName_ = pathName_ + "/" + KNITTING_SYMBOL_DESC;
  filePtr_ = new QFile(descriptionFileName_);
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
bool KnittingSymbolReader::read()
{
  /* parse file and make sure we can read it */
  QString errStr;
  int errLine;
  int errCol;
  if (!readDoc_.setContent(filePtr_, true, &errStr, &errLine, &errCol))
  {
    QMessageBox::critical(0,"sconcho DOM Parser",
      QString("Error parsing\n%1\nat line %2 column %3; %4")
      .arg(descriptionFileName_) .arg(errLine) .arg(errCol)
      .arg(errStr));

    return false;
  }

  /* make sure we're reading a sconcho description file */
  QDomElement root = readDoc_.documentElement();
  if ( root.tagName() != "sconcho" ) return false;

  /* parse the description */
  bool status = false;
  QDomNode node = root.firstChild();
  if (node.toElement().tagName() == "knittingSymbol")
  {
    status = parse_symbol_description_(node);
  }

  return status;
}



/**************************************************************
 *
 * PRIVATE FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// read a single PatternGridItem from our input stream
//-------------------------------------------------------------
bool KnittingSymbolReader::parse_symbol_description_(
  const QDomNode& itemNode)
{
  /* loop over all the properties we expect for the description */
  QString svgName("");
  QString category("");
  QString description("");
  QString patternName("");
  QString patternDescription("");
  int patternWidth = 0;
  
  QDomNode node = itemNode.firstChild();
  while (!node.isNull())
  {

    if (node.toElement().tagName() == "svgName")
    {
      QDomNode childNode(node.firstChild());
      svgName = childNode.toText().data();
    }

    if (node.toElement().tagName() == "category")
    {
      QDomNode childNode(node.firstChild());
      category = childNode.toText().data();
    }
    
    if (node.toElement().tagName() == "patternName")
    {
      QDomNode childNode(node.firstChild());
      patternName = childNode.toText().data();
    }

    if (node.toElement().tagName() == "patternDescription")
    {
      QDomNode childNode(node.firstChild());
      patternDescription = childNode.toText().data();
    }

    if (node.toElement().tagName() == "patternWidth")
    {
      QDomNode childNode(node.firstChild());
      patternWidth = childNode.toText().data().toInt();
    }

    node = node.nextSibling();
  }

  /* make sure the svg file exists */
  QString svgFileName = pathName_ + "/" + svgName + ".svg";
  QFile svgFilePtr(svgFileName);
  if (!svgFilePtr.open(QFile::ReadOnly))
  {
    return false;
  }
  
  /* construct the knitting symbol pointer */
  KnittingSymbolPtr newSymbol = KnittingSymbolPtr(
    new KnittingSymbol(
      pathName_ + "/" + svgName + ".svg",
      patternName,
      category,
      QSize(patternWidth,1),
      patternDescription));

  constructedSymbol_ = newSymbol;

  return true;
}


QT_END_NAMESPACE
