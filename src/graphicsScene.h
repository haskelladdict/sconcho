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

/* convenience constants */
namespace 
{
  const int UNSELECTED = -100;
  const int NOSHIFT    = -101;
};


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

  explicit GraphicsScene(const QPoint& origin, 
    const QSize& gridsize, int cellSize, QObject* myParent = 0);
  bool Init();

  /* accessor functions */ 
  const KnittingSymbolPtr get_selected_symbol();
  const QColor& get_background_color();
  bool withColor();

  /* helper functions */
  void reset_grid(const QSize& newSize);


signals:

  void mouse_moved(QPointF position);
  void statusBar_error(QString msg);
  void statusBar_message(QString msg);
  void mouse_zoom_in();
  void mouse_zoom_out();
 

public slots:

  void update_selected_symbol(const KnittingSymbolPtr symbol);
  void grid_item_selected(PatternGridItem* item, bool status);
  void grid_item_reset(PatternGridItem*);
  void update_selected_background_color(const QColor& aColor);
  void color_state_changed(int state); 
  void deselect_all_active_items();

  
protected:

  void mousePressEvent(QGraphicsSceneMouseEvent* mouseEvent);
  void mouseMoveEvent(QGraphicsSceneMouseEvent* mouseEvent);
  void wheelEvent(QGraphicsSceneWheelEvent* wheelEvent);


private slots:

  void delete_col_();
  void delete_row_();
  void insert_left_of_col_();
  void insert_right_of_col_();
  void insert_above_row_();
  void insert_below_row_();

  
private:

  /* construction status variable */
  int status_;

  /* basic dimensions */
  QPoint origin_;
  int numCols_;
  int numRows_;
  int cellSize_;

  /* holds the index of the currently selected column/row if any */
  int selectedCol_;
  int selectedRow_;

  /* basic font properties */
  QFont textFont_;

  /* list of currenly selected items */
  QMap<int,PatternGridItem*> activeItems_;

  /* pointers to current user selections (knitting symbol,
   * color, pen size ..) */
  KnittingSymbolPtr selectedSymbol_;
  QColor backgroundColor_;
  QColor defaultColor_;
  bool wantColor_;

  /* set up functions for canvas */
  void create_pattern_grid_();
  void create_grid_labels_();

  /* helper functions */
  void try_place_knitting_symbol_();
  void colorize_highlighted_cells_();
  QPair<int,int> get_cell_coords_(const QPointF& mousePosition);
  int compute_horizontal_label_shift_(int num);
  QColor determine_selected_cells_color_();
  bool sort_selected_items_row_wise_(QList<RowItems>& rows);
  bool process_selected_items_(QList<RowLayout>& processedCellLayout,
      const QList<RowItems>& rowSelection, int targetPatternSize);


  void select_column_(int col);
  void select_row_(int row);
  void insert_col_(int col);
  void insert_row_(int row);
  void expand_grid_(int colStart, int rowStart);
  void manage_columns_rows_(const QPoint& pos, int col, int row);
  void select_region_(const QRect& region);

  QPoint compute_cell_origin_(int col, int row) const;
  int compute_cell_index_(PatternGridItem* anItem) const;
};


#endif
