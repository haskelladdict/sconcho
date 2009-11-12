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

#ifndef KEY_LABEL_ITEM_H
#define KEY_LABEL_ITEM_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGraphicsTextItem>

/* local include */
#include "basicDefs.h"

QT_BEGIN_NAMESPACE


/* a few forward declarations */
class QKeyEvent;


/***************************************************************
 * 
 * The GraphicsView handles sconcho's main graphics interface
 * canvas 
 *
 ***************************************************************/
class KeyLabelItem
  :
  public QGraphicsTextItem,
  public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit KeyLabelItem(const QString& labelID, const QString& text, 
    QGraphicsItem* parent=0);
  bool Init();
 
  /* return our object type; needed for qgraphicsitem_cast */
  enum { Type = UserType + KEY_LABEL_ITEM_TYPE };
  int type() const;


signals:

  void label_changed(QString id, QString labelText);


protected:

  void keyPressEvent(QKeyEvent* anEvent);


private:

  /* construction status variable */
  int status_;

  /* name under which upstream knows us */
  QString IDString_; 
};


QT_END_NAMESPACE

#endif
