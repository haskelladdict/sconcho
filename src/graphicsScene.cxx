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
#include <QMessageBox>
#include <QSettings>
#include <QSignalMapper>

/* local headers */
#include "basicDefs.h"
#include "rowColDeleteInsertDialog.h"
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
#include "settings.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
GraphicsScene::GraphicsScene( const QPoint& anOrigin,
                              const QSize& gridDim,
                              const QSettings& aSetting,
                              KnittingSymbolPtr defaultSymbol,
                              MainWindow* myParent )
    :
    QGraphicsScene( myParent ),
    updateActiveItems_( true ),
    origin_( anOrigin ),
    numCols_( gridDim.width() ),
    numRows_( gridDim.height() ),
    gridCellDimensions_( extract_cell_dimensions_from_settings( aSetting ) ),
    textFont_( extract_font_from_settings( aSetting ) ),
    selectedCol_( UNSELECTED ),
    selectedRow_( UNSELECTED ),
    settings_( aSetting ),
    selectedSymbol_( emptyKnittingSymbol ),
    defaultSymbol_( defaultSymbol ),
    backgroundColor_( Qt::white ),
    defaultColor_( Qt::white ),
    legendIsVisible_( false )
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}



//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool GraphicsScene::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED ) {
    return false;
  }

  /* build canvas */
  create_pattern_grid_();
  create_grid_labels_();

  /* install signal handlers */
  connect( this,
           SIGNAL( mouse_moved( QPointF ) ),
           parent(),
           SLOT( update_mouse_position_display( QPointF ) )
         );

  connect( this,
           SIGNAL( statusBar_message( QString ) ),
           parent(),
           SLOT( show_statusBar_message( QString ) )
         );

  connect( this,
           SIGNAL( statusBar_error( QString ) ),
           parent(),
           SLOT( show_statusBar_error( QString ) )
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
void GraphicsScene::reset_grid( const QSize& newSize )
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
  const QList<PatternGridItemDescriptorPtr>& newItems )
{
  assert( newItems.size() != 0 );
  reset_canvas_();

  int maxCol = 0;
  int maxRow = 0;
  foreach( PatternGridItemDescriptorPtr rawItem, newItems ) {
    int col = rawItem->location.x();
    int row = rawItem->location.y();

    maxCol = qMax( col, maxCol );
    maxRow = qMax( row, maxRow );

    PatternGridItem* item =
      new PatternGridItem( rawItem->dimension, gridCellDimensions_, col, row,
                           this, rawItem->backgroundColor );
    item->Init();
    item->setPos( compute_cell_origin_( col, row ) );
    item->insert_knitting_symbol( rawItem->patternSymbolPtr );

    /* add it to our scene */
    add_patternGridItem_( item );
  }

  /* adjust dimensions */
  numCols_ = maxCol + 1;
  numRows_ = maxRow + 1;

  /* add labels and rescale */
  create_grid_labels_();
}



//-------------------------------------------------------------
// here we create all the extra label items, i.e., the ones
// that are not controlled by the chart itself
//-------------------------------------------------------------
void GraphicsScene::instantiate_legend_items(
  const QList<LegendEntryDescriptorPtr>& extraLegendItems )
{
  foreach( LegendEntryDescriptorPtr rawItem, extraLegendItems ) {
    notify_legend_of_item_addition_( rawItem->patternSymbolPtr,
                                     backgroundColor_, "extraLegendItem" );
  }
}



//-------------------------------------------------------------
// this function is called after a previously saved sconcho
// project file has been read in. It places the legend items
// at their previously saved locations on the canvas.
// NOTE: This function has to be called after load new canvas
//-------------------------------------------------------------
void GraphicsScene::place_legend_items(
  const QList<LegendEntryDescriptorPtr>& newLegendEntries )
{
  foreach( LegendEntryDescriptorPtr entryDesc, newLegendEntries ) {
    /* find the legend entry by entryID
     * NOTE: We need to do some careful checking here!
     * If we encounter a legend entry that we don't have
     * for some reason we just skip it */
    QString entryID = entryDesc->entryID;
    if ( legendEntries_.find( entryID ) == legendEntries_.end() ) {
      qDebug() << "Error: Problem parsing legend item "
      << entryID << " in input file";
      continue;
    }
    LegendEntry entry = legendEntries_[entryID];

    /* position item and label */
    QPointF itemPos = entryDesc->itemLocation;
    QPointF labelPos = entryDesc->labelLocation;

    entry.first->setPos( itemPos );
    entry.second->setPos( labelPos );

    /* set label text and update our presently stored text */
    QString labelText = entryDesc->labelText;
    entry.second->setPlainText( labelText );
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
  foreach( QGraphicsView* aView, views() ) {
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
void GraphicsScene::select_region( const QRectF& aRegion )
{
  QList<QGraphicsItem*> allItems( items( aRegion ) );

  /* grab PatterGridItems and select them
   * NOTE: We can not just select the cells as we find
   * them among all items since their order is arbitrary
   * causing the selected area to be filled improperly
   * for larger symbols (just like randomly selecting
   * cells in the region would). Hence we sort all cells
   * first by index and then select them in order */
  QMap<int, PatternGridItem*> gridItems;
  foreach( QGraphicsItem* anItem, allItems ) {
    PatternGridItem* cell =
      qgraphicsitem_cast<PatternGridItem*>( anItem );
    if ( cell != 0 ) {
      int cellIndex = compute_cell_index_( cell );
      gridItems[cellIndex] = cell;
    }
  }

  /* disable canvas update until we're done selecting,
   * then we update and re-enable*/
  disable_canvas_update_();

  QList<PatternGridItem*> sortedItems( gridItems.values() );
  foreach( PatternGridItem* cell, sortedItems ) {
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
  /* disable all non-legend items */
  foreach( QGraphicsItem* anItem, items() ) {
    QGraphicsSvgItem* svgItem =
      qgraphicsitem_cast<QGraphicsSvgItem*>( anItem );

    if ( !svgItem ) {
      anItem->hide();
    }
  }

  /* show legend items */
  foreach( QGraphicsItem* anItem, get_all_legend_items_() ) {
    anItem->show();
  }
}



//---------------------------------------------------------------
// show all items on the canvas
//---------------------------------------------------------------
void GraphicsScene::show_all_items()
{
  foreach( QGraphicsItem* anItem, items() ) {
    anItem->show();
  }
}



//-------------------------------------------------------------
// compute the rectangle on the canvas which is currently
// visible depending on if the legend is turned on or not
//-------------------------------------------------------------
QRectF GraphicsScene::get_visible_area() const
{
  QList<QGraphicsItem*> visibleItems;
  foreach( QGraphicsItem* anItem, items() ) {
    QGraphicsSvgItem* svgItem =
      qgraphicsitem_cast<QGraphicsSvgItem*>( anItem );

    if ( !svgItem && anItem->isVisible() ) {
      visibleItems.push_back( anItem );
    }
  }

  return get_bounding_rect( visibleItems );
}



//----------------------------------------------------------------
// compute the center of the pattern grid
//----------------------------------------------------------------
QPoint GraphicsScene::get_grid_center() const
{
  int centerRow = static_cast<int>( numRows_ / 2.0 );
  int centerCol = static_cast<int>( numCols_ / 2.0 );

  QPoint theCenter = compute_cell_origin_( centerRow, centerCol );

  /* shift by half a cell if the number of rows and/or cells
   * is uneven */
  if ( numCols_ % 2 != 0 ) {
    theCenter.setX( theCenter.x() + gridCellDimensions_.width() / 2.0 );
  }

  if ( numRows_ % 2 != 0 ) {
    theCenter.setY( theCenter.y() + gridCellDimensions_.height() / 2.0 );
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
  const KnittingSymbolPtr symbol )
{
  selectedSymbol_ = symbol;

  /* we'll also try to place the newly picked item into
   * the currently selected cells */
  update_active_items_();
}



//-------------------------------------------------------------
// add this symbol to the legend
//-------------------------------------------------------------
void GraphicsScene::add_symbol_to_legend(
  const KnittingSymbolPtr symbol )
{
  notify_legend_of_item_addition_( symbol, backgroundColor_,
                                   "extraLegendItem" );
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
void GraphicsScene::grid_item_selected( PatternGridItem* anItem,
                                        bool status )
{
  /* compute index based on row and col */
  int index = compute_cell_index_( anItem );

  /* first update our list of currently selected items */
  if ( status ) {
    activeItems_[index] = anItem;
  } else {
    activeItems_.remove( index );
  }

  if ( updateActiveItems_ ) {
    update_active_items_();
  }

}



//------------------------------------------------------------
//------------------------------------------------------------
void GraphicsScene::update_selected_background_color(
  const QColor& aColor )
{
  backgroundColor_ = aColor;
}



//------------------------------------------------------------
// rest a grid item to its original state, i.e., convert
// it back into empty single unit cells
//------------------------------------------------------------
void GraphicsScene::grid_item_reset( PatternGridItem* anItem )
{
  /* figure out where item is and how many cells it spans */
  QPoint origin( anItem->origin() );
  QSize dim( anItem->dim() );
  int column = anItem->col();
  int row = anItem->row();

  /* get rid of the old cell making sure that we punt if from
   * the set of activeItems if present */
  remove_patternGridItem_( anItem );

  /* start filling the hole with new cells */
  int numNewCells = dim.width();
  for ( int i = 0; i < numNewCells; ++i ) {
    PatternGridItem* item = new PatternGridItem( QSize( 1, 1 ), gridCellDimensions_,
        column + i, row, this );
    item->Init();
    item->insert_knitting_symbol( defaultSymbol_ );
    item->setPos( compute_cell_origin_( column + i, row ) );
    add_patternGridItem_( item );
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
  foreach( PatternGridItem* anItem, activeItems_ ) {
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
  if ( activeItems_.empty() ) {
    emit statusBar_error( "Nothing selected" );
    return;
  }

  /* first make sure the user selected a complete rectangle */
  QList<RowItems> rowList;
  sort_active_items_row_wise_( rowList );

  /* remove the top and bottom empty rows */
  while ( rowList.first().empty() ) {
    rowList.pop_front();
  }

  while ( rowList.last().empty() ) {
    rowList.pop_back();
  }
  assert( !rowList.empty() );

  QPair<bool, int> initialStatus = is_row_contiguous_( rowList.at( 0 ) );
  bool status = initialStatus.first;
  for ( int index = 1; index < rowList.size(); ++index ) {
    QPair<bool, int> currentStatus =
      is_row_contiguous_( rowList.at( index ) );
    if ( currentStatus != initialStatus ) {
      status = false;
    }
  }

  if ( !status ) {
    emit statusBar_error( "Selected cells don't form a rectangle" );
    return;
  }

  /* find bounding rectangle and create rectangle */
  QRect boundingRect = find_bounding_rectangle_( rowList );

  /* fire up dialog for customizing pattern grid rectangles */
  PatternGridRectangleDialog rectangleDialog;
  rectangleDialog.Init();
  QPen rectanglePen = rectangleDialog.pen();

  PatternGridRectangle* marker = new PatternGridRectangle( boundingRect,
      rectanglePen );
  marker->Init();
  marker->setZValue( 1.0 );
  addItem( marker );
  deselect_all_active_items();
}



//------------------------------------------------------------
// load canvas' chache with updated settings
//------------------------------------------------------------
void GraphicsScene::load_settings()
{
  gridCellDimensions_ = extract_cell_dimensions_from_settings( settings_ );
  textFont_ = extract_font_from_settings( settings_ );
}



//------------------------------------------------------------
// update our current canvas after a change in settings
//------------------------------------------------------------
void GraphicsScene::update_after_settings_change()
{
  int oldCellHeight = gridCellDimensions_.height();
  load_settings();

  QList<QGraphicsItem*> allItems( items() );
  foreach( QGraphicsItem* anItem, allItems ) {
    PatternGridItem* cell = qgraphicsitem_cast<PatternGridItem*>( anItem );

    if ( cell != 0 ) {
      cell->resize();
      cell->setPos( compute_cell_origin_( cell->col(), cell->row() ) );
    }
  }

  /* shift all legend items and rescale the svg containing items */
  int cellHeightChange = gridCellDimensions_.height() - oldCellHeight;
  shift_legend_items_vertically_( 0, cellHeightChange*numRows_, cellHeightChange );
  foreach( QGraphicsItem* anItem, get_all_svg_legend_items_() ) {
    LegendItem* cell = qgraphicsitem_cast<LegendItem*>( anItem );

    if ( cell != 0 ) {
      cell->resize();
    }
  }

  /* update the labels */
  create_grid_labels_();
  update_legend_labels_();
}



//-------------------------------------------------------------
// shows or hides legend items depending on their current
// state
//-------------------------------------------------------------
void GraphicsScene::toggle_legend_visibility()
{
  if ( legendIsVisible_ ) {
    foreach( LegendEntry item, legendEntries_ ) {
      item.first->hide();
      item.second->hide();
    }
    legendIsVisible_ = false;
  } else {
    foreach( LegendEntry item, legendEntries_ ) {
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
// this slot opens a dialog to control adding and deleting
// of rows
//-------------------------------------------------------------
void GraphicsScene::open_row_col_menu_()
{
  assert( selectedRow_ >= 0 );
  assert( selectedRow_ < numRows_ );
  assert( selectedCol_ >= 0 );
  assert( selectedCol_ < numCols_ );

  if ( selectedRow_ == UNSELECTED || selectedCol_ == UNSELECTED ) {
    return;
  }

  RowColDeleteInsertDialog rowColDialog( selectedRow_, numRows_,
                                         selectedCol_, numCols_ );
  rowColDialog.Init();

  connect( &rowColDialog,
           SIGNAL( insert_rows( int, int, int ) ),
           this,
           SLOT( insert_rows_( int, int, int ) )
         );


  connect( &rowColDialog,
           SIGNAL( delete_row( int ) ),
           this,
           SLOT( delete_row_( int ) )
         );


  connect( &rowColDialog,
           SIGNAL( insert_columns( int, int, int ) ),
           this,
           SLOT( insert_columns_( int, int, int ) )
         );


  connect( &rowColDialog,
           SIGNAL( delete_column( int ) ),
           this,
           SLOT( delete_column_( int ) )
         );

  rowColDialog.exec();
}


//-------------------------------------------------------------
// this slots deletes selectedCol from the pattern grid array
// NOTE: delecting columns is a bit more tricky than deleting
// rows since we have to bail if the selected column has cells
// that span more than a single unit cell, i.e., columns.
//-------------------------------------------------------------
void GraphicsScene::delete_column_( int aDeadCol )
{
  int deadCol = numCols_ - aDeadCol;

  if ( !can_column_be_deleted( numCols_, aDeadCol ) ) {
    return;
  }

  assert( deadCol >= 0 );
  assert( deadCol < numCols_ );

  deselect_all_active_items();

  QList<QGraphicsItem*> allItems( items() );
  QList<PatternGridItem*> gridItems;

  /* go through all items and make sure that the cells
   * of the selected rows are all unit cells and don't
   * span multiple columns */
  int targetColCounter = 0;
  foreach( QGraphicsItem* anItem, allItems ) {
    PatternGridItem* cell =
      qgraphicsitem_cast<PatternGridItem*>( anItem );

    if ( cell != 0 ) {
      if ( cell->col() == deadCol &&
           cell->dim().width() == 1 ) {
        targetColCounter += 1;
      }

      gridItems.push_back( cell );
    }
  }

  /* if we have less than numRows_ in deletedColCounter there
   * was at least on multi column cell in the column */
  if ( targetColCounter < numRows_ ) {
    emit statusBar_error( "cannot delete columns with "
                          "cells that span multiple columns" );
    return;
  }


  /* go through all grid cells and
   * - delete the ones in the selectedRow_
   * - shift the ones in a row greater than selectedRow_
   *   up by one
   */
  foreach( PatternGridItem* cell, gridItems ) {
    if ( cell->col() == deadCol ) {
      remove_patternGridItem_( cell );
    } else if ( cell->col() > deadCol ) {
      cell->reseat( cell->col() - 1, cell->row() );
      cell->setPos( compute_cell_origin_( cell->col(), cell->row() ) );
    }
  }

  /* update position of legend items */
  shift_legend_items_horizontally_( deadCol, -gridCellDimensions_.width() );

  /* unselect row and update row counter */
  numCols_ = numCols_ - 1;

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect( itemsBoundingRect() );
}



//-------------------------------------------------------------
// this slots deletes selectedRow from the pattern grid array
// NOTE 1: deadRow is in user row coordinates and we have to
// convert it into internal row coordinate (i.e. top row has
// index zero and increasing downward).
// NOTE 2: Also make sure we only delete valid rows and leave
// at least one.
//-------------------------------------------------------------
void GraphicsScene::delete_row_( int aDeadRow )
{
  int deadRow = numRows_ - aDeadRow;

  if ( !can_row_be_deleted( numRows_, aDeadRow ) ) {
    return;
  }

  deselect_all_active_items();

  /* go through all grid cells and
   * - delete the ones in aDeadRow
   * - shift the ones in a row greater than aDeadRow
   *   up by one
   *
   * Important: We can't just delete as we go since
   * this also nukes the svg item children which
   * we are also iterating over
   */
  QList<QGraphicsItem*> allItems( items() );
  QList<PatternGridItem*> patternItems;
  foreach( QGraphicsItem* anItem, allItems ) {
    PatternGridItem* cell =
      qgraphicsitem_cast<PatternGridItem*>( anItem );

    if ( cell != 0 ) {
      patternItems.push_back( cell );
    }
  }

  foreach( PatternGridItem* patItem, patternItems ) {
    if ( patItem->row() == deadRow ) {
      remove_patternGridItem_( patItem );
    } else if ( patItem->row() > deadRow ) {
      patItem->reseat( patItem->col(), patItem->row() - 1 );
      patItem->setPos(
        compute_cell_origin_( patItem->col(), patItem->row() ) );
    }
  }

  /* update position of legend items */
  shift_legend_items_vertically_( deadRow, -gridCellDimensions_.height() );

  /* unselect row and update row counter */
  numRows_ = numRows_ - 1;

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect( itemsBoundingRect() );
}


//-------------------------------------------------------------
// insert new columns into grid
//-------------------------------------------------------------
void GraphicsScene::insert_columns_( int columnCount, int pivotCol, int direction )
{
  if ( !can_column_be_inserted( numCols_, pivotCol ) ) {
    return;
  }

  for ( int count = 0; count < columnCount; ++count ) {
    insert_single_column_( numCols_ - pivotCol + direction );
  }
}




//-----------------------------------------------------------------
// this slot inserts the requested number of rows at the pivot
// location
// NOTE: pivotRow is in user row coordinates and we have to
// convert it into internal row coordinate (i.e. top row has
// index zero and increasing downward). Also location is either
// 0 for inserting below or 1 for inserting above.
//-----------------------------------------------------------------
void GraphicsScene::insert_rows_( int rowCount, int pivotRow, int direction )
{
  if ( !can_row_be_inserted( numRows_, pivotRow ) ) {
    return;
  }

  for ( int count = 0; count < rowCount; ++count ) {
    insert_single_row_( numRows_ - pivotRow - direction );
  }
}





//--------------------------------------------------------------
// this slot marks a pattern grid rectangle for deletion
// FIXME: The casting is a bit nasty - can we get rid of it.
// Since this SLOT is filled via a signal we can only
// deliver a QObject via QSignalMapper
//--------------------------------------------------------------
void GraphicsScene::mark_rectangle_for_deletion_( QObject* rectObj )
{
  PatternGridRectangle* rect =
    qobject_cast<PatternGridRectangle*>( rectObj );
  removeItem( rect );
  rect->deleteLater();
}



//--------------------------------------------------------------
// this slot fires up a customization dialog to change the
// properties of the selected rectangle
// FIXME: The casting is a bit nasty - can we get rid of it.
// Since this SLOT is filled via a signal we can only
// deliver a QObject via QSignalMapper
//--------------------------------------------------------------
void GraphicsScene::customize_rectangle_( QObject* rectObj )
{
  PatternGridRectangle* rect =
    qobject_cast<PatternGridRectangle*>( rectObj );

  PatternGridRectangleDialog rectangleDialog;
  rectangleDialog.Init();
  QPen rectanglePen = rectangleDialog.pen();

  rect->set_pen( rectanglePen );
}



//-------------------------------------------------------------
// this slot update the text we store for a particular
// legend label
//-------------------------------------------------------------
void GraphicsScene::update_key_label_text_( QString labelID,
    QString newLabelText )
{
  symbolDescriptors_[labelID] = newLabelText;
}



//-------------------------------------------------------------
// Add a symbol plus description to the legend if neccessary.
// This function checks if the added symbol already exists
// in the legend. If not, create it.
// The extraTag parameter allows more fine grained control
// of who "owns" a legend entry (e.g. the chart itself or
// the user added it directly from the symbolSelectorWidget.
//-------------------------------------------------------------
void GraphicsScene::notify_legend_of_item_addition_(
  const KnittingSymbolPtr symbol, QColor aColor, QString tag )
{
  QString symbolName = symbol->patternName();
  QString symbolCategory = symbol->category();
  QString colorName  = aColor.name();
  QString fullName = get_legend_item_name( symbolCategory,
                     symbolName, colorName, tag );

  /* update reference count */
  int currentValue = usedKnittingSymbols_[fullName] + 1;
  assert( currentValue > 0 );
  usedKnittingSymbols_[fullName] = currentValue;

  /* if the symbol got newly added we add a description unless
   * it already existed previously and show it in the legend */
  if ( currentValue == 1 ) {
    /* compute position for next label item */
    int xPosSym = origin_.x();
    int yPos = get_next_legend_items_y_position_();

    LegendItem* newLegendItem = new LegendItem( symbol->dim(), tag,
        gridCellDimensions_, aColor );
    connect( newLegendItem,
             SIGNAL( delete_from_legend( KnittingSymbolPtr, QColor, QString ) ),
             this,
             SLOT( notify_legend_of_item_removal_( KnittingSymbolPtr, QColor,
                                                   QString ) )
           );
    newLegendItem->Init();
    newLegendItem->insert_knitting_symbol( symbol );
    newLegendItem->setPos( xPosSym, yPos );
    newLegendItem->setFlag( QGraphicsItem::ItemIsMovable );
    newLegendItem->setZValue( 1 );
    addItem( newLegendItem );

    /* add label */
    QString description = get_symbol_description_( symbol, colorName );
    int xPosLabel = ( symbol->dim().width() + 0.5 ) * gridCellDimensions_.width()
                    + origin_.x();

    LegendLabel* newTextItem =
      new LegendLabel( fullName, description );
    newTextItem->Init();
    newTextItem->setPos( xPosLabel, yPos );
    newTextItem->setFont( textFont_ );
    newTextItem->setFlag( QGraphicsItem::ItemIsMovable );
    newTextItem->setZValue( 1 );
    addItem( newTextItem );
    connect( newTextItem,
             SIGNAL( label_changed( QString, QString ) ),
             this,
             SLOT( update_key_label_text_( QString, QString ) )
           );

    legendEntries_[fullName] = LegendEntry( newLegendItem, newTextItem );

    if ( !legendIsVisible_ ) {
      newLegendItem->hide();
      newTextItem->hide();
    } else {
      emit show_whole_scene();
    }
  }
}



//-------------------------------------------------------------
// Remove a symbol plus description from the legend if neccessary.
// This function checks if the removed symbol is the "last of
// its kind" and if so removed it.
//-------------------------------------------------------------
void GraphicsScene::notify_legend_of_item_removal_(
  const KnittingSymbolPtr symbol, QColor aColor, QString tag )
{
  QString symbolName = symbol->patternName();
  QString symbolCategory = symbol->category();
  QString colorName  = aColor.name();
  QString fullName = get_legend_item_name( symbolCategory,
                     symbolName, colorName, tag );

  int currentValue = usedKnittingSymbols_[fullName] - 1;
  assert( currentValue >= 0 );
  usedKnittingSymbols_[fullName] = currentValue;

  /* remove symbol if reference count hits 0 */
  if ( currentValue == 0 ) {
    usedKnittingSymbols_.remove( fullName );

    LegendEntry deadItem = legendEntries_[fullName];
    removeItem( deadItem.first );
    deadItem.first->deleteLater();
    removeItem( deadItem.second );
    deadItem.second->deleteLater();
    legendEntries_.remove( fullName );
  }
}


//-------------------------------------------------------------
// this function copies the current active item selection
//-------------------------------------------------------------
void GraphicsScene::copy_items_()
{
  copiedItems_.objects.clear();
  CopyRegionDimension regionDim( INT_MAX, 0, INT_MAX, 0 );

  QMap<int, PatternGridItem*>::const_iterator iter =
    activeItems_.constBegin();
  while ( iter != activeItems_.constEnd() ) {

    QPair<int, int> location = compute_from_cell_index_( iter.key() );
    adjust_copy_region( regionDim, location );

    /* copy item */
    PatternGridItem* source = iter.value();
    CopyObjectItemPtr item = CopyObjectItemPtr( new CopyObjectItem );
    item->symbol    = source->get_knitting_symbol();
    item->backColor = source->color();
    item->size      = source->dim();
    item->row       = source->row();
    item->column    = source->col();
    copiedItems_.objects.push_back( item );

    ++iter;
  }

  /* now that we know the total extent we can normalize each
   * item and compute the width and height of the copy region */
  int rowOrigin = regionDim.get<0>();
  int colOrigin = regionDim.get<2>();
  foreach( CopyObjectItemPtr item, copiedItems_.objects ) {
    item->row = item->row - rowOrigin;
    item->column = item->column - colOrigin;

    assert( item->row >= 0 );
    assert( item->column >= 0 );
  }

  copiedItems_.height = regionDim.get<1>() - rowOrigin + 1;
  copiedItems_.width  = regionDim.get<3>() - colOrigin + 1;
}



//-------------------------------------------------------------
// this function pastes whatever is in the current selection
// assuming this is possible based on the present grid
// geometry and user selection on the grid.
//-------------------------------------------------------------
void GraphicsScene::paste_items_()
{
  /* make sure the copy object fits */
  if (( selectedRow_ + copiedItems_.height ) > numRows_
      || ( selectedCol_ + copiedItems_.width ) > numCols_ ) {
    QMessageBox::critical( 0, tr( "Paste Error" ),
                           tr( "Pasted selection does not fit "
                               "into current grid!" ) );
    return;
  }

  foreach( CopyObjectItemPtr item, copiedItems_.objects ) {
    int targetCol = selectedCol_ + item->column;
    int targetRow = selectedRow_ + item->row;

    PatternGridItem* deadItem = patternGridItem_at_( targetCol, targetRow );
    remove_patternGridItem_( deadItem );

    PatternGridItem* newItem =
      new PatternGridItem( item->size, gridCellDimensions_, targetCol,
                           targetRow, this, item->backColor );

    newItem->Init();
    newItem->insert_knitting_symbol( item->symbol );
    newItem->setPos( compute_cell_origin_( targetCol, targetRow ) );
    add_patternGridItem_( newItem );
  }
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
  QGraphicsSceneMouseEvent* mouseEvent )
{
  QPointF currentPos = mouseEvent->scenePos();

  /* let our parent know that we moved */
  emit mouse_moved( currentPos );

  return QGraphicsScene::mouseMoveEvent( mouseEvent );
}



//---------------------------------------------------------------
// event handler for mouse press events
//---------------------------------------------------------------
void GraphicsScene::mousePressEvent(
  QGraphicsSceneMouseEvent* mouseEvent )
{
  if ( mouseEvent->button() == Qt::RightButton ) {
    bool handled = handle_click_on_marker_rectangle_( mouseEvent );

    if ( !handled ) {
      handle_click_on_grid_array_( mouseEvent );
    }
  } else {
    handle_click_on_grid_labels_( mouseEvent );
  }

  return QGraphicsScene::mousePressEvent( mouseEvent );
}



/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/


//-------------------------------------------------------------
// this function inserts a single columne into the chart at
// column aCol
//-------------------------------------------------------------
void GraphicsScene::insert_single_row_( int aRow )
{
  deselect_all_active_items();

  /* shift rows to make space */
  expand_grid_( NOSHIFT, aRow );

  /* now insert the new row */
  for ( int column = 0; column < numCols_; ++column ) {
    PatternGridItem* anItem = new PatternGridItem(
      QSize( 1, 1 ), gridCellDimensions_, column, aRow + 1,
      this, defaultColor_ );

    anItem->Init();
    anItem->setPos( compute_cell_origin_( column, aRow + 1 ) );
    anItem->insert_knitting_symbol( defaultSymbol_ );
    add_patternGridItem_( anItem );
  }

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect( itemsBoundingRect() );
}



//-------------------------------------------------------------
// this function inserts a single columne into the chart at
// column aCol. We go through all items and make sure that that
// inserting the columns won't cut through any multi row cells
// NOTE: The special case here is adding a column at the
// right or left of the pattern grid in which case we're
// always in good shape and the below test will actually
// fail when adding at the right
//-------------------------------------------------------------
void GraphicsScene::insert_single_column_( int aCol )
{
  deselect_all_active_items();

  if ( aCol != 0 && aCol != numCols_ ) {
    int targetColCounter = 0;
    QList<QGraphicsItem*> allItems( items() );
    foreach( QGraphicsItem* anItem, allItems ) {
      PatternGridItem* cell =
        qgraphicsitem_cast<PatternGridItem*>( anItem );

      if ( cell != 0 ) {
        /* in order to make sure we won't cut through a wide cell, we
         * check if the origin of the cell is in the current cell. If not,
         * it will surely start in the cell to the left and we would cut
         * it in this case */
        QPointF actualOrigin( cell->scenePos() );
        QPointF neededOrigin( compute_cell_origin_( aCol, cell->row() ) );

        /* FIXME: we shouldn't be comparing QPointFs !!! */
        if ( cell->col() == aCol && actualOrigin == neededOrigin ) {
          targetColCounter += 1;
        }
      }
    }

    /* if we have less than numCols_ in deletedColCounter there
     * was at least on multi column cell in the column */
    if ( targetColCounter < numRows_ ) {
      QMessageBox::critical( 0, tr( "Invalid Column" ), tr( "cannot insert column" )
                             + tr( "between cells that span multiple columns" ) );
      return;
    }
  }


  /* expand the grid to make space */
  expand_grid_( aCol, NOSHIFT );

  /* now insert the new column */
  for ( int row = 0; row < numRows_; ++row ) {
    PatternGridItem* anItem = new PatternGridItem( QSize( 1, 1 ),
        gridCellDimensions_, aCol, row, this, defaultColor_ );

    anItem->Init();
    anItem->setPos( compute_cell_origin_( aCol, row ) );
    anItem->insert_knitting_symbol( defaultSymbol_ );
    add_patternGridItem_( anItem );
  }

  /* redraw the labels */
  create_grid_labels_();

  /* update sceneRect
   * NOTE: This may be a bottleneck for large grids */
  setSceneRect( itemsBoundingRect() );
}



//-------------------------------------------------------------
// this function goes through all active items and changes
// the color of each on to the one that is currently
// selected.
//-------------------------------------------------------------
void GraphicsScene::change_selected_cells_colors_()
{
  foreach( PatternGridItem* item, activeItems_ ) {
    /* remove us from the legend */
    notify_legend_of_item_removal_( item->get_knitting_symbol(),
                                    item->color(), "chartLegendItem" );

    item->set_background_color( backgroundColor_ );

    /* re-add newly colored symbol to the legend */
    notify_legend_of_item_addition_( item->get_knitting_symbol(),
                                     item->color(), "chartLegendItem" );

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

  if ( cellsNeeded == 0 ) {
    return;
  }

  /* make sure the number of selected items is an integer multiple
   * of the required item size */
  if ( activeItems_.size() % cellsNeeded != 0 ) {
    emit statusBar_error( tr( "Number of selected cells is"
                              "not a multiple of the pattern size" ) );
  }

  /* sort selected items row wise */
  QList<RowItems> rowList;
  bool sortStatus = sort_active_items_row_wise_( rowList );
  if ( !sortStatus ) {
    return;
  }

  /* check if each row has the proper arrangement of
   * highlighted cells to fit the selected pattern item */
  QList<RowLayout> replacementCells;
  bool finalStatus = process_selected_items_( replacementCells,
                     rowList, cellsNeeded );
  if ( !finalStatus ) {
    return;
  }


  /* delete previously highligthed cells */
  QList<PatternGridItem*> deadItems( activeItems_.values() );
  foreach( PatternGridItem* item, deadItems ) {
    remove_patternGridItem_( item );
  }


  /* at this point all rows are in the proper shape to be
   * replaced by the current symbol */
  for ( int row = 0; row < replacementCells.size(); ++row ) {
    for ( int cell = 0; cell < replacementCells.at( row ).size(); ++cell ) {
      int column = replacementCells.at( row )[cell].first;
      int aWidth  = replacementCells.at( row )[cell].second;

      PatternGridItem* anItem = new PatternGridItem(
        QSize( aWidth, 1 ),
        gridCellDimensions_,
        column,
        row,
        this,
        backgroundColor_ );

      anItem->Init();
      anItem->insert_knitting_symbol( selectedSymbol_ );
      anItem->setPos( compute_cell_origin_( column, row ) );
      add_patternGridItem_( anItem );
    }
  }

  /* clear selection */
  activeItems_.clear();
}



//-----------------------------------------------------------------
// compute the shift for horizontal labels so they are centered
// in each grid cell
//-----------------------------------------------------------------
int GraphicsScene::compute_horizontal_label_shift_( int aNum,
    int fontSize ) const
{
  double size = gridCellDimensions_.width() * 0.5;
  double numWidth = fontSize * 0.5;
  double count = 0;
  if ( aNum < 10 ) {
    count = 1.5;
  } else if ( aNum < 100 ) {
    count = 2.0;
  } else {
    count = 3;
  }

  return static_cast<int>( size - numWidth * count );
}



//----------------------------------------------------------------
// sort all currently selected cells in a row by row fashion
// returns true on success and false on failure
//----------------------------------------------------------------
bool GraphicsScene::sort_active_items_row_wise_(
  QList<RowItems>& theRows ) const
{
  for ( int i = 0; i < numRows_; ++i ) {
    RowItems tempList;
    theRows.push_back( tempList );
  }

  QMap<int, PatternGridItem*>::const_iterator iter =
    activeItems_.constBegin();
  while ( iter != activeItems_.constEnd() ) {
    int row = static_cast<int>( iter.key() / numCols_ );
    theRows[row].push_back( iter.value() );
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
  int selectedPatternSize )
{
  for ( int row = 0; row < rowLayout.size(); ++row ) {
    RowItems rowItem = rowLayout.at( row );

    int rowLength = 0;
    foreach( PatternGridItem* anItem, rowItem ) {
      rowLength += ( anItem->dim() ).width();
    }

    /* if the rowLength is not divisible by cellsNeeded we
     * are done */
    if ( rowLength % selectedPatternSize != 0 ) {
      emit statusBar_error( tr( "Improper total number of cells." ) );
      return false;
    }

    RowLayout cellBounds;
    foreach( PatternGridItem* anItem, rowItem ) {
      int curStart = ( anItem->col() );
      int curWidth = ( anItem->dim() ).width();

      if ( !cellBounds.empty() ) {
        int lastStart = cellBounds.back().first;
        int lastWidth = cellBounds.back().second;

        /* see if we are extending the last cell */
        if ( lastStart + lastWidth == curStart ) {
          cellBounds.pop_back();
          cellBounds.push_back(
            QPair<int, int>( lastStart, lastWidth + curWidth ) );
        } else {
          cellBounds.push_back( QPair<int, int>( curStart, curWidth ) );
        }
      } else {
        cellBounds.push_back( QPair<int, int>( curStart, curWidth ) );
      }
    }


    /* generate row message String */
    QString rowIndex;
    rowIndex.setNum( row + 1 );
    QString rowMsg( "row " + rowIndex + ": " );

    RowLayout finalCells;
    /* reorganize all blocks into multiples of selectedPatternSize */
    for ( int i = 0; i < cellBounds.size(); ++i ) {
      int currentOrigin = cellBounds.at( i ).first;
      int currentWidth = cellBounds.at( i ).second;

      div_t multiple = div( currentWidth, selectedPatternSize );
      if ( multiple.rem != 0 ) {
        emit statusBar_error( rowMsg + "non-matching block size" );
        return false;
      }

      if ( multiple.quot != 1 ) {
        for ( int cell = 0; cell < multiple.quot; ++cell ) {
          finalCells.push_back( QPair<int, int>(
                                  currentOrigin + cell*selectedPatternSize,
                                  selectedPatternSize ) );
        }
      } else {
        finalCells.push_back( cellBounds.at( i ) );
      }
    }

    /* this row checks out */
    finalCellLayout.push_back( finalCells );
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
  QList<PatternGridItem*> patternItems( activeItems_.values() );
  foreach( PatternGridItem* anItem, patternItems ) {
    anItem->set_background_color( backgroundColor_ );
  }
}


//--------------------------------------------------------------
// given a point on the canvas, determines which column/row the
// click was in.
// NOTE: the point does not have to be in the actual pattern
// grid and the caller is responsible to make sense out of
// what ever column/row pair it receives
//---------------------------------------------------------------
QPair<int, int> GraphicsScene::get_cell_coords_(
  const QPointF& mousePos ) const
{
  qreal xPosRel = mousePos.x() - origin_.x();
  qreal yPosRel = mousePos.y() - origin_.y();

  int column = static_cast<int>( floor( xPosRel / gridCellDimensions_.width() ) );
  int row    = static_cast<int>( floor( yPosRel / gridCellDimensions_.height() ) );

  return QPair<int, int>( column, row );
}



//-------------------------------------------------------------
// activate a complete row
// In order to accomplish this we create a rectangle that
// covers all cells in the row, then get all the items and
// the select them all.
// NOTE: This is simular to what we do with the RubberBand.
//-------------------------------------------------------------
void GraphicsScene::select_row_( int rowId )
{
  /* selector box dimensions */
  int xShift    = static_cast<int>( gridCellDimensions_.width() * 0.25 );
  int yShift    = static_cast<int>( gridCellDimensions_.height() * 0.25 );
  int xHalfCell = static_cast<int>( gridCellDimensions_.width() * 0.5 );
  int yHalfCell = static_cast<int>( gridCellDimensions_.height() * 0.5 );

  QPoint boxOrigin( origin_.x() + xShift,
                    rowId * gridCellDimensions_.height() + yShift );

  QSize boxDim(( numCols_ - 1 ) * gridCellDimensions_.width() + xHalfCell,
               yHalfCell );

  select_region( QRect( boxOrigin, boxDim ) );
}



//-------------------------------------------------------------
// activate a complete column
// In order to accomplish this we create a rectangle that
// covers all cells in the column, then get all the items and
// the select them all.
// NOTE: This is simular to what we do with the RubberBand.
//-------------------------------------------------------------
void GraphicsScene::select_column_( int colId )
{
  /* selector box dimensions */
  int xShift    = static_cast<int>( gridCellDimensions_.width() * 0.25 );
  int yShift    = static_cast<int>( gridCellDimensions_.height() * 0.25 );
  int xHalfCell = static_cast<int>( gridCellDimensions_.width() * 0.5 );
  int yHalfCell = static_cast<int>( gridCellDimensions_.height() * 0.5 );

  QPoint boxOrigin( colId * gridCellDimensions_.width() + xShift, yShift );
  QSize boxDim( xHalfCell, ( numRows_ - 1 ) * gridCellDimensions_.height()
                + yHalfCell );

  /* select items */
  select_region( QRect( boxOrigin, boxDim ) );
}



//----------------------------------------------------------------
// compute the origin of a grid cell based on its column and
// row index
//----------------------------------------------------------------
QPoint GraphicsScene::compute_cell_origin_( int col, int row ) const
{
  return QPoint( origin_.x() + col * gridCellDimensions_.width(),
                 origin_.y() + row * gridCellDimensions_.height() );
}



//-----------------------------------------------------------------
// returns a pointer to the PatternGridItem at the given row
// and column indices
//-----------------------------------------------------------------
PatternGridItem* GraphicsScene::patternGridItem_at_( int col, int row ) const
{
  assert( col >= 0 && col <= numCols_ );
  assert( row >= 0 && row <= numRows_ );

  QPointF center( origin_.x() + ( col + 0.5 ) * gridCellDimensions_.width(),
                  origin_.y() + ( row + 0.5 ) * gridCellDimensions_.height() );

  QList<PatternGridItem*> foundItems;
  QList<QGraphicsItem*> allItems = items( center );
  foreach( QGraphicsItem* anItem, allItems ) {
    PatternGridItem* cell = qgraphicsitem_cast<PatternGridItem*>( anItem );

    if ( cell != 0 ) {
      foundItems.push_back( cell );
    }
  }

  assert( foundItems.size() == 1 );

  return foundItems.first();
}


//-----------------------------------------------------------------
// compute the index of a given cell based on its present row
// and column
//-----------------------------------------------------------------
int GraphicsScene::compute_cell_index_( PatternGridItem* anItem ) const
{
  return ( anItem->row() * numCols_ ) + anItem->col();
}



//-----------------------------------------------------------------
// compute the row and column of a given cell based on the
// cell index
//-----------------------------------------------------------------
QPair<int, int> GraphicsScene::compute_from_cell_index_( int index ) const
{
  int row = static_cast<int>( index / numCols_ );
  int col = index;
  if ( row != 0 ) {
    col = index % numCols_;
  }

  return QPair<int, int>( row, col );
}


//-------------------------------------------------------------
// create the grid
//-------------------------------------------------------------
void GraphicsScene::create_pattern_grid_()
{
  /* grid */
  for ( int col = 0; col < numCols_; ++col ) {
    for ( int row = 0; row < numRows_; ++row ) {
      PatternGridItem* item =
        new PatternGridItem( QSize( 1, 1 ), gridCellDimensions_, col, row, this );
      item->Init();
      item->setPos( compute_cell_origin_( col, row ) );
      item->insert_knitting_symbol( defaultSymbol_ );

      /* add it to our scene */
      add_patternGridItem_( item );
    }
  }
}



//-------------------------------------------------------------
// create or update the column labels
//-------------------------------------------------------------
void GraphicsScene::create_grid_labels_()
{
  /* remove all existing labels if there are any */
  QList<QGraphicsItem*> allItems( items() );
  QList<PatternGridLabel*> allLabels;
  foreach( QGraphicsItem* aLabel, allItems ) {
    PatternGridLabel* label =
      qgraphicsitem_cast<PatternGridLabel*>( aLabel );

    if ( label != 0 ) {
      allLabels.push_back( label );
    }
  }

  foreach( PatternGridLabel* aLabel, allLabels ) {
    removeItem( aLabel );
    aLabel->deleteLater();
  }

  /* add new column labels */
  QString label;
  qreal yPos = origin_.y() + numRows_ * gridCellDimensions_.height() + 1;

  for ( int col = 0; col < numCols_; ++col ) {
    int colNum = numCols_ - col;
    PatternGridLabel* text = new PatternGridLabel(
      label.setNum( colNum ),
      PatternGridLabel::ColLabel
    );

    int shift =
      compute_horizontal_label_shift_( colNum, textFont_.pointSize() );
    text->setPos( origin_.x() + col*gridCellDimensions_.width() + shift, yPos );
    text->setFont( textFont_ );
    addItem( text );
  }


  /* add new row labels
   * FIXME: the exact placement of the labels is hand-tuned
   * and probably not very robust */
  QFontMetrics metric( textFont_ );
  int fontHeight = metric.ascent();
  for ( int row = 0; row < numRows_; ++row ) {
    PatternGridLabel* text = new PatternGridLabel(
      label.setNum( numRows_ - row ),
      PatternGridLabel::RowLabel
    );

    text->setPos( origin_.x() + ( numCols_*gridCellDimensions_.width() )
                  + 0.1*gridCellDimensions_.width(),
                  origin_.y() + row*gridCellDimensions_.height()
                  + 0.5*( gridCellDimensions_.height() - 1.8*fontHeight ) );
    text->setFont( textFont_ );
    addItem( text );
  }
}



//---------------------------------------------------------------
// shift the pattern grid by one column and/or row wise starting
// at the specified column and row indices.
// This is mainly used when inserting/deleting columns/rows
//--------------------------------------------------------------
void GraphicsScene::expand_grid_( int colPivot, int rowPivot )
{
  QList<QGraphicsItem*> allItems( items() );

  /* go through all items and make sure that that
   * inserting the columns won't cut through any
   * multy row cells */
  foreach( QGraphicsItem* anItem, allItems ) {
    PatternGridItem* cell =
      qgraphicsitem_cast<PatternGridItem*>( anItem );

    if ( cell != 0 ) {
      /* do we want to shift the columns */
      if ( colPivot != NOSHIFT ) {
        if ( cell->col() >= colPivot ) {
          cell->reseat( cell->col() + 1, cell->row() );
          cell->setPos( compute_cell_origin_( cell->col(), cell->row() ) );
        }
      }

      /* do we want to shift the rows */
      if ( rowPivot != NOSHIFT ) {
        if ( cell->row() > rowPivot ) {
          /* Note: we shift the cell first and can the just
           * use its new position, i.e. no row()+1 in set Pos */
          cell->reseat( cell->col(), cell->row() + 1 );
          cell->setPos( compute_cell_origin_( cell->col(), cell->row() ) );
        }
      }
    }
  }

  /* adjust the row/col count and also shift the legend items */
  if ( colPivot != NOSHIFT ) {
    shift_legend_items_horizontally_( colPivot, gridCellDimensions_.width() );
    numCols_ += 1;
  }

  if ( rowPivot != NOSHIFT ) {
    shift_legend_items_vertically_( rowPivot, gridCellDimensions_.height() );
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
  QList<QGraphicsItem*> allItems( items() );
  QList<QGraphicsItem*> nonSvgItems;
  foreach( QGraphicsItem* anItem, allItems ) {
    if ( anItem->type() != QGraphicsSvgItem::Type ) {
      nonSvgItems.push_back( anItem );
    }
  }

  foreach( QGraphicsItem* finalItem, nonSvgItems ) {
    removeItem( finalItem );
    delete finalItem;
  }
}



//------------------------------------------------------------
// update the canvas, i.e., add the currently selected
// knitting symbol/color to all active items.
//------------------------------------------------------------
void GraphicsScene::update_active_items_()
{
  if ( selectedSymbol_->patternName() != "" ) {
    try_place_knitting_symbol_();
  }
}



//-----------------------------------------------------------
// return if a row of PatternGridItems is contiguous, i.e.
// there are no holes, and the number of unit cells covered
// by the row (holes not counted)
//-----------------------------------------------------------
QPair<bool, int> GraphicsScene::is_row_contiguous_(
  const RowItems& aRow ) const
{
  /* an empty row is contiguous */
  if ( aRow.empty() ) {
    return QPair<bool, int>( true, 0 );
  }

  int currentCol = aRow.at( 0 )->col();
  int rowWidth   = aRow.at( 0 )->dim().width();
  int totalWidth = 0;
  bool status    = true;
  for ( int index = 1; index < aRow.size(); ++index ) {
    int rowCol   = aRow.at( index )->col();
    if (( currentCol + rowWidth ) != rowCol ) {
      status = false;
    }

    currentCol = rowCol;
    totalWidth += rowWidth;
    rowWidth = aRow.at( index )->dim().width();
  }

  return QPair<bool, int>( status, totalWidth );
}


//-------------------------------------------------------------
// given a list of RowItems, determines the size of the
// rectangle that bounds them all. The rows are assumed
// to be in increasing order of y with respect to the
// origin
//-------------------------------------------------------------
QRect GraphicsScene::find_bounding_rectangle_(
  const QList<RowItems>& rows ) const
{
  assert( !rows.empty() );

  /* get index of upper left corner */
  RowItems firstRow = rows.first();
  assert( !firstRow.empty() );
  int upperLeftColIndex = firstRow.first()->col();
  int upperLeftRowIndex = firstRow.first()->row();

  /* get index of lower right corner */
  RowItems lastRow = rows.last();
  assert( !lastRow.empty() );
  int lowerRightColIndex  = lastRow.last()->col();
  int lowerRightRowIndex  = lastRow.last()->row();
  int lowerRightCellWidth = lastRow.last()->dim().width();
  int lowerRightCellHeight = lastRow.last()->dim().height();

  /* compute coordinates */
  QPoint upperLeftCorner( origin_.x() + upperLeftColIndex * gridCellDimensions_.width(),
                          origin_.y() + upperLeftRowIndex
                          * gridCellDimensions_.height() );

  QPoint lowerRightCorner( origin_.x() - 1
                           + ( lowerRightColIndex + lowerRightCellWidth )
                           * gridCellDimensions_.width(),
                           origin_.y() - 1
                           + ( lowerRightRowIndex + lowerRightCellHeight )
                           * gridCellDimensions_.height() );

  return QRect( upperLeftCorner, lowerRightCorner );
}



//--------------------------------------------------------------
// handle mouse clicks on the boundary of any of the marker
// rectangles
//--------------------------------------------------------------
bool GraphicsScene::handle_click_on_marker_rectangle_(
  const QGraphicsSceneMouseEvent* mouseEvent )
{
  /* get all items at pos and grab all patternGridRectangles
   * if any */
  QPointF mousePos( mouseEvent->scenePos() );
  QList<QGraphicsItem*> itemsUnderMouse = items( mousePos );

  QList<PatternGridRectangle*> rectangles;
  foreach( QGraphicsItem* anItem, itemsUnderMouse ) {
    PatternGridRectangle* rectAngle =
      qgraphicsitem_cast<PatternGridRectangle*>( anItem );
    if ( rectAngle != 0 ) {
      if ( rectAngle->selected( mousePos ) ) {
        rectangles.push_back( rectAngle );
      }
    }
  }

  if ( !rectangles.empty() ) {
    /* we allow only one rectangle to be selected at a time */
    if ( rectangles.size() > 1 ) {
      emit statusBar_error( tr( "Multiple rectangles selected." ) );
      return false;
    }

    show_rectangle_manage_menu_( rectangles.front(),
                                 mouseEvent->screenPos() );

    return true;
  }

  return false;
}



//--------------------------------------------------------------
// handle mouse clicks inside the grid array
//--------------------------------------------------------------
bool GraphicsScene::handle_click_on_grid_array_(
  const QGraphicsSceneMouseEvent* mouseEvent )
{
  QPair<int, int> arrayIndex( get_cell_coords_( mouseEvent->scenePos() ) );
  int column = arrayIndex.first;
  int row    = arrayIndex.second;


  /* show menu only if we're inside the pattern grid */
  if ( column >= 0 &&  column < numCols_ &&
       row >= 0 && row < numRows_ ) {

    /* indicate currently selected rows and columns */
    selectedCol_ = column;
    selectedRow_ = row;

    /* fire up menu */
    QMenu gridMenu;
    QAction* copyAction = gridMenu.addAction( "&Copy" );
    QAction* pasteAction = gridMenu.addAction( "&Paste" );

    gridMenu.addSeparator();

    QAction* rowAction  = gridMenu.addAction( "Insert/delete rows & columns" );

    connect( rowAction,
             SIGNAL( triggered() ),
             this,
             SLOT( open_row_col_menu_() ) );

    connect( copyAction,
             SIGNAL( triggered() ),
             this,
             SLOT( copy_items_() ) );

    connect( pasteAction,
             SIGNAL( triggered() ),
             this,
             SLOT( paste_items_() ) );

    gridMenu.exec( mouseEvent->screenPos() );
  }


  return true;
}



//----------------------------------------------------------------
// handle mouse clicks on the grid labels
//----------------------------------------------------------------
bool GraphicsScene::handle_click_on_grid_labels_(
  const QGraphicsSceneMouseEvent* mouseEvent )
{
  QPointF currentPos = mouseEvent->scenePos();
  QPair<int, int> arrayIndex( get_cell_coords_( currentPos ) );
  int column = arrayIndex.first;
  int row    = arrayIndex.second;

  if ( column == numCols_ ) {
    select_row_( row );
  } else if ( row == numRows_ ) {
    select_column_( column );
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
  PatternGridRectangle* rect, const QPoint& pos )
{

  QMenu rectangleMenu;

  QAction* deleteRectAction =
    rectangleMenu.addAction( tr( "delete rectangle" ) );
  QSignalMapper* rectangleDeleter = new QSignalMapper( this );
  rectangleDeleter->setMapping( deleteRectAction, rect );

  connect( deleteRectAction,
           SIGNAL( triggered() ),
           rectangleDeleter,
           SLOT( map() ) );

  connect( rectangleDeleter,
           SIGNAL( mapped( QObject* ) ),
           this,
           SLOT( mark_rectangle_for_deletion_( QObject* ) ) );


  QAction* customizeRectAction =
    rectangleMenu.addAction( tr( "customize rectangle" ) );
  QSignalMapper* rectangleCustomizer = new QSignalMapper( this );
  rectangleCustomizer->setMapping( customizeRectAction, rect );

  connect( customizeRectAction,
           SIGNAL( triggered() ),
           rectangleCustomizer,
           SLOT( map() ) );

  connect( rectangleCustomizer,
           SIGNAL( mapped( QObject* ) ),
           this,
           SLOT( customize_rectangle_( QObject* ) ) );


  rectangleMenu.exec( pos );
}



//-------------------------------------------------------------
// use this function to add a PatternGridItem to the scene.
// In addition to that we also update the referene count of
// currently active knitting symbols
//-------------------------------------------------------------
void GraphicsScene::add_patternGridItem_( PatternGridItem* anItem )
{
  addItem( anItem );
  notify_legend_of_item_addition_( anItem->get_knitting_symbol(),
                                   anItem->color(), "chartLegendItem" );
}



//-------------------------------------------------------------
// use this function to remove a PatternGridItem from the scene.
// In addition to that we also update the referene count of
// currently active knitting symbols
//-------------------------------------------------------------
void GraphicsScene::remove_patternGridItem_( PatternGridItem* anItem )
{
  removeItem( anItem );
  notify_legend_of_item_removal_( anItem->get_knitting_symbol(),
                                  anItem->color(), "chartLegendItem" );

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
  KnittingSymbolPtr aSymbol, QString colorName )
{
  QString description =
    aSymbol->patternName() + " = " + aSymbol->instructions();
  QString fullName = aSymbol->category() + aSymbol->patternName()
                     + colorName;
  if ( !symbolDescriptors_.contains( fullName ) ) {
    symbolDescriptors_[fullName] = description;
  } else {
    description = symbolDescriptors_[fullName];
  }

  return format_string( description );
}



//---------------------------------------------------------------
// computes the best possible y position for a new legend item.
// We try to place right under all currently exisiting legend
// items and the pattern grid
//---------------------------------------------------------------
int GraphicsScene::get_next_legend_items_y_position_() const
{
  QList<QGraphicsItem*> allLegendGraphicsItems =
    get_all_legend_items_();

  int yMaxLegend = static_cast<int>(
                     floor( get_max_y_coordinate( allLegendGraphicsItems ) ) );
  int yMaxGrid = ( numRows_ + 1 ) * gridCellDimensions_.height()  + origin_.y();
  int yMax = qMax( yMaxGrid, yMaxLegend );

  return ( yMax + gridCellDimensions_.width() * 0.5 );
}



//--------------------------------------------------------------
// return a list of all QGraphicsItems currently in the legend
//--------------------------------------------------------------
QList<QGraphicsItem*> GraphicsScene::get_all_legend_items_() const
{
  return get_all_text_legend_items_() + get_all_svg_legend_items_();
}



//--------------------------------------------------------------
// return a list of all QGraphicsItems containing text
// currently in the legend
//--------------------------------------------------------------
QList<QGraphicsItem*> GraphicsScene::get_all_text_legend_items_() const
{
  QList<LegendEntry> allLegendEntries( legendEntries_.values() );
  QList<QGraphicsItem*> allLegendGraphicsItems;
  foreach( LegendEntry item, allLegendEntries ) {
    allLegendGraphicsItems.push_back( item.second );
  }

  return allLegendGraphicsItems;
}



//--------------------------------------------------------------
// return a list of all QGraphicsItems containing an SVG
// item currently in the legend
//--------------------------------------------------------------
QList<QGraphicsItem*> GraphicsScene::get_all_svg_legend_items_() const
{
  QList<LegendEntry> allLegendEntries( legendEntries_.values() );
  QList<QGraphicsItem*> allLegendGraphicsItems;
  foreach( LegendEntry item, allLegendEntries ) {
    allLegendGraphicsItems.push_back( item.first );
  }

  return allLegendGraphicsItems;
}



//-------------------------------------------------------------
// Update the legend labels after a settings change
//-------------------------------------------------------------
void GraphicsScene::update_legend_labels_()
{
  QList<LegendEntry> allItems( legendEntries_.values() );

  foreach( LegendEntry item, allItems ) {
    item.second->setFont( textFont_ );
  }
}



//-------------------------------------------------------------
// shift all legend items below pivot by "distance"
// vertically
//-------------------------------------------------------------
void GraphicsScene::shift_legend_items_vertically_( int pivot,
    int globalDistance, int perItemDistance )
{
  int pivotYPos = pivot * gridCellDimensions_.height();

  /* shift all svg legend items; use a QMultimap for sorting
   * legend items by y position */
  QList<QGraphicsItem*> svgLegendItems = get_all_svg_legend_items_();
  move_graphicsItems_vertically( svgLegendItems, pivotYPos,
                                 globalDistance, perItemDistance );

  /* shift all svg legend items; use a QMultimap for sorting
   * legend items by y position */
  QList<QGraphicsItem*> textLegendItems = get_all_text_legend_items_();
  move_graphicsItems_vertically( textLegendItems, pivotYPos,
                                 globalDistance, perItemDistance );
}



//-------------------------------------------------------------
// shift all legend items right of pivot by distance
// horizontally. Leave items that are above or below the
// pattern grid alone.
//-------------------------------------------------------------
void GraphicsScene::shift_legend_items_horizontally_( int pivot,
    int distance )
{
  int pivotXPos = pivot * gridCellDimensions_.width();

  /* find all legend items right of the pivot */
  QList<QGraphicsItem*> allLegendItems = get_all_legend_items_();

  foreach( QGraphicsItem* item, allLegendItems ) {
    QPointF itemPos = item->pos();
    if ( itemPos.x() > pivotXPos
         && itemPos.y() > 0.0
         && itemPos.y() < ( numRows_ * gridCellDimensions_.height() ) ) {
      item->setPos( itemPos.x() + distance, itemPos.y() );
    }
  }
}



QT_END_NAMESPACE
