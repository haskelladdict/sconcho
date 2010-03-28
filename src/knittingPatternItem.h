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

#ifndef KNITTING_PATTERN_ITEM_H
#define KNITTING_PATTERN_ITEM_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QColor>
#include <QGraphicsItem>
#include <QPen>


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
    public QObject,
    public QGraphicsItem,
    public boost::noncopyable
{

public:

  explicit KnittingPatternItem( const QSize& aDim,
                                const QSize& aspectRatio,
                                const QColor& backColor = Qt::white,
                                const QPoint& loc = QPoint( 0, 0 ) );
  bool Init();

  /* return our object type; needed for qgraphicsitem_cast */
  enum { Type = UserType + KNITTING_PATTERN_ITEM_TYPE };
  int type() const;

  /* reimplement pure virtual base class methods */
  QRectF boundingRect() const;
  void paint( QPainter *painter,
              const QStyleOptionGraphicsItem *option, QWidget *widget );

  /* insert a new knitting symbol to be displayed */
  void insert_knitting_symbol( KnittingSymbolPtr symbol );

  /* color related functions */
  void set_background_color( const QColor& newColor );
  const QColor& color() const { return backColor_; }

  /* accessors for properties */
  const QPoint& origin() const { return loc_; }
  const QSize& dim() const { return dim_; }
  const KnittingSymbolPtr get_knitting_symbol() const;


protected:

  /* a few setters for our children */
  void select_background_color() { currentColor_ = backColor_; }
  void select_highlight_color() { currentColor_ = highlightColor_; }

  /* fit the svg item snug into our frame */
  void fit_svg_();


private:

  /* some tracking variables */
  int status_;

  /* our data symbol */
  QGraphicsSvgItem* svgItem_;
  KnittingSymbolPtr knittingSymbol_;

  /* drawing related objects */
  QPen pen_;
  QColor backColor_;
  QColor currentColor_;
  QColor highlightColor_;

  /* our location and dimensions */
  QSize dim_;
  QPoint loc_;
  const QSize& cellAspectRatio_;

  /* functions */
  void set_up_pens_brushes_();
};


QT_END_NAMESPACE

#endif
