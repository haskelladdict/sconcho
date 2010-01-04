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
#include <QDebug>
#include <QHBoxLayout>
#include <QPushButton>
#include <QToolButton>
#include <QVBoxLayout>

/** local headers */
#include "basicDefs.h"
#include "colorSelectorItem.h"
#include "colorSelectorWidget.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
ColorSelectorWidget::ColorSelectorWidget(QWidget* myParent)
    :
      QWidget(myParent)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool ColorSelectorWidget::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* call individual initialization routines */
  create_layout_();

  return true;
}


/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 *************************************************************/

/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// switch the currently selected color selected to the newly
// selected one
//-------------------------------------------------------------
void ColorSelectorWidget::highlight_color_button(
  ColorSelectorItem* newActiveItem)
{
  activeSelector_->unselect();
  activeSelector_ = newActiveItem;
  activeSelector_->select();

  emit color_changed(newActiveItem->get_color());
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//----------------------------------------------------------------
// main interface creation function
//----------------------------------------------------------------
void ColorSelectorWidget::create_layout_()
{
  QHBoxLayout* topSelectorLayout = new QHBoxLayout;
  QList<QString> topColorList;
  topColorList << "white" << "red" << "green"
               << "blue" << "cyan";

  foreach(QString color, topColorList)
  {
    ColorSelectorItem* newItem = new ColorSelectorItem(color,this);
    newItem ->Init();
    topSelectorLayout->addWidget(newItem);

    /* activate white as default background color */
    if ( color == "white" )
    {
      newItem->select();
      activeSelector_ = newItem;
    }
  }


  QHBoxLayout* bottomSelectorLayout = new QHBoxLayout;
  QList<QString> bottomColorList;
  bottomColorList << "yellow" << "gray" << "magenta"
               << "darkBlue" << "darkMagenta";

  foreach(QString color, bottomColorList)
  {
    ColorSelectorItem* newItem = new ColorSelectorItem(color,this);
    newItem ->Init();
    bottomSelectorLayout->addWidget(newItem);
  }
  
  QVBoxLayout* mainLayout = new QVBoxLayout;
  mainLayout->addLayout(topSelectorLayout);
  mainLayout->addLayout(bottomSelectorLayout);
  setLayout(mainLayout);
}




QT_END_NAMESPACE
