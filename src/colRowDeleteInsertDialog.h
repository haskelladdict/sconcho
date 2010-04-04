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

#ifndef COL_ROW_DELETE_INSERT_DIALOG_H
#define COL_ROW_DELETE_INSERT_DIALOG_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QDialog>

/* local includes */
#include "ui_insertDeleteRowsWidget.h"


QT_BEGIN_NAMESPACE


/* forward declarations */
class QComboBox;
class QGroupBox;
class QSpinBox;


/**************************************************************
 *
 * this dialog provides the ability to delete or insert rows
 * in the main pattern grid
 *
 **************************************************************/
class RowDeleteInsertDialog
    :
    public QDialog,
    public Ui::RowDeleteInsertDialog,
    public boost::noncopyable
{

  Q_OBJECT


public:

  explicit RowDeleteInsertDialog( int selectedRow, int maxRows,
                                  QWidget* myParent = 0 );
  bool Init();


signals:

  void insert_rows(int num, int pivot, int location);
  

private slots:

  void insert_clicked_();


private:

  /* some tracking variables */
  int status_;
  int selectedRow_;
  int maxRows_;

  /* interface creation functions */
  void customize_insert_layout_();
};


QT_END_NAMESPACE


#endif
