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
#include <QComboBox>
#include <QDebug>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QList>
#include <QLineEdit>
#include <QPushButton>
#include <QSpinBox>
#include <QString>
#include <QStringList>
#include <QTabWidget>
#include <QVBoxLayout>

/** local headers */
#include "basicDefs.h"
#include "colRowDeleteInsertDialog.h"



QT_BEGIN_NAMESPACE


/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
RowDeleteInsertDialog::RowDeleteInsertDialog( int selectedRow,
    int maxRows,
    QWidget* myParent )
    :
    QDialog( myParent ),
    selectedRow_( selectedRow ),
    maxRows_( maxRows )
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool RowDeleteInsertDialog::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED ) {
    return false;
  }

  setupUi( this );

  customize_insert_layout_();
  customize_delete_layout_();
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

//-------------------------------------------------------------
// insert based on what the user selected
//-------------------------------------------------------------
void RowDeleteInsertDialog::insert_clicked_()
{
  /* figure out what the user selected */
  int numRows = numRowsWidget->value();
  int location = insertLocationWidget->currentIndex();
  int pivot = pivotRowLocation->value();

  emit insert_rows( numRows, pivot, location );
  close();
}


//-------------------------------------------------------------
// delete based on what the user selected
//-------------------------------------------------------------
void RowDeleteInsertDialog::delete_clicked_()
{
  emit delete_row( deleteRowWidget->value() );
  close();
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// this function customizes the insert row widget
//-------------------------------------------------------------
void RowDeleteInsertDialog::customize_insert_layout_()
{
  pivotRowLocation->setValue( maxRows_ - selectedRow_ );

  connect( insertButton,
           SIGNAL( clicked() ),
           this,
           SLOT( insert_clicked_() )
         );

  connect( insertCancelButton,
           SIGNAL( clicked() ),
           this,
           SLOT( close() )
         );
}



//-------------------------------------------------------------
// this function customizes the delete row widget
//-------------------------------------------------------------
void RowDeleteInsertDialog::customize_delete_layout_()
{
  deleteRowWidget->setValue( maxRows_ - selectedRow_ );

  connect( deleteButton,
           SIGNAL( clicked() ),
           this,
           SLOT( delete_clicked_() )
         );

  connect( deleteCancelButton,
           SIGNAL( clicked() ),
           this,
           SLOT( close() )
         );
}


QT_END_NAMESPACE
