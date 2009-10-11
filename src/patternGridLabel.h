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

#ifndef PATTERN_GRID_LABEL_H
#define PATTERN_GRID_LABEL_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGraphicsTextItem>
#include <QString>


QT_BEGIN_NAMESPACE


/* define our user type */
namespace 
{
  const int PATTERN_GRID_LABEL_TYPE = 2;
};


/***************************************************************
 * 
 * PatterGridLabel really is not much more than a 
 * QGraphicsTextItem that was overloaded so we can give it 
 * a seperate user type to easy dealing with it on the canvas
 *
 ***************************************************************/
class PatternGridLabel
  :
    public QGraphicsTextItem,
    public boost::noncopyable
{
  
public:

  explicit PatternGridLabel(const QString& text, int labelType,
      QGraphicsItem* aParent = 0);
  bool Init();

  /* return our object type; needed for qgraphicsitem_cast */
  enum { Type = UserType + PATTERN_GRID_LABEL_TYPE };
  int type() const;

  /* what kind of label we are */
  enum { ColLabel = 0, RowLabel = 1 };
  int label_type() const; 


private:

  /* some tracking variables */
  int status_;

  /* what kind of label are we */
  int labelType_;
};


QT_END_NAMESPACE


#endif
