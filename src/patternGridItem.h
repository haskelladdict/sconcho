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
#include <QVariant>

/* local includes */
#include "knittingSymbol.h"

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


  explicit PatternGridItem(const QPoint& loc, const QSize& aDim, 
      int scale, int column, int row, GraphicsScene* myParent = 0);
  bool Init();


  /* reimplement pure virtual base class methods */
  QRectF boundingRect() const;
  void paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
    QWidget *widget);

  /* return our object type; needed for qgraphicsitem_cast */
  enum { Type = UserType + 1 };
  int type() const;

  /* this function selects a cell and highlights/unhightlights it
   * based on its current status */
  void select();
  
  /* insert a new knitting symbol to be displayed */
  void insert_knitting_symbol(KnittingSymbolPtr symbol);

  /* accessors for properties */
  const QPoint& origin() { return loc_; }
  const QSize& dim() { return dim_; }
  int col() { return columnIndex_; }
  int row() { return rowIndex_; }  
  


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

  /* our data symbol */
  QGraphicsSvgItem* svgItem_;
  KnittingSymbolPtr knittingSymbol_;

  /* our location and dimensions */
  QPoint loc_;
  QSize dim_;
  int scaling_;
  int columnIndex_;
  int rowIndex_;
 
  /* drawing related objects */
  QPen pen_;
  QBrush activeBrush_;
  QBrush inactiveBrush_;
  QBrush* currentBrush_;

  /* functions */
  void set_up_pens_brushes_();
  void fit_svg_();
  void highlight_on_();
  void highlight_off_();
};



#endif
