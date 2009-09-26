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
#include <QDialog>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QSpinBox>


/** local headers */
#include "basicDefs.h"
#include "gridDimensionDialog.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
GridDimensionDialog::GridDimensionDialog(QWidget* myParent)
    :
      QDialog(myParent),
      done_(false),
      columns_(10),
      rows_(10)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool GridDimensionDialog::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* call individual initialization routines */
  setFixedSize(QSize(250,130));
  setModal(true);
  setWindowTitle(tr("Enter grid dimensions"));
  
  /* selector for number of columns */
  QHBoxLayout* xdimLayout = new QHBoxLayout;
  QLabel* xdimLabel = new QLabel(tr("number of columns"));
  QSpinBox* xdimSelector = new QSpinBox;
  xdimSelector->setRange(0,400);
  xdimSelector->setValue(columns_);
  connect(xdimSelector, SIGNAL(valueChanged(int)),
          this,SLOT(change_column_count(int)));

  xdimLayout->addWidget(xdimLabel);
  xdimLayout->addStretch(1);
  xdimLayout->addWidget(xdimSelector);

  /* selector for number of rows */
  QHBoxLayout* ydimLayout = new QHBoxLayout;
  QLabel* ydimLabel = new QLabel(tr("number of rows"));
  QSpinBox* ydimSelector = new QSpinBox;
  ydimSelector->setRange(0,400);
  ydimSelector->setValue(rows_);
  connect(ydimSelector, SIGNAL(valueChanged(int)),
          this,SLOT(change_row_count(int)));

  ydimLayout->addWidget(ydimLabel);
  ydimLayout->addStretch(1);
  ydimLayout->addWidget(ydimSelector);

  /* generate main layout */
  QGroupBox* mainGrouper = new QGroupBox;
  QVBoxLayout* mainLayout = new QVBoxLayout;
  mainLayout->addLayout(xdimLayout);
  mainLayout->addLayout(ydimLayout);
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
QSize GridDimensionDialog::dim()
{
  return QSize(columns_, rows_);
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
void GridDimensionDialog::change_column_count(int newCols)
{
  columns_ = newCols;
}


void GridDimensionDialog::change_row_count(int newRows)
{
  rows_ = newRows;
}


//-------------------------------------------------------------
// done with selecting, return selected grid size as QSize
//-------------------------------------------------------------
void GridDimensionDialog::okClicked_()
{
  done(QDialog::Accepted);  
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/


