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

#ifndef PATTERN_KEY_CANVAS_H
#define PATTERN_KEY_CANVAS_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGraphicsScene>

/* local includes */
#include "basicDefs.h"

QT_BEGIN_NAMESPACE


/* a few forward declarations */
class QGraphicsTextItem;
class QSettings;


/***************************************************************
 * 
 * The PatternKeyCanvas allows manipulation of the 
 * QGraphicsItems belonging to the pattern key
 *
 ***************************************************************/
class PatternKeyCanvas
  :
    public QGraphicsScene,
    public boost::noncopyable
{
  
  Q_OBJECT

  
public:


  explicit PatternKeyCanvas(const QSettings& settings, 
    QObject* myParent = 0);
  bool Init();

  /* setters for properties */
  //void new_settings(const QSettings& newSettings); 

//protected:

//  void mousePressEvent(QGraphicsSceneMouseEvent* event);
 
    
private:

  /* some tracking variables */
  int status_;

  /* our graphic items */
  QGraphicsTextItem* mainText_;

  /* properties objects */
  const QSettings& settings_;

  /* interface creation functions */
  void create_main_label_();
};


QT_END_NAMESPACE

#endif
