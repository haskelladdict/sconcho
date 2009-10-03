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
#include <QTextStream>

/* local includes */
#include "basicDefs.h"
#include "graphicsScene.h"
#include "io.h"


//----------------------------------------------------------------
// given the name of a knitting pattern, return the path
// it can be found at 
//----------------------------------------------------------------
QString get_pattern_path(const QString& name)
{
  return PATTERN_PATH + "/" + name + ".svg";
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
  writeStream_->flush();
  delete writeStream_;
  
  filePtr_->close();
  delete filePtr_;

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

  /* open write stream */
  filePtr_ = new QFile(fileName_);
  if (!filePtr_->open(QFile::WriteOnly | QFile::Truncate))
  {
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
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// save all PatternGridItems to our write stream
//-------------------------------------------------------------
bool CanvasIOWriter::save_patternGridItems_(QDomElement& root)
{
  qDebug() << "save patternGridItems";

  QDomElement eventTag = writeDoc_.createElement("event");
  QDomElement dateTag = writeDoc_.createElement("date");
  QDomElement contentTag = writeDoc_.createElement("content");
  QDomText date = writeDoc_.createTextNode("foobar2");
  QDomText content = 
    writeDoc_.createTextNode("foobar");

  root.appendChild(eventTag);
  eventTag.appendChild(dateTag);
  eventTag.appendChild(contentTag);
  dateTag.appendChild(date);
  contentTag.appendChild(content);

  return true;
} 
