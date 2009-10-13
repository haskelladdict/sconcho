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

#ifndef PATTERN_GRID_RECTANGLE_DIALOG_H
#define PATTERN_GRID_RECTANGLE_DIALOG_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QDialog>
#include <QPen>

QT_BEGIN_NAMESPACE

/* forward declarations */
class QPushButton;


/***************************************************************
 * 
 * This dialog allows the user to configure the rectangle
 * markers
 *
 ***************************************************************/
class PatternGridRectangleDialog 
  :
    public QDialog,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit PatternGridRectangleDialog(QWidget* myParent = 0);
  bool Init();

  /* getters and setters for pen */
  QPen pen() const;
  void set_pen(const QPen& newPen) { currentPen_ = newPen; }


private slots:

  void okClicked_();
  void change_line_width_(int newWidth);
  void pick_color_();


private:

  /* some tracking variables */
  int status_;
  bool done_;

  /* private data member */
  QPushButton* colorSelector_;
  QPen currentPen_;
};


QT_END_NAMESPACE

#endif
