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
      parent_(myParent)
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
    const QString& fileName, const QString& symbolName) const
{
  SymbolSelectorItem* symbol = new SymbolSelectorItem(fileName);
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
     mainLayout->addLayout(create_symbol_layout_(path + symbols[i] + ".svg", 
           symbols[i]));
  }
  mainLayout->addStretch(1);
  setLayout(mainLayout);
}



SymbolSelectorItem::SymbolSelectorItem(const QString& name, QWidget* myParent)
  :
    QGroupBox(myParent),
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

  return true;
}


/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/

/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

/**************************************************************
 *
 * PROTECTED SLOTS
 *
 *************************************************************/

//---------------------------------------------------------------
// event handler for mouse move events
//---------------------------------------------------------------
void SymbolSelectorItem::mousePressEvent(QMouseEvent* mouseEvent)
{
  setStyleSheet(selectedStyleSheet_);
  repaint();
  /* let our parent know that we moved */
  //emit mouse_moved(currentPos);
  qDebug() << "clicked on " << name_;
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

