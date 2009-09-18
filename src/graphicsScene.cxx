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
#include <QKeyEvent>


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
  shiftPressed_(false),
  origin_(QPoint(0,0)),
  numCols_(0),
  numRows_(0),
  cellSize_(0),
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

  /* install signal handlers */
  connect(this,
          SIGNAL(mouse_moved(QPointF)),
          parent(),
          SLOT(update_mouse_position_display(QPointF))
         );

  connect(this,
          SIGNAL(statusBar_message(QString)),
          parent(),
          SLOT(show_statusBar_message(QString))
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


//-------------------------------------------------------------
// accessor function for status of shift key
//-------------------------------------------------------------
bool GraphicsScene::shift_pressed()
{
  return shiftPressed_;
}


//-------------------------------------------------------------
// create the grid
//-------------------------------------------------------------
void GraphicsScene::create_pattern_grid(const QPoint& theOrigin, 
    const QSize& dimension, int size)
{
  origin_ = theOrigin;
  numCols_ = dimension.width();
  numRows_ = dimension.height();
  cellSize_ = size;

  for (int col=0; col < numCols_; ++col)
  {
    for (int row=0; row < numRows_; ++row)
    {
      QPoint origin(origin_.x() +(col*cellSize_), 
                    origin_.y() +(row*cellSize_));
      PatternGridItem* item = 
        new PatternGridItem(origin, QSize(1,1), cellSize_, this);
      item->Init();

      /* add it to our scene */
      addItem(item);
    }
  }
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

  /* we'll also try to place the newly picked item into
   * the currently selected cells */
  try_place_knitting_symbol_();
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

  try_place_knitting_symbol_();
}



//------------------------------------------------------------
// rest a grid item to its original state, i.e., convert
// it back into empty single unit cells
//------------------------------------------------------------
void GraphicsScene::grid_item_reset(PatternGridItem* anItem)
{
  /* figure out where item is and how many cells it spans */
  QPoint origin(anItem->origin());
  QSize dim(anItem->dim());

  /* get rid of the old cell making sure that we punt if from
   * the set of activeItems if present */
  activeItems_.removeAll(anItem);
  removeItem(anItem);

  /* start filling the hole with new cells */
  int numNewCells = dim.width();
  for (int i = 0; i < numNewCells; ++i)
  {
    QPoint newOrigin(origin.x() + i*cellSize_, origin.y());
    PatternGridItem* item = 
      new PatternGridItem(newOrigin, QSize(1,1), cellSize_, this);
    item->Init();
    addItem(item);
  }
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


//--------------------------------------------------------------
// event handlers for key press and key release events
//--------------------------------------------------------------
void GraphicsScene::keyPressEvent(QKeyEvent* keyEvent)
{
  if (keyEvent->key() == Qt::Key_Shift)
  {
    shiftPressed_ = true;
  }

  QGraphicsScene::keyPressEvent(keyEvent);
}


void GraphicsScene::keyReleaseEvent(QKeyEvent* keyEvent)
{
  if (keyEvent->key() == Qt::Key_Shift)
  {
    shiftPressed_ = false;
  }

  QGraphicsScene::keyPressEvent(keyEvent);
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// this function tries to place the currently active
// knitting symbol into the selected pattern grid cells
//-------------------------------------------------------------
void GraphicsScene::try_place_knitting_symbol_()
{
  /* check how many cells we need for the currently selected
   * knitting symbol */
  QSize size = selectedSymbol_->dim();
  int cellsNeeded = size.width() * size.height();

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
    emit statusBar_message("Number of selected grid units does not "
        "match selected pattern size");
    return;
  }

  /* all items need to be in a single row */
  if ( yCoords.size() != 1 )
  {
    emit statusBar_message("The selected items have to be in a "
        "single row");
    return;
  }

  /* check if origins are adjacent */
  QList<int> dimOrigins = dims.keys();
  qSort(dimOrigins.begin(), dimOrigins.end());
  for (int i=0; i < dimOrigins.size()-1; ++i)
  {
    int expectedNeighborPos = dimOrigins[i] 
      + dims[dimOrigins[i]] * cellSize_;
    int actualNeighborPos = dimOrigins[i+1];
    if ( expectedNeighborPos != actualNeighborPos )
    {
      emit statusBar_message("The selected items have to be adjacent");
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
  PatternGridItem* item = 
    new PatternGridItem(newOrigin, QSize(totalWidth,1), 
      cellSize_, this);
  item->Init();
  addItem(item);

  /* place knitting symbol and purge previously active items */
  activeItems_.clear();
  item->insert_knitting_symbol(selectedSymbol_);

  /* clear StatusBar */
  emit statusBar_message("");
}

