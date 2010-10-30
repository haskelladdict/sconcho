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

#ifndef COLOR_SELECTOR_ITEM_H
#define COLOR_SELECTOR_ITEM_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QString>
#include <QLabel>


/* forward declarations */
class QColor;
class QHBoxLayout;
class QMouseEvent;


QT_BEGIN_NAMESPACE

/***************************************************************
 *
 * ColorSelectorItem manages a single color selector for use
 * in a ColorSelectorWidget
 *
 ***************************************************************/
class ColorSelectorItem
    :
    public QLabel,
    public boost::noncopyable
{

  Q_OBJECT

public:

  explicit ColorSelectorItem( const QColor& aColor,
                              QWidget* myParent = 0 );
  bool Init();


  /* some basic accessors */
  void select();
  void unselect();
  const QColor& get_color() const { return color_; }
  void set_color( const QColor& aColor );


signals:

  void highlight_me( ColorSelectorItem* us );


protected:

  void mousePressEvent( QMouseEvent* mouseEvent );


private:

  /* status variables */
  int status_;
  bool selected_;
  QColor color_;

  /* a few helper functions */
  QString get_active_stylesheet_();
  QString get_inactive_stylesheet_();
};


QT_END_NAMESPACE

#endif
