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

/* STL includes */

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QMainWindow>
#include <QString>

/* local includes */
#include "graphicsScene.h"

/* a few forward declarations */
class GraphicsScene;
class QGraphicsView;
class QLabel;
class QMenuBar;
class QSplitter;
class QStatusBar;

/* convenience typedefs */


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

//signals:


//public slots:

  
private slots:
        
  void show_file_open_menu_();
  void show_file_export_menu_();
  void show_print_menu_();
  void quit_sconcho_();

  
private:

  /* status variable */
  int status_;

  /* interface generation functions */
  void create_menu_bar_();
  void create_file_menu_();
  void create_status_bar_();
  void create_graphics_scene_();
  void create_main_splitter_();

  /* general helper functions */

  /* widget data members */
  QSplitter* mainSplitter_;

  /* menu bar stuff */
  QMenuBar* menuBar_;

  /* status bar stuff */
  QStatusBar* statusBar_;
  QLabel* statusBarMessages_;

  /* canvas on which the actual data is being displayed */
  GraphicsScene* canvas_;
  QGraphicsView* canvasView_;
};


#endif
