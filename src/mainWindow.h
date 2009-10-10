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

#ifndef MAIN_WINDOW_H
#define MAIN_WINDOW_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QMainWindow>
#include <QSettings>
#include <QSize>
#include <QString>


QT_BEGIN_NAMESPACE


/* a few forward declarations */
class GraphicsScene;
class PatternView;
class PreferencesDialog;
class QGroupBox;
class QLabel;
class QMenuBar;
class QPushButton;
class QSplitter;
class QStatusBar;
class QTabWidget;
class QVBoxLayout;
class SymbolSelectorWidget;


/* convenience typedefs and constants */
const QSize initialSize(700,500);


/* use anonymous namespace to define some constants */
namespace {
  const QString NAME = "sconcho";
  const QString VERSION = "0.0";
  const QString IDENTIFIER = NAME + " v" + VERSION;
}


/***************************************************************
 * 
 * The MainWindow class organizes the layout of sconcho's main
 * window
 *
 ***************************************************************/
class MainWindow 
  : 
    public QMainWindow,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit MainWindow();
  bool Init();

  /* this is a way for our children to retrieve the
   * settings */
  const QSettings& settings() const { return settings_; }


signals:

  void color_changed(QColor aColor);


public slots:

  void update_mouse_position_display(QPointF newPos);
  void show_statusBar_message(QString msg);
  void show_statusBar_error(QString msg);
  void zoom_in();
  void zoom_out();
 

private slots:

  void fit_in_view_();
  void pan_down_();
  void pan_left_();
  void pan_right_();
  void pan_up_();
  void pick_color_();
  void quit_sconcho_();
  void reset_grid_();
  void show_about_qt_dialog_();
  void show_file_open_dialog_();
  void show_file_save_dialog_();
  void show_file_export_dialog_();
  void show_sconcho_dialog_();
  void show_print_dialog_();
  void show_preferences_dialog_();

   
private:

  /* status variable */
  int status_;

  /* interface generation functions */
  void create_menu_bar_();
  void create_file_menu_();
  void create_edit_menu_();
  void create_view_menu_();
  void create_grid_menu_();
  void create_help_menu_();
  void create_status_bar_();
  void create_graphics_scene_();
  void create_main_splitter_();
  void create_property_widget_();
  void create_symbols_widget_();
  void create_toolbar_();

  /* widget data members */
  QSplitter* mainSplitter_;
  QMenuBar* menuBar_;

  /* status bar stuff */
  QStatusBar* statusBar_;
  QLabel* statusBarMessages_;
  QLabel* currentMousePosWidget_;

  /* canvas on which the actual data is being displayed */
  GraphicsScene* canvas_;
  PatternView* canvasView_;

  /* widgets for selectors */
  QGroupBox* colorSelectorGrouper_;
  QPushButton* colorSelector_;
  QSettings settings_;
  SymbolSelectorWidget* symbolSelector_;

  /* helper function */
  QSize show_grid_dimension_dialog_();
  void export_canvas_(const QString& fileName);
  void save_canvas_(const QString& fileName);
  void load_canvas_(const QString& fileName);
  void initialize_settings_();
};

QT_END_NAMESPACE

#endif
