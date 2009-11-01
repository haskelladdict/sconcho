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
#include <QList>
#include <QPoint>

/* local includes */
#include "basicDefs.h"
#include "knittingSymbol.h"


QT_BEGIN_NAMESPACE


/* a few forward declarations */
class KeyLabelItem;
class KnittingPatternItem;
class QGraphicsTextItem;
class QSettings;


/* helper struct to keep track of a symbol/label pair */
namespace KeyCanvas
{
  struct LabelItem
  {
    KnittingPatternItem* pattern;
    KeyLabelItem* description;
  };
};


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


  explicit PatternKeyCanvas(QPoint origin, int aSize, 
    const QSettings& settings, QObject* myParent = 0);
  bool Init();

  /* add or remove symbol from legend canvas */
  void add_symbol(KnittingSymbolPtr newSymbol, const QString& desc);
  void remove_symbol(const QString& deadSymbolName);


public slots:

  void update_after_settings_change();


signals:

  void key_label_changed(QString id, QString newText);


private:

  /* some tracking variables */
  int status_;

  /* origin of display */
  QPoint origin_;

  /* list of currently displayed KnittingPatternItems in
   * the order they are displayed on the screen so we can
   * easily figure out where to insert a new item */
  QList<KeyCanvas::LabelItem> displayedItems_;

  /* size of a cell for displaying knitting patterns present
   * on canvas and number of rows currently shown */
  int cellSize_;
  int cellMargin_;

  /* our graphic items */
  QGraphicsTextItem* mainText_;

  /* properties objects */
  const QSettings& settings_;

  /* interface creation functions */
  void create_main_label_();

  /* helper functions */
  int get_text_x_position_(const KnittingPatternItem* anItem) const;
  int get_insertion_index_(int newSymbolSize) const;
};


QT_END_NAMESPACE

#endif
