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

/* Qt headers */
#include <QDebug>
#include <QGraphicsSceneMouseEvent>
#include <QMenu>

/* local headers */
#include "legendItem.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
LegendItem::LegendItem( const QSize& aDim, const QString& tag,
                        const QSize& aspectRatio, const QColor& aBackColor, const QPoint& aLoc )
    :
    KnittingPatternItem( aDim, aspectRatio, aBackColor, aLoc ),
    idTag_( tag )
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool LegendItem::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED ) {
    return false;
  }

  /* initialize our parent */
  KnittingPatternItem::Init();

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
// return our custom type
//--------------------------------------------------------------
int LegendItem::type() const
{
  return Type;
}


/**************************************************************
 *
 * PROTECTED MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// event handler for mouse press event
//-------------------------------------------------------------
void LegendItem::mousePressEvent(
  QGraphicsSceneMouseEvent* mouseEvent )
{
  /* a right button click opens up a menu with further actions */
  if ( mouseEvent->button() == Qt::RightButton ) {
    show_options_menu_( mouseEvent->screenPos() );
  }

  KnittingPatternItem::mousePressEvent( mouseEvent );
}



/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// gets everything ready for deleting ourselved ans sends
// a signal to canvas once done
//-------------------------------------------------------------
void LegendItem::delete_me_()
{
  emit delete_from_legend( get_knitting_symbol(), color(),
                           idTag_ );
}



/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// menu with options available through right clicking on the
// symbol
//-------------------------------------------------------------
void LegendItem::show_options_menu_( const QPoint& symPos ) const
{
  QMenu legendItemMenu;
  QAction* deleteItemAction = legendItemMenu.addAction( "delete" );

  /* grey action out unless we are an extra item */
  if ( idTag_ != "extraLegendItem" ) {
    deleteItemAction->setDisabled( true );
  }

  connect( deleteItemAction,
           SIGNAL( triggered() ),
           this,
           SLOT( delete_me_() )
         );

  legendItemMenu.exec( symPos );
}



QT_END_NAMESPACE
