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

#ifndef PATTERN_GRID_ITEM_H
#define PATTERN_GRID_ITEM_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QBrush>
#include <QColor>
#include <QGraphicsItem>
#include <QPen>
#include <QList>

/* local includes */
#include "basicDefs.h"
#include "knittingPatternItem.h"
#include "knittingSymbol.h"


QT_BEGIN_NAMESPACE


/* a few forward declarations */
class GraphicsScene;
class QGraphicsSceneMouseEvent;
class QGraphicsSvgItem;
class QPainter;
class QStyleOptionGraphicsItem;


/***************************************************************
 * 
 * The GraphicsScene handles the sconcho's main drawing
 * canvas 
 *
 ***************************************************************/
class PatternGridItem
  :
    public KnittingPatternItem
{
  
  Q_OBJECT

  
public:

  explicit PatternGridItem(const QPoint& loc, const QSize& aDim, 
      int scale, int columnID, int rowID, 
      GraphicsScene* myParent = 0,
      const QColor& backColor = Qt::white);
  bool Init();

  /* return our object type; needed for qgraphicsitem_cast */
  enum { Type = UserType + PATTERN_GRID_ITEM_TYPE };
  int type() const;

  /* this function selects a cell and highlights/unhightlights it
   * based on its current status */
  void select();
  
  /* reseat this cell to the given new coordinates */
  void reseat(const QPoint& newOrigin, int newCol, int newRow);

  /* accessors for properties */
  int col() const { return columnIndex_; }
  int row() const { return rowIndex_; }  


signals:

  void item_selected(PatternGridItem* us, bool status);
  void item_reset(PatternGridItem* us);


protected:

  void mousePressEvent(QGraphicsSceneMouseEvent* event);
 
    
private:

  /* some tracking variables */
  int status_;
  bool selected_;

  /* our parent scene */
  GraphicsScene* parent_;

  /* our location and dimensions */
  int columnIndex_;
  int rowIndex_;
 
  /* functions */
  void highlight_on_();
  void highlight_off_();
};


QT_END_NAMESPACE

#endif
