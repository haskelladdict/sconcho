/***************************************************************
*
* (c) 2009-2010 Markus Dittrich 
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
#include <cmath>

/* Qt headers */
#include <QDebug>
#include <QFont>
#include <QFontMetrics>
#include <QGraphicsItem>
#include <QGraphicsItemGroup>
#include <QGraphicsLineItem>
#include <QGraphicsSceneMouseEvent>
#include <QGraphicsSceneWheelEvent>
#include <QGraphicsTextItem>
#include <QGraphicsSvgItem>
#include <QGraphicsView>
#include <QKeyEvent>
#include <QMenu>
#include <QSettings>
#include <QSignalMapper>

/* local headers */
#include "basicDefs.h"
#include "graphicsScene.h"
#include "helperFunctions.h"
#include "knittingSymbol.h"
#include "legendItem.h"
#include "legendLabel.h"
#include "mainWindow.h"
#include "patternGridItem.h"
#include "patternGridLabel.h"
#include "patternGridRectangle.h"
#include "patternGridRectangleDialog.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
GraphicsScene::GraphicsScene(const QPoint& anOrigin, 
    const QSize& gridDim, int aSize, const QSettings& aSetting,
    KnittingSymbolPtr defaultSymbol, MainWindow* myParent)
  :
  QGraphicsScene(myParent),
  updateActiveItems_(true),
  origin_(anOrigin),
  numCols_(gridDim.width()),
  numRows_(gridDim.height()),
  cellSize_(aSize),
  selectedCol_(UNSELECTED),
  selectedRow_(UNSELECTED),
  settings_(aSetting),
  selectedSymbol_(emptyKnittingSymbol),
  defaultSymbol_(defaultSymbol),
  backgroundColor_(Qt::white),
  defaultColor_(Qt::white),
  legendIsVisible_(false)
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
  return true;
}


/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// this function nukes the current pattern grid and creates
// a brand new one 
//-------------------------------------------------------------
void GraphicsScene::reset_grid(const QSize& newSize)
{
  reset_canvas_();

  /* generate new grid */
  numCols_ = newSize.width();
  numRows_ = newSize.height();
  create_pattern_grid_();
  create_grid_labels_();
}



//-------------------------------------------------------------
// this function is called after a previously saved sconcho
// project file has been read in. It nukes the present pattern
// and re-creates the previously saved one.
//-------------------------------------------------------------
void GraphicsScene::load_new_canvas(
    const QList<PatternGridItemDescriptorPtr>& newItems)
{
  assert(newItems.size() != 0);
  reset_canvas_();

  int maxCol = 0;
  int maxRow = 0;
  foreach(PatternGridItemDescriptorPtr rawItem, newItems)
  {
    int col = rawItem->location.x();
    int row = rawItem->location.y();
    
    maxCol = qMax(col, maxCol);
    maxRow = qMax(row, maxRow);

    PatternGridItem* item = 
        new PatternGridItem(rawItem->dimension, cellSize_, col, row, 
          this, rawItem->backgroundColor);
    item->Init();
    item->setPos(compute_cell_origin_(col, row));
    item->insert_knitting_symbol(rawItem->patternSymbolPtr);

    /* add it to our scene */
    add_patternGridItem_(item);
  }
  
  /* adjust dimensions */
  numCols_ = maxCol + 1;
  numRows_ = maxRow + 1;

  /* add labels and rescale */
  create_grid_labels_();
}



//-------------------------------------------------------------
// this function is called after a previously saved sconcho
// project file has been read in. It places the legend items
// at their previously saved locations on the canvas.
// NOTE: This function has to be called after load new canvas
//-------------------------------------------------------------
void GraphicsScene::place_legend_items(
  const QList<LegendEntryDescriptorPtr>& newLegendEntries)
{
  assert(newLegendEntries.size() != 0);

  foreach(LegendEntryDescriptorPtr entryDesc, newLegendEntries)
  {
    /* find the legend entry by entryID */
    QString entryID = entryDesc->entryID;
    LegendEntry entry = legendEntries_[entryID];

    /* position item and label */
    QPointF itemPos = entryDesc->itemLocation;
    QPointF labelPos = entryDesc->labelLocation;

    entry.first->setPos(itemPos);
    entry.second->setPos(labelPos);

    /* set label text and update our presently stored text */
    QString labelText = entryDesc->labelText;
    entry.second->setPlainText(labelText);
    symbolDescriptors_[entryID] = labelText;
  }
}




//--------------------------------------------------------------
// this function takes care of resetting the canvas, i.e.,
// deleting items, cleaning up data structures 
//--------------------------------------------------------------
void GraphicsScene::reset_canvas_()
{
  purge_all_canvas_items_();
  purge_legend_();

  
  /* reset all views containting us */
  foreach(QGraphicsView* aView, views())
  {
    aView->resetMatrix();
  }
}


//--------------------------------------------------------------
// select all PatterGridItems in the region enclosed by
// the Rectangle.
//
// NOTE: The reason for the QRectF instead of QRect is
// that we need to call this function from the PatternView
// in which case we only have a QRectF available. All the
// QRect passed in inside GraphicsScene should cast
// fine into a QRectF so thats probably an ok think to do.
//--------------------------------------------------------------
void GraphicsScene::select_region(const QRectF& aRegion)
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

  /* disable canvas update until we're done selecting,
   * then we update and re-enable*/
  disable_canvas_update_();

  QList<PatternGridItem*> sortedItems(gridItems.values());
  foreach(PatternGridItem* cell, sortedItems)
  {
    cell->select();
  }

  update_active_items_();
  enable_canvas_update_();
}



//----------------------------------------------------------------
// hide all but the legend items
//----------------------------------------------------------------
void GraphicsScene::hide_all_but_legend()
{
  /* get list of all items that are not part of the legend
   * and are not svg items */
  QList<QGraphicsItem*> allItems = items();

  /* disable all non-legend items */
  foreach (QGraphicsItem* anItem, allItems)
  {
    QGraphicsSvgItem* svgItem =
      qgraphicsitem_cast<QGraphicsSvgItem*>(anItem);

    if(!svgItem)
    {
      anItem->hide();
    }
  }

  /* show legend items */
  foreach (QGraphicsItem* anItem, get_list_of_legend_items_())
  {
    anItem->show();
  }
}


//---------------------------------------------------------------
// show all items on the canvas
//---------------------------------------------------------------
void GraphicsScene::show_all_items()
{
  foreach (QGraphicsItem* anItem, items())
  {
    anItem->show();
  }
}


//-------------------------------------------------------------
// compute the rectangle on the canvas which is currently
// visible depending on if the legend is turned on or not
//-------------------------------------------------------------
QRectF GraphicsScene::get_visible_area() const
{
  /* get dimensions of pattern grid which never extends
   * above and right of the origin (0,0) */
  int xMaxPatternGrid = (numCols_ + 1) * cellSize_;
  int yMaxPatternGrid = (numRows_ + 1) * cellSize_;
  
  QPointF upperLeft(0.0,0.0);
  QPointF lowerRight(xMaxPatternGrid, yMaxPatternGrid);

  /* if the legend is also visible we need to take it
   * into account */
  if (legendIsVisible_)
  {
    QList<QGraphicsItem*> allLegendItems(get_list_of_legend_items_());
    QRectF legendBounds(get_bounding_rect(allLegendItems));

    /* adjust dimensions given by pattern grid */
    if (legendBounds.left() < upperLeft.x())
    {
      upperLeft.setX(legendBounds.left());
    }

    if (legendBounds.top() < upperLeft.y())
    {
      upperLeft.setY(legendBounds.top());
    }

    if (legendBounds.right() > lowerRight.x())
    {
      lowerRight.setX(legendBounds.right());
    }

    if (legendBounds.bottom() > lowerRight.y())
    {
      lowerRight.setY(legendBounds.bottom());
    }
  }

  return QRectF(upperLeft, lowerRight);
}


//----------------------------------------------------------------
// compute the center of the pattern grid
//----------------------------------------------------------------
QPoint GraphicsScene::get_grid_center() const
{
  int centerRow = static_cast<int>(numRows_/2.0);
  int centerCol = static_cast<int>(numCols_/2.0);

  QPoint theCenter = compute_cell_origin_(centerRow, centerCol);
  
  /* shift by half a cell if the number of rows and/or cells
   * is uneven */
  if (numCols_ % 2 != 0)
  {
    theCenter.setX(theCenter.x() + cellSize_/2.0);
  }

  if (numRows_ % 2 != 0)
  {
    theCenter.setY(theCenter.y() + cellSize_/2.0);
  }

  return theCenter;
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
  update_active_items_();
}


//-------------------------------------------------------------
// update the present list of grid items; if the number of
// selected items matches the number we need based on the
// knitting symbol and they are adjacent we either try
// placing the symbol or color the cells.
//
// NOTE: placement can be temporarty disabled, e.g., if we are 
// selecting a whole range of items (e.g., via rubberband or 
// row/column wise) in order to avoid premature placement of
// knitting symbols that don't really fit into the total
// available space.
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

  if (updateActiveItems_)
  {
    update_active_items_();
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
  remove_patternGridItem_(anItem);

  /* start filling the hole with new cells */
  int numNewCells = dim.width();
  for (int i = 0; i < numNewCells; ++i)
  {
    PatternGridItem* item = 
      new PatternGridItem(QSize(1,1), 
                          cellSize_, 
                          column+i, 
                          row, 
                          this);
    item->Init();
    item->insert_knitting_symbol(defaultSymbol_);
    item->setPos(compute_cell_origin_(column+i,row));
    add_patternGridItem_(item);
  }

  /* make sure to delect all items since the current item
   * may have been part of the active items */
  deselect_all_active_items();
}


//---------------------------------------------------------------
// deselects all items currenty marked as active
//---------------------------------------------------------------
void GraphicsScene::deselect_all_active_items()
{
  disable_canvas_update_();
  foreach(PatternGridItem* anItem, activeItems_)
  {
    anItem->select();
  }
  activeItems_.clear();
  enable_canvas_update_();
}


//-------------------------------------------------------------
// this slot requests that all currently active grid cells
// be surrounded by a rectangle
//-------------------------------------------------------------
void GraphicsScene::mark_active_cells_with_rectangle() 
{
  if (activeItems_.empty())
  {
    emit statusBar_error("Nothing selected");
    return;
  }

  /* first make sure the user selected a complete rectangle */
  QList<RowItems> rowList;
  sort_active_items_row_wise_(rowList);

  /* remove the top and bottom empty rows */
  while (rowList.first().empty())
  {
    rowList.pop_front();
  }

  while (rowList.last().empty())
  {
    rowList.pop_back();
  }
  assert(!rowList.empty());

  QPair<bool,int> initialStatus = is_row_contiguous_(rowList.at(0));
  bool status = initialStatus.first;
  for(int index = 1; index < rowList.size(); ++index)
  {
    QPair<bool,int> currentStatus = 
      is_row_contiguous_(rowList.at(index));
    if (currentStatus != initialStatus)
    {
      status = false;
    }
  }

  if (!status)
  {
    emit statusBar_error("Selected cells don't form a rectangle");
    return;
  }

  /* find bounding rectangle and create rectangle */
  QRect boundingRect = find_bounding_rectangle_(rowList);

  /* fire up dialog for customizing pattern grid rectangles */
  PatternGridRectangleDialog rectangleDialog; 
  rectangleDialog.Init();
  QPen rectanglePen = rectangleDialog.pen();

  PatternGridRectangle* marker = new PatternGridRectangle(boundingRect,
      rectanglePen);
  marker->Init();
  marker->setZValue(1.0);
  addItem(marker);
  deselect_all_active_items();
}


//------------------------------------------------------------
// update our current canvas after a change in settings
//------------------------------------------------------------
void GraphicsScene::update_after_settings_change()
{
  create_grid_labels_();
  update_legend_labels_();
}


//-------------------------------------------------------------
// shows or hides legend items depending on their current
// state
//-------------------------------------------------------------
void GraphicsScene::toggle_legend_visibility() 
{
  if (legendIsVisible_)
  {
    foreach(LegendEntry item, legendEntries_)
    {
      item.first->hide();
      item.second->hide();
    }
    legendIsVisible_ = false;
  }
  else
  {
    foreach(LegendEntry item, legendEntries_)
    {
      item.first->show();
      item.second->show();
    }
    legendIsVisible_ = true;

    emit show_whole_scene();
  }
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
      remove_patternGridItem_(cell);
    }
    else if (cell->col() > selectedCol_)
    {
      cell->reseat(cell->col() - 1, cell->row());
      cell->setPos(compute_cell_origin_(cell->col(), cell->row()));
    }
  }

  /* update position of legend items */
  shift_legend_items_horizontally_(selectedCol_, -cellSize_);

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
   *
   * Important: We can't just delete as we go since 
   * this also nukes the svg item children which 
   * we are also iterating over
   */
  QList<QGraphicsItem*> allItems(items());
  QList<PatternGridItem*> patternItems;
  foreach(QGraphicsItem* anItem, allItems)
  {
    PatternGridItem* cell = 
      qgraphicsitem_cast<PatternGridItem*>(anItem);
    
    if (cell != 0)
    {
      patternItems.push_back(cell);
    }
  }

  foreach(PatternGridItem* patItem, patternItems)
  {
    if (patItem->row() == selectedRow_)
    {
      remove_patternGridItem_(patItem);
    }
    else if (patItem->row() > selectedRow_)
    {
      patItem->reseat(patItem->col(), patItem->row() - 1);
      patItem->setPos(
        compute_cell_origin_(patItem->col(), patItem->row()));
    }
  }

  /* update position of legend items */
  shift_legend_items_vertically_(selectedRow_, -cellSize_);

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
        QPointF actualOrigin(cell->scenePos());
        QPointF neededOrigin(compute_cell_origin_(aCol, cell->row()));

        /* FIXME: we shouldn't be comparing QPointFs !!! */
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
          QSize(1,1),
          cellSize_,
          aCol,
          row,
          this,
          defaultColor_);

    anItem->Init();
    anItem->setPos(compute_cell_origin_(aCol, row));  
    add_patternGridItem_(anItem);
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
          QSize(1,1),
          cellSize_,
          column,
          aRow+1,
          this,
          defaultColor_);

    anItem->Init();
    anItem->setPos(compute_cell_origin_(column, aRow+1)); 
    add_patternGridItem_(anItem);
  }


  /* unselect row and update row counter */
  selectedRow_ = UNSELECTED;

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect 
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect(itemsBoundingRect());
}



//--------------------------------------------------------------
// this slot marks a pattern grid rectangle for deletion
// FIXME: The casting is a bit nasty - can we get rid of it.
// Since this SLOT is filled via a signal we can only
// deliver a QObject via QSignalMapper
//--------------------------------------------------------------
void GraphicsScene::mark_rectangle_for_deletion_(QObject* rectObj) 
{ 
    PatternGridRectangle* rect = 
      qobject_cast<PatternGridRectangle*>(rectObj);
    removeItem(rect);
    rect->deleteLater();
}


//--------------------------------------------------------------
// this slot fires up a customization dialog to change the
// properties of the selected rectangle 
// FIXME: The casting is a bit nasty - can we get rid of it.
// Since this SLOT is filled via a signal we can only
// deliver a QObject via QSignalMapper
//--------------------------------------------------------------
void GraphicsScene::customize_rectangle_(QObject* rectObj) 
{ 
  PatternGridRectangle* rect = 
    qobject_cast<PatternGridRectangle*>(rectObj);

  PatternGridRectangleDialog rectangleDialog; 
  rectangleDialog.Init();
  QPen rectanglePen = rectangleDialog.pen();

  rect->set_pen(rectanglePen);
}


//-------------------------------------------------------------
// this slot update the text we store for a particular
// legend label
//-------------------------------------------------------------
void GraphicsScene::update_key_label_text_(QString labelID, 
  QString newLabelText)
{
  symbolDescriptors_[labelID] = newLabelText;
}



/**************************************************************
 *
 * PROTECTED 
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

  return QGraphicsScene::mouseMoveEvent(mouseEvent);
}


//---------------------------------------------------------------
// event handler for mouse press events
//---------------------------------------------------------------
void GraphicsScene::mousePressEvent(
    QGraphicsSceneMouseEvent* mouseEvent)
{
  if (mouseEvent->button() == Qt::RightButton)
  {
    bool handled = handle_click_on_marker_rectangle_(mouseEvent);

    if (!handled)
    {
      handle_click_on_grid_array_(mouseEvent);
    }
  }
  else
  {
    handle_click_on_grid_labels_(mouseEvent);
  }

  return QGraphicsScene::mousePressEvent(mouseEvent);
}



/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// this function goes through all active items and changes
// the color of each on to the one that is currently
// selected.
//-------------------------------------------------------------
void GraphicsScene::change_selected_cells_colors_()
{
  foreach(PatternGridItem* item, activeItems_)
  {
    /* remove us from the legend */
    notify_legend_of_item_removal_(item);
    
    item->set_background_color(backgroundColor_);

    /* re-add newly colored symbol to the legend */
    notify_legend_of_item_addition_(item);
    
  }

  deselect_all_active_items();
}


  
//-------------------------------------------------------------
// this function tries to place the currently active
// knitting symbol into the selected pattern grid cells
//-------------------------------------------------------------
void GraphicsScene::try_place_knitting_symbol_()
{
  /* check how many cells we need for the currently selected
   * knitting symbol */
  QSize size = selectedSymbol_->dim();
  int cellsNeeded = size.width(); 

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

  /* sort selected items row wise */
  QList<RowItems> rowList;
  bool sortStatus = sort_active_items_row_wise_(rowList);
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
  QList<PatternGridItem*> deadItems(activeItems_.values()); 
  foreach(PatternGridItem* item, deadItems)
  {
    remove_patternGridItem_(item);
  }


  /* at this point all rows are in the proper shape to be
   * replaced by the current symbol */
  for (int row=0; row < replacementCells.size(); ++row)
  {
    for (int cell=0; cell < replacementCells.at(row).size(); ++cell)
    {
      int column = replacementCells.at(row)[cell].first;
      int aWidth  = replacementCells.at(row)[cell].second;

      PatternGridItem* anItem = new PatternGridItem (
          QSize(aWidth,1),
          cellSize_,
          column,
          row,
          this,
          backgroundColor_);

      anItem->Init();
      anItem->insert_knitting_symbol(selectedSymbol_);
      anItem->setPos(compute_cell_origin_(column, row));  
      add_patternGridItem_(anItem);
    }
  }

  /* clear selection */
  activeItems_.clear();
}


//-----------------------------------------------------------------
// compute the shift for horizontal labels so they are centered
// in each grid cell
//-----------------------------------------------------------------
int GraphicsScene::compute_horizontal_label_shift_(int aNum, 
    int fontSize) const
{
  double size = cellSize_ * 0.5;
  double numWidth = fontSize * 0.5;
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
bool GraphicsScene::sort_active_items_row_wise_(
  QList<RowItems>& theRows) const
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
  /* if coloring is selected we set the color of all
   * curently active Items */
  QList<PatternGridItem*> patternItems(activeItems_.values());
  foreach(PatternGridItem* anItem, patternItems)
  {
    anItem->set_background_color(backgroundColor_);
  }
}


//--------------------------------------------------------------
// given a point on the canvas, determines which column/row the
// click was in. 
// NOTE: the point does not have to be in the actual pattern
// grid and the caller is responsible to make sense out of
// what ever column/row pair it receives
//---------------------------------------------------------------
QPair<int,int> GraphicsScene::get_cell_coords_(
    const QPointF& mousePos) const
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

  select_region(QRect(boxOrigin, boxDim));
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
  select_region(QRect(boxOrigin, boxDim));
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

    connect(rowDeleteAction, 
            SIGNAL(triggered()), 
            this, 
            SLOT(delete_row_())
           );

    connect(rowInsertAboveAction, 
            SIGNAL(triggered()),
            this, 
            SLOT(insert_above_row_())
           );

    connect(rowInsertBelowAction, 
            SIGNAL(triggered()),
            this, 
            SLOT(insert_below_row_())
           );

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
        new PatternGridItem(QSize(1,1), cellSize_, col, row, this);
      item->Init();
      item->setPos(compute_cell_origin_(col, row)); 
      item->insert_knitting_symbol(defaultSymbol_);

      /* add it to our scene */
      add_patternGridItem_(item);
    }
  }
}



//-------------------------------------------------------------
// create or update the column labels
//-------------------------------------------------------------
void GraphicsScene::create_grid_labels_()
{
  /* retrieve current canvas font */
  QFont currentFont = extract_font_from_settings(settings_);

  /* remove all existing labels if there are any */
  QList<QGraphicsItem*> allItems(items());
  QList<PatternGridLabel*> allLabels;
  foreach(QGraphicsItem* aLabel, allItems)
  {
    PatternGridLabel* label = 
      qgraphicsitem_cast<PatternGridLabel*>(aLabel);

    if (label != 0)
    {
      allLabels.push_back(label);
    }
  }  

  foreach(PatternGridLabel* aLabel, allLabels)
  {
    removeItem(aLabel);
    aLabel->deleteLater();
  }

  /* add new column labels */
  QString label;
  qreal yPos = origin_.y() + numRows_ * cellSize_ + 1; 

  for (int col=0; col < numCols_; ++col)
  {
    int colNum = numCols_ - col;
    PatternGridLabel* text = new PatternGridLabel(
        label.setNum(colNum), 
        PatternGridLabel::ColLabel
        );

    int shift = 
      compute_horizontal_label_shift_(colNum, currentFont.pointSize());
    text->setPos(origin_.x() + col*cellSize_ + shift, yPos); 
    text->setFont(currentFont);
    addItem(text);
  }


  /* add new row labels 
   * FIXME: the exact placement of the labels is hand-tuned
   * and probably not very robust */
  QFontMetrics metric(currentFont);
  int fontHeight = metric.ascent();
  for (int row=0; row < numRows_; ++row)
  {
    PatternGridLabel* text= new PatternGridLabel(
        label.setNum(numRows_ - row),
        PatternGridLabel::RowLabel
        );

    text->setPos(origin_.x() + (numCols_*cellSize_) + 0.1*cellSize_, 
      origin_.y() + row*cellSize_ + 0.5*(cellSize_ - 1.8*fontHeight));
    text->setFont(currentFont);
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
          cell->reseat(cell->col() + 1,cell->row());
          cell->setPos(compute_cell_origin_(cell->col(), cell->row()));
        }
      }

      /* do we want to shift the rows */
      if (rowPivot != NOSHIFT)
      {
        if (cell->row() > rowPivot)
        {
          /* Note: we shift the cell first and can the just
           * use its new position, i.e. no row()+1 in set Pos */
          cell->reseat(cell->col(),cell->row() + 1);
          cell->setPos(compute_cell_origin_(cell->col(), cell->row()));
        }
      }
    }
  }

  /* adjust the row/col count and also shift the legend items */
  if (colPivot != NOSHIFT)
  {
    shift_legend_items_horizontally_(colPivot, cellSize_);
    numCols_ += 1;
  }

  if (rowPivot != NOSHIFT)
  {
    shift_legend_items_vertically_(rowPivot, cellSize_);
    numRows_ += 1;
  }
}



//---------------------------------------------------------------
// clean up all data structure created for the legend 
//---------------------------------------------------------------
void GraphicsScene::purge_legend_()
{
  /* purge containers */
  legendEntries_.clear();
  symbolDescriptors_.clear();
  usedKnittingSymbols_.clear();

  legendIsVisible_ = false;
}


//---------------------------------------------------------------
// remove all items on canvas 
//
// NOTE: Since the SVGItems are owned by each PatternGridItem
// we have to make sure we don't remove them explicitly.
//
// NOTE: Since we call delete directly, make sure that this
// function is never called in an event handler.
//---------------------------------------------------------------
void GraphicsScene::purge_all_canvas_items_()
{
  /* collect all non svgItems first */
  QList<QGraphicsItem*> allItems(items());
  QList<QGraphicsItem*> nonSvgItems;
  foreach(QGraphicsItem* anItem, allItems)
  {
    if (anItem->type() != QGraphicsSvgItem::Type)
    {
      nonSvgItems.push_back(anItem);
    }
  }

  foreach(QGraphicsItem* finalItem, nonSvgItems)
  {
    removeItem(finalItem);
    delete finalItem;
  } 
}


//------------------------------------------------------------
// update the canvas, i.e., add the currently selected 
// knitting symbol/color to all active items.
//------------------------------------------------------------
void GraphicsScene::update_active_items_()
{
  if (selectedSymbol_->patternName() != "")
  {
    try_place_knitting_symbol_();
  }
}


//-----------------------------------------------------------
// return if a row of PatternGridItems is contiguous, i.e.
// there are no holes, and the number of unit cells covered
// by the row (holes not counted)
//-----------------------------------------------------------
QPair<bool,int> GraphicsScene::is_row_contiguous_(
    const RowItems& aRow) const
{
  /* an empty row is contiguous */
  if (aRow.empty())
  {
    return QPair<bool,int>(true,0);
  }

  int currentCol = aRow.at(0)->col();
  int rowWidth   = aRow.at(0)->dim().width();
  int totalWidth = 0;
  bool status    = true;
  for (int index = 1; index < aRow.size(); ++index)
  {
    int rowCol   = aRow.at(index)->col();
    if ((currentCol + rowWidth) != rowCol)
    {
      status = false;
    }

    currentCol = rowCol;
    totalWidth += rowWidth;
    rowWidth = aRow.at(index)->dim().width();
  }

  return QPair<bool,int>(status, totalWidth);
}


//-------------------------------------------------------------
// given a list of RowItems, determines the size of the 
// rectangle that bounds them all. The rows are assumed
// to be in increasing order of y with respect to the
// origin
//-------------------------------------------------------------
QRect GraphicsScene::find_bounding_rectangle_(
    const QList<RowItems>& rows) const
{
  assert(!rows.empty());

  /* get index of upper left corner */
  RowItems firstRow = rows.first();
  assert(!firstRow.empty());
  int upperLeftColIndex = firstRow.first()->col();
  int upperLeftRowIndex = firstRow.first()->row();

  /* get index of lower right corner */
  RowItems lastRow = rows.last();
  assert(!lastRow.empty());
  int lowerRightColIndex  = lastRow.last()->col();
  int lowerRightRowIndex  = lastRow.last()->row();
  int lowerRightCellWidth = lastRow.last()->dim().width();
  int lowerRightCellHeight = lastRow.last()->dim().height();

  /* compute coordinates */
  QPoint upperLeftCorner(origin_.x() + upperLeftColIndex * cellSize_,
    origin_.y() + upperLeftRowIndex * cellSize_);
  
  QPoint lowerRightCorner(origin_.x() - 1
    + (lowerRightColIndex + lowerRightCellWidth) * cellSize_,
    origin_.y() - 1
    + (lowerRightRowIndex + lowerRightCellHeight) * cellSize_); 

  return QRect(upperLeftCorner, lowerRightCorner);
}


//--------------------------------------------------------------
// handle mouse clicks on the boundary of any of the marker
// rectangles
//--------------------------------------------------------------
bool GraphicsScene::handle_click_on_marker_rectangle_(
    const QGraphicsSceneMouseEvent* mouseEvent) 
{
  /* get all items at pos and grab all patternGridRectangles
   * if any */
  QPointF mousePos(mouseEvent->scenePos());
  QList<QGraphicsItem*> itemsUnderMouse = items(mousePos);

  QList<PatternGridRectangle*> rectangles;
  foreach(QGraphicsItem* anItem, itemsUnderMouse)
  {
    PatternGridRectangle* rectAngle = 
      qgraphicsitem_cast<PatternGridRectangle*>(anItem);
    if (rectAngle != 0)
    {
      if (rectAngle->selected(mousePos))
      {
        rectangles.push_back(rectAngle);
      }
    }
  }

  if (!rectangles.empty())
  {
    /* we allow only one rectangle to be selected at a time */
    if (rectangles.size() > 1)
    {
      emit statusBar_error(tr("Multiple rectangles selected."));
      return false;
    }

    show_rectangle_manage_menu_(rectangles.front(),
        mouseEvent->screenPos());

    return true;
  }
 
  return false;
}



//--------------------------------------------------------------
// handle mouse clicks inside the grid array
//--------------------------------------------------------------
bool GraphicsScene::handle_click_on_grid_array_(
    const QGraphicsSceneMouseEvent* mouseEvent)
{
  QPair<int,int> arrayIndex(get_cell_coords_(mouseEvent->scenePos()));
  int column = arrayIndex.first;
  int row    = arrayIndex.second;

  /* FIXME: manage_columns_rows_ calls the proper member function
   * via a signal and can't therefore provide the column/row
   * ID by itself which is why we have to use a silly
   * private variable. Is there any way we can avoid this?
   *
   * Also we show the menu only if we're inside the pattern
   * grid plus a margin of a single cellSize_ in all directions */
  if ( row > -1 || row < (numRows_ + 1) || column > -1 
       || column < (numCols_ + 1)) 
  { 
    selectedCol_ = column;
    selectedRow_ = row;
    manage_columns_rows_(mouseEvent->screenPos(), column, row);
  }

  return true;
}


//----------------------------------------------------------------
// handle mouse clicks on the grid labels
//----------------------------------------------------------------
bool GraphicsScene::handle_click_on_grid_labels_(
    const QGraphicsSceneMouseEvent* mouseEvent)
{
  QPointF currentPos = mouseEvent->scenePos();
  QPair<int,int> arrayIndex(get_cell_coords_(currentPos));
  int column = arrayIndex.first;
  int row    = arrayIndex.second;

  if (column == numCols_)
  {
    select_row_(row);
  }
  else if (row == numRows_)
  {
    select_column_(column);
  }

  return true;
}


//---------------------------------------------------------------
// generate a menu allowing the user to customize or delete
// a pattern grid rectangle 
// FIXME: This function uses a bit of a hack. In order to
// deliver the to be deleted/edited rectangle to the SLOT
// via connect we have to invoke a SignalMapper involving
// some casting downstream. Can we somehow avoid this??
//--------------------------------------------------------------
void GraphicsScene::show_rectangle_manage_menu_(
    PatternGridRectangle* rect, const QPoint& pos)
{
  
  QMenu rectangleMenu;

  QAction* deleteRectAction = 
    rectangleMenu.addAction(tr("delete rectangle"));
  QSignalMapper* rectangleDeleter = new QSignalMapper(this);
  rectangleDeleter->setMapping(deleteRectAction, rect);
  
  connect(deleteRectAction,
          SIGNAL(triggered()),
          rectangleDeleter,
          SLOT(map()));

  connect(rectangleDeleter,
          SIGNAL(mapped(QObject*)),
          this,
          SLOT(mark_rectangle_for_deletion_(QObject*)));


  QAction* customizeRectAction =
    rectangleMenu.addAction(tr("customize rectangle"));
  QSignalMapper* rectangleCustomizer = new QSignalMapper(this);
  rectangleCustomizer->setMapping(customizeRectAction, rect);

  connect(customizeRectAction,
          SIGNAL(triggered()),
          rectangleCustomizer,
          SLOT(map()));

  connect(rectangleCustomizer,
          SIGNAL(mapped(QObject*)),
          this,
          SLOT(customize_rectangle_(QObject*)));


  rectangleMenu.exec(pos);
}



//-------------------------------------------------------------
// use this function to add a PatternGridItem to the scene.
// In addition to that we also update the referene count of
// currently active knitting symbols
//-------------------------------------------------------------
void GraphicsScene::add_patternGridItem_(PatternGridItem* anItem)
{
  addItem(anItem);
  notify_legend_of_item_addition_(anItem);
}


//-------------------------------------------------------------
// use this function to remove a PatternGridItem from the scene.
// In addition to that we also update the referene count of
// currently active knitting symbols
//-------------------------------------------------------------
void GraphicsScene::remove_patternGridItem_(PatternGridItem* anItem)
{
  removeItem(anItem);
  notify_legend_of_item_removal_(anItem);
  
  /* delete it for good */
  anItem->deleteLater();
}



//-------------------------------------------------------------
// get the description for the knitting symbol. If this is
// the first time we ask for it we use the symbols base name
// and also store it in the map that keeps track of the name
// from now one
//-------------------------------------------------------------
QString GraphicsScene::get_symbol_description_(
  KnittingSymbolPtr aSymbol, QString colorName)
{
  QString description = 
    aSymbol->patternName() + " = " + aSymbol->instructions();
  QString fullName = aSymbol->category() + aSymbol->patternName() 
                     + colorName;
  if (!symbolDescriptors_.contains(fullName))
  {
    symbolDescriptors_[fullName] = description;
  }
  else
  {
    description = symbolDescriptors_[fullName];
  }

  return description;
}
 


//-------------------------------------------------------------
// Add a symbol plus description to the legend if neccessary.
// This function checks if the added symbol already exists
// in the legend. If not, create it.
//-------------------------------------------------------------
void GraphicsScene::notify_legend_of_item_addition_(
    const PatternGridItem* item)
{
  KnittingSymbolPtr symbol = item->get_knitting_symbol();
  QString symbolName = symbol->patternName();
  QString symbolCategory = symbol->category();
  QString colorName  = item->color().name();
  QString fullName = symbolCategory + symbolName + colorName;

  /* update reference count */
  int currentValue = usedKnittingSymbols_[fullName] + 1;
  assert(currentValue > 0);
  usedKnittingSymbols_[fullName] = currentValue;

  /* if the symbol got newly added we add a description unless
   * it already existed previously and show it in the legend */
  if (currentValue == 1)
  {
    QString description = get_symbol_description_(symbol, colorName);

    /* compute position for next label item */
    int xPosSym = origin_.x();
    int xPosLabel = (symbol->dim().width() + 0.5) * cellSize_ + origin_.x();
    int yPos = get_next_legend_items_y_position_();

    LegendItem* newLegendItem = new LegendItem(symbol->dim(), 
      cellSize_, item->color());
    newLegendItem->Init();
    newLegendItem->insert_knitting_symbol(symbol);
    newLegendItem->setPos(xPosSym, yPos);
    newLegendItem->setFlag(QGraphicsItem::ItemIsMovable);
    newLegendItem->setZValue(1);
    addItem(newLegendItem);

    /* add label */
    QFont currentFont = extract_font_from_settings(settings_);
    LegendLabel* newTextItem = 
      new LegendLabel(fullName, description);
    newTextItem->Init();
    newTextItem->setPos(xPosLabel, yPos);
    newTextItem->setFont(currentFont);
    newTextItem->setFlag(QGraphicsItem::ItemIsMovable);
    newTextItem->setZValue(1);
    addItem(newTextItem);
    connect(newTextItem,
            SIGNAL(label_changed(QString, QString)),
            this,
            SLOT(update_key_label_text_(QString, QString))
           );

    legendEntries_[fullName] = LegendEntry(newLegendItem, newTextItem);

    if (!legendIsVisible_)
    {
      newLegendItem->hide();
      newTextItem->hide();
    }
    else
    {
      emit show_whole_scene();
    }

  }
}
       

//---------------------------------------------------------------
// computes the best possible y position for a new legend item.
// We try to place right under all currently exisiting legend
// items and the pattern grid 
//---------------------------------------------------------------
int GraphicsScene::get_next_legend_items_y_position_() const
{
  QList<QGraphicsItem*> allLegendGraphicsItems = 
    get_list_of_legend_items_();

  int yMaxLegend = static_cast<int>(
      floor(get_max_y_coordinate(allLegendGraphicsItems)));
  int yMaxGrid = numRows_ * cellSize_ + origin_.y();
  int yMax = qMax(yMaxGrid, yMaxLegend);
 
  return (yMax + cellSize_ * 1.5);
}


//--------------------------------------------------------------
// return a list of all QGraphicsItems currently in the legend
//--------------------------------------------------------------
QList<QGraphicsItem*> GraphicsScene::get_list_of_legend_items_() const
{
  QList<LegendEntry> allLegendEntries(legendEntries_.values());
  QList<QGraphicsItem*> allLegendGraphicsItems;
  foreach(LegendEntry item, allLegendEntries)
  {
    allLegendGraphicsItems.push_back(item.first);
    allLegendGraphicsItems.push_back(item.second);
  }

  return allLegendGraphicsItems;
}


//-------------------------------------------------------------
// Remove a symbol plus description from the legend if neccessary.
// This function checks if the removed symbol is the "last of
// its kind" and if so removed it.
//-------------------------------------------------------------
void GraphicsScene::notify_legend_of_item_removal_(
  const PatternGridItem* item)
{
  KnittingSymbolPtr symbol = item->get_knitting_symbol();
  QString symbolName = symbol->patternName();
  QString symbolCategory = symbol->category();
  QString colorName  = item->color().name();
  QString fullName = symbolCategory + symbolName + colorName;

  int currentValue = usedKnittingSymbols_[fullName] - 1;
  assert(currentValue >= 0);
  usedKnittingSymbols_[fullName] = currentValue;

  /* remove symbol if reference count hits 0 */
  if (currentValue == 0)
  {
    usedKnittingSymbols_.remove(fullName);

    LegendEntry deadItem = legendEntries_[fullName];
    removeItem(deadItem.first);
    deadItem.first->deleteLater();
    removeItem(deadItem.second);
    deadItem.second->deleteLater();
    legendEntries_.remove(fullName);
  }
}
        

//-------------------------------------------------------------
// Update the legend labels after a settings change
//-------------------------------------------------------------
void GraphicsScene::update_legend_labels_()
{
  QList<LegendEntry> allItems(legendEntries_.values());
  QFont currentFont = extract_font_from_settings(settings_);
  
  foreach(LegendEntry item, allItems)
  {
    item.second->setFont(currentFont);
  }
}
      

//-------------------------------------------------------------
// shift all legend items below pivot by "distance" 
// vertically
//-------------------------------------------------------------
void GraphicsScene::shift_legend_items_vertically_(int pivot, 
  int distance)
{
  /* find all legend items below the pivot */
  QList<QGraphicsItem*> allLegendItems = get_list_of_legend_items_();
  QList<QGraphicsItem*> toBeShiftedItems;
  int pivotYPos = pivot * cellSize_;

  foreach(QGraphicsItem* item, allLegendItems)
  {
    QPointF itemPos = item->pos();
    if (itemPos.y() > pivotYPos)
    {
      item->setPos(itemPos.x(), itemPos.y() + distance);
    }
  }
}
  

//-------------------------------------------------------------
// shift all legend items right of pivot by distance 
// horizontally. Leave items that are above or below the 
// pattern grid alone.
//-------------------------------------------------------------
void GraphicsScene::shift_legend_items_horizontally_(int pivot, 
  int distance)
{
  /* find all legend items right of the pivot */
  QList<QGraphicsItem*> allLegendItems = get_list_of_legend_items_();
  QList<QGraphicsItem*> toBeShiftedItems;
  int pivotXPos = pivot * cellSize_;

  foreach(QGraphicsItem* item, allLegendItems)
  {
    QPointF itemPos = item->pos();
    if (itemPos.x() > pivotXPos 
        && itemPos.y() > 0.0 
        && itemPos.y() < (numRows_ * cellSize_) )
    {
      item->setPos(itemPos.x() + distance, itemPos.y());
    }
  }
}
 

  
QT_END_NAMESPACE
