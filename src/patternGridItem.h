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
#include <QBrush>
#include <QGraphicsItem>
#include <QPen>
#include <QList>

/* local includes */

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
    public QObject,
    public QGraphicsItem,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit PatternGridItem(const QPoint& loc, const QSize& aDim, const int scale,
      GraphicsScene* myParent = 0);
  bool Init();


  /* reimplement pure virtual base class methods */
  QRectF boundingRect() const;
  void paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
    QWidget *widget);

  /* accessors for properties */
  const QPoint& origin() { return loc_; }
  const QSize& dim() { return dim_; }


signals:

  void item_selected(PatternGridItem* us, bool status);


//public slots:


protected:

  void mousePressEvent(QGraphicsSceneMouseEvent* event);

 
//private slots:
    
private:

  /* some tracking variables */
  int status_;
  bool selected_;

  /* our parent scene */
  GraphicsScene* parent_;

  /* our data symbol */
  QGraphicsSvgItem* svgItem_;

  /* our location and dimensions */
  QPoint loc_;
  QSize dim_;
  int scaling_;
 
  /* drawing related objects */
  QPen pen_;
  QBrush activeBrush_;
  QBrush inactiveBrush_;
  QBrush* currentBrush_;

  /* functions */
  void set_up_pens_brushes_();
  void fit_svg_();
};



#endif
