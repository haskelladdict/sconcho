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

/* Qt headers */
#include <QDebug>
#include <QGraphicsTextItem>
#include <QPainter>

/* local headers */
#include "graphicsScene.h"
#include "patternKeyItem.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternKey::PatternKey(const QPoint& aLoc, const QFont& aFont,
  GraphicsScene* myParent)
    :
      QGraphicsItem(),
      parent_(myParent),
      loc_(aLoc),
      textFont_(aFont)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternKey::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  setPos(loc_);

  create_main_label_();

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
QRectF PatternKey::boundingRect() const
{
  return QRectF(loc_.x() - pen_.width() * 0.5, 
                loc_.y() - pen_.width() * 0.5,
                100,
                10);
}

  
//------------------------------------------------------------
// overload pure virtual base class function painting 
// ourselves
//------------------------------------------------------------
void PatternKey::paint(QPainter *painter, 
  const QStyleOptionGraphicsItem *option, QWidget *widget)
{
/*  painter->setPen(pen_);

  QBrush aBrush(currentColor_);
  painter->setBrush(aBrush);

  painter->drawRect(QRectF(loc_, QPoint(100,100))); */
}


//--------------------------------------------------------------
// return our custom type
// so we can cast via 
//--------------------------------------------------------------
int PatternKey::type() const
{
  return Type;
}
  

//-------------------------------------------------------------
// set the font to newFont and updates all children objects
// that need to be changed
//-------------------------------------------------------------
void PatternKey::set_font(const QFont& newFont)
{
  textFont_ = newFont;

  mainText_->setFont(textFont_);
}


/**************************************************************
 *
 * PROTECTED MEMBER FUNCTIONS 
 *
 *************************************************************/

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
// create the main label
//-------------------------------------------------------------
void PatternKey::create_main_label_()
{
  mainText_ = new QGraphicsTextItem(tr("Legend"),this);
  mainText_->setFont(textFont_);
  mainText_->setTextInteractionFlags(Qt::TextEditable);
}


QT_END_NAMESPACE
