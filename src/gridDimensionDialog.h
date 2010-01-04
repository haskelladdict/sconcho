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

#ifndef GRID_DIMENSION_DIALOG_H
#define GRID_DIMENSION_DIALOG_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QDialog>

QT_BEGIN_NAMESPACE


/***************************************************************
 * 
 * This dialog provides the user with the opportunity to 
 * change the size of the pattern grid
 *
 ***************************************************************/
class GridDimensionDialog 
  :
    public QDialog,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit GridDimensionDialog(QWidget* myParent = 0);
  bool Init();

  /* return selected dimensions */
  QSize dim();


private slots:

  void okClicked_();
  void change_column_count(int columns);
  void change_row_count(int rows);


private:

  /* some tracking variables */
  int status_;
  bool done_;

  /* status variables */
  int columns_;
  int rows_;
};


QT_END_NAMESPACE

#endif
