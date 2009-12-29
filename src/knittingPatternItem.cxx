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

/* Qt headers */
#include <QColor>
#include <QDebug>
#include <QGraphicsSvgItem>
#include <QPainter>

/* local headers */
#include "knittingPatternItem.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
KnittingPatternItem::KnittingPatternItem(const QSize& aDim, 
  int aScale, const QColor& aBackColor, const QPoint& aLoc) 
    :
      QGraphicsItem(),
      svgItem_(0),
      knittingSymbol_(new KnittingSymbol("","","",QSize(0,0),"")),
      backColor_(aBackColor),
      dim_(aDim),
      loc_(aLoc),
      scaling_(aScale)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool KnittingPatternItem::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* set up some properties */
  setFlags(QGraphicsItem::ItemClipsChildrenToShape);
  
  /* call individual initialization routines */
  set_up_pens_brushes_();

  return true;
}

//--------------------------------------------------------------
// return our custom type
//--------------------------------------------------------------
int KnittingPatternItem::type() const
{
  return Type;
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
QRectF KnittingPatternItem::boundingRect() const
{
  return QRectF(loc_.x() - pen_.width() * 0.5, 
                loc_.y() - pen_.width() * 0.5,
                scaling_ * dim_.width() + pen_.width() * 0.5,
                scaling_ * dim_.height() + pen_.width() * 0.5);
}
  
  
//------------------------------------------------------------
// overload pure virtual base class function painting 
// ourselves
//------------------------------------------------------------
void KnittingPatternItem::paint(QPainter *painter, 
  const QStyleOptionGraphicsItem *option, QWidget *widget)
{
  Q_UNUSED(widget);
  Q_UNUSED(option);
  
  painter->setPen(pen_);
  QBrush aBrush(currentColor_);
  painter->setBrush(aBrush);

  painter->drawRect(QRectF(loc_, scaling_*dim_));
}


//-------------------------------------------------------------
// insert a new knitting symbol
//-------------------------------------------------------------
void KnittingPatternItem::insert_knitting_symbol(
  KnittingSymbolPtr aSymbol)
{
  /* update pointers */
  knittingSymbol_ = aSymbol;
  QString symbolPath(aSymbol->path());

  /* delete the previous svgItem if there was one */
  if ( svgItem_ != 0 ) 
   {
    delete svgItem_;
    svgItem_ = 0;
  }

  if (symbolPath != "")
  { 
    svgItem_ = new QGraphicsSvgItem(symbolPath,this);
    fit_svg_();
  }
}
 

//--------------------------------------------------------------
// return a pointer to the currently embedded knitting symbol 
//--------------------------------------------------------------
const KnittingSymbolPtr KnittingPatternItem::get_knitting_symbol()
  const
{
  return knittingSymbol_;
}


//-------------------------------------------------------------
// change the background color
//-------------------------------------------------------------
void KnittingPatternItem::set_background_color(const QColor& newColor)
{
  backColor_ = newColor;
}


/**************************************************************
 *
 * PROTECTED MEMBER FUNCTIONS 
 *
 *************************************************************/

//---------------------------------------------------------------
// scale and shift svg item so it fits into our bounding 
// box
//---------------------------------------------------------------
void KnittingPatternItem::fit_svg_()
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
void KnittingPatternItem::set_up_pens_brushes_()
{
  /* pen used */
  pen_.setWidthF(1.0);
  pen_.setColor(Qt::black);

  /* set up highlight color */
  highlightColor_ = QColor(Qt::gray);

  currentColor_ = backColor_;
}



QT_END_NAMESPACE
