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
  cellSize_(30),
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
  /* first update our list of currently selected items */
  if (status)
  {
    activeItems_.append(anItem);
  }
  else
  {
    activeItems_.removeOne(anItem);
  }

  /* check how many cells we need for the currently selected
   * knitting symbol */
  QSize size = selectedSymbol_->dim();
  int cellsNeeded = size.width() * size.height();

  /* not the correct number of cells */
  if ( activeItems_.length() != cellsNeeded )
  {
    qDebug() << "Please select " << cellsNeeded << " adjacent cells!";
    return;
  }

  /* if we only need and have a single cell we're already good */
  if ( activeItems_.size() == 1 )
  {
    return;
  }


  /* we have the correct number, now make sure that 
   * selected cells are adjacent */
  QSet<int> yCoords;
  QMap<int,int> dims;
  for (int i=0; i < activeItems_.length(); ++i)
  {
    QPoint origin = activeItems_[i]->origin();
    QSize cellDim = activeItems_[i]->dim();
    yCoords.insert(origin.y());
    dims[origin.x()] = cellDim.width();
  }

  /* compute total selected width and make sure it matches
   * what we need */
  int totalWidth = 0;
  QList<int> widths = dims.values();
  for (int i=0; i < widths.size(); ++i)
  {
    totalWidth += widths[i];
  }

  if (totalWidth != cellsNeeded)
  {
    qDebug() << "The total number of selected units does not match";
    return;
  }

  /* all items need to be in a single row */
  if ( yCoords.size() != 1 )
  {
    qDebug() << "The selected items have to be in a single row";
    return;
  }

  /* check if origins are adjacent */
  QList<int> dimOrigins = dims.keys();
  qSort(dimOrigins.begin(), dimOrigins.end());
  for (int i=0; i < dimOrigins.size()-1; ++i)
  {
    int expectedNeighbor =  dimOrigins[i] + dims[dimOrigins[i]] * cellSize_;
    int actualNeighbor = dimOrigins[i+1];
    if ( expectedNeighbor != actualNeighbor )
    {
      qDebug() << "The selected items have to be adjacent " << expectedNeighbor << " " << actualNeighbor;
      return;
    }
  }

  /* delete selected cells and replace by a single one of the
   * requested size */
  QPoint newOrigin(dimOrigins[0], yCoords.toList()[0]);
    for (int i=0; i < activeItems_.size(); ++i)
  {
    removeItem(activeItems_[i]);
  }
  
  /* clear list of active items */
  activeItems_.clear();

  PatternGridItem* item = 
    new PatternGridItem(newOrigin, QSize(totalWidth,1), cellSize_, this);
  item->Init();

  /* add it to our scene */
  addItem(item);

  qDebug() << "All is well";

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

  for (int col=0; col < 10; ++col)
  {
    for (int row=0; row < 10; ++row)
    {
      QPoint origin(originX+(col*cellSize_), originY+(row*cellSize_));
      PatternGridItem* item = 
        new PatternGridItem(origin, QSize(1,1), cellSize_, this);
      item->Init();

      /* add it to our scene */
      addItem(item);
    }
  }
}
  
