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

#ifndef PATTERN_GRID_H
#define PATTERN_GRID_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGraphicsItem>

/* local includes */

/* a few forward declarations */
class QGraphicsScene;
class QPainter;
class QStyleOptionGraphicsItem;


/***************************************************************
 * 
 * The GraphicsScene handles the sconcho's main drawing
 * canvas 
 *
 ***************************************************************/
class PatternGrid
  : 
    public boost::noncopyable
{
  
//  Q_OBJECT

    
public:

  explicit PatternGrid(QGraphicsScene* aScene);
  bool Init();

//  QRectF boundingRect() const;
//  void paint(QPainter *painter,
//             const QStyleOptionGraphicsItem *option,
//             QWidget *widget);
  
//signals:


//public slots:

  
//private slots:
    
private:

  /* construction status variable */
  int status_;

  /* pointer to the main graphics scene */
  QGraphicsScene* theScene_;
  
  /* member data */
  //QGraphicsItemGroup* grid_;
  
  /* helper functions */
  //void create_grid_item_();
};


#endif
