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

#ifndef SYMBOL_SELECTOR_WIDGET_H 
#define SYMBOL_SELECTOR_WIDGET_H 

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QGroupBox>
#include <QTabWidget>

/* local includes */
#include "knittingSymbol.h"

/* forward declarations */
class QHBoxLayout;
class QMouseEvent;
class QSvgWidget;
class SymbolSelectorItem;



QT_BEGIN_NAMESPACE

/***************************************************************
 * 
 * The GraphicsScene handles the sconcho's main drawing
 * canvas 
 *
 ***************************************************************/
class SymbolSelectorWidget
  : 
    public QTabWidget,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit SymbolSelectorWidget(int cellSize, QWidget* myParent = 0);
  bool Init();

  /* access to currently selected symbol */
  KnittingSymbolPtr selected_symbol() const { return defaultSymbol_; }


signals:

  void selected_symbol_changed(const KnittingSymbolPtr symbol);


public slots:

   void change_highlighted_item(SymbolSelectorItem*, bool state);

    
private:

  /* some tracking variables */
  int status_;

  /* size of a unit pattern symbol cell in pixels */
  int cellSize_;

  /* the currently selected symbol */
  SymbolSelectorItem* highlightedItem_;

  /* our default knitting symbol (the one with with all
   * cells are initially pre-filled */
  KnittingSymbolPtr defaultSymbol_;

  /* functions */
  QHBoxLayout* create_symbol_layout_(const QString& name, 
      const QSize& size); 
  
  void create_tabs_();
};


QT_END_NAMESPACE

#endif
