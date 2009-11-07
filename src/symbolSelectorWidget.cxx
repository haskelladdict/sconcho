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
#include <QScrollArea>
#include <QSvgWidget>
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
SymbolSelectorWidget::SymbolSelectorWidget(int cellSize,
  QWidget* myParent)
    :
      QTabWidget(myParent),
      cellSize_(cellSize),
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

  /* initialize empty symbol object */
  emptySymbol_ = KnittingSymbolPtr(
      new KnittingSymbol("","",QSize(0,0),"",""));

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
    emit selected_symbol_changed(emptySymbol_);
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
    const QString& symbolName, const QSize& aSize)
{
  /* create a new knittingSymbol object */
  QString patternPath = get_pattern_path(symbolName);
  KnittingSymbolPtr sym = KnittingSymbolPtr(
      new KnittingSymbol(patternPath,
                         symbolName,
                         aSize,
                         "",
                         ""));

  SymbolSelectorItem* symbol = 
    new SymbolSelectorItem(cellSize_, sym, this);
  symbol->Init();
 
  QLabel* symbolLabel = new QLabel(sym->baseName());
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
  /* basic symbols */
  QList<QString> symbols;
  symbols.push_back("basic/knit");
  symbols.push_back("basic/purl");
  symbols.push_back("basic/yo");
  symbols.push_back("basic/doubledec");
  symbols.push_back("basic/k2tog");
  symbols.push_back("basic/ssk");
  symbols.push_back("basic/m1");
  symbols.push_back("basic/ktbl");
  symbols.push_back("basic/ptbl");
  symbols.push_back("basic/nostitch");

  QVBoxLayout* basicLayout = new QVBoxLayout;
  for (int i = 0; i < symbols.length(); ++i)
  {
     basicLayout->addLayout(create_symbol_layout_(
           symbols[i], QSize(1,1)));
  }
  basicLayout->addStretch(1);
  
  QScrollArea* basicSymbolsScroll = new QScrollArea(this);
  QWidget* basicSymbols = new QWidget;
  basicSymbols->setLayout(basicLayout);
  basicSymbolsScroll->setWidget(basicSymbols);
  addTab(basicSymbolsScroll, QString("basic"));

  /* 2 stitch cables */
  QVBoxLayout* two_st_cableLayout = new QVBoxLayout;
  two_st_cableLayout->addLayout(
      create_symbol_layout_("2_st_cables/LT", QSize(2,1)));
  two_st_cableLayout->addLayout(
      create_symbol_layout_("2_st_cables/RT", QSize(2,1)));
  two_st_cableLayout->addStretch(1);

  QScrollArea* two_st_cableScroll = new QScrollArea(this);
  QWidget* two_st_cableSymbols = new QWidget;
  two_st_cableSymbols->setLayout(two_st_cableLayout);
  two_st_cableScroll->setWidget(two_st_cableSymbols);
  addTab(two_st_cableScroll, QString("2 st. cables"));

  /* 3 stitch cables */
  QVBoxLayout* three_st_cableLayout = new QVBoxLayout;
  three_st_cableLayout->addLayout(
    create_symbol_layout_("3_st_cables/1over2left-purl",
                          QSize(3,1)));
  three_st_cableLayout->addLayout(
    create_symbol_layout_("3_st_cables/1over2right-purl",
                          QSize(3,1)));
  three_st_cableLayout->addLayout(
    create_symbol_layout_("3_st_cables/1over2left",
                          QSize(3,1)));
  three_st_cableLayout->addLayout(
    create_symbol_layout_("3_st_cables/1over2right",
                          QSize(3,1)));
  three_st_cableLayout->addLayout(
    create_symbol_layout_("3_st_cables/2over1left-purl",
                          QSize(3,1)));
  three_st_cableLayout->addLayout(
    create_symbol_layout_("3_st_cables/2over1right-purl",
                          QSize(3,1)));
  three_st_cableLayout->addLayout(
    create_symbol_layout_("3_st_cables/2over1left",
                          QSize(3,1)));
  three_st_cableLayout->addLayout(
    create_symbol_layout_("3_st_cables/2over1right",
                          QSize(3,1)));
  three_st_cableLayout->addStretch(1);
  
  QScrollArea* three_st_cableScroll = new QScrollArea(this); 
  QWidget* three_st_cableSymbols = new QWidget;
  three_st_cableSymbols->setLayout(three_st_cableLayout);
  three_st_cableScroll->setWidget(three_st_cableSymbols);
  addTab(three_st_cableScroll, QString("3 st. cables"));

  /* 4 stitch cables */
  QVBoxLayout* four_st_cableLayout = new QVBoxLayout;
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/1over3left-purl",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/1over3right-purl",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/1over3left",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/1over3right",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/2over2left-purl",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/2over2right-purl",
                          QSize(4,1))); 
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/2over2left",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/2over2right",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/3over1left-purl",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/3over1right-purl",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/3over1left",
                          QSize(4,1)));
  four_st_cableLayout->addLayout(
    create_symbol_layout_("4_st_cables/3over1right",
                          QSize(4,1)));
  four_st_cableLayout->addStretch(1);
  
  QScrollArea* four_st_cableScroll = new QScrollArea(this);  
  QWidget* four_st_cableSymbols = new QWidget;
  four_st_cableSymbols->setLayout(four_st_cableLayout);
  four_st_cableScroll->setWidget(four_st_cableSymbols);
  addTab(four_st_cableScroll, QString("4 st. cables"));

  /* 6 stitch cables */
  QVBoxLayout* five_st_cableLayout = new QVBoxLayout;
  five_st_cableLayout->addLayout(
    create_symbol_layout_("5_st_cables/2over3left-purl",
                          QSize(5,1)));
  five_st_cableLayout->addLayout(
    create_symbol_layout_("5_st_cables/2over3right-purl",
                          QSize(5,1)));
  five_st_cableLayout->addLayout(
    create_symbol_layout_("5_st_cables/2over3left",
                          QSize(5,1)));
  five_st_cableLayout->addLayout(
    create_symbol_layout_("5_st_cables/2over3right",
                          QSize(5,1)));
  five_st_cableLayout->addLayout(
    create_symbol_layout_("5_st_cables/3over2left-purl",
                          QSize(5,1)));
  five_st_cableLayout->addLayout(
    create_symbol_layout_("5_st_cables/3over2right-purl",
                          QSize(5,1)));
  five_st_cableLayout->addLayout(
    create_symbol_layout_("5_st_cables/3over2left",
                          QSize(5,1)));
  five_st_cableLayout->addLayout(
    create_symbol_layout_("5_st_cables/3over2right",
                          QSize(5,1)));
  five_st_cableLayout->addStretch(1);
  
  QScrollArea* five_st_cableScroll = new QScrollArea(this);   
  QWidget* five_st_cableSymbols = new QWidget;
  five_st_cableSymbols->setLayout(five_st_cableLayout);
  five_st_cableScroll->setWidget(five_st_cableSymbols);
  addTab(five_st_cableScroll, QString("5 st. cables"));


  /* 6 stitch cables */
  QVBoxLayout* six_st_cableLayout = new QVBoxLayout;
  six_st_cableLayout->addLayout(
    create_symbol_layout_("6_st_cables/3over3left-purl",
                          QSize(6,1)));
  six_st_cableLayout->addLayout(
    create_symbol_layout_("6_st_cables/3over3right-purl",
                          QSize(6,1)));
  six_st_cableLayout->addLayout(
    create_symbol_layout_("6_st_cables/3over3left",
                          QSize(6,1)));
  six_st_cableLayout->addLayout(
    create_symbol_layout_("6_st_cables/3over3right",
                          QSize(6,1)));
  six_st_cableLayout->addStretch(1);

  QScrollArea* six_st_cableScroll = new QScrollArea(this);   
  QWidget* six_st_cableSymbols = new QWidget;
  six_st_cableSymbols->setLayout(six_st_cableLayout);
  six_st_cableScroll->setWidget(six_st_cableSymbols);
  addTab(six_st_cableScroll, QString("6 st. cables"));
}


QT_END_NAMESPACE
