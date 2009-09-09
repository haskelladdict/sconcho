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

/** Qt headers */
#include <QGraphicsItemGroup>
#include <QGraphicsLineItem>
#include <QGraphicsRectItem>
#include <QGraphicsSvgItem>
#include <QGraphicsScene>
#include <QPainter>


/** local headers */
#include "basicDefs.h"
#include "patternGrid.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternGrid::PatternGrid(QGraphicsScene* myScene)
  :
  theScene_(myScene)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternGrid::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  QPen thePen;
  thePen.setWidth(2);
  thePen.setJoinStyle(Qt::MiterJoin);

  int originX = 0;
  int originY = 0;
  int width = 50;
  int height = 50;

  for (int col=0; col < 3; ++col)
  {
    for (int row=0; row < 3; ++row)
    {
      QGraphicsRectItem* item = new QGraphicsRectItem( originX+(col*width),
                                                       originY+(row*height),
                                                       width, height);
      item->setPen(thePen);

      /* add it to our scene */
      theScene_->addItem(item);
    }
  }
      
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

//-------------------------------------------------------------
// function returning the bounding box of the object
//-------------------------------------------------------------
/*QRectF PatternGrid::boundingRect() const
{
  return QRectF(10,10,20,20);
}
*/


//--------------------------------------------------------------
// function doing the actual painting
//--------------------------------------------------------------
/*void PatternGrid::paint(QPainter *painter,
                        const QStyleOptionGraphicsItem *option,
                        QWidget *widget)
{
  //painter->drawRoundedRect(-10, -10, 20, 20, 5, 5);
}*/

  

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
