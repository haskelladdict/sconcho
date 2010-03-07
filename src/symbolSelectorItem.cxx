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
#include <QMenu>
#include <QMouseEvent>
#include <QSvgWidget>

/** local headers */
#include "basicDefs.h"
#include "symbolSelectorItem.h"


QT_BEGIN_NAMESPACE


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
SymbolSelectorItem::SymbolSelectorItem(int cellSize,
  KnittingSymbolPtr symbol, QWidget* myParent)
  :
    QFrame(myParent),
    selected_(false),
    unitSize_(cellSize),
    symbol_(symbol)
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
  selectedStyleSheet_ = "border-width: 1px;"
                        "border-style: solid;"
                        "border-color: red;"
                        "background-color: lightblue;";


  unselectedStyleSheet_ = "border-width: 1px;"
                          "border-style: solid;"
                          "border-color: black;"
                          "background-color: white;";

  setStyleSheet(unselectedStyleSheet_);
  
  /* create and adjust our QSvgWidget */
  QSvgWidget* symbolSvg_ = new QSvgWidget(symbol_->path());
  QSize symbolSize = unitSize_ * symbol_->dim();
  symbolSvg_->setMaximumSize(symbolSize);

  QHBoxLayout* svgLayout = new QHBoxLayout;
  svgLayout->setContentsMargins(0,0,0,0);
  svgLayout->addWidget(symbolSvg_);
  setLayout(svgLayout);

  /* add tool tip */
  setToolTip(symbol_->instructions());
  
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
const KnittingSymbolPtr SymbolSelectorItem::symbol_info() const
{
  return symbol_;
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
  /* a right button click opens up a menu for further action */
  if (mouseEvent->button() == Qt::RightButton)
  {
    show_symbol_menu_(mouseEvent->globalPos());
  }
  else
  {
    if (selected_)
    {
      emit highlight_me(this, false);
    }
    else
    {
      emit highlight_me(this, true);
    }
  }

  repaint();
}




/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

//------------------------------------------------------------
// send our KnittingSymbol to our parent widget so it can
// be added to the legend
//------------------------------------------------------------
void SymbolSelectorItem::send_legend_item_()
{
  emit new_legend_item(symbol_);
}



/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//---------------------------------------------------------------
// open a simple menu with further actions possible for 
// knitting symbol items (like adding them to the legend)
//---------------------------------------------------------------
void SymbolSelectorItem::show_symbol_menu_(const QPoint& symPos) const
{
  QMenu symbolMenu;
  QAction* addToLegendAction = symbolMenu.addAction("add to legend");

  connect(addToLegendAction,
          SIGNAL(triggered()),
          this,
          SLOT(send_legend_item_())
         );

  symbolMenu.exec(symPos);
}



QT_END_NAMESPACE
