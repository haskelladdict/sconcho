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

#ifndef KNITTING_PATTERN_ITEM_H
#define KNITTING_PATTERN_ITEM_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QBrush>
#include <QColor>
#include <QGraphicsItem>
#include <QPen>
//#include <QList>

/* local includes */
#include "basicDefs.h"
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
class KnittingPatternItem
  :
    public QGraphicsItem,
    public boost::noncopyable
{
  
public:


  explicit KnittingPatternItem(const QPoint& loc, const QSize& aDim, 
      int scale, int columnID, int rowID, 
      const QColor& backColor = Qt::white);
  bool Init();

  /* reimplement pure virtual base class methods */
  QRectF boundingRect() const;
  void paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
    QWidget *widget);

  /* insert a new knitting symbol to be displayed */
  void insert_knitting_symbol(KnittingSymbolPtr symbol);

  /* reseat this cell to the given new coordinates */
  void reseat(const QPoint& newOrigin, int newCol, int newRow);

  /* set the background color */
  void set_background_color(const QColor& newColor);

  /* accessors for properties */
  const QPoint& origin() const { return loc_; } 
  const QSize& dim() const { return dim_; }
  int col() const { return columnIndex_; }
  int row() const { return rowIndex_; }
  const QString& get_knitting_symbol_name() const;
  const KnittingSymbolPtr get_knitting_symbol() const;


private:

  /* some tracking variables */
  int status_;

  /* our data symbol */
  QGraphicsSvgItem* svgItem_;
  KnittingSymbolPtr knittingSymbol_;

  /* drawing related objects */
  QPen pen_;
  QColor backColor_;

  /* our location and dimensions */
  QPoint loc_;
  QSize dim_;
  int scaling_;
  int columnIndex_;
  int rowIndex_;
 
  /* functions */
  void set_up_pens_brushes_();
  void fit_svg_();
};


QT_END_NAMESPACE

#endif
