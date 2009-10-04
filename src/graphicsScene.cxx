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
#include <algorithm>
#include <vector>
#include <cmath>

/* Qt headers */
#include <QDebug>
#include <QGraphicsItem>
#include <QGraphicsItemGroup>
#include <QGraphicsLineItem>
#include <QGraphicsSceneMouseEvent>
#include <QGraphicsSceneWheelEvent>
#include <QGraphicsTextItem>
#include <QGraphicsView>
#include <QKeyEvent>
#include <QMenu>


/* local headers */
#include "basicDefs.h"
#include "graphicsScene.h"
#include "knittingSymbol.h"
#include "patternGridItem.h"
#include "patternGridLabel.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
GraphicsScene::GraphicsScene(const QPoint& anOrigin, 
    const QSize& gridDim, int aSize, QObject* myParent)
  :
  QGraphicsScene(myParent),
  origin_(anOrigin),
  numCols_(gridDim.width()),
  numRows_(gridDim.height()),
  cellSize_(aSize),
  selectedCol_(UNSELECTED),
  selectedRow_(UNSELECTED),
  textFont_("Arial",8),
  selectedSymbol_(
      KnittingSymbolPtr(new KnittingSymbol("","",QSize(0,0),"",""))),
  backgroundColor_(Qt::white),
  defaultColor_(Qt::white),
  wantColor_(false)
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

  /* build canvas */
  create_pattern_grid_();
  create_grid_labels_();

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
 
  connect(this,
          SIGNAL(statusBar_error(QString)),
          parent(),
          SLOT(show_statusBar_error(QString))
         );
 
  connect(this,
          SIGNAL(mouse_zoom_in()),
          parent(),
          SLOT(zoom_in()));

  connect(this,
          SIGNAL(mouse_zoom_out()),
          parent(),
          SLOT(zoom_out()));

  return true;
}


/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// accessor functions for properties
//-------------------------------------------------------------
const KnittingSymbolPtr GraphicsScene::get_selected_symbol()
{
  return selectedSymbol_;
}


const QColor& GraphicsScene::get_background_color()
{
  return backgroundColor_;
}


bool GraphicsScene::withColor()
{
  return wantColor_;
}


//-------------------------------------------------------------
// this function nukes the current pattern grid and creates
// a brand new one 
//-------------------------------------------------------------
void GraphicsScene::reset_grid(const QSize& newSize)
{
  purge_all_canvas_items_();

  /* generate new grid */
  numCols_ = newSize.width();
  numRows_ = newSize.height();
  create_pattern_grid_();
  create_grid_labels_();
  setSceneRect(itemsBoundingRect());
  foreach(QGraphicsView* aView, views())
  {
    aView->fitInView(itemsBoundingRect(),Qt::KeepAspectRatio);
  }
}



//-------------------------------------------------------------
// this function nukes the current pattern grid and creates
// a previous one as specified in the list of 
// PatterGridItemDescriptors.
//-------------------------------------------------------------
void GraphicsScene::reset_canvas(
    const QList<PatternGridItemDescriptor>& newItems)
{
  assert(newItems.size() != 0);

  purge_all_canvas_items_();

  int maxCol = 0;
  int maxRow = 0;
  foreach(PatternGridItemDescriptor anItem, newItems)
  {
    int col = anItem.location.x();
    int row = anItem.location.y();
   
    maxCol = int_max(col, maxCol);
    maxRow = int_max(row, maxRow);

    PatternGridItem* item = 
      new PatternGridItem(compute_cell_origin_(col, row), 
            anItem.dimension, cellSize_, col, row, this,
            anItem.backgroundColor);
    item->Init();

    /* add it to our scene */
    addItem(item);
  }
  
  /* adjust dimensions */
  numCols_ = maxCol + 1;
  numRows_ = maxRow + 1;

  /* add labels and rescale */
  create_grid_labels_();
  setSceneRect(itemsBoundingRect());
  foreach(QGraphicsView* aView, views())
  {
    aView->fitInView(itemsBoundingRect(),Qt::KeepAspectRatio);
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
// knitting symbol and they are adjacent we either try
// placing the symbol or color the cells.
//--------------------------------------------------------------
void GraphicsScene::grid_item_selected(PatternGridItem* anItem, 
    bool status)
{
  /* compute index based on row and col */
  int index = compute_cell_index_(anItem);

  /* first update our list of currently selected items */
  if (status)
  {
    activeItems_[index]= anItem;
  }
  else
  {
    activeItems_.remove(index);
  }

  /* if a knitting symbol is selected we try placing it,
   * otherwise we color the cells if requested */
  if (selectedSymbol_->path() != "")
  {
    try_place_knitting_symbol_();
  }
  else if (wantColor_)
  {
    colorize_highlighted_cells_();
  } 
}


//------------------------------------------------------------
//------------------------------------------------------------
void GraphicsScene::update_selected_background_color(
    const QColor& aColor)
{
  backgroundColor_ = aColor;
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



//-------------------------------------------------------------
// record if a user request coloring of cells or not
//-------------------------------------------------------------
void GraphicsScene::color_state_changed(int state)
{
  if (state == Qt::Checked)
  {
    wantColor_ = true;
    colorize_highlighted_cells_();
  }
  else
  {
    wantColor_ = false;
  }
}


//---------------------------------------------------------------
// deselects all items currenty marked as active
//---------------------------------------------------------------
void GraphicsScene::deselect_all_active_items()
{
  foreach(PatternGridItem* anItem, activeItems_)
  {
    anItem->select();
  }
  activeItems_.clear();
}



/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// this slots deletes selectedCol from the pattern grid array
// NOTE: delecting columns is a bit more tricky than deleting
// rows since we have to bail if the selected column has cells
// that span more than a single unit cell, i.e., columns.
//-------------------------------------------------------------
void GraphicsScene::delete_col_()
{
  assert(selectedCol_ >= 0);
  assert(selectedCol_ < numCols_);

  if (selectedCol_ == UNSELECTED)
  {
    return;
  }
  
  deselect_all_active_items();

  QList<QGraphicsItem*> allItems(items());
  QList<PatternGridItem*> gridItems;

  /* go through all items and make sure that the cells
   * of the selected rows are all unit cells and don't
   * span multiple columns */
  int targetColCounter = 0;
  foreach(QGraphicsItem* anItem, allItems)
  {
    PatternGridItem* cell = 
      qgraphicsitem_cast<PatternGridItem*>(anItem);

    if (cell != 0)
    {
      if (cell->col() == selectedCol_ &&
          cell->dim().width() == 1)
      {
        targetColCounter += 1;
      }
      
      gridItems.push_back(cell);
    }
  }
        
  /* if we have less than numRows_ in deletedColCounter there
   * was at least on multi column cell in the column */
  if ( targetColCounter < numRows_ )
  {
    emit statusBar_error("cannot delete columns with "
      "cells that span multiple columns");
    selectedCol_ = UNSELECTED;
    return;
  }


  /* go through all grid cells and
   * - delete the ones in the selectedRow_
   * - shift the ones in a row greater than selectedRow_
   *   up by one
   */
  foreach(PatternGridItem* cell, gridItems)
  {
    if (cell->col() == selectedCol_)
    {
      removeItem(cell);
    }
    else if (cell->col() > selectedCol_)
    {
      cell->reseat(
              compute_cell_origin_(cell->col() - 1, cell->row()),
              cell->col() - 1,
              cell->row());
    }
  }

  /* unselect row and update row counter */
  numCols_ = numCols_ - 1;
  selectedCol_ = UNSELECTED;

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect 
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect(itemsBoundingRect());
}


//-------------------------------------------------------------
// this slots deletes selectedRow from the pattern grid array
//-------------------------------------------------------------
void GraphicsScene::delete_row_()
{
  assert(selectedRow_ >= 0);
  assert(selectedRow_ < numRows_); 

  if (selectedRow_ == UNSELECTED)
  {
    return;
  }

  deselect_all_active_items();

  /* go through all grid cells and
   * - delete the ones in the selectedRow_
   * - shift the ones in a row greater than selectedRow_
   *   up by one
   */
  QList<QGraphicsItem*> allItems(items());
  foreach(QGraphicsItem* anItem, allItems)
  {
    PatternGridItem* cell = 
      qgraphicsitem_cast<PatternGridItem*>(anItem);

    if (cell != 0)
    {
      if (cell->row() == selectedRow_)
      {
        removeItem(cell);
      }
      else if (cell->row() > selectedRow_)
      {
        cell->reseat(
                compute_cell_origin_(cell->col(), cell->row()-1),
                cell->col(),
                cell->row() - 1);
      }
    }
  }

  /* unselect row and update row counter */
  numRows_ = numRows_ - 1;
  selectedRow_ = UNSELECTED;

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect 
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect(itemsBoundingRect());
}



//-------------------------------------------------------------
// insert new columns into grid
//-------------------------------------------------------------
void GraphicsScene::insert_left_of_col_()
{
  if (selectedCol_ == UNSELECTED)
  {
    return;
  }

  insert_col_(selectedCol_);
}


void GraphicsScene::insert_right_of_col_()
{
  if (selectedCol_ == UNSELECTED)
  {
    return;
  }

  insert_col_(selectedCol_ + 1);
}



void GraphicsScene::insert_col_(int aCol)
{
  deselect_all_active_items();

  /* go through all items and make sure that that
   * inserting the columns won't cut through any
   * multy row cells 
   * NOTE: The special case here is adding a column at the 
   * right or left of the pattern grid in which case we're 
   * always in good shape and the below test will actually
   * fail when adding at the right */
  if (aCol != 0 && aCol != numCols_)
  {
    int targetColCounter = 0;
    QList<QGraphicsItem*> allItems(items());
    foreach(QGraphicsItem* anItem, allItems)
    {
      PatternGridItem* cell = 
        qgraphicsitem_cast<PatternGridItem*>(anItem);

      if (cell != 0)
      {
        /* in order to make sure we won't cut through
         * a wide cell, we check if the origin of the cell
         * is in the current cell. If not, it will surely
         * start in the cell to the left and we would cut
         * it in this case */
        QPoint actualOrigin(cell->origin());
        QPoint neededOrigin(compute_cell_origin_(aCol, cell->row()));

        if (cell->col() == aCol && actualOrigin == neededOrigin )
        {
          targetColCounter += 1;
        }
      }
    }

    /* if we have less than numCols_ in deletedColCounter there
     * was at least on multi column cell in the column */
    if ( targetColCounter < numRows_ )
    {
      emit statusBar_error("cannot insert column in between "
          "cells that span multiple columns");
      selectedCol_ = UNSELECTED;
      return;
    }
  }


  /* expand the grid to make space */
  expand_grid_(aCol, NOSHIFT);


  /* now insert the new column */
  for (int row = 0; row < numRows_; ++row)
  {
    PatternGridItem* anItem = new PatternGridItem (
          compute_cell_origin_(aCol, row),  
          QSize(1,1),
          cellSize_,
          aCol,
          row,
          this,
          defaultColor_);

    anItem->Init();
    addItem(anItem);
  }


  /* unselect row and update row counter */
  selectedCol_ = UNSELECTED;

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect 
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect(itemsBoundingRect());
}


//-------------------------------------------------------------
// insert new rows into grid
//-------------------------------------------------------------
void GraphicsScene::insert_above_row_()
{
  if (selectedRow_ == UNSELECTED)
  {
    return;
  }

  insert_row_(selectedRow_ - 1);
}



void GraphicsScene::insert_below_row_()
{
  if (selectedRow_ == UNSELECTED)
  {
    return;
  }

  insert_row_(selectedRow_);
}



void GraphicsScene::insert_row_(int aRow)
{
  deselect_all_active_items();

  /* shift rows to make space */
  expand_grid_(NOSHIFT, aRow);

  /* now insert the new row */
  for (int column = 0; column < numCols_; ++column)
  {
    PatternGridItem* anItem = new PatternGridItem (
          compute_cell_origin_(column, aRow+1),  
          QSize(1,1),
          cellSize_,
          column,
          aRow+1,
          this,
          defaultColor_);

    anItem->Init();
    addItem(anItem);
  }


  /* unselect row and update row counter */
  selectedRow_ = UNSELECTED;

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect 
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect(itemsBoundingRect());
}


/**************************************************************
 *
 * PROTECTED 
 *
 *************************************************************/


//--------------------------------------------------------------
// event handler for mouse wheel events
//--------------------------------------------------------------
void GraphicsScene::wheelEvent(QGraphicsSceneWheelEvent* aWheelEvent)
{
  if (aWheelEvent->modifiers().testFlag(Qt::ControlModifier) 
      && aWheelEvent->delta() > 0)
  {
    emit mouse_zoom_in();
  }
  else if (aWheelEvent->modifiers().testFlag(Qt::ControlModifier)
           && aWheelEvent->delta() < 0)
  {
    emit mouse_zoom_out();
  }
}



//---------------------------------------------------------------
// event handler for mouse move events
//---------------------------------------------------------------
void GraphicsScene::mouseMoveEvent(
    QGraphicsSceneMouseEvent* mouseEvent)
{
  QPointF currentPos = mouseEvent->scenePos();

  /* let our parent know that we moved */
  emit mouse_moved(currentPos);

  return QGraphicsScene::mouseMoveEvent(mouseEvent);
}


//---------------------------------------------------------------
// event handler for mouse press events
//---------------------------------------------------------------
void GraphicsScene::mousePressEvent(
    QGraphicsSceneMouseEvent* mouseEvent)
{
  QPointF currentPos = mouseEvent->scenePos();
  QPair<int,int> index(get_cell_coords_(currentPos));

  /* if the user clicked on the index cells (the ones
   * the have the column/row numbers in them) we:
   *
   * - hightlight the whole row/cell if it is a left-click
   * - open a row/column delete/insert/add dialog if it is
   *   a right click 
   */
  int column = index.first;
  int row    = index.second;
  if (mouseEvent->button() == Qt::RightButton)
  {
    /* FIXME: manage_columns_rows_ calls the proper member function
     * via a signal and can't therefore provide the column/row
     * ID by itself which is why we have to use a silly
     * private variable. Is there any way we can avoid this?
     *
     * Also we show the menu only if we're inside the pattern
     * grid plus a margin of a single cellSize_ in all directions */
    if ( row > -1 || row < (numRows_ + 1) 
      || column > -1 || column < (numCols_ + 1) )
    { 
      selectedCol_ = column;
      selectedRow_ = row;
      manage_columns_rows_(mouseEvent->screenPos(), column, row);
    }
  }
  else
  {
    if (column == -1)
    {
      qDebug() << "select row " << row;
      select_row_(row);
    }
    else if (row == numRows_)
    {
      qDebug() << "select column " << column;
      select_column_(column);
    }
  }

  return QGraphicsScene::mousePressEvent(mouseEvent);
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
    emit statusBar_error(tr("Number of selected cells is"
           "not a multiple of the pattern size"));
  }

  /* try to come up with a proper color for the cells to
   * be replaced */
  QColor cellColor = determine_selected_cells_color_();

  /* sort selected items row wise */
  QList<RowItems> rowList;
  bool sortStatus = sort_selected_items_row_wise_(rowList);
  if (!sortStatus)
  { 
    return;
  }

  /* check if each row has the proper arrangement of 
   * highlighted cells to fit the selected pattern item */
  QList<RowLayout> replacementCells;
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

      PatternGridItem* anItem = new PatternGridItem (
          compute_cell_origin_(column, row),  
          QSize(aWidth,1),
          cellSize_,
          column,
          row,
          this,
          cellColor);

      anItem->Init();
      anItem->insert_knitting_symbol(selectedSymbol_);
      addItem(anItem);
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
    count = 2.0;
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
  QList<RowLayout>& finalCellLayout, const QList<RowItems>& rowLayout, 
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
      emit statusBar_error(tr("Improper total number of cells."));
      return false;
    }

    RowLayout cellBounds;
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
 
    RowLayout finalCells;
    /* reorganize all blocks into multiples of selectedPatternSize */
    for (int i=0; i < cellBounds.size(); ++i)
    {
      int currentOrigin = cellBounds.at(i).first;
      int currentWidth = cellBounds.at(i).second;

      div_t multiple = div(currentWidth, selectedPatternSize);
      if (multiple.rem != 0)
      {
        emit statusBar_error(rowMsg + "non-matching block size");
        return false;
      }

      if (multiple.quot != 1)
      {
        for (int cell=0; cell < multiple.quot; ++cell)
        {
          finalCells.push_back(QPair<int,int>(
              currentOrigin + cell*selectedPatternSize,
              selectedPatternSize));
        }
      }
      else
      {
        finalCells.push_back(cellBounds.at(i));
      }
    }

    /* this row checks out */
    finalCellLayout.push_back(finalCells);
  }

  return true;
}



//--------------------------------------------------------------
// color all highlighted cells in the presently currently
// selected color. In reality, this really boils down to
// deselecting them all since they will pick up the current
// highlight color in the process :)
//--------------------------------------------------------------
void GraphicsScene::colorize_highlighted_cells_()
{
  deselect_all_active_items();
}



//--------------------------------------------------------------
// when placing knitting symbols in selected cells we try
// to preserve the current cell colors. This is tricky since
// there could be cases in which a several cell wide symbol
// spans unit cells with multiple colors. Hence, for now we
// only do one of two things
//
// 1) If all selected cells have the same color with pick it
// 2) Otherwise we use the default color, Qt::white
//--------------------------------------------------------------
QColor GraphicsScene::determine_selected_cells_color_()
{
  QList<PatternGridItem*> cells(activeItems_.values());

  if (cells.size() == 0)
  {
    return defaultColor_;
  }

  QColor cellColor(cells.at(0)->color());
  foreach(PatternGridItem* anItem, cells)
  {
    if (anItem->color() != cellColor)
    {
      return defaultColor_;
    }
  }

  return cellColor;
}



//--------------------------------------------------------------
// given a point on the canvas, determines which column/row the
// click was in. 
// NOTE: the point does not have to be in the actual pattern
// grid and the caller is responsible to make sense out of
// what ever column/row pair it receives
//---------------------------------------------------------------
QPair<int,int> GraphicsScene::get_cell_coords_(
    const QPointF& mousePos)
{
  qreal xPosRel = mousePos.x() - origin_.x();
  qreal yPosRel = mousePos.y() - origin_.y();

  int column = static_cast<int>(floor(xPosRel/cellSize_));
  int row    = static_cast<int>(floor(yPosRel/cellSize_));

  return QPair<int,int>(column,row);
}
 


//-------------------------------------------------------------
// activate a complete row
// In order to accomplish this we create a rectangle that 
// covers all cells in the row, then get all the items and
// the select them all. 
// NOTE: This is simular to what we do with the RubberBand.
//-------------------------------------------------------------
void GraphicsScene::select_row_(int rowId)
{
  /* selector box dimensions */
  int shift    = static_cast<int>(cellSize_*0.25);
  int halfCell = static_cast<int>(cellSize_*0.5);

  QPoint boxOrigin(origin_.x() + shift,
                   rowId * cellSize_ + shift);

  QSize boxDim((numCols_ - 1) * cellSize_ + halfCell, halfCell);

  /* select items */
  select_region_(QRect(boxOrigin, boxDim));
}



//-------------------------------------------------------------
// activate a complete column
// In order to accomplish this we create a rectangle that 
// covers all cells in the column, then get all the items and
// the select them all. 
// NOTE: This is simular to what we do with the RubberBand.
//-------------------------------------------------------------
void GraphicsScene::select_column_(int colId)
{
  /* selector box dimensions */
  int shift    = static_cast<int>(cellSize_*0.25);
  int halfCell = static_cast<int>(cellSize_*0.5);

  QPoint boxOrigin(colId * cellSize_ + shift, shift);
  QSize boxDim(halfCell, (numRows_ - 1) * cellSize_ + halfCell);

  /* select items */
  select_region_(QRect(boxOrigin, boxDim));
}


//--------------------------------------------------------------
// select all PatterGridItems in the region enclosed by
// the Rectangle
//--------------------------------------------------------------
void GraphicsScene::select_region_(const QRect& aRegion)
{
  QList<QGraphicsItem*> allItems(items(aRegion));

  /* grab PatterGridItems and select them 
   * NOTE: We can not just select the cells as we find
   * them among all items since their order is arbitrary
   * causing the selected area to be filled improperly
   * for larger symbols (just like randomly selecting
   * cells in the region would). Hence we sort all cells
   * first by index and then select them in order */
  QMap<int,PatternGridItem*> gridItems;
  foreach(QGraphicsItem* anItem, allItems)
  {
    PatternGridItem* cell = 
      qgraphicsitem_cast<PatternGridItem*>(anItem);
    if (cell != 0)
    {
      int cellIndex = compute_cell_index_(cell);
      gridItems[cellIndex] = cell;
    }
  }

  QList<PatternGridItem*> sortedItems(gridItems.values());
  foreach(PatternGridItem* cell, sortedItems)
  {
    cell->select();
  }
}



//----------------------------------------------------------------
// compute the origin of a grid cell based on its column and
// row index
//----------------------------------------------------------------
QPoint GraphicsScene::compute_cell_origin_(int col, int row) const
{
  return QPoint(origin_.x() + col * cellSize_, 
                origin_.y() + row * cellSize_);
}



//-----------------------------------------------------------------
// compute the index of a given cell based on its present row
// and column
//-----------------------------------------------------------------
int GraphicsScene::compute_cell_index_(PatternGridItem* anItem) const
{
  return (anItem->row() * numCols_) + anItem->col();
}


//-----------------------------------------------------------------
// this function is responsible for opening up a dialog allowing
// the user to delete/insert/add rows and initiates the necessary
// steps according to the selection
//-----------------------------------------------------------------
void GraphicsScene::manage_columns_rows_(const QPoint& pos, 
    int colID, int rowID)
{
  QMenu colRowMenu;

  /* show menu only if we're inside the pattern grid */
  if (colID >= 0 && colID < numCols_ &&
      rowID >= 0 && rowID < numRows_)
  {
    /* column related entries */
    QString colString;
    colString.setNum(numCols_ - colID);

    QAction* colDeleteAction = 
      colRowMenu.addAction("delete column " + colString);
    QAction* colInsertLeftOfAction = 
      colRowMenu.addAction("insert left of column " + colString);
    QAction* colInsertRightOfAction = 
      colRowMenu.addAction("insert right of column " + colString);
    
    connect(colDeleteAction, SIGNAL(triggered()), 
      this, SLOT(delete_col_()));
    connect(colInsertLeftOfAction, SIGNAL(triggered()),
      this, SLOT(insert_left_of_col_()));
    connect(colInsertRightOfAction, SIGNAL(triggered()),
      this, SLOT(insert_right_of_col_()));

    colRowMenu.addSeparator();
 
    /* row related entries */
    QString rowString;
    rowString.setNum(numRows_ - rowID);

    QAction* rowDeleteAction = 
      colRowMenu.addAction("delete row " + rowString);
    QAction* rowInsertAboveAction = 
      colRowMenu.addAction("insert above row " + rowString);
    QAction* rowInsertBelowAction = 
      colRowMenu.addAction("insert below row " + rowString);

    connect(rowDeleteAction, SIGNAL(triggered()), 
        this, SLOT(delete_row_()));
    connect(rowInsertAboveAction, SIGNAL(triggered()),
        this, SLOT(insert_above_row_()));
    connect(rowInsertBelowAction, SIGNAL(triggered()),
        this, SLOT(insert_below_row_()));

    colRowMenu.exec(pos);
  }
}
  

//-------------------------------------------------------------
// create the grid
//-------------------------------------------------------------
void GraphicsScene::create_pattern_grid_()
{
  /* grid */
  for (int col=0; col < numCols_; ++col)
  {
    for (int row=0; row < numRows_; ++row)
    {
      PatternGridItem* item = 
        new PatternGridItem(compute_cell_origin_(col, row), 
            QSize(1,1), cellSize_, col, row, this);
      item->Init();

      /* add it to our scene */
      addItem(item);
    }
  }
}



//-------------------------------------------------------------
// create or update the column labels
//-------------------------------------------------------------
void GraphicsScene::create_grid_labels_()
{
  /* remove all existing labels if there are any */
  QList<QGraphicsItem*> allItems(items());
  foreach(QGraphicsItem* aLabel, allItems)
  {
    PatternGridLabel* label = 
      qgraphicsitem_cast<PatternGridLabel*>(aLabel);

    if (label != 0)
    {
      removeItem(label);
    }
  }  


  /* add new column labels */
  QString label;
  qreal yPos = origin_.y() + numRows_ * cellSize_ + 1; 
  for (int col=0; col < numCols_; ++col)
  {
    int colNum = numCols_ - col;
    PatternGridLabel* text= new PatternGridLabel(
        label.setNum(colNum), 
        PatternGridLabel::ColLabel
        );

    int shift = compute_horizontal_label_shift_(colNum);
    text->setPos(origin_.x() + col*cellSize_ + shift, yPos); 
    text->setFont(textFont_);
    addItem(text);
  }


  /* add new row labels */
  for (int row=0; row < numRows_; ++row)
  {
    PatternGridLabel* text= new PatternGridLabel(
        label.setNum(numRows_ - row),
        PatternGridLabel::RowLabel
        );

    text->setPos(origin_.x() - cellSize_, 
      origin_.y() + row * cellSize_ + textFont_.pointSize());
    text->setFont(textFont_);
    addItem(text);
  }
}



//---------------------------------------------------------------
// shift the pattern grid by one column and/or row wise starting
// at the specified column and row indices.
// This is mainly used when inserting/deleting columns/rows
//--------------------------------------------------------------
void GraphicsScene::expand_grid_(int colPivot, int rowPivot)
{
  QList<QGraphicsItem*> allItems(items());

  /* go through all items and make sure that that
   * inserting the columns won't cut through any
   * multy row cells */
  foreach(QGraphicsItem* anItem, allItems)
  {
    PatternGridItem* cell = 
      qgraphicsitem_cast<PatternGridItem*>(anItem);

    if (cell != 0)
    {
      /* do we want to shift the columns */
      if (colPivot != NOSHIFT)
      {
        if (cell->col() >= colPivot)
        {
          cell->reseat(
                  compute_cell_origin_(cell->col() + 1, cell->row()),
                  cell->col() + 1,
                  cell->row());
        }
      }

      /* do we want to shift the rows */
      if (rowPivot != NOSHIFT)
      {
        if (cell->row() > rowPivot)
        {
          cell->reseat(
                  compute_cell_origin_(cell->col(), cell->row()+1),
                  cell->col(),
                  cell->row() + 1);
        }
      }
    }
  }

  /* adjust the row/col count */
  if (colPivot != NOSHIFT)
  {
    numCols_ += 1;
  }

  if (rowPivot != NOSHIFT)
  {
    numRows_ += 1;
  }
}


//---------------------------------------------------------------
// remove all items on canvas 
//---------------------------------------------------------------
void GraphicsScene::purge_all_canvas_items_()
{
  QList<QGraphicsItem*> allItems(items());
  foreach(QGraphicsItem* anItem, allItems)
  {
    removeItem(anItem);
  }
}


