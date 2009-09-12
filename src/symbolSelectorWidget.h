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

/* forward declarations */
class QHBoxLayout;
class QMouseEvent;
class QSvgWidget;



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
  
//  Q_OBJECT

    
public:

  explicit SymbolSelectorWidget(QWidget* myParent = 0);
  bool Init();


//signals:


//public slots:


// protected:

//private slots:
    
private:

  /* some tracking variables */
  int status_;

  /* our parent */
  QWidget* parent_;

  /* functions */
  QHBoxLayout* create_symbol_layout_(const QString& fileName, 
      const QString& symbolName) const;
  void create_tabs_();
};


class SymbolSelectorItem 
  :
    public QGroupBox,
    public boost::noncopyable
{
  
//  Q_OBJECT

public:

  explicit SymbolSelectorItem(const QString& name, QWidget* myParent = 0);
  bool Init();


//signals:


//public slots:


protected:

  void mousePressEvent(QMouseEvent* mouseEvent);

//private slots:
    
private:

  
  /* some tracking variables */
  int status_;
  QString selectedStyleSheet_;
  QString unselectedStyleSheet_;

  /* the pathname identifying us */
  QString name_;

  /* the QSvgWidget we own */
  QSvgWidget* symbolSvg_;
}; 

#endif
