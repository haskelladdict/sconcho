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
#include <float.h>


/* Qt headers */
#include <QColor>
#include <QDebug>
#include <QGraphicsSceneMouseEvent>

/* local headers */
#include "graphicsScene.h"
#include "patternGridItem.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternGridItem::PatternGridItem( const QSize& aDim,
                                  const QSize& aspectRatio, int aCol, int aRow,
                                  GraphicsScene* myParent, const QColor& aBackColor,
                                  const QPoint& aLoc )
    :
    KnittingPatternItem( aDim, aspectRatio, aBackColor, aLoc ),
    selected_( false ),
    parent_( myParent ),
    columnIndex_( aCol ),
    rowIndex_( aRow )
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternGridItem::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED ) {
    return false;
  }

  /* initialize our parent */
  KnittingPatternItem::Init();

  /* set up some properties */
  setFlags( QGraphicsItem::ItemIsSelectable );

  /* some signals and slots */
  connect( this,
           SIGNAL( item_selected( PatternGridItem*, bool ) ),
           parent_,
           SLOT( grid_item_selected( PatternGridItem*, bool ) ) );

  connect( this,
           SIGNAL( item_reset( PatternGridItem* ) ),
           parent_,
           SLOT( grid_item_reset( PatternGridItem* ) ) );


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

//--------------------------------------------------------------
// move this cell to a new location (in the pattern grid
// array) on the canvas.
//--------------------------------------------------------------
void PatternGridItem::reseat( int newCol, int newRow )
{
  columnIndex_ = newCol;
  rowIndex_ = newRow;
}


//--------------------------------------------------------------
// select this grid cell and turn highlighting on/off based
// on its current status
//--------------------------------------------------------------
void PatternGridItem::select()
{
  if ( selected_ ) {
    highlight_off_();
    emit item_selected( this, false );
  } else {
    highlight_on_();
    emit item_selected( this, true );
  }

  update();
}


//--------------------------------------------------------------
// return our custom type
//--------------------------------------------------------------
int PatternGridItem::type() const
{
  return Type;
}


/**************************************************************
 *
 * PROTECTED MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// handle mouse press events
//-------------------------------------------------------------
void PatternGridItem::mousePressEvent(
  QGraphicsSceneMouseEvent* anEvent )
{
  /* ignore right mouse clicks */
  if ( anEvent->button() == Qt::RightButton ) {
    return;
  }

  /* if the user has control pressed we ignore this event */
  if ( anEvent->modifiers().testFlag( Qt::ControlModifier ) ) {
    anEvent->ignore();
    return;
  }

  /* if the user has shift pressed this is a reset event
   * otherwise a select/deselect event */
  if ( anEvent->modifiers().testFlag( Qt::ShiftModifier ) ) {
    emit item_reset( this );
  } else {
    select();
  }
}


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

//-----------------------------------------------------------------
// helper function for doing the internal housekeeping during
// selecting/deselecting
// NOTE: these functions should not emit an item_selected signal
//-----------------------------------------------------------------
void PatternGridItem::highlight_on_()
{
  selected_ = true;
//  currentColor_ = highlightColor_;
  select_highlight_color();
}


void PatternGridItem::highlight_off_()
{
  selected_ = false;
//  currentColor_ = backColor_;
  select_background_color();
}


QT_END_NAMESPACE
