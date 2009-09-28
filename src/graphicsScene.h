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

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QColor>
#include <QGraphicsScene>
#include <QPair>
#include <QList>
#include <QMap>

/* local includes */
#include "knittingSymbol.h"


/* a few forward declarations */
class PatternGridItem;
class QGraphicsSceneMouseEvent;
class QGraphicsSceneWheelEvent; 
class QKeyEvent;

/* convenience typedefs */
typedef QList<QPair<int, int> > RowLayout;
typedef QList<PatternGridItem*> RowItems;



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

  explicit GraphicsScene(QObject* myParent);
  bool Init();

  /* accessor functions */ 
  const KnittingSymbolPtr get_selected_symbol();
  const QColor& get_background_color();
  bool withColor();

  /* create the main pattern grid item */
  void create_pattern_grid(const QPoint& origin, const QSize& dim, 
      int cellSize);


signals:

  void mouse_moved(QPointF position);
  void statusBar_message(QString msg);
  void mouse_zoom_in();
  void mouse_zoom_out();
 

public slots:

  void update_selected_symbol(const KnittingSymbolPtr symbol);
  void grid_item_selected(PatternGridItem* item, bool status);
  void grid_item_reset(PatternGridItem*);
  void update_selected_background_color(const QColor& aColor);
  void color_state_changed(int state); 
  void delete_active_cells();

  
protected:

  void mousePressEvent(QGraphicsSceneMouseEvent* mouseEvent);
  void mouseMoveEvent(QGraphicsSceneMouseEvent* mouseEvent);
  void wheelEvent(QGraphicsSceneWheelEvent* wheelEvent);

  
private:

  /* construction status variable */
  int status_;

  /* basic dimensions */
  QPoint origin_;
  int numCols_;
  int numRows_;
  int cellSize_;

  /* basic font properties */
  QFont textFont_;

  /* list of currenly selected items */
  QMap<int,PatternGridItem*> activeItems_;

  /* pointers to current user selections (knitting symbol,
   * color, pen size ..) */
  KnittingSymbolPtr selectedSymbol_;
  QColor backgroundColor_;
  bool wantColor_;

  /* helper functions */
  void try_place_knitting_symbol_();
  void colorize_highlighted_cells_();
  QPair<int,int> get_cell_coords_(const QPointF& mousePosition);
  int compute_horizontal_label_shift_(int num);
  QColor determine_selected_cells_color_();
  bool sort_selected_items_row_wise_(QList<RowItems>& rows);
  bool process_selected_items_(QList<RowLayout>& processedCellLayout,
      const QList<RowItems>& rowSelection, int targetPatternSize);
  QPoint compute_cell_origin_(int col, int row);
  void select_row_(int row);
  void select_column_(int col);
  void select_region_(const QRect& region);
};


#endif
