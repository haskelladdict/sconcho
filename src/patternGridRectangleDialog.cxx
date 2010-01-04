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
#include <QColorDialog>
#include <QDialog>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QSpinBox>


/** local headers */
#include "basicDefs.h"
#include "patternGridRectangleDialog.h"

QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternGridRectangleDialog::PatternGridRectangleDialog(
    QWidget* myParent)
    :
      QDialog(myParent),
      done_(false),
      colorSelector_(new QPushButton),
      currentPen_(QPen(Qt::red, 4.0))
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternGridRectangleDialog::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* call individual initialization routines */
  setModal(true);
  setWindowTitle(tr("Enter grid rectangle properties"));
 
  /* color selector */
  QLabel* lineColorLabel = new QLabel(tr("line color"));
  colorSelector_->setPalette(currentPen_.color());
  connect(colorSelector_,
          SIGNAL(clicked()),
          this,
          SLOT(pick_color_()));

  QHBoxLayout* colorButtonLayout = new QHBoxLayout;
  colorButtonLayout->addWidget(lineColorLabel);
  colorButtonLayout->addWidget(colorSelector_);

  /* line width selector */
  QLabel* lineWidthLabel = new QLabel(tr("line width"));
  QSpinBox* lineWidthSelector = new QSpinBox;
  lineWidthSelector->setRange(0,100);
  lineWidthSelector->setValue(currentPen_.width());
  connect(lineWidthSelector, 
          SIGNAL(valueChanged(int)),
          this,
          SLOT(change_line_width_(int)));

  QHBoxLayout* lineWidthLayout = new QHBoxLayout;
  lineWidthLayout->addWidget(lineWidthLabel);
  lineWidthLayout->addWidget(lineWidthSelector);

  /* generate main layout */
  QGroupBox* mainGrouper = new QGroupBox;
  QVBoxLayout* mainLayout = new QVBoxLayout;
  mainLayout->addLayout(colorButtonLayout);
  mainLayout->addLayout(lineWidthLayout);
  mainGrouper->setLayout(mainLayout);

  /* add ok button and connect it */
  QPushButton* okButton = new QPushButton(tr("OK"));
  connect(okButton,
          SIGNAL(clicked()),
          this,
          SLOT(okClicked_()));
  okButton->setFixedWidth(50);
  QHBoxLayout *buttonLayout = new QHBoxLayout;
  buttonLayout->addStretch(1);
  buttonLayout->addWidget(okButton, Qt::AlignHCenter);
  buttonLayout->addStretch(1);

  QVBoxLayout* widgetLayout = new QVBoxLayout;
  widgetLayout->addWidget(mainGrouper);
  widgetLayout->addLayout(buttonLayout);
  widgetLayout->addStretch(1);
  
  setLayout(widgetLayout);
  exec();

  return true;
}


//-------------------------------------------------------------
// return selected dimensions
//-------------------------------------------------------------
QPen PatternGridRectangleDialog::pen() const
{
  return currentPen_;
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

//-------------------------------------------------------------
// slots changing the row/column counts triggered by spin
// boxes
//-------------------------------------------------------------

//-------------------------------------------------------------
// done with selecting, return selected grid size as QSize
//-------------------------------------------------------------
void PatternGridRectangleDialog::okClicked_()
{
  done(QDialog::Accepted);  
}


//-------------------------------------------------------------
// change line width of our pen
//-------------------------------------------------------------
void PatternGridRectangleDialog::change_line_width_(int newWidth)
{
  currentPen_.setWidth(newWidth);
}


//--------------------------------------------------------------
// fire up a color selector dialog and change our current
// pen according to the user selection
//--------------------------------------------------------------
void PatternGridRectangleDialog::pick_color_()
{
  QColor selection = QColorDialog::getColor(currentPen_.color(),
      this, "Select rectangle color");

  currentPen_.setColor(selection);

  QPalette selectorPalette = QPalette(selection);
  colorSelector_->setPalette(selectorPalette);
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

QT_END_NAMESPACE
