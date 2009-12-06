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

#ifndef PATTERN_GRID_RECTANGLE_H
#define PATTERN_GRID_RECTANGLE_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGraphicsRectItem>
#include <QObject>
#include <QPen>

/* local includes */
#include "basicDefs.h"


QT_BEGIN_NAMESPACE


/***************************************************************
 * 
 * PatterGridRectangle is a simple rectangle of a certain
 * width and color that makes a certain rectangular array
 * of canvas cells
 *
 ***************************************************************/
class PatternGridRectangle
  :
    public QObject,
    public QGraphicsRectItem,
    public boost::noncopyable
{
 
  Q_OBJECT

public:

  explicit PatternGridRectangle(const QRectF& position, QPen pen,
    QGraphicsItem* aParent = 0);
  bool Init();

  bool selected(const QPointF& clickPos) const;
  void set_pen(QPen newPen);
  

  /* return our object type; needed for qgraphicsitem_cast */
  enum { Type = UserType + PATTERN_GRID_RECTANGLE_TYPE };
  int type() const;


private:

  /* some tracking variables */
  int status_;

  /* variables */
  QPen currentPen_;

};


QT_END_NAMESPACE


#endif
