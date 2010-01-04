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

/** Qt headers */
#include <QColor>
#include <QDebug>
#include <QHBoxLayout>
#include <QMouseEvent>

/** local headers */
#include "basicDefs.h"
#include "colorSelectorItem.h"


QT_BEGIN_NAMESPACE


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
ColorSelectorItem::ColorSelectorItem(const QColor& aColor,
  QWidget* myParent)
  :
    QLabel(myParent),
    selected_(false),
    color_(aColor)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}



//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool ColorSelectorItem::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  setStyleSheet(get_inactive_stylesheet_());
  
  /* connect slots */
  connect(this,
          SIGNAL(highlight_me(ColorSelectorItem*)),
          parent(),
          SLOT(highlight_color_button(ColorSelectorItem*))
         );

  return true;
}


//------------------------------------------------------------
// mark us as selected unselectd
//------------------------------------------------------------
void ColorSelectorItem::select()
{
  selected_ = true;
  setStyleSheet(get_active_stylesheet_());
}


void ColorSelectorItem::unselect()
{
  selected_ = false;
  setStyleSheet(get_inactive_stylesheet_());
}


//-------------------------------------------------------------
// update the current color
//-------------------------------------------------------------
void ColorSelectorItem::set_color(const QColor& aColor)
{
  color_ = aColor;

  /* update the background */
  if (selected_)
  {
    setStyleSheet(get_active_stylesheet_());
  }
  else
  {
    setStyleSheet(get_inactive_stylesheet_());
  }
}
    


/**************************************************************
 *
 * PROTECTED MEMBER FUNCTIONS 
 *
 *************************************************************/

//---------------------------------------------------------------
// event handler for mouse move events
//---------------------------------------------------------------
void ColorSelectorItem::mousePressEvent(QMouseEvent* mouseEvent)
{
  Q_UNUSED(mouseEvent)

  if (!selected_)
  {
    emit highlight_me(this);
  }

  repaint();
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// returns the active stylesheet
//-------------------------------------------------------------
QString ColorSelectorItem::get_active_stylesheet_()
{
  QString activeStyleSheet =
    "border-width: 1px;"
    "border-style: dotted;"
    "border-color: black;"
    "background-clip: content;"
    "padding: 2px;"
    "min-height: 20px;"
    "max-height: 20px;"
    "min-width: 20px;"
    "max-width: 20px;";

  activeStyleSheet += "background-color: " + color_.name() + ";";

  return activeStyleSheet;
}


//-------------------------------------------------------------
// returns the in-active stylesheet
//-------------------------------------------------------------
QString ColorSelectorItem::get_inactive_stylesheet_()
{
  QString inactiveStyleSheet =
    "border-width: 1px;"
    "border-style: solid;"
    "border-color: black;"
    "background-clip: content;"
    "margin: 2px;"
    "min-height: 20px;"
    "max-height: 20px;"
    "min-width: 20px;"
    "max-width: 20px;";

  inactiveStyleSheet += "background-color: " + color_.name() + ";";

  return inactiveStyleSheet;
}

QT_END_NAMESPACE
