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
#include "rowColDeleteInsertDialog.h"



QT_BEGIN_NAMESPACE


/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
RowColDeleteInsertDialog::RowColDeleteInsertDialog(
  int selectedRow, int maxRows, int selectedCol, int maxCols,
  QWidget* myParent )
    :
    QDialog( myParent ),
    selectedRow_( selectedRow ),
    maxRows_( maxRows ),
    selectedColumn_( selectedCol ),
    maxColumns_( maxCols )
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool RowColDeleteInsertDialog::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED ) {
    return false;
  }

  setupUi( this );

  customize_insert_row_layout_();
  customize_delete_row_layout_();
  customize_insert_column_layout_();
  customize_delete_column_layout_();

  connect( closeButton,
           SIGNAL( clicked() ),
           this,
           SLOT( close() )
         );
  
  insertDeleteTabWidget->setCurrentIndex( 0 );
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
void RowColDeleteInsertDialog::insert_row_clicked_()
{
  /* figure out what the user selected */
  int numRows = numRowsWidget->value();
  int location = insertRowLocationWidget->currentIndex();
  int pivot = pivotRowLocation->value();

  emit insert_rows( numRows, pivot, location );
}


//-------------------------------------------------------------
// delete based on what the user selected
//-------------------------------------------------------------
void RowColDeleteInsertDialog::delete_row_clicked_()
{
  emit delete_row( deleteRowWidget->value() );
}



//-------------------------------------------------------------
// insert based on what the user selected
//-------------------------------------------------------------
void RowColDeleteInsertDialog::insert_column_clicked_()
{
  /* figure out what the user selected */
  int numColumns = numColumnsWidget->value();
  int location = insertColumnLocationWidget->currentIndex();
  int pivot = pivotColumnLocation->value();

  emit insert_columns( numColumns, pivot, location );
}



//-------------------------------------------------------------
// delete based on what the user selected
//-------------------------------------------------------------
void RowColDeleteInsertDialog::delete_column_clicked_()
{
  emit delete_column( deleteColumnWidget->value() );
}



/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// this function customizes the insert row widget
//-------------------------------------------------------------
void RowColDeleteInsertDialog::customize_insert_row_layout_()
{
  pivotRowLocation->setValue( maxRows_ - selectedRow_ );

  connect( insertRowButton,
           SIGNAL( clicked() ),
           this,
           SLOT( insert_row_clicked_() )
         );

}



//-------------------------------------------------------------
// this function customizes the delete row widget
//-------------------------------------------------------------
void RowColDeleteInsertDialog::customize_delete_row_layout_()
{
  deleteRowWidget->setValue( maxRows_ - selectedRow_ );

  connect( deleteRowButton,
           SIGNAL( clicked() ),
           this,
           SLOT( delete_row_clicked_() )
         );
}



//-------------------------------------------------------------
// this function customizes the insert row widget
//-------------------------------------------------------------
void RowColDeleteInsertDialog::customize_insert_column_layout_()
{
  pivotColumnLocation->setValue( maxColumns_ - selectedColumn_ );

  connect( insertColumnButton,
           SIGNAL( clicked() ),
           this,
           SLOT( insert_column_clicked_() )
         );
}



//-------------------------------------------------------------
// this function customizes the delete column widget
//-------------------------------------------------------------
void RowColDeleteInsertDialog::customize_delete_column_layout_()
{
  deleteColumnWidget->setValue( maxColumns_ - selectedColumn_ );
  
  connect( deleteColumnButton,
           SIGNAL( clicked() ),
           this,
           SLOT( delete_column_clicked_() )
         );
}




QT_END_NAMESPACE
