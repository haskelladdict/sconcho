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
#include "io.h"


QT_BEGIN_NAMESPACE


/* a few forward declarations */
class LegendItem;
class LegendLabel;
class KnittingPatternItem;
class PatternGridItem;
class PatternGridRectangle;
class QGraphicsSceneMouseEvent;
class QKeyEvent;
class QSettings;
class MainWindow;

namespace 
{
  /* convenience constants */ const int UNSELECTED = -100;
  const int NOSHIFT    = -101;

  /* convenience typedefs */
  typedef QList<QPair<int, int> > RowLayout;
  typedef QList<PatternGridItem*> RowItems;

  typedef QPair<LegendItem*,LegendLabel*> LegendEntry;
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
    int cellSize, const QSettings& settings, 
    KnittingSymbolPtr defaultSymbol, MainWindow* myParent = 0);
  bool Init();

  /* helper functions */
  void select_region(const QRectF& region);
  void reset_grid(const QSize& newSize);
  void load_new_canvas(
    const QList<PatternGridItemDescriptorPtr>& newItems);
  void place_legend_items(
    const QList<LegendEntryDescriptorPtr>& newLegendEntries);
  QRectF get_visible_area() const;

  /* legend releated stuff */
  bool legend_is_visible() const { return legendIsVisible_; }
  void hide_all_but_legend();
  void show_all_items();
  QMap<QString,LegendEntry> get_legend_entries() const 
  { 
    return legendEntries_;
  }


signals:

  void mouse_moved(QPointF position);
  void statusBar_error(QString msg); 
  void statusBar_message(QString msg);


public slots:

  void update_selected_symbol(const KnittingSymbolPtr symbol);
  void grid_item_selected(PatternGridItem* item, bool status);
  void grid_item_reset(PatternGridItem* item);
  void update_selected_background_color(const QColor& aColor);
  void color_state_changed(int state); 
  void deselect_all_active_items();
  void mark_active_cells_with_rectangle();
  void update_after_settings_change();
  void toggle_legend_visibility();

  
protected:

  void mousePressEvent(QGraphicsSceneMouseEvent* mouseEvent);
  void mouseMoveEvent(QGraphicsSceneMouseEvent* mouseEvent);


private slots:

  void delete_col_();
  void delete_row_();
  void insert_left_of_col_();
  void insert_right_of_col_();
  void insert_above_row_();
  void insert_below_row_();
  void mark_rectangle_for_deletion_(QObject* foo);
  void customize_rectangle_(QObject* foo);
  void update_key_label_text_(QString, QString);

  
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
  const QSettings& settings_;

  /* list of currenly selected items */
  QMap<int,PatternGridItem*> activeItems_;

  /* pointers to current user selections (knitting symbol,
   * color, pen size ..) */
  KnittingSymbolPtr selectedSymbol_;
  KnittingSymbolPtr defaultSymbol_;
  QColor backgroundColor_;
  QColor defaultColor_;
  bool wantColor_;

  /* set up functions for canvas */
  void create_pattern_grid_();
  void create_grid_labels_();
  void create_pattern_key_();

  /* items related to the legend */
  bool legendIsVisible_;
  void notify_legend_of_item_addition_(const PatternGridItem* anItem);
  void notify_legend_of_item_removal_(const PatternGridItem* anItem);
  void shift_legend_items_vertically_(int pivot, int distance);
  void shift_legend_items_horizontally_(int pivot, int distance);
  void update_legend_labels_();
  int get_next_legend_items_y_position_() const;
  QList<QGraphicsItem*> get_list_of_legend_items_() const;

  /* List of items in the current Legend */
  QMap<QString,LegendEntry> legendEntries_;

  /* map holding the descriptor for all currently "known"
   * knitting symbols (even ones not currently shown, e.g.
   * for symbols that were previously visible, had their 
   * text changed and then disappered again since the user
   * removed all instances of the symbol from the pattern) */
  QMap<QString,QString> symbolDescriptors_;
  QString get_symbol_description_(KnittingSymbolPtr aSymbol,
    QString aColorName);
  
  /* reference count of knitting symbols currently in use */
  QMap<QString,int> usedKnittingSymbols_;

  /* use these to add/remove PatternGridItems to the scene */
  void add_patternGridItem_(PatternGridItem* anItem);
  void remove_patternGridItem_(PatternGridItem* anItem);

  /* these functions take care of resetting the canvas */
  void reset_canvas_();
  void purge_all_canvas_items_();
  void purge_legend_();
  
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

  bool handle_click_on_marker_rectangle_(
    const QGraphicsSceneMouseEvent* mouseEvent); 
  void show_rectangle_manage_menu_(PatternGridRectangle* aRect,
      const QPoint& pos);

  bool handle_click_on_grid_array_(
    const QGraphicsSceneMouseEvent* mouseEvent);
  bool handle_click_on_grid_labels_(
    const QGraphicsSceneMouseEvent* mouseEvent);

  QPair<bool,int> is_row_contiguous_(const RowItems& items) const;
  QRect find_bounding_rectangle_(const QList<RowItems>& rows) const;

};


QT_BEGIN_NAMESPACE

#endif
