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

  /* compute the new symbol position somewhere below the lowest 
   * item present on the canvas */
  qreal xOrigin = 0.0;
  qreal yOrigin = 0.0;
  QList<QGraphicsItem*> allItems(items());
  foreach(QGraphicsItem* anItem, allItems)
  {
    qreal xPos = anItem->scenePos().x();
    qreal yPos = anItem->scenePos().y();

    if (xOrigin > xPos)
    {
      xOrigin = xPos;
    }

    if (yOrigin < yPos)
    {
      yOrigin = yPos;
    }
  }
  int newXPos = static_cast<int>(xOrigin);
  int newYPos = static_cast<int>(yOrigin) + cellSize_ + cellMargin_;


  /* create new symbol */
  KnittingPatternItem* newSymbolItem = new KnittingPatternItem(
      QPoint(newXPos, newYPos), newSymbol->dim(), cellSize_, 0, 0);
  newSymbolItem->Init();
  newSymbolItem->insert_knitting_symbol(newSymbol);
  newSymbolItem->setFlag(QGraphicsItem::ItemIsMovable);
  addItem(newSymbolItem);


  /* create new label */
  QFont currentFont = extract_font_from_settings(settings_);
  QString labelID = newSymbol->fullName();
  KeyLabelItem* newTextItem = new KeyLabelItem(labelID, description);
  newTextItem->Init();
  int textXPos = get_text_x_position_(newSymbolItem);
  newTextItem->setPos(newXPos + textXPos, newYPos);
  newTextItem->setFont(currentFont);
  newTextItem->setFlag(QGraphicsItem::ItemIsMovable);
  addItem(newTextItem);
  connect(newTextItem,
          SIGNAL(label_changed(QString, QString)),
          this,
          SIGNAL(key_label_changed(QString, QString))
         );

  /* add symbol/label pair to tracker */
  KeyCanvas::LabelItem newLabelItem;
  newLabelItem.pattern = newSymbolItem;
  newLabelItem.description = newTextItem;
  displayedItems_.push_back(newLabelItem);
}


//-------------------------------------------------------------
// remove unused symbol from legend canvas 
//-------------------------------------------------------------
void PatternKeyCanvas::remove_symbol(const QString& deadSymbolName)
{
  /* find index of to be removed symbol */
  int counter = 0;
  KnittingPatternItem* deadPatternItem;
  KeyLabelItem* deadLabelItem;

  foreach(KeyCanvas::LabelItem label, displayedItems_)
  {
    deadPatternItem = label.pattern;
    if ( deadPatternItem->get_knitting_symbol_name() 
         == deadSymbolName)
    {
      deadLabelItem = label.description;
      break;
    }

    ++counter;
  }

  /* remove symbol */
  removeItem(deadPatternItem);
  deadPatternItem->deleteLater();
  removeItem(deadLabelItem);
  deadLabelItem->deleteLater();
  displayedItems_.removeAt(counter);
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
  QPoint fontLocation(origin_.x(), origin_.y());
  mainText_ = new QGraphicsTextItem(tr("Legend"));
  mainText_->setFont(currentFont);
  mainText_->setFlag(QGraphicsItem::ItemIsMovable);
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
