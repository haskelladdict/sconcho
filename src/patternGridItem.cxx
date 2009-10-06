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
#include <QGraphicsLineItem>
#include <QGraphicsRectItem>
#include <QGraphicsSvgItem>
#include <QGraphicsScene>
#include <QGraphicsSceneMouseEvent>
#include <QPainter>

/* local headers */
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
PatternGridItem::PatternGridItem(const QPoint& aLoc, 
  const QSize& aDim, int aScale, int aCol, int aRow,
  GraphicsScene* myParent, const QColor& aBackColor)
    :
      QGraphicsItem(),
      selected_(false),
      parent_(myParent),
      svgItem_(0),
      knittingSymbol_(new KnittingSymbol("","",QSize(0,0),"","")),
      loc_(aLoc),
      dim_(aDim),
      scaling_(aScale),
      columnIndex_(aCol),
      rowIndex_(aRow),
      backColor_(aBackColor)
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

  /* set up some properties */
  setFlags(QGraphicsItem::ItemIsSelectable);
  
  /* call individual initialization routines */
  set_up_pens_brushes_();

  /* some signals and slots */
  connect(this, 
          SIGNAL(item_selected(PatternGridItem*, bool)), 
          parent_, 
          SLOT(grid_item_selected(PatternGridItem*, bool)));

  connect(this, 
          SIGNAL(item_reset(PatternGridItem*)), 
          parent_, 
          SLOT(grid_item_reset(PatternGridItem*)));


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
  return QRectF(loc_.x() - pen_.width() * 0.5, 
                loc_.y() - pen_.width() * 0.5,
                scaling_ * dim_.width() + pen_.width() * 0.5,
                scaling_ * dim_.height() + pen_.width() * 0.5);
}
  
  
//------------------------------------------------------------
// overload pure virtual base class function painting 
// ourselves
//------------------------------------------------------------
void PatternGridItem::paint(QPainter *painter, 
  const QStyleOptionGraphicsItem *option, QWidget *widget)
{
  painter->setPen(pen_);

  QBrush aBrush(currentColor_);
  painter->setBrush(aBrush);

  painter->drawRect(QRectF(loc_, scaling_*dim_));
}


//-------------------------------------------------------------
// insert a new knitting symbol
//-------------------------------------------------------------
void PatternGridItem::insert_knitting_symbol(KnittingSymbolPtr aSymbol)
{
  /* update pointers */
  knittingSymbol_ = aSymbol;
  QString symbolPath(aSymbol->path());

  /* set the background color to the currently selected one 
   * if requested and turn hightlight off */
  highlight_off_();

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
 
void PatternGridItem::set_background_color(const QColor& newColor)
{
  backColor_ = newColor;
}

//--------------------------------------------------------------
// move this cell to a new location (in the pattern grid
// array) on the canvas.
//--------------------------------------------------------------
void PatternGridItem::reseat(const QPoint& newOrigin, int newCol, 
    int newRow)
{
  /* schedule event with canvas */
  prepareGeometryChange();

  /* update */
  loc_ = newOrigin;
  columnIndex_ = newCol;
  rowIndex_ = newRow;

  /* fix up the svg item */
  fit_svg_();
} 


//--------------------------------------------------------------
// select this grid cell and turn highlighting on/off based
// on its current status
//--------------------------------------------------------------
void PatternGridItem::select()
{
  if (selected_)
  {
    highlight_off_();
    emit item_selected(this, false);
  }
  else
  {
    highlight_on_();
    emit item_selected(this, true);
  }

  update();
}



//--------------------------------------------------------------
// return the full name of our embedded knitting symbol if
// we have one and the empty string otherwise
//--------------------------------------------------------------
const QString& PatternGridItem::knittingSymbolName() const
{
  return knittingSymbol_->fullName();
}

  

//--------------------------------------------------------------
// return our custom type
// so we can cast via 
//--------------------------------------------------------------
int PatternGridItem::type() const
{
  return Type;
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
  QGraphicsSceneMouseEvent* anEvent)
{
  /* ignore right mouse clicks */
  if (anEvent->button() == Qt::RightButton)  
  {
    return;
  }
  
  /* if the user has control pressed we ignore this event */
  if (anEvent->modifiers().testFlag(Qt::ControlModifier))
  {
    anEvent->ignore();
    return;
  }

  /* if the user has shift pressed this is a reset event
   * otherwise a select/deselect event */
  if (anEvent->modifiers().testFlag(Qt::ShiftModifier))
  {
    emit item_reset(this);
  }
  else
  {
    select();
  }
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
void PatternGridItem::set_up_pens_brushes_()
{
  /* pen used */
  pen_.setWidthF(1.0);
  pen_.setColor(Qt::black);

  /* set up highlight color */
  highlightColor_ = QColor(Qt::gray);

  currentColor_ = backColor_;
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
  svgItem_->setPos(boxRect.x(), boxRect.y());
}


//-----------------------------------------------------------------
// helper function for doing the internal housekeeping during
// selecting/deselecting
// NOTE: these functions should not emit an item_selected signal
//-----------------------------------------------------------------
void PatternGridItem::highlight_on_()
{
  selected_ = true;
  currentColor_ = highlightColor_;
}


void PatternGridItem::highlight_off_()
{
  selected_ = false;
  currentColor_ = backColor_; 
}

