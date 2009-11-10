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
#include <QGraphicsItemGroup>
#include <QGraphicsTextItem>
#include <QGraphicsView>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QSettings>
#include <QSplitter>
#include <QVBoxLayout>


/** local headers */
#include "basicDefs.h"
#include "helperFunctions.h"
#include "keyLabelItem.h"
#include "knittingPatternItem.h"
#include "patternKeyCanvas.h"
#include "patternKeyDialog.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternKeyDialog::PatternKeyDialog(int cellSize,
  const QSettings& aSetting, QWidget* myParent)
    :
      QDialog(myParent),
      cellSize_(cellSize),
      settings_(aSetting),
      mainSplitter_(new QSplitter)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternKeyDialog::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* set properties */
  setMinimumSize(300,400);
  setWindowFlags(Qt::Window);

  /* call individual initialization routines */
  setModal(false);
  setWindowTitle(tr("Edit pattern key"));

  /* create interface */
  create_canvas_();
  create_buttons_();

  /* generate main layout */
  mainSplitter_->addWidget(patternKeyView_);
  QVBoxLayout* mainLayout = new QVBoxLayout;
  mainLayout->addWidget(mainSplitter_);
  mainLayout->addLayout(buttonLayout_);
  setLayout(mainLayout);


  /* some plumbing */
  connect(this,
          SIGNAL(settings_changed()),
          patternKeyCanvas_,
          SLOT(update_after_settings_change())
         );

  connect(patternKeyCanvas_,
          SIGNAL(key_label_changed(QString, QString)),
          this,
          SLOT(update_key_label_(QString, QString))
         );

  return true;
}


/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/


//-------------------------------------------------------------
// every time a symbol is added on the canvas this slot is
// invoked to reference count the current number of symbols
// present
//-------------------------------------------------------------
void PatternKeyDialog::add_knitting_symbol(
  KnittingSymbolPtr newSymbol, const QColor& color)
{
  /* update reference count */
  QString symbolName = newSymbol->fullName();
  QString colorName = color.name();
  QString fullName = symbolName + colorName;
  int currentValue = usedKnittingSymbols_[fullName] + 1;
  assert(currentValue > 0);
 
  usedKnittingSymbols_[fullName] = currentValue;

  /* if the currentValue is one the symbol has come "into
   * existence" and we need to show it on the legend canvas;
   * if this is the very first time the user selected it
   * we also add the default descriptor text to the 
   * symbolDescriptor_ map */
  if (currentValue == 1)
  {
    if (!symbolDescriptors_.contains(fullName))
    {
      QString description = newSymbol->baseName();
      symbolDescriptors_[fullName] = description;
    }

    /* show it on the canvas */
    patternKeyCanvas_->add_symbol(newSymbol, 
      symbolDescriptors_[fullName], color);
  }

}


//-------------------------------------------------------------
// every time a symbol is removed from the canvas this slot is
// invoked to reference count the current number of symbols
// present
//-------------------------------------------------------------
void PatternKeyDialog::remove_knitting_symbol(
  KnittingSymbolPtr deadSymbol, const QColor& color)
{
  /* update reference count */
  QString symbolName = deadSymbol->fullName();
  QString colorName  = color.name();
  QString fullName = symbolName + colorName;
  int currentValue = usedKnittingSymbols_[fullName] - 1;
  usedKnittingSymbols_[fullName] = currentValue;

  assert(currentValue >= 0);
 
  /* remove symbol if reference count hits 0 */
  if (currentValue == 0)
  {
    usedKnittingSymbols_.remove(fullName);
    patternKeyCanvas_->remove_symbol(symbolName, colorName);
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

//-------------------------------------------------------------
// this slot is called when a currently visible key label 
// changes its text via user interaction 
//-------------------------------------------------------------
void PatternKeyDialog::update_key_label_(QString labelID, 
  QString newLabelText)
{
  symbolDescriptors_[labelID] = newLabelText; 
}


//-------------------------------------------------------------
// this slot opens up a file export dialog for saving the
// content of the legend canvas to a file
//-------------------------------------------------------------
void PatternKeyDialog::export_legend_()
{
  QString fileName = show_file_export_dialog();
  export_scene(fileName, patternKeyCanvas_);
}


//-------------------------------------------------------------
// this slot opens up a file export dialog for saving the
// content of the legend canvas to a file
//-------------------------------------------------------------
void PatternKeyDialog::print_legend_()
{
  print_scene(patternKeyCanvas_);
}

//-------------------------------------------------------------
// this slot gathers all of the legend as a QGraphicsItemGroup
// and exports it to the main canvas
//-------------------------------------------------------------
void PatternKeyDialog::export_to_canvas_()
{
  /* unfortunately, we can't just grab all items via item() since
   * then the QSvgItems contained in each knittingPatternItem
   * will be reparented and disociate from their pattern items.
   * Hence we grab the labels and pattern items by hand and add 
   * them */
  QList<QGraphicsItem*> allItems(patternKeyCanvas_->items());
  QList<QGraphicsItem*> toBeGroupedItems;
  foreach(QGraphicsItem* anItem, allItems)
  {
    /* add knitting patterns to group */
    KnittingPatternItem* knitItem =
      qgraphicsitem_cast<KnittingPatternItem*>(anItem);
    if (knitItem != 0)
    {
      toBeGroupedItems.push_back(knitItem);
    }

    /* add labels to group */
    KeyLabelItem* labelItem =
      qgraphicsitem_cast<KeyLabelItem*>(anItem);
    if (labelItem != 0)
    {
      toBeGroupedItems.push_back(labelItem);
    }

    /* add text items to group */
    QGraphicsTextItem* textItem =
      qgraphicsitem_cast<QGraphicsTextItem*>(anItem);
    if (textItem != 0)
    {
      toBeGroupedItems.push_back(textItem);
    }

  }


  legendGrouper_ = patternKeyCanvas_->createItemGroup(toBeGroupedItems);

  emit export_legend_canvas(legendGrouper_);
 
  patternKeyCanvas_->destroyItemGroup(legendGrouper_);
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//------------------------------------------------------------
// create the pattern key canvas and the associated 
// QGraphicsView
//------------------------------------------------------------
void PatternKeyDialog::create_canvas_()
{
  QPoint origin(0,0);
  patternKeyCanvas_ = 
    new PatternKeyCanvas(origin, cellSize_, settings_, this);  
  patternKeyCanvas_->Init();
  patternKeyView_ = new QGraphicsView(patternKeyCanvas_);
  patternKeyView_->setRenderHints(QPainter::Antialiasing);
  patternKeyView_->setViewportUpdateMode(
      QGraphicsView::FullViewportUpdate);
}


//-------------------------------------------------------------
// create and wire up the dialog buttons
//-------------------------------------------------------------
void PatternKeyDialog::create_buttons_()
{
  buttonLayout_ = new QHBoxLayout;

  /* export button */
  QPushButton* exportToFileButton = 
    new QPushButton(QIcon(":/icons/fileexport.png"),
        tr("export to file"));
  connect(exportToFileButton,
          SIGNAL(clicked()),
          this,
          SLOT(export_legend_()));

  /* print button */
  QPushButton* printButton = 
    new QPushButton(QIcon(":/icons/fileprint.png"), tr("print"));
  connect(printButton,
          SIGNAL(clicked()),
          this,
          SLOT(print_legend_()));

  /* export to canvas button */
  QPushButton* exportToCanvasButton = 
    new QPushButton(QIcon(":/icons/rectangle.png"),
        tr("export to canvas"));
  connect(exportToCanvasButton,
          SIGNAL(clicked()),
          this,
          SLOT(export_to_canvas_()));


  /* close button */
  QPushButton* closeButton = 
    new QPushButton(QIcon(":/icons/stop.png"), tr("close"));
  connect(closeButton,
          SIGNAL(clicked()),
          this,
          SLOT(hide())
         );

  /* assemble the complete layout */
  buttonLayout_->addWidget(exportToFileButton);
  buttonLayout_->addWidget(printButton);
  buttonLayout_->addStretch(1);
  buttonLayout_->addWidget(exportToCanvasButton);
  buttonLayout_->addWidget(closeButton);

}



QT_END_NAMESPACE
