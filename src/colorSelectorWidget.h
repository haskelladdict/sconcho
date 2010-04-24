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

#ifndef COLOR_SELECTOR_WIDGET_H
#define COLOR_SELECTOR_WIDGET_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QWidget>

/* local includes */

/* forward declarations */
class ColorSelectorItem;
class QHBoxLayout;
class QPushButton;


QT_BEGIN_NAMESPACE

/***************************************************************
 *
 * This widget provides sconcho's color selecting ability
 *
 ***************************************************************/
class ColorSelectorWidget
    :
    public QWidget,
    public boost::noncopyable
{

  Q_OBJECT


public:

  explicit ColorSelectorWidget( const QList<QColor>& colors,
                                QWidget* myParent = 0 );
  bool Init();

  /* return a list of currently active colors */
  QList<QColor> get_colors() const;
  void set_colors( const QList<QColor>& newColors );


signals:

  void color_changed( const QColor& newColor );


public slots:

  void highlight_color_button( ColorSelectorItem* newActiveItem );


private slots:

  void customize_color_();


private:

  /* some tracking variables */
  int status_;

  /* default colors for selector */
  QList<QColor> selectorColors_;

  /* list of pointers to color selector */
  QList<ColorSelectorItem*> colorSelectors_;

  /* currently highlighted color selector */
  ColorSelectorItem* activeSelector_;

  /* widgets */
  QHBoxLayout* buttonLayout_;
  QPushButton* customizeColorButton_;
  
  /* widget creation routines */
  void create_layout_();
  void create_color_customize_button_();

  /* helper functions */
  void pad_colors_();
  void set_color_selector_button_( const QColor& newColor );
};


QT_END_NAMESPACE

#endif
