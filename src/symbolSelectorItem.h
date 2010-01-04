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

#ifndef SYMBOL_SELECTOR_ITEM_H 
#define SYMBOL_SELECTOR_ITEM_H 

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QString>
#include <QFrame>

/* local includes */
#include "knittingSymbol.h"


/* forward declarations */
class QHBoxLayout;
class QMouseEvent;
class QSvgWidget;


QT_BEGIN_NAMESPACE

/***************************************************************
 * 
 * SymbolSelectorItem manages a single symbol selector widget
 *
 ***************************************************************/
class SymbolSelectorItem 
  :
    public QFrame,
    public boost::noncopyable
{
  
  Q_OBJECT

public:

  explicit SymbolSelectorItem(int cellSize, KnittingSymbolPtr name, 
    QWidget* myParent = 0);
  bool Init();


  /* some basic accessors */
  void select();
  void unselect();
  const KnittingSymbolPtr symbol_info() const;


signals:
  
  void highlight_me(SymbolSelectorItem* us, bool state);


protected:

  void mousePressEvent(QMouseEvent* mouseEvent);

    
private:

  /* status variables */
  int status_;
  bool selected_;
  QString selectedStyleSheet_;
  QString unselectedStyleSheet_;

  /* size (in px) for display purposes of a single symbol unit */
  int unitSize_;  

  /* object holding all the info about the underlying 
   * knitting symbol */
  KnittingSymbolPtr symbol_;
}; 


QT_END_NAMESPACE

#endif
