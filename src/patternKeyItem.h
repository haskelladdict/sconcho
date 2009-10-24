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

#ifndef PATTERN_KEY_ITEM_H
#define PATTERN_KEY_ITEM_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QFont>
#include <QGraphicsItem>
#include <QPen>

/* local includes */
#include "basicDefs.h"

QT_BEGIN_NAMESPACE


/* a few forward declarations */
class GraphicsScene;
class QGraphicsSceneMouseEvent;
class QGraphicsTextItem;
class QPainter;
class QStyleOptionGraphicsItem;


/***************************************************************
 * 
 * The GraphicsScene handles the sconcho's main drawing
 * canvas 
 *
 ***************************************************************/
class PatternKey
  :
    public QObject,
    public QGraphicsItem,
    public boost::noncopyable
{
  
  Q_OBJECT

  
public:


  explicit PatternKey(const QPoint& loc, const QFont& font,
      GraphicsScene* myParent = 0);
  bool Init();

  /* reimplement pure virtual base class methods */
  QRectF boundingRect() const;
  void paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
    QWidget *widget);

  /* return our object type; needed for qgraphicsitem_cast */
  enum { Type = UserType + PATTERN_KEY_TYPE };
  int type() const;

  /* accessors for properties */
  const QPoint& origin() const { return loc_; } 
  const QSize& dim() const { return dim_; }

  /* setters for properties */
  void set_font(const QFont& newFont); 

//protected:

//  void mousePressEvent(QGraphicsSceneMouseEvent* event);
 
    
private:

  /* some tracking variables */
  int status_;

  /* our parent scene */
  GraphicsScene* parent_;

  /* our location and dimensions */
  QPoint loc_;
  QSize dim_;

  /* our graphic items */
  QGraphicsTextItem* mainText_;

  /* properties objects */
  QFont textFont_;
  QPen pen_;
  QColor backColor_;
  QColor currentColor_;
  QColor highlightColor_;

  /* interface creation functions */
  void create_main_label_();
};


QT_END_NAMESPACE

#endif
