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
#include <QColorDialog>
#include <QDebug>
#include <QHBoxLayout>
#include <QMenu>
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

  connect(this,
          SIGNAL(selector_color_changed(const QColor&)),
          parent(),
          SIGNAL(color_changed(const QColor&))
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
  emit selector_color_changed(color_);
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
  if ((mouseEvent->button() == Qt::LeftButton) && !selected_)
  {
    emit highlight_me(this);
  }
  else if (mouseEvent->button() == Qt::RightButton)
  {
    show_property_menu_(mouseEvent->globalPos());
  }

  repaint();
}



/*************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

//------------------------------------------------------------
// show a color selector dialog to let user select our new
// color
//------------------------------------------------------------
void ColorSelectorItem::pick_color_()
{
  QColor selection = QColorDialog::getColor(color_ , 0,
    "Select custom color");
  
  set_color(selection);
  emit selector_color_changed(color_);
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


//--------------------------------------------------------------
// show menu to allow user to customize the our color
//--------------------------------------------------------------
void ColorSelectorItem::show_property_menu_(const QPoint& aPos)
{
  QMenu propertyMenu;
  QAction* customizeColorAction =  
    propertyMenu.addAction("customize color");

  connect(customizeColorAction,
          SIGNAL(triggered()),
          this,
          SLOT(pick_color_())
         );

  propertyMenu.exec(aPos);
}



QT_END_NAMESPACE
