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
#include <QGroupBox>
#include <QHBoxLayout>
#include <QMouseEvent>
#include <QSvgWidget>

/** local headers */
#include "basicDefs.h"
#include "symbolSelectorItem.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
SymbolSelectorItem::SymbolSelectorItem(const QString& name, 
    QWidget* myParent)
  :
    QGroupBox(myParent),
    selected_(false),
    name_(name),
    symbolSvg_(new QSvgWidget(name))
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}



//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool SymbolSelectorItem::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* define style sheets */
  selectedStyleSheet_ = "border-width: 2px;"
                        "border-style: solid;"
                        "border-color: red;"
                        "background-color: lightblue;";


  unselectedStyleSheet_ = "border-width: 2px;"
                          "border-style: solid;"
                          "border-color: black;"
                          "background-color: white;";



  /* define the layout holding the pattern */ 
  setStyleSheet(unselectedStyleSheet_);

  /* adjust our QSvgWidget */
  symbolSvg_->setFixedSize(QSize(20,20));

  QHBoxLayout* svgLayout = new QHBoxLayout;
  svgLayout->addWidget(symbolSvg_);
  setLayout(svgLayout);

  /* connect slots */
  connect(this,
          SIGNAL(highlight_me(SymbolSelectorItem*, bool)),
          parent(),
          SLOT(change_highlighted_item(SymbolSelectorItem*,bool))
         );

  return true;
}


//------------------------------------------------------------
// mark us as selected unselectd
//------------------------------------------------------------
void SymbolSelectorItem::select()
{
  selected_ = true;
  setStyleSheet(selectedStyleSheet_);
}


void SymbolSelectorItem::unselect()
{
  selected_ = false;
  setStyleSheet(unselectedStyleSheet_);
}


//------------------------------------------------------------
// return our name 
//------------------------------------------------------------
QString SymbolSelectorItem::symbol_name()
{
  return name_;
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


/**************************************************************
 *
 * PROTECTED MEMBER FUNCTIONS 
 *
 *************************************************************/

//---------------------------------------------------------------
// event handler for mouse move events
//---------------------------------------------------------------
void SymbolSelectorItem::mousePressEvent(QMouseEvent* mouseEvent)
{
  if (selected_)
  {
    emit highlight_me(this, false);
  }
  else
  {
    emit highlight_me(this, true);
  }

  repaint();
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


