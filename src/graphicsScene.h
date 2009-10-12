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
#include <QFont>
#include <QGraphicsScene>
#include <QPair>
#include <QList>
#include <QMap>

/* local includes */
#include "knittingSymbol.h"
#include "io.h"


QT_BEGIN_NAMESPACE


/* a few forward declarations */
class PatternGridItem;
class QGraphicsSceneMouseEvent;
class QGraphicsSceneWheelEvent; 
class QKeyEvent;

namespace 
{
  /* convenience constants */
  const int UNSELECTED = -100;
  const int NOSHIFT    = -101;

  /* convenience typedefs */
  typedef QList<QPair<int, int> > RowLayout;
  typedef QList<PatternGridItem*> RowItems;
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

  explicit GraphicsScene(const QPoint& origin, const QSize& gridsize, 
      int cellSize, QFont font, QObject* myParent = 0);
  bool Init();

  /* setters */
  void set_font(QFont font);

  /* helper functions */
  void select_region(const QRectF& region);
  void reset_grid(const QSize& newSize);
  void reset_canvas(const QList<PatternGridItemDescriptor>& newItems);


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
  void mark_active_cells_with_rectangle();

  
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

  /* do we want active items to be updated */
  bool updateActiveItems_;

  /* basic dimensions */
  QPoint origin_;
  int numCols_;
  int numRows_;
  int cellSize_;

  /* holds the index of the currently selected column/row if any */
  int selectedCol_;
  int selectedRow_;

  /* reference to settings */
  QFont canvasFont_;

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

  /* use this to remove items from canvas */
  void purge_all_canvas_items_();
  
  /* helper functions */
  void try_place_knitting_symbol_();
  void colorize_highlighted_cells_();
  QPair<int,int> get_cell_coords_(const QPointF& mousePosition) const;
  int compute_horizontal_label_shift_(int num, int fontSize) const;
  QColor determine_selected_cells_color_() const;
  bool sort_active_items_row_wise_(QList<RowItems>& rows) const;
  bool process_selected_items_(QList<RowLayout>& processedCellLayout,
    const QList<RowItems>& rowSelection, int targetPatternSize);

  void select_column_(int col);
  void select_row_(int row);
  void insert_col_(int col);
  void insert_row_(int row);
  void expand_grid_(int colStart, int rowStart);
  void manage_columns_rows_(const QPoint& pos, int col, int row);

  void enable_canvas_update_() { updateActiveItems_ = true; }
  void disable_canvas_update_() { updateActiveItems_ = false; }
  void update_active_items_();

  QPoint compute_cell_origin_(int col, int row) const;
  int compute_cell_index_(PatternGridItem* anItem) const;

  QPair<bool,int> is_row_contiguous_(const RowItems& items) const;
  QRect find_bounding_rectangle_(const QList<RowItems>& rows) const;

  /* simple max helper function */
  int int_max(int a, int b) { return a > b ? a : b; }
};


QT_BEGIN_NAMESPACE

#endif
