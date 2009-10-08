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

#ifndef IO_H 
#define IO_H 

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QString>
#include <QtXml/QDomDocument>
#include <QtXml/QDomElement>
#include <QtXml/QDomNode>

/* forward declarations */
class GraphicsScene;
class PatternGridItem;
class QFile;
class QTextStream;

QT_BEGIN_NAMESPACE


/* given the name of a knitting pattern, return the path
 * it can be found at */
QString get_pattern_path(const QString& name);



/*******************************************************************
 *
 * CanvasIOWriter is responsible for writing the current content
 * of our canvas out to a file in our own sconcho pattern format.
 *
 ******************************************************************/
class CanvasIOWriter
  :
    public boost::noncopyable
{

public:

  explicit CanvasIOWriter(const GraphicsScene* theScene, 
      const QString& fileName);
  ~CanvasIOWriter();
  bool Init();

  /* save content of canvas */
  bool save();


private:

  /* status variable */
  int status_;

  /* variables */
  const GraphicsScene* ourScene_;
  QString fileName_;
  QFile* filePtr_;
  QTextStream* writeStream_;
  QDomDocument writeDoc_;

  /* helper functions */
  bool save_patternGridItems_(QDomElement& rootElement);
};



/*******************************************************************
 *
 * PatternGridItemDescriptor is a data structure that contains
 * all the information allowing GraphicsScene to reconstruct
 * a previous view loaded from a file
 *
 ******************************************************************/
struct PatternGridItemDescriptor
{
  QPoint location;
  QSize dimension;
  QColor backgroundColor;
  QString knittingSymbolName;
};



/*******************************************************************
 *
 * CanvasIOReader is responsible for reading a previously stored
 * canvas content and instructing the canvas to re-build it
 *
 ******************************************************************/
class CanvasIOReader
  :
    public boost::noncopyable
{

public:

  explicit CanvasIOReader(GraphicsScene* theScene, 
    const QString& fileName);
  ~CanvasIOReader();
  bool Init();

  /* save content of canvas */
  bool read();


private:

  /* status variable */
  int status_;

  /* variables */
  GraphicsScene* ourScene_;
  QString fileName_;
  QFile* filePtr_;
  QDomDocument readDoc_;

  /* QList of generated patternGridItems based on input file */
  QList<PatternGridItemDescriptor> newPatternGridItems_;

  /* helper functions */
  bool parse_patternGridItem_(const QDomNode& itemNode);
};

QT_END_NAMESPACE

#endif
