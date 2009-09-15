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
#include <QDebug>
#include <QGraphicsItem>
#include <QGraphicsItemGroup>
#include <QGraphicsLineItem>
#include <QGraphicsSceneMouseEvent>


/** local headers */
#include "basicDefs.h"
#include "graphicsScene.h"
#include "knittingSymbol.h"
#include "patternGridItem.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
GraphicsScene::GraphicsScene(QObject* myParent)
  :
  QGraphicsScene(myParent),
  selectedSymbol_(
      KnittingSymbolPtr(new KnittingSymbol("","",QSize(0,0),"","")))
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool GraphicsScene::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  create_grid_item_();


  /* install signal handlers */
  connect(this,
          SIGNAL(mouse_moved(QPointF)),
          parent(),
          SLOT(update_mouse_position_display(QPointF))
         );

  
  return true;
}


/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// accessor function to get at the symbol name 
//-------------------------------------------------------------
const KnittingSymbolPtr GraphicsScene::get_selected_symbol()
{
  return selectedSymbol_;
}


 
/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// update our local copy of the name of the currently selected
// symbol
//-------------------------------------------------------------
void GraphicsScene::update_selected_symbol(
    const KnittingSymbolPtr symbol)
{
  selectedSymbol_ = symbol;
}


//-------------------------------------------------------------
// update the present list of grid items; if the number of
// selected items matches the number we need based on the
// knitting symbol and they are adjacent we can place the
// symbol
//--------------------------------------------------------------
void GraphicsScene::grid_item_selected(PatternGridItem* anItem, 
    bool status)
{
  if (status)
  {
    activeItems_.append(anItem);
  }
  else
  {
    activeItems_.removeOne(anItem);
  }

  qDebug() << "*** " << activeItems_.size();
}



/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

/**************************************************************
 *
 * PROTECTED SLOTS
 *
 *************************************************************/

//---------------------------------------------------------------
// event handler for mouse move events
//---------------------------------------------------------------
void GraphicsScene::mouseMoveEvent(
    QGraphicsSceneMouseEvent* mouseEvent)
{
  QPointF currentPos = mouseEvent->scenePos();

  /* let our parent know that we moved */
  emit mouse_moved(currentPos);
}



/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/


//-------------------------------------------------------------
// create the grid
//-------------------------------------------------------------
void GraphicsScene::create_grid_item_()
{
  int originX = 0;
  int originY = 0;
  int aWidth = 30;
  int aHeight = 30;

  for (int col=0; col < 10; ++col)
  {
    for (int row=0; row < 10; ++row)
    {
      QPoint origin(originX+(col*aWidth), originY+(row*aHeight));
      PatternGridItem* item = 
        new PatternGridItem(origin, QSize(1,1), 30, this);
      item->Init();

      /* add it to our scene */
      addItem(item);
    }
  }
}
  
