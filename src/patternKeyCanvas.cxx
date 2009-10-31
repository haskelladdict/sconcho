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

/* Qt headers */
#include <QDebug>
#include <QColor>
#include <QGraphicsTextItem>
#include <QPainter>
#include <QSettings>

/* local headers */
#include "helperFunctions.h"
#include "patternGridItem.h"
#include "patternKeyCanvas.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternKeyCanvas::PatternKeyCanvas(QPoint origin, int aSize, 
  const QSettings& settings, QObject* myParent)
    :
      QGraphicsScene(myParent),
      origin_(origin),
      cellSize_(aSize),
      cellMargin_(10),
      settings_(settings)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternKeyCanvas::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  create_main_label_();

  return true;
}



/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// update the items on our canvas after the user changed
// some settings
//-------------------------------------------------------------
void PatternKeyCanvas::update_after_settings_change()
{
  QFont newFont = extract_font_from_settings(settings_);
  
  /* change main text */
  mainText_->setFont(newFont);
}


/**************************************************************
 *
 * PUBLIC MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// add new symbol to legend canvas 
//-------------------------------------------------------------
void PatternKeyCanvas::add_symbol(KnittingSymbolPtr newSymbol)
{
  /* make sure we don't add the empty symbol */
  if (newSymbol->fullName() == "")
  {
    return;
  }

  /* We want to display items in order of increasing 
   * symbol size. Hence we go through the list of currently
   * displayed items until we find the correct location */
  int currentSize = newSymbol->dim().width();
  int row = 0;
  while (row < displayedItems_.size())
  {
    KnittingSymbolPtr symbol = 
      displayedItems_.at(row)->get_knitting_symbol();
    int symbolSize = symbol->dim().width();

    if (symbolSize > currentSize)
    {
      break;
    }

    ++row;
  }

  /* shift all remaining items by one */
  for (int counter = row; counter < displayedItems_.size(); ++counter)
  {
    QPoint newOrigin(origin_.x(), 
        origin_.y() + (counter + 1) * (cellSize_ + cellMargin_));

    KnittingPatternItem* currentItem = displayedItems_.at(counter);
    currentItem->reseat(newOrigin, 0, counter + 1);
  }

  /* add new item */
  QPoint newOrigin(origin_.x(), 
      origin_.y() + row * (cellSize_ + cellMargin_));
  KnittingPatternItem* newItem = new KnittingPatternItem(
      newOrigin, newSymbol->dim(), cellSize_, 0, row);
  newItem->Init();
  newItem->insert_knitting_symbol(newSymbol);
  addItem(newItem);
  displayedItems_.insert(row, newItem);

  setSceneRect(itemsBoundingRect());
}




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
// create the main label
//-------------------------------------------------------------
void PatternKeyCanvas::create_main_label_()
{
  QFont currentFont = extract_font_from_settings(settings_);
  QPoint fontLocation(origin_.x(), origin_.y() - 1.2 * cellSize_);
  mainText_ = new QGraphicsTextItem(tr("Legend"));
  mainText_->setFont(currentFont);
  mainText_->setTextInteractionFlags(Qt::TextEditable);
  mainText_->setPos(fontLocation);
  addItem(mainText_);
}


QT_END_NAMESPACE
