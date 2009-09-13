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

#ifndef SYMBOL_SELECTOR_ITEM_H 
#define SYMBOL_SELECTOR_ITEM_H 

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGroupBox>
#include <QString>

/* local includes */

/* forward declarations */
class QHBoxLayout;
class QMouseEvent;
class QSvgWidget;


/***************************************************************
 * 
 * SymbolSelectorItem manages a single symbol selector widget
 *
 ***************************************************************/
class SymbolSelectorItem 
  :
    public QGroupBox,
    public boost::noncopyable
{
  
  Q_OBJECT

public:

  explicit SymbolSelectorItem(const QString& name, 
      QWidget* myParent = 0);
  bool Init();


  /* some basic accessors */
  void select();
  void unselect();
  QString symbol_name();


signals:
  
  void highlight_me(SymbolSelectorItem* us, bool state);


protected:

  void mousePressEvent(QMouseEvent* mouseEvent);

    
private:

  /* some tracking variables */
  int status_;
  bool selected_;
  QString selectedStyleSheet_;
  QString unselectedStyleSheet_;

  /* the pathname identifying us */
  QString name_;

  /* the QSvgWidget we own */
  QSvgWidget* symbolSvg_;
}; 

#endif
