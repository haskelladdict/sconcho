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

#ifndef IO_H
#define IO_H

/* boost includes */
#include <boost/utility.hpp>
#include <boost/shared_ptr.hpp>

/* QT includes */
#include <QList>
#include <QString>
#include <QStringList>
#include <QtXml/QDomDocument>
#include <QtXml/QDomElement>
#include <QtXml/QDomNode>


/* local includes */
#include "knittingSymbol.h"


QT_BEGIN_NAMESPACE


/* forward declarations */
class GraphicsScene;
class PatternGridItem;
class QColor;
class QFile;
class QSettings;
class QTextStream;


/* convenience typedefs */
typedef QPair<KnittingSymbolPtr, int> ParsedSymbol;


//--------------------------------------------------------------
// this function tries to load all knitting symbols it can
// find (at the default and user defined paths), creates
// the corresponding KnittingSymbolPtrs and returns them
// all in a QList
//--------------------------------------------------------------
QList<ParsedSymbol> load_all_symbols();



//--------------------------------------------------------------
// this function takes a path and looks for directories
// containing instructions for knitting symbols
//--------------------------------------------------------------
QList<ParsedSymbol> load_symbols_from_path( const QString& path );



//--------------------------------------------------------------
// this function collects all paths where knitting pattern
// symbols might be located
//--------------------------------------------------------------
QStringList get_all_symbol_paths();



//--------------------------------------------------------------
// given the name of a knitting pattern, return the path
// it can be found at
//--------------------------------------------------------------
QString get_pattern_path( const QString& name );



//---------------------------------------------------------------
// given the list of all available knitting symbols and the
// category+name of a symbol retrieve the proper
// KnittingSymbolPtr. Returns true on success and false otherwise
//---------------------------------------------------------------
bool retrieve_knitting_symbol(
  const QList<KnittingSymbolPtr>& allSymbols,
  const QString& category,
  const QString& name,
  KnittingSymbolPtr& symbolPtr );



//---------------------------------------------------------------
// looks for a particular environmental variable in a StringList
// of the full environment and returns its value as a QString
// if present
//---------------------------------------------------------------
QString search_for_environmental_variable( const QString& item );



//---------------------------------------------------------------
// this functions fires up a file export dialog and returns
// the selected filename or an empty string if none
// was entered
//---------------------------------------------------------------
QString show_file_export_dialog( const QString& filePath );



//---------------------------------------------------------------
// this functions export the content of a QGraphicsScene to
// a file
//---------------------------------------------------------------
void export_scene( const QString& fileName, GraphicsScene* theScene );



//---------------------------------------------------------------
// this function prints the content of a QGraphicsScene
//---------------------------------------------------------------
void print_scene( GraphicsScene* theScene );



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

  explicit CanvasIOWriter( const GraphicsScene* theScene,
                           const QList<QColor>& activeColors,
                           const QSettings& settings,
                           const QString& fileName );
  ~CanvasIOWriter();
  bool Init();

  /* save content of canvas */
  bool save();


private:

  /* status variable */
  int status_;

  /* variables */
  const GraphicsScene* ourScene_;
  const QList<QColor>& projectColors_;
  const QSettings& settings_;
  QString fileName_;
  QFile* filePtr_;
  QTextStream* writeStream_;
  QDomDocument writeDoc_;

  /* helper functions */
  bool save_patternGridItems_( QDomElement& rootElement );
  bool save_legendInfo_( QDomElement& rootElement );
  bool save_colorInfo_( QDomElement& rootElement );
  bool save_gridCellDimensions_( QDomElement& rootElement );
  bool save_textFont_( QDomElement& rootElement );
};



/*******************************************************************
 *
 * PatternGridItemDescriptor is a data structure that contains
 * all the information allowing GraphicsScene to reconstruct
 * a previous view loaded from a file
 *
 ******************************************************************/
struct PatternGridItemDescriptor {
  QPoint location;
  QSize dimension;
  QColor backgroundColor;
  KnittingSymbolPtr patternSymbolPtr;
};

typedef boost::shared_ptr<PatternGridItemDescriptor>
PatternGridItemDescriptorPtr;


/*******************************************************************
 *
 * LegendEntryDescriptor is a data structure that contains
 * all the information allowing GraphicsScene to reconstruct
 * the position and text of legend items derived both from the
 * chart as well as extra items
 *
 ******************************************************************/
struct LegendEntryDescriptor {
  QString entryID;
  QPointF itemLocation;
  QPointF labelLocation;
  QString labelText;
  KnittingSymbolPtr patternSymbolPtr;
};

typedef boost::shared_ptr<LegendEntryDescriptor>
LegendEntryDescriptorPtr;



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

  explicit CanvasIOReader( const QString& fileName,
                           const QList<KnittingSymbolPtr>& allSymbols,
                           QSettings& settings_ );
  ~CanvasIOReader();
  bool Init();

  /* read content of canvas */
  bool read();

  /* accessors for parsed information */
  const QList<PatternGridItemDescriptorPtr>& get_pattern_items() const {
    return newPatternGridItems_;
  }

  const QList<LegendEntryDescriptorPtr>& get_legend_items() const {
    return newLegendEntryDescriptors_;
  }

  const QList<LegendEntryDescriptorPtr>& get_extra_legend_items() const {
    return newExtraLegendItemDescriptors_;
  }

  const QList<QColor>& get_project_colors() const {
    return projectColors_;
  }



private:

  /* status variable */
  int status_;

  /* variables */
  QString fileName_;
  const QList<KnittingSymbolPtr>& allSymbols_;
  QSettings& settings_;
  QFile* filePtr_;
  QDomDocument readDoc_;

  /* QList of parsed patternGridItems based on input file */
  QList<PatternGridItemDescriptorPtr> newPatternGridItems_;

  /* QList of parsed legend descriptors coming from the chart */
  QList<LegendEntryDescriptorPtr> newLegendEntryDescriptors_;

  /* QList of extra parsed legend descriptors */
  QList<LegendEntryDescriptorPtr> newExtraLegendItemDescriptors_;

  /* QList of selector colors */
  QList<QColor> projectColors_;

  /* helper functions */
  bool parse_patternGridItems_( const QDomNode& itemNode );
  bool parse_legendItems_( const QDomNode& itemNode );
  bool parse_projectColors_( const QDomNode& itemNode );
  bool parse_gridCellDimensions_( const QDomNode& itemNode );
  bool parse_textFont_( const QDomNode& itemNode );
  void add_to_extraLegendItems_( const QString& entryID, double itemXPos,
                                 double itemYPos, double labelXPos, double labelYPos,
                                 const QString& labelText );
  void add_to_chartLegendItems_( const QString& entryID, double itemXPos,
                                 double itemYPos, double labelXPos, double labelYPos,
                                 const QString& labelText );
};



/*******************************************************************
 *
 * KnittingSymbolReader is responsible for reading a stored knitting
 * symbol from disc
 *
 ******************************************************************/
class KnittingSymbolReader
    :
    public boost::noncopyable
{

public:

  explicit KnittingSymbolReader( const QString& path );
  ~KnittingSymbolReader();
  bool Init();

  /* try to load the knitting symbol */
  bool read();

  /* if reading succeeded (i.e., make sure to check the return
   * value of read first) returns a fully constructed pair of
   * knitting symbol object and its position on the widget */
  QPair<KnittingSymbolPtr, int> get_symbol() const;


private:

  /* status variable */
  int status_;

  /* variables */
  QString pathName_;
  QString descriptionFileName_;
  QFile* filePtr_;
  QDomDocument readDoc_;

  /* final parsed results */
  KnittingSymbolPtr constructedSymbol_;
  int interfacePosition_;

  /* helper functions */
  bool parse_symbol_description_( const QDomNode& itemNode );
};



QT_END_NAMESPACE

#endif
