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

#ifndef PATTERN_GRID_H
#define PATTERN_GRID_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGraphicsItem>
#include <QList>

/* local includes */

/* a few forward declarations */
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
    public QGraphicsItem,
    public boost::noncopyable
{
  
//  Q_OBJECT

    
public:

  explicit PatternGridItem(qreal x, qreal y, qreal width, qreal 
      height, QGraphicsItem* myParent = 0);
  bool Init();


  /* reimplement pure virtual base class methods */
  QRectF boundingRect() const;
  void paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
    QWidget *widget);


//signals:


//public slots:


protected:

  void mousePressEvent(QGraphicsSceneMouseEvent* event);

 

//private slots:
    
private:

  /* some tracking variables */
  int status_;
  bool selected_;

  /* our parent */
  QGraphicsItem* parent_;

  /* our data symbol */
  QGraphicsSvgItem* svgItem_;

  /* our location and dimensions */
  qreal x_;
  qreal y_;
  qreal width_;
  qreal height_;

  /* drawing related objects */
  QPen unselectedPen_;
  QPen hoveredPen_;
  QPen selectedPen_;
  QPen activePen_;


  /* functions */
  void set_up_pens_();
};



#endif
