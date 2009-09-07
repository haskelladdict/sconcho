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

#ifndef GRAPHICS_SCENE_H 
#define GRAPHICS_SCENE_H 

/* STL includes */

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGraphicsScene>

/* local includes */

/* a few forward declarations */


/***************************************************************
 * 
 * The GraphicsScene handles the sconcho's main drawing
 * canvas 
 *
 ***************************************************************/
class GraphicsScene
  : 
    public QGraphicsScene,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit GraphicsScene(QObject* myParent) : 
        QGraphicsScene(myParent) {};


//signals:


//public slots:

  
//private slots:
  
};


#endif
