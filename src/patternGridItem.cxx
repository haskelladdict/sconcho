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

/* C++ headers */
#include <float.h>


/** Qt headers */
#include <QColor>
#include <QDebug>
#include <QGraphicsItemGroup>
#include <QGraphicsLineItem>
#include <QGraphicsRectItem>
#include <QGraphicsSvgItem>
#include <QGraphicsScene>
#include <QPainter>


/** local headers */
#include "basicDefs.h"
#include "graphicsScene.h"
#include "patternGridItem.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternGridItem::PatternGridItem(qreal aX, qreal aY, qreal aWidth,
  qreal aHeight, GraphicsScene* myParent)
    :
      selected_(false),
      parent_(myParent),
      svgItem_(0),
      x_(aX),
      y_(aY),
      width_(aWidth),
      height_(aHeight)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternGridItem::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* call individual initialization routines */
  set_up_pens_();

  /*svgItem_ = new QGraphicsSvgItem("../svg/susile.svg",this);
  svgItem_->setVisible(false);
  svgItem_->moveBy(x_ + width_*0.25, y_ + height_*0.25);
  */

  return true;
}



/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/



/**************************************************************
 *
 * PUBLIC MEMBER FUNCTIONS
 *
 *************************************************************/

//------------------------------------------------------------
// overload pure virtual base class function returning our
// dimensions
//------------------------------------------------------------
QRectF PatternGridItem::boundingRect() const
{
  return QRectF(x_, y_, width_, height_);
}
  
  
//------------------------------------------------------------
// overload pure virtual base class function painting 
// ourselves
//------------------------------------------------------------
void PatternGridItem::paint(QPainter *painter, 
  const QStyleOptionGraphicsItem *option, QWidget *widget)
{
  painter->setPen(activePen_);
  painter->drawRect(x_, y_, width_, height_);
}



/**************************************************************
 *
 * PROTECTED MEMBER FUNCTIONS 
 *
 *************************************************************/

//-------------------------------------------------------------
// handle mouse press events 
//-------------------------------------------------------------
void PatternGridItem::mousePressEvent(
  QGraphicsSceneMouseEvent* event)
{
  /* delete the previous svgItem if there was one */
  if ( svgItem_ != 0 ) 
  {
    delete svgItem_;
    svgItem_ = 0;
  }

  /* get name of currently selected symbol from our parent */
  QString symbolName = parent_->get_selected_symbol_name();
  if (symbolName != "")
  {
    svgItem_ = new QGraphicsSvgItem(symbolName,this);
    fit_svg_();
    svgItem_->setVisible(true);
  }

  /* repaint */
  update();
}


/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// set up all the pens we use for drawing
//-------------------------------------------------------------
void PatternGridItem::set_up_pens_()
{
  /* pen used when unselected */
  unselectedPen_.setWidth(2);
  unselectedPen_.setJoinStyle(Qt::MiterJoin);
  unselectedPen_.setColor(Qt::black);

  /* pen used when hovered on */
  hoveredPen_.setWidth(2);
  hoveredPen_.setJoinStyle(Qt::MiterJoin);
  hoveredPen_.setColor(Qt::blue);

  /* pen used when selected */
  selectedPen_.setWidth(2);
  selectedPen_.setJoinStyle(Qt::MiterJoin);
  selectedPen_.setColor(Qt::red);

  /* select active pen */
  activePen_ = unselectedPen_;
}


//---------------------------------------------------------------
// scale and shift svg item so it fits into our bounding 
// box
//---------------------------------------------------------------
void PatternGridItem::fit_svg_()
{
  if (svgItem_ == 0)
  {
    return;
  }

  /* get bounding boxes */
  QRectF svgRect = svgItem_->sceneBoundingRect();
  QRectF boxRect = sceneBoundingRect();

  /* scale */
  double scaleX = 1.0;
  if ( svgRect.width() > DBL_EPSILON )
  {
    scaleX = boxRect.width()/svgRect.width();
  }

  double scaleY = 1.0;
  if ( svgRect.height() > DBL_EPSILON )
  {
    scaleY = boxRect.height()/svgRect.height();
  }

  svgItem_->scale(scaleX, scaleY);

  /* translate */
  svgItem_->moveBy(boxRect.x(), boxRect.y());
}
