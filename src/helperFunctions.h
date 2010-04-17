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

/****************************************************************
 *
 * this is a collection of useful helper functions
 *
 ***************************************************************/

#ifndef HELPER_FUNCTIONS_H
#define HELPER_FUNCTIONS_H

/* Qt includes */
#include <QList>
#include <QPair>
#include <QString>


QT_BEGIN_NAMESPACE

/* forward declarations */
class GraphicsScene;
class QGraphicsItem;
class QGraphicsScene;
class QSettings;


//---------------------------------------------------------------
// given a list of QGraphicsItems returns the maximum y
// coordinate
//---------------------------------------------------------------
qreal get_max_y_coordinate( const QList<QGraphicsItem*> items );



//---------------------------------------------------------------
// given a list of QGraphicsItems returns the minimum y
// coordinate
//---------------------------------------------------------------
QRectF get_bounding_rect( const QList<QGraphicsItem*> items );



//---------------------------------------------------------------
// this function splits a string of the form
// <string>[:<int>]
// into <string> and <int> and returns them as a QPair.
// if no <int> is present we return INT_MAX instead
//---------------------------------------------------------------
QPair<QString, int> split_into_category_and_position(
  const QString& parseString );



//---------------------------------------------------------------
// this function takes a string, typically a pattern description
// and tries to format them a bit nicer since they come as one
// long string. We don't want to be fancy here and basically
// just break possible long lines into a bunch of shorter ones.
//---------------------------------------------------------------
QString format_string( const QString& oldString );



//---------------------------------------------------------------
// this function assembles the name of a legend entry from
// the pieces.
// NOTE: Any change to this function may break backward
// compatibility for sconcho project files
//---------------------------------------------------------------
QString get_legend_item_name( const QString& symbolCategory,
                              const QString& symbolName, const QString& colorName,
                              const QString& tag );



//---------------------------------------------------------------
// takes a legendID and returns true if the item is a widgetItem
// (i.e. has a widgetItem identifier) and false otherwise
//---------------------------------------------------------------
bool is_extraLegendItem( const QString& idString );



//---------------------------------------------------------------
// takes a legendID and returns the name of described symbol
//---------------------------------------------------------------
QString get_legend_item_name( const QString& theID );



//---------------------------------------------------------------
// takes a legendID and returns the category of described symbol
//---------------------------------------------------------------
QString get_legend_item_category( const QString& theID );



//---------------------------------------------------------------
// takes a QList of GraphicsItems and moves them vertically by
// the given global and local offset. I.e. all items are first
// moved by the global offset. Then in a list of items sorted
// by increasing y coordinate, the 0 item is moved 0*(local offset),
// the 1st item is moved 1*(local offset) etc.
//---------------------------------------------------------------
void move_graphicsItems_vertically( const QList<QGraphicsItem*>& items,
                                    int pivot, int globalOffset,
                                    int localOffset );



//----------------------------------------------------------------
// check if a certain row can be deleted
// NOTE: deadRow is in user coordinates not in internal
// coordinates.
//----------------------------------------------------------------
bool can_row_be_deleted( int numRows, int deadRow );



//----------------------------------------------------------------
// check if a certain row can be deleted
// NOTE: pivotRow is in user coordinates not in internal
// coordinates.
//----------------------------------------------------------------
bool can_row_be_inserted( int numRows, int pivotRow );



//----------------------------------------------------------------
// check if a certain column can be deleted
// NOTE: deadCol is in user coordinates not in internal
// coordinates.
//----------------------------------------------------------------
bool can_column_be_deleted( int numColumns, int deadColumn );



QT_END_NAMESPACE

#endif
