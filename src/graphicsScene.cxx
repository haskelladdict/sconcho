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
GraphicsScene::GraphicsScene(QObject* myParent)
  :
  QGraphicsScene(myParent),
  origin_(QPoint(0,0)),
  numCols_(0),
  numRows_(0),
  cellSize_(0),
  selectedColumn_(UNSELECTED),
  selectedRow_(UNSELECTED),
  textFont_("Arial",8),
  selectedSymbol_(
      KnittingSymbolPtr(new KnittingSymbol("","",QSize(0,0),"",""))),
  backgroundColor_(Qt::white),
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
      PatternGridItem* item = 
        new PatternGridItem(compute_cell_origin_(col, row), 
            QSize(1,1), cellSize_, col, row, this);
      item->Init();

      /* add it to our scene */
      addItem(item);
    }
  }

  /* grid labels
   * NOTE: In accordance with standard knitting practice
   *       the row/column count starts in the lower right
   *       corner.
   * FIXME: placement of lables needs to become smarter */
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

  

/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// this slots deletes selectedRow from the pattern grid array
//-------------------------------------------------------------
void GraphicsScene::delete_row_()
{
  if (selectedRow_ == UNSELECTED)
  {
    return;
  }

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

  /* unselect row */
  selectedRow_ = UNSELECTED;
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
  if (column == -1)
  {
    if (mouseEvent->button() == Qt::RightButton)
    {
      /* FIXME: manage_row calls the proper member function
       * via a signal and can't therefore provide the row
       * ID by itself which is why we have to use a silly
       * private variable. Is there any way we can avoid this? */
      selectedRow_ = row;
      manage_rows_(mouseEvent->screenPos(), row);
    }
    else
    {
      select_row_(row);
    }
  }
  else if (row == numRows_)
  {
    select_column_(column);
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
    emit statusBar_message(tr("Number of selected cells is"
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

      PatternGridItem* item = new PatternGridItem (
          compute_cell_origin_(column, row),  
          QSize(aWidth,1),
          cellSize_,
          column,
          row,
          this,
          cellColor);

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
      emit statusBar_message(tr("Improper total number of cells."));
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
        emit statusBar_message(rowMsg + "non-matching block size");
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
// selected color
//--------------------------------------------------------------
void GraphicsScene::colorize_highlighted_cells_()
{
   foreach(PatternGridItem* anItem, activeItems_)
   {
     anItem->select();
   }

   activeItems_.clear();
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
  QColor defaultColor(Qt::white);
  QList<PatternGridItem*> cells(activeItems_.values());

  if (cells.size() == 0)
  {
    return defaultColor;
  }

  QColor cellColor(cells.at(0)->color());
  foreach(PatternGridItem* anItem, cells)
  {
    if (anItem->color() != cellColor)
    {
      return defaultColor;
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

 // qDebug() << column << "&" << row;

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

  /* grab PatterGridItems and select them */
  foreach(QGraphicsItem* anItem, allItems)
  {
    PatternGridItem* cell = 
      qgraphicsitem_cast<PatternGridItem*>(anItem);
    if (cell != 0)
    {
      cell->select();
    }
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
void GraphicsScene::manage_rows_(const QPoint& pos, int rowID)
{
  /* open up a menu and connect the slots */
  QMenu rowMenu;
  QAction* deleteAction    = rowMenu.addAction("delete row");
  QAction* insertAction    = rowMenu.addAction("insert row");
  QAction* addTopAction    = rowMenu.addAction("add row at top");
  QAction* addBottomAction = rowMenu.addAction("add row at bottom");

  connect(deleteAction, SIGNAL(triggered()), 
          this, SLOT(delete_row_()));

  rowMenu.exec(pos);
}
  



