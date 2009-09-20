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
#include <QGraphicsTextItem>
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
  controlPressed_(false),
  shiftPressed_(false),
  origin_(QPoint(0,0)),
  numCols_(0),
  numRows_(0),
  cellSize_(0),
  textFont_("Arial",8),
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
// accessor function for status of shift and control keys
//-------------------------------------------------------------
bool GraphicsScene::shift_pressed()
{
  return shiftPressed_;
}

bool GraphicsScene::control_pressed()
{
  return controlPressed_;
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

  /* grid */
  for (int col=0; col < numCols_; ++col)
  {
    for (int row=0; row < numRows_; ++row)
    {
      QPoint origin(origin_.x() +(col*cellSize_), 
                    origin_.y() +(row*cellSize_));
      PatternGridItem* item = 
        new PatternGridItem(origin, QSize(1,1), cellSize_, 
            col, row, this);
      item->Init();

      /* add it to our scene */
      addItem(item);
    }
  }

  /* grid labels
   * FIXME: placement of lables needs to become smarter */
  QString label;
  for (int col=0; col < numCols_; ++col)
  {
    QGraphicsTextItem* text= 
      new QGraphicsTextItem(label.setNum(col+1));
    int shift = compute_horizontal_label_shift_(col);
    text->setPos(origin_.x() + col*cellSize_ + shift, 
      origin_.y() - 2 * textFont_.pointSize());
    text->setFont(textFont_);
    addItem(text);
  }

  for (int row=0; row < numRows_; ++row)
  {
    QGraphicsTextItem* text= 
      new QGraphicsTextItem(label.setNum(row+1));
    text->setPos(origin_.x() - cellSize_, 
      origin_.y() + row * cellSize_ + textFont_.pointSize());
    text->setFont(textFont_);
    addItem(text);
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
  /* compute index based on row and col */
  int index = (anItem->row() * numCols_) + anItem->col();

  /* first update our list of currently selected items */
  if (status)
  {
    activeItems_[index]= anItem;
  }
  else
  {
    activeItems_.remove(index);
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
  int column = anItem->col();
  int row = anItem->row();

  /* get rid of the old cell making sure that we punt if from
   * the set of activeItems if present */
 // activeItems_.removeAll(anItem);
  removeItem(anItem);

  /* start filling the hole with new cells */
  int numNewCells = dim.width();
  for (int i = 0; i < numNewCells; ++i)
  {
    QPoint newOrigin(origin.x() + i*cellSize_, origin.y());
    PatternGridItem* item = 
      new PatternGridItem(newOrigin, 
                          QSize(1,1), 
                          cellSize_, 
                          column+i, 
                          row, 
                          this);
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
  switch(keyEvent->key())
  {
    case Qt::Key_Shift:
      shiftPressed_ = true;
      break;
    
    case Qt::Key_Control:
      controlPressed_ = true;
      break;

    default:
      break;
  }

  QGraphicsScene::keyPressEvent(keyEvent);
}


void GraphicsScene::keyReleaseEvent(QKeyEvent* keyEvent)
{
  switch(keyEvent->key())
  {
    case Qt::Key_Shift:
      shiftPressed_ = false;
      break;
    
    case Qt::Key_Control:
      controlPressed_ = false;
      break;

    default:
      break;
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
  int cellsNeeded = size.width(); // * size.height();

  if (cellsNeeded == 0)
  {
    return;
  }

  /* make sure the number of selected items is an integer multiple
   * of the required item size */
  if ( activeItems_.size() % cellsNeeded != 0 )
  {
    emit statusBar_message(tr("Number of selected cells is"
           "not a multiple of the pattern size"));
  }

  /* sort selected items row wise */
  QList<RowItems> rowList;
  bool sortStatus = sort_selected_items_row_wise_(rowList);
  if (!sortStatus)
  { 
    return;
  }

  /* check if each row has the proper arrangement of 
   * highlighted cells to fit the selected pattern item */
  QList<CellMask> replacementCells;
  bool finalStatus = process_selected_items_(replacementCells, 
    rowList, cellsNeeded);

  if (!finalStatus)
  {
    return;
  }


  /* delete previously highligthed cells */
  foreach(PatternGridItem* item, activeItems_.values())
  {
    removeItem(item);
  }
  activeItems_.clear();

  
  /* at this point all rows are in the proper shape to be
   * replaced by the current symbol */
  for (int row=0; row < replacementCells.size(); ++row)
  {
    for (int cell=0; cell < replacementCells.at(row).size(); ++cell)
    {
      int column = replacementCells.at(row)[cell].first;
      int aWidth  = replacementCells.at(row)[cell].second;

      PatternGridItem* item = new PatternGridItem (
          QPoint(origin_.x() + column * cellSize_, 
                 origin_.y() + row * cellSize_),
          QSize(aWidth,1),
          cellSize_,
          column,
          row,
          this);

      item->Init();
      item->insert_knitting_symbol(selectedSymbol_);
      addItem(item);
    }
  }
    
  /* clear StatusBar */
  emit statusBar_message("");
}


//-----------------------------------------------------------------
// compute the shift for horizontal labels so they are centered
// in each grid cell
//-----------------------------------------------------------------
int GraphicsScene::compute_horizontal_label_shift_(int aNum)
{
  double size = cellSize_ * 0.5;
  double numWidth = textFont_.pointSize() * 0.5;
  double count = 0;
  if (aNum < 10)
  {
    count = 1.5;
  }
  else if (aNum < 100)
  {
    count = 2.5;
  }
  else
  {
    count = 3;
  }

  return static_cast<int>(size - numWidth * count);
}


//----------------------------------------------------------------
// sort all currently selected cells in a row by row fashion
// returns true on success and false on failure
//----------------------------------------------------------------
bool GraphicsScene::sort_selected_items_row_wise_(
  QList<RowItems>& theRows)
{
  for (int i=0; i < numRows_; ++i)
  {
    RowItems tempList;
    theRows.push_back(tempList);
  }

  QMap<int, PatternGridItem*>::const_iterator iter = 
    activeItems_.constBegin();
  while (iter != activeItems_.constEnd()) 
  {
    int row = static_cast<int>(iter.key()/numCols_); 
    theRows[row].push_back(iter.value());
    ++iter;
  }

  return true;
}


//--------------------------------------------------------------
// check if each row has the proper arrangement of 
// highlighted cells to fit the selected pattern item and
// arrange highlighted cells in bunches of targetPatternSize
// NOTE: selectedPatternSize is expected to be non-zero
//--------------------------------------------------------------
bool GraphicsScene::process_selected_items_(
  QList<CellMask>& finalCellLayout, const QList<RowItems>& rowLayout, 
  int selectedPatternSize)
{
  for (int row=0; row < rowLayout.size(); ++row)
  {
    RowItems rowItem = rowLayout.at(row);

    int rowLength = 0;
    foreach(PatternGridItem* anItem, rowItem)
    {
      rowLength += (anItem->dim()).width();
    }
    
    /* if the rowLength is not divisible by cellsNeeded we
     * are done */
    if (rowLength % selectedPatternSize != 0)
    {
      emit statusBar_message(tr("Improper total number of cells."));
      return false;
    }

    CellMask cellBounds;
    foreach(PatternGridItem* anItem, rowItem)
    {
      int curStart = (anItem->col());
      int curWidth = (anItem->dim()).width();
      if (!cellBounds.empty())
      {
        int lastStart = cellBounds.back().first;
        int lastWidth = cellBounds.back().second;

        /* see if we are extending the last cell */
        if ( lastStart + lastWidth == curStart )
        {
          cellBounds.pop_back();
          cellBounds.push_back(
            QPair<int,int>(lastStart, lastWidth+curWidth));
        }
        else
        {
          cellBounds.push_back(QPair<int,int>(curStart, curWidth));
        }
      }
      else
      {
        cellBounds.push_back(QPair<int,int>(curStart, curWidth));
      }
    }

    
    /* generate row message String */
    QString rowIndex;
    rowIndex.setNum(row+1);
    QString rowMsg("row " + rowIndex + ": ");
   
    /* reorganize all blocks into multiples of selectedPatternSize */
    for (int i=0; i < cellBounds.size(); ++i)
    {
      int currentOrigin = cellBounds.at(i).first;
      int currentWidth = cellBounds.at(i).second;
      div_t multiple = div(currentWidth, selectedPatternSize);

      if (multiple.rem != 0)
      {
        emit statusBar_message(rowMsg + "non-matching block size");
        return false;
      }

      if (multiple.quot != 1)
      {
        for (int cell=0; cell < multiple.quot; ++cell)
        {
          cellBounds.push_back(QPair<int,int>(
              currentOrigin + cell*selectedPatternSize,
              selectedPatternSize));
        }
        cellBounds.removeAt(i);
      }
    }

    /* this row checks out */
    finalCellLayout.push_back(cellBounds);
  }

  return true;
}

