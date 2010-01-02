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
#include <QHBoxLayout>
#include <QLabel>
#include <QMultiHash>
#include <QScrollArea>
#include <QTabWidget>
#include <QVBoxLayout>

/** local headers */
#include "basicDefs.h"
#include "io.h"
#include "symbolSelectorItem.h"
#include "symbolSelectorWidget.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
SymbolSelectorWidget::SymbolSelectorWidget(
  const QList<KnittingSymbolPtr>& symbols, int cellSize,
  QWidget* myParent)
    :
      QTabWidget(myParent),
      cellSize_(cellSize),
      allSymbols_(symbols),
      highlightedItem_(0),
      defaultSymbol_(emptyKnittingSymbol)
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
    emit selected_symbol_changed(newItem->symbol_info());
  }
  else
  {
    highlightedItem_ = 0;
    emit selected_symbol_changed(emptyKnittingSymbol);
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
  KnittingSymbolPtr aSym)
{
  /* the knitting symbol is our default so we'll have
   * to keep a pointer to it */
  if (aSym->patternName() == "knit")
  {
    defaultSymbol_ = aSym;
  }

  SymbolSelectorItem* symbol = 
    new SymbolSelectorItem(cellSize_, aSym, this);
  symbol->Init();
 
  QLabel* symbolLabel = new QLabel(aSym->patternName());
  QHBoxLayout* symbolLayout = new QHBoxLayout;
  symbolLayout->addWidget(symbol);
  symbolLayout->addSpacing(20);
  symbolLayout->addWidget(symbolLabel);
  symbolLayout->addStretch(1);

  return symbolLayout;
}


//-------------------------------------------------------------
// create all tabs
//-------------------------------------------------------------
void SymbolSelectorWidget::create_tabs_()
{
  /* organize all knitting symbols into their categories */
  QMultiHash<QString,KnittingSymbolPtr> symbolHash;
  foreach(KnittingSymbolPtr sym, allSymbols_)
  {
    symbolHash.insert(sym->category(), sym);
  }

  /* loop over all categories and greate the tabs */
  QList<QString> theKeys(symbolHash.uniqueKeys());
  QList<QString>::iterator key;
  for (key = theKeys.begin(); key != theKeys.end(); ++key)
  {
    QVBoxLayout* symbolLayout = new QVBoxLayout;
    foreach(KnittingSymbolPtr aSym, symbolHash.values(*key))
    {
      symbolLayout->addLayout(create_symbol_layout_(aSym));
    }
   
    /* create the tab */
    QScrollArea* scrollArea = new QScrollArea(this);
    QWidget* symbolsWidget = new QWidget;
    symbolsWidget->setLayout(symbolLayout);
    scrollArea->setWidget(symbolsWidget);
    addTab(scrollArea, *key);

    if (*key == "basic")
    {
      setCurrentWidget(scrollArea);
    }
  }
}


QT_END_NAMESPACE
