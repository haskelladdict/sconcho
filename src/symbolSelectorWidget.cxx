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
#include <QLabel>
#include <QMouseEvent>
#include <QSvgWidget>
#include <QTabWidget>
#include <QVBoxLayout>

/** local headers */
#include "basicDefs.h"
#include "symbolSelectorItem.h"
#include "symbolSelectorWidget.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
SymbolSelectorWidget::SymbolSelectorWidget(QWidget* myParent)
    :
      QTabWidget(myParent),
      highlightedItem_(0)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool SymbolSelectorWidget::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* call individual initialization routines */
  create_tabs_();

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
// switch the currently highlighted item
// If state == true and item requests to be highlighted. In
// this case we first unselect the currently selected item
// if any and then select the new item.
// If state == false we simply unselect.
//-------------------------------------------------------------
void SymbolSelectorWidget::change_highlighted_item(
    SymbolSelectorItem* newItem, bool state)
{
  if (highlightedItem_ != 0)
  {
    highlightedItem_->unselect();
  }

  if (state)
  {
    highlightedItem_ = newItem;
    highlightedItem_->select();
    emit selected_symbol_changed(newItem->symbol_name());
  }
  else
  {
    highlightedItem_ = 0;
    emit selected_symbol_changed("");
  }
} 




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

//-------------------------------------------------------------
// add an SvgWidget representing an knitting pattern to the
// list of available widgets 
//-------------------------------------------------------------
QHBoxLayout* SymbolSelectorWidget::create_symbol_layout_(
    const QString& fileName, const QString& symbolName) 
{
  SymbolSelectorItem* symbol = new SymbolSelectorItem(fileName,
      this);
  symbol->Init();
 
  QLabel* symbolLabel = new QLabel(symbolName);
  QHBoxLayout* symbolLayout = new QHBoxLayout;
  symbolLayout->addWidget(symbol);
  symbolLayout->addWidget(symbolLabel);
  symbolLayout->addStretch(1);

  return symbolLayout;
}


//-------------------------------------------------------------
// create all tabs
//-------------------------------------------------------------
void SymbolSelectorWidget::create_tabs_()
{
  QString path = "../trunk/symbols/";
  QList<QString> symbols;
  symbols.push_back("knit");
  symbols.push_back("purl");
  symbols.push_back("yo");

  QVBoxLayout* mainLayout = new QVBoxLayout(this);
  for (int i = 0; i < symbols.length(); ++i)
  {
     mainLayout->addLayout(create_symbol_layout_(
           path + symbols[i] + ".svg", 
           symbols[i]));
  }
  mainLayout->addStretch(1);
  setLayout(mainLayout);
}


