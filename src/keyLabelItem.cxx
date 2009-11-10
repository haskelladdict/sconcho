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
#include <QKeyEvent>

/** local headers */
#include "basicDefs.h"
#include "keyLabelItem.h"

QT_BEGIN_NAMESPACE


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
KeyLabelItem::KeyLabelItem(const QString& labelID, 
  const QString& text, QGraphicsItem* aParent)
  :
  QGraphicsTextItem(text, aParent),
  IDString_(labelID)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 *************************************************************/

//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool KeyLabelItem::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* set some basic properties */
  setTextInteractionFlags(Qt::TextEditorInteraction);
  
  return true;
}

//--------------------------------------------------------------
// return our custom type
//--------------------------------------------------------------
int KeyLabelItem::type() const
{
  return Type;
}


/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/

/**************************************************************
 *
 * PROTECTED 
 *
 *************************************************************/

//------------------------------------------------------------
// capture keypress events and make sure we send the current
// legend text upstream to the PatternKeyDialog
//------------------------------------------------------------
void KeyLabelItem::keyPressEvent(QKeyEvent* anEvent)
{
  QGraphicsTextItem::keyPressEvent(anEvent);
  emit label_changed(IDString_, toPlainText());
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

QT_END_NAMESPACE
