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
#include <float.h>
#include <limits.h>

/* qt includes */
#include <QDebug>
#include <QGraphicsItem>
#include <QMultiMap>

/* local includes */
#include "graphicsScene.h"
#include "helperFunctions.h"
#include "settings.h"


QT_BEGIN_NAMESPACE

//---------------------------------------------------------------
// given a list of QGraphicsItems returns the maximum y
// coordinate
//---------------------------------------------------------------
qreal get_max_y_coordinate( const QList<QGraphicsItem*> items )
{
  qreal yMax = -DBL_MAX;
  foreach( QGraphicsItem* anItem, items ) {
    qreal yPos = anItem->scenePos().y()
                 + anItem->boundingRect().height();
    if ( yMax < yPos ) {
      yMax = yPos;
    }
  }

  return yMax;
}


//---------------------------------------------------------------
// given a list of QGraphicsItems returns the bounding rectangle
//---------------------------------------------------------------
QRectF get_bounding_rect( const QList<QGraphicsItem*> items )
{
  qreal yMin = DBL_MAX;
  qreal yMax = -DBL_MAX;
  qreal xMin = DBL_MAX;
  qreal xMax = -DBL_MAX;

  foreach( QGraphicsItem* anItem, items ) {
    QRectF bound( anItem->mapRectToParent( anItem->boundingRect() ) );

    if ( xMin > bound.left() ) {
      xMin = bound.left();
    }

    if ( xMax < bound.right() ) {
      xMax = bound.right();
    }

    if ( yMin > bound.top() ) {
      yMin = bound.top();
    }

    if ( yMax < bound.bottom() ) {
      yMax = bound.bottom();
    }
  }

  return QRectF( xMin, yMin, ( xMax - xMin ), ( yMax - yMin ) );
}


//---------------------------------------------------------------
// this function splits a string of the form
// <string>[:<int>]
// into <string> and <int> and returns them as a QPair.
// if no <int> is present we return INT_MAX instead
//---------------------------------------------------------------
QPair<QString, int> split_into_category_and_position(
  const QString& aParseString )
{
  QStringList result = aParseString.split( ":" );
  assert( !result.isEmpty() );

  bool status = false;
  int ordering = result.last().toInt( &status );
  if (( result.length() < 2 ) || ( status == false ) ) {
    return QPair<QString, int>( aParseString, INT_MAX );
  } else {
    result.removeLast();
    return QPair<QString, int>( result.join( ":" ), ordering );
  }
}


//---------------------------------------------------------------
// this function takes a string, typically a pattern description
// and tries to format them a bit nicer since they come as one
// long string. We don't want to be fancy here and basically
// just break possible long lines into a bunch of shorter ones.
//---------------------------------------------------------------
QString format_string( const QString& oldString )
{
  int maxLineLength = 40;

  QStringList splitString = oldString.split( " " );
  QString outString;
  int lengthCount = 0;
  foreach( QString item, splitString ) {
    if ( lengthCount > maxLineLength ) {
      outString += "\n";
      lengthCount = 0;
    }

    outString += item;
    outString += " ";
    lengthCount += ( item.length() + 1 );
  }

  return outString;
}


//---------------------------------------------------------------
// this function assembles the name of a legend entry from
// the pieces.
// NOTE: Any change to this function may break backward
// compatibility for sconcho project files
//---------------------------------------------------------------
QString get_legend_item_name( const QString& aSymbolCategory,
                              const QString& aSymbolName, const QString& aColorName,
                              const QString& aTag )
{
  return aSymbolCategory + ":" + aSymbolName + ":" + aColorName
         + ":" + aTag;
}



//---------------------------------------------------------------
// takes a legendID and returns true if the item is a widgetItem
// (i.e. has a widgetItem identifier) and false otherwise
//---------------------------------------------------------------
bool is_extraLegendItem( const QString& idString )
{
  QStringList splitString = idString.split( ":" );
  return ( splitString.last() == "extraLegendItem" );
}



//---------------------------------------------------------------
// takes a legendID and returns the name of described symbol
//---------------------------------------------------------------
QString get_legend_item_name( const QString& idString )
{
  QStringList splitString = idString.split( ":" );
  if ( splitString.length() > 1 ) {
    return splitString.at( 1 );
  } else {
    return "";
  }
}




//---------------------------------------------------------------
// takes a legendID and returns the category of described symbol
//---------------------------------------------------------------
QString get_legend_item_category( const QString& idString )
{
  QStringList splitString = idString.split( ":" );
  if ( splitString.length() > 0 ) {
    return splitString.at( 0 );
  } else {
    return "";
  }
}



//---------------------------------------------------------------
// takes a QList of GraphicsItems and moves them by the
// given global and local offset. I.e. all items are first
// moved by the global offset. Then in a list of items sorted
// by increasing y coordinate, the 0 item is moved 0*(local offset),
// the 1st item is moved 1*(local offset) etc.
// NOTE: Only items with y coordinate > pivot are shifted
//---------------------------------------------------------------
void move_graphicsItems_vertically( const QList<QGraphicsItem*>& allItems,
                                    int pivot, int globalOffset, int localOffset )
{
  QMultiMap<double, QGraphicsItem*> sortedByYPos;
  foreach( QGraphicsItem* item, allItems ) {
    sortedByYPos.insert( item->pos().y(), item );
  }

  int counter = 0;
  foreach( QGraphicsItem* item, sortedByYPos.values() ) {
    QPointF itemPos = item->pos();
    if ( itemPos.y() > pivot ) {
      item->setPos( itemPos.x(),
                    itemPos.y() + globalOffset + counter * localOffset );
      counter++;
    }
  }
}



QT_END_NAMESPACE
