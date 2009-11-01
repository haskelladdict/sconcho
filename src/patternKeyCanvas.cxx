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
#include "keyLabelItem.h"
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

  /* setup interface */
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

  /* change pattern symbol labels */
  foreach(KeyCanvas::LabelItem item, displayedItems_)
  {
    KeyLabelItem* currentLabel = item.description;
    currentLabel->setFont(newFont);
  }
}


/**************************************************************
 *
 * PUBLIC MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// add new symbol to legend canvas 
//-------------------------------------------------------------
void PatternKeyCanvas::add_symbol(KnittingSymbolPtr newSymbol,
    const QString& description)
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
    KeyCanvas::LabelItem item = displayedItems_.at(row);
    KnittingSymbolPtr symbol = item.pattern->get_knitting_symbol();
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
    int yPos = origin_.y() + (counter + 1) * (cellSize_ + cellMargin_);

    KeyCanvas::LabelItem item = displayedItems_.at(counter);

    KnittingPatternItem* currentItem = item.pattern;
    currentItem->reseat(QPoint(0,yPos), 0, counter + 1);

    int textXPos = get_text_x_position_(currentItem);
    KeyLabelItem* currentText = item.description;
    currentText->setPos(QPoint(textXPos, yPos));
  }

  /* add new item */
  int newYPos = origin_.y() + row * (cellSize_ + cellMargin_);
  KnittingPatternItem* newSymbolItem = new KnittingPatternItem(
      QPoint(0, newYPos), newSymbol->dim(), cellSize_, 0, row);
  newSymbolItem->Init();
  newSymbolItem->insert_knitting_symbol(newSymbol);
  addItem(newSymbolItem);

  QFont currentFont = extract_font_from_settings(settings_);
  KeyLabelItem* newTextItem = new KeyLabelItem(description);
  newTextItem->Init();
  int textXPos = get_text_x_position_(newSymbolItem);
  newTextItem->setPos(textXPos, newYPos);
  newTextItem->setFont(currentFont);
  addItem(newTextItem);

  KeyCanvas::LabelItem newLabelItem;
  newLabelItem.pattern = newSymbolItem;
  newLabelItem.description = newTextItem;
  displayedItems_.insert(row, newLabelItem);

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


//-------------------------------------------------------------
// returns the x position where the QGraphicsTextItem should 
// go based on the width of the symbol 
//-------------------------------------------------------------
int PatternKeyCanvas::get_text_x_position_(
  const KnittingPatternItem* anItem) const
{
  int symbolWidth = anItem->get_knitting_symbol()->dim().width();
  int textXPos = (symbolWidth + 1) * cellSize_;

  return textXPos;
}



QT_END_NAMESPACE
