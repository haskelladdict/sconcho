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

/** Qt headers */
#include <QAction>
#include <QCheckBox>
#include <QColorDialog>
#include <QDebug>
#include <QDir>
#include <QFileDialog>
#include <QFont>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QMenu>
#include <QMenuBar>
#include <QMessageBox>
#include <QPrinter>
#include <QPrintDialog>
#include <QPushButton>
#include <QSettings>
#include <QSplitter>
#include <QStatusBar>
#include <QTimer>
#include <QToolBar>
#include <QToolButton>
#include <QVBoxLayout>

/** local headers */
#include "aboutSconcho.h"
#include "basicDefs.h"
#include "graphicsScene.h"
#include "gridDimensionDialog.h"
#include "helperFunctions.h"
#include "io.h"
#include "mainWindow.h"
#include "patternKeyDialog.h"
#include "patternView.h"
#include "preferencesDialog.h"
#include "symbolSelectorWidget.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
MainWindow::MainWindow() 
  :
    mainSplitter_(new QSplitter),
    settings_("sconcho","settings")
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool MainWindow::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  setWindowTitle(tr("sconcho"));
  setMinimumSize(initialSize);

  initialize_settings_();

  /* populate the main interface 
   * NOTE: We NEED to first create the patterKeyDialog and
   * symbolsWidget before we add the graphicsScence since the
   * supply some required objects */
//  create_pattern_key_dialog_();
  create_symbols_widget_();
  create_graphics_scene_();
  create_toolbar_();
  create_property_widget_();
  create_menu_bar_();
  create_status_bar_();
  create_property_symbol_layout_();
  create_timers_();

  connect(symbolSelector_,
          SIGNAL(selected_symbol_changed(const KnittingSymbolPtr)),
          canvas_,
          SLOT(update_selected_symbol(const KnittingSymbolPtr)),
          Qt::DirectConnection
         );

  connect(this,
          SIGNAL(color_changed(QColor)),
          canvas_,
          SLOT(update_selected_background_color(QColor)),
          Qt::DirectConnection
         );

  connect(this,
          SIGNAL(settings_changed()),
          canvas_,
          SLOT(update_after_settings_change())
         );
         

  /* set up main interface and set initial splitter sizes */
  mainSplitter_->addWidget(canvasView_);
  mainSplitter_->addWidget(propertyBox_);
  QList<int> sizes;
  sizes << 450 << 250;
  mainSplitter_->setSizes(sizes);
  setCentralWidget(mainSplitter_);
  return true;
}

/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// update the display widget with the current mouse position
//-------------------------------------------------------------
void MainWindow::update_mouse_position_display(QPointF newPosition)
{
  QString xPos;
  xPos.setNum(newPosition.x());
  QString yPos;
  yPos.setNum(newPosition.y());
  
  QString newLabel = "X : " + xPos + "   " + "Y : " + yPos;
  currentMousePosWidget_->setText(newLabel);
}


//-------------------------------------------------------------
// show messages in status bar 
//-------------------------------------------------------------
void MainWindow::show_statusBar_message(QString aMessage)
{
  QPalette aPalette = statusBarMessages_->palette();
  aPalette.setBrush(QPalette::WindowText, Qt::black);
  statusBarMessages_->setPalette(aPalette);
  statusBarMessages_->setText(aMessage);
}


//-------------------------------------------------------------
// show errors in status bar 
//-------------------------------------------------------------
void MainWindow::show_statusBar_error(QString aMessage)
{
  QPalette aPalette = statusBarMessages_->palette();
  aPalette.setBrush(QPalette::WindowText, Qt::red);
  statusBarMessages_->setPalette(aPalette);
  statusBarMessages_->setText(aMessage);
}


//--------------------------------------------------------------
// clear the status bar
//--------------------------------------------------------------
void MainWindow::clear_statusBar()
{
  QPalette aPalette = statusBarMessages_->palette();
  aPalette.setBrush(QPalette::WindowText, Qt::black);
  statusBarMessages_->setPalette(aPalette);
  statusBarMessages_->setText(tr("Nice pattern!"));
}


//--------------------------------------------------------------
// zooming
//
// These are public since we need to call them from our canvas
// if the user utilizes her mouse wheel for zooming in/out
//--------------------------------------------------------------
void MainWindow::zoom_in()
{
  canvasView_->scale(1.1,1.1);
}


void MainWindow::zoom_out()
{
  canvasView_->scale(0.9,0.9);
}



//------------------------------------------------------------
// tries to fit the current content on the canvas
// into the active view
//------------------------------------------------------------
void MainWindow::fit_in_view()
{
  QRectF canvasRect(canvas_->sceneRect());
  canvasRect.adjust(-30,-30,0,0);
  canvasView_->setSceneRect(canvasRect);
  canvasView_->centerOn(canvasRect.center());
}



/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// SLOT: show file open menu
//-------------------------------------------------------------
void MainWindow::show_file_open_dialog_()
{
  QString currentDirectory = QDir::currentPath();
  QString openFileName = QFileDialog::getOpenFileName(this,
    tr("open data file"), currentDirectory,
    tr("sconcho pattern files (*.spf)"));

  if ( openFileName.isEmpty() )
  {
    return;
  }

  /* extract file extension and make sure it corresponds to
   * a supported format */
  QFileInfo openFileInfo(openFileName);
  QString extension = openFileInfo.completeSuffix();

  if (extension != "spf")
  {
    QMessageBox::warning(this, tr("Warning"),
      tr("Can not open file with format ") + extension,
      QMessageBox::Ok);
    return;
  }

  load_canvas_(openFileName);
}

  
//-------------------------------------------------------------
// SLOT: show file save menu
//-------------------------------------------------------------
void MainWindow::show_file_save_dialog_()
{
  QString currentDirectory = QDir::currentPath();
  QString saveFileName = QFileDialog::getSaveFileName(this,
    tr("Save Pattern"), currentDirectory,
    tr("sconcho pattern files (*.spf)"));

  if ( saveFileName.isEmpty() )
  {
    return;
  }

  /* extract file extension and make sure it corresponds to
   * a supported format */
  QFileInfo saveFileInfo(saveFileName);
  QString extension = saveFileInfo.completeSuffix();

  if (extension != "spf")
  {
    QMessageBox::warning(this, tr("Warning"),
      tr("Unknown file format ") + extension,
      QMessageBox::Ok);
    return;
  }

  save_canvas_(saveFileName);
}



//-------------------------------------------------------------
// SLOT: show file export menu
//-------------------------------------------------------------
void MainWindow::export_canvas_dialog_()
{
  QString exportFilename = show_file_export_dialog();
  if (exportFilename.isEmpty())
  {
    return;
  }
  
  export_scene(exportFilename, canvas_);
}


//------------------------------------------------------------
// SLOT: show the print menu
//------------------------------------------------------------
void MainWindow::show_print_dialog_()
{
  print_scene(canvas_);
}


//-------------------------------------------------------------
// SLOT: close the application
//-------------------------------------------------------------
void MainWindow::quit_sconcho_()
{
  QMessageBox::StandardButton answer = QMessageBox::warning(this,
      tr("Warning"), tr("Are you sure you want to quit?"),
      QMessageBox::Yes | QMessageBox::No);

  if ( answer == QMessageBox::Yes )
  {
    exit(0);
  }
}


//------------------------------------------------------------
// SLOT: fire up color dialog and tell canvas about the
// currently selected color
//------------------------------------------------------------
void MainWindow::pick_color_()
{
  QColor selection = QColorDialog::getColor(Qt::white,this,
      "Select background color");

  QPalette selectorPalette = QPalette(selection);
  colorSelector_->setPalette(selectorPalette);

  emit color_changed(selection);
}



//------------------------------------------------------------
// SLOTS for zooming and paning
//------------------------------------------------------------
void MainWindow::pan_down_()
{
  canvasView_->translate(0,-30);
}


void MainWindow::pan_left_()
{
  canvasView_->translate(30,0);
}


void MainWindow::pan_right_()
{
  canvasView_->translate(-30,0);
}


void MainWindow::pan_up_()
{
  canvasView_->translate(0,30);
}



//------------------------------------------------------------
// this slot handles user requests to reset the pattern grid
// and create a new one of a certain dimension
//------------------------------------------------------------
void MainWindow::reset_grid_()
{
  /* first off, let's warn the user that she is about to
   * loose all her work */
  QMessageBox warn(QMessageBox::Critical, tr("Warning"),
      "Resetting the grid will cause the loss of "
      "everything that is in the current pattern "
      "grid. Is this ok?",
      QMessageBox::Ok | QMessageBox::Cancel);

  int status = warn.exec();
  
  if (status != QMessageBox::Ok)
  {
    return;
  }

  /* ask for new grid dimensions and reset canvas */
  QSize newDimensions = show_grid_dimension_dialog_();
  canvas_->reset_grid(newDimensions);
}


//-------------------------------------------------------------
// slot responsible for displaying a the default Qt info
// widget
//-------------------------------------------------------------
void MainWindow::show_about_qt_dialog_()
{
  QMessageBox::aboutQt(this,tr("About Qt"));
}


//------------------------------------------------------------- 
// slot responsible for displaying our very own personalized
// sconcho info and copyright notice
//------------------------------------------------------------- 
void MainWindow::show_sconcho_dialog_() 
{ 
  AboutSconchoWidget about; 
  about.exec(); 
} 


//------------------------------------------------------------
// fire up the preferences dialog
//------------------------------------------------------------
void MainWindow::show_preferences_dialog_()
{
  PreferencesDialog prefDialog(settings_);
  prefDialog.Init();

  /* update all child widgets with new preferences */
  emit settings_changed();
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//------------------------------------------------------------
// create the menu bar
//------------------------------------------------------------
void MainWindow::create_menu_bar_()
{
  menuBar_ = new QMenuBar(this);
  setMenuBar(menuBar_);

  /* create the individual menu options */
  create_file_menu_();
  create_edit_menu_();
  create_view_menu_();
  create_grid_menu_();
  create_help_menu_();
} 


//------------------------------------------------------------
// create the file menu 
//------------------------------------------------------------
void MainWindow::create_file_menu_()
{
  QMenu* fileMenu = menuBar_->addMenu(tr("&File"));

  /* open */
  QAction* openAction =
    new QAction(QIcon(":/icons/fileopen.png"),tr("&Open"), this);
  fileMenu->addAction(openAction);
  openAction->setShortcut(tr("Ctrl+O"));
  connect(openAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(show_file_open_dialog_()));

  fileMenu->addSeparator();

  /* save */
  QAction* saveAction =
    new QAction(QIcon(":/icons/filesave.png"),tr("&Save"), this);
  fileMenu->addAction(saveAction);
  saveAction->setShortcut(tr("Ctrl+S"));
  connect(saveAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(show_file_save_dialog_()));

  /* export */
  QAction* exportAction =
    new QAction(QIcon(":/icons/fileexport.png"),tr("&Export"), this);
  fileMenu->addAction(exportAction);
  exportAction->setShortcut(tr("Ctrl+E"));
  connect(exportAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(export_canvas_dialog_()));

  /* print */
  QAction* printAction =
    new QAction(QIcon(":/icons/fileprint.png"),tr("&Print"), this);
  fileMenu->addAction(printAction);
  printAction->setShortcut(tr("Ctrl+P"));
  connect(printAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(show_print_dialog_()));

  fileMenu->addSeparator();

  /* exit */
  QAction* exitAction =
    new QAction(QIcon(":/icons/exit.png"),tr("E&xit"), this);
  fileMenu->addAction(exitAction);
  exitAction->setShortcut(tr("Ctrl+X"));
  connect(exitAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(quit_sconcho_()));
} 



//------------------------------------------------------------
// create the edit menu for general pattern grid controls 
//------------------------------------------------------------
void MainWindow::create_edit_menu_()
{
  QMenu* editMenu = menuBar_->addMenu(tr("&Edit"));

  /* preferences */
  QAction* preferencesAction = 
    new QAction(tr("&Preferences"), this);
  editMenu->addAction(preferencesAction);
  connect(preferencesAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(show_preferences_dialog_()));
} 


//------------------------------------------------------------
// create the view menu for general view control of canvas
//------------------------------------------------------------
void MainWindow::create_view_menu_()
{
  QMenu* viewMenu = menuBar_->addMenu(tr("&View"));

  /* zoom in */
  QAction* zoomInAction =
    new QAction(QIcon(":/icons/viewmag+.png"),tr("&Zoom in"), this);
  viewMenu->addAction(zoomInAction);
  zoomInAction->setShortcut(tr("Ctrl++"));
  connect(zoomInAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(zoom_in()));

  /* zoom out */
  QAction* zoomOutAction =
    new QAction(QIcon(":/icons/viewmag-.png"),tr("&Zoom out"), this);
  viewMenu->addAction(zoomOutAction);
  zoomOutAction->setShortcut(tr("Ctrl+-"));
  connect(zoomOutAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(zoom_out()));

  /* zoom in */
  QAction* fitAction =
    new QAction(QIcon(":/icons/viewmagfit.png"),tr("&Fit view"), this);
  viewMenu->addAction(fitAction);
  fitAction->setShortcut(tr("Ctrl+0"));
  connect(fitAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(fit_in_view()));
} 


//------------------------------------------------------------
// create the grid menu for general pattern grid controls 
//------------------------------------------------------------
void MainWindow::create_grid_menu_()
{
  QMenu* gridMenu = menuBar_->addMenu(tr("&Grid"));

  /* reset */
  QAction* gridResetAction = 
    new QAction(tr("&Reset Grid"), this);
  gridMenu->addAction(gridResetAction);
  gridResetAction->setShortcut(tr("Ctrl+R"));
  connect(gridResetAction, 
          SIGNAL(triggered()), 
          this,
          SLOT(reset_grid_()));
} 



//------------------------------------------------------------
// create the grid menu for general pattern grid controls 
//------------------------------------------------------------
void MainWindow::create_help_menu_()
{
  QMenu* helpMenu = menuBar_->addMenu(tr("&Help"));

  /* add entries */
  QAction* aboutAction = new QAction(tr("&About"),this);
  helpMenu->addAction(aboutAction);
  connect(aboutAction, SIGNAL(triggered()), this,
      SLOT(show_sconcho_dialog_()));

  QAction* aboutQtAction = new QAction(tr("About Qt"),this);
  helpMenu->addAction(aboutQtAction);
  connect(aboutQtAction, SIGNAL(triggered()), this,
      SLOT(show_about_qt_dialog_()));
} 



//------------------------------------------------------------
// create the status bar
//------------------------------------------------------------
void MainWindow::create_status_bar_()
{
  statusBar_ = new QStatusBar(this);
  statusBar_->setSizeGripEnabled(false);

  /* add welcome message widget */
  QString message = "Welcome to " + IDENTIFIER;
  statusBarMessages_ = new QLabel(message);
  statusBarMessages_->setMinimumWidth(200);
  statusBar_->addWidget(statusBarMessages_,1);

  /* add widget to display the mouse position */
  currentMousePosWidget_ = new QLabel;
  currentMousePosWidget_->setMinimumWidth(200);
  currentMousePosWidget_->setAlignment(Qt::AlignCenter);
  statusBar_->addPermanentWidget(currentMousePosWidget_,0);
  

  /* add to main window */
  setStatusBar(statusBar_);
}


//-------------------------------------------------------------
// initialize all the settings
//-------------------------------------------------------------
void MainWindow::initialize_settings_()
{
  /* font properties for canvas text */
  QString preferenceFont = settings_.value("global/font").toString();
  if (preferenceFont == "")
  {
    settings_.setValue("global/font","Arial,10,-1,5,50,0,0,0,0,0");
  }
}


//-------------------------------------------------------------
// create the main GraphicsScene widget
//-------------------------------------------------------------
void MainWindow::create_graphics_scene_()
{
  /* ask user for the grid size */
  QSize gridSize = show_grid_dimension_dialog_();

  /* get default symbol from symbol selector widget */
  KnittingSymbolPtr defaultSymbol = symbolSelector_->selected_symbol();

  /* create canvas */
  QPoint origin(0,0);
  canvas_ = new GraphicsScene(origin, gridSize, GRID_CELL_SIZE, 
      settings_, defaultSymbol, this);
  if ( !canvas_->Init() )
  {
    qDebug() << "Failed to initialize canvas";
  }

  canvasView_ = new PatternView(canvas_);
  canvasView_->Init();

  fit_in_view();
}


//-------------------------------------------------------------
// create the widget showing the available symbols 
//-------------------------------------------------------------
void MainWindow::create_symbols_widget_()
{
  symbolSelector_ = new SymbolSelectorWidget(GRID_CELL_SIZE, this);
  symbolSelector_->Init();
}


//-------------------------------------------------------------
// create toolbar
//-------------------------------------------------------------
void MainWindow::create_toolbar_()
{
  QToolBar* toolBar = new QToolBar(this);

  QToolButton* openButton = new QToolButton(this);
  openButton->setIcon(QIcon(":/icons/fileopen.png"));
  openButton->setToolTip(tr("open data file"));
  toolBar->addWidget(openButton);
  connect(openButton,SIGNAL(clicked()),this,
      SLOT(show_file_open_dialog_()));


  QToolButton* saveButton = new QToolButton(this);
  saveButton->setIcon(QIcon(":/icons/filesave.png"));
  saveButton->setToolTip(tr("save"));
  toolBar->addWidget(saveButton);
  connect(saveButton,
          SIGNAL(clicked()),
          this,
          SLOT(show_file_save_dialog_()));
 
  QToolButton* exportButton = new QToolButton(this);
  exportButton->setIcon(QIcon(":/icons/fileexport.png"));
  exportButton->setToolTip(tr("export canvas"));
  toolBar->addWidget(exportButton);
  connect(exportButton,
          SIGNAL(clicked()),
          this,
          SLOT(export_canvas_dialog_()));
 
  QToolButton* printButton = new QToolButton(this);
  printButton->setIcon(QIcon(":/icons/fileprint.png"));
  printButton->setToolTip(tr("print canvas"));
  toolBar->addWidget(printButton);
  connect(printButton,
          SIGNAL(clicked()),
          this,
          SLOT(show_print_dialog_()));

  toolBar->addSeparator();

  QToolButton* zoomInButton = new QToolButton(this);
  zoomInButton->setIcon(QIcon(":/icons/viewmag+.png"));
  zoomInButton->setToolTip(tr("zoom in"));
  toolBar->addWidget(zoomInButton);
  connect(zoomInButton,
          SIGNAL(clicked()),
          this,
          SLOT(zoom_in()));
  
  QToolButton* zoomOutButton = new QToolButton(this);
  zoomOutButton->setIcon(QIcon(":/icons/viewmag-.png"));
  zoomOutButton->setToolTip(tr("zoom out"));
  toolBar->addWidget(zoomOutButton);
  connect(zoomOutButton,
          SIGNAL(clicked()),
          this,
          SLOT(zoom_out()));

  QToolButton* resetButton = new QToolButton(this);
  resetButton->setIcon(QIcon(":/icons/viewmagfit.png"));
  resetButton->setToolTip(tr("fit view"));
  toolBar->addWidget(resetButton);
  connect(resetButton,
          SIGNAL(clicked()),
          this,
          SLOT(fit_in_view()));
  
  toolBar->addSeparator();
 
  QToolButton* leftMoveButton = new QToolButton(this);
  leftMoveButton->setIcon(QIcon(":/icons/left.png"));
  leftMoveButton->setToolTip(tr("move canvas left"));
  toolBar->addWidget(leftMoveButton);
  connect(leftMoveButton,
          SIGNAL(clicked()),
          this,
          SLOT(pan_left_()));
  
  QToolButton* rightMoveButton = new QToolButton(this);
  rightMoveButton->setIcon(QIcon(":/icons/right.png"));
  rightMoveButton->setToolTip(tr("move canvas right"));
  toolBar->addWidget(rightMoveButton);
  connect(rightMoveButton,
          SIGNAL(clicked()),
          this,
          SLOT(pan_right_()));

  QToolButton* upMoveButton = new QToolButton(this);
  upMoveButton->setIcon(QIcon(":/icons/up.png"));
  upMoveButton->setToolTip(tr("move canvas up"));
  toolBar->addWidget(upMoveButton);
  connect(upMoveButton,
          SIGNAL(clicked()),
          this,
          SLOT(pan_up_()));
  
  QToolButton* downMoveButton = new QToolButton(this);
  downMoveButton->setIcon(QIcon(":/icons/down.png"));
  downMoveButton->setToolTip(tr("move canvas down"));
  toolBar->addWidget(downMoveButton);
  connect(downMoveButton,
          SIGNAL(clicked()),
          this,
          SLOT(pan_down_()));
  
  toolBar->addSeparator();

  QToolButton* resetSelectionButton = new QToolButton(this);
  resetSelectionButton->setIcon(QIcon(":/icons/stop.png"));
  resetSelectionButton->setToolTip(tr("reset current selection"));
  toolBar->addWidget(resetSelectionButton);
  connect(resetSelectionButton,
          SIGNAL(clicked()),
          canvas_,
          SLOT(deselect_all_active_items()));

  QToolButton* markRectangleButton = new QToolButton(this);
  markRectangleButton->setIcon(QIcon(":/icons/rectangle.png"));
  markRectangleButton->setToolTip(tr("mark selection with rectangle"));
  toolBar->addWidget(markRectangleButton);
  connect(markRectangleButton,
          SIGNAL(clicked()),
          canvas_,
          SLOT(mark_active_cells_with_rectangle()));

  QToolButton* toggleKeyButton = new QToolButton(this);
  toggleKeyButton->setIcon(QIcon(":/icons/key.png"));
  toggleKeyButton->setToolTip(tr("toggle pattern key"));
  toolBar->addWidget(toggleKeyButton);
  connect(toggleKeyButton,
          SIGNAL(clicked()),
          canvas_,
          SLOT(toggle_legend_visibility()));

  addToolBar(toolBar);
}


//-------------------------------------------------------------
// create graph property widget (color selector, line width
// selector)
//-------------------------------------------------------------
void MainWindow::create_property_widget_()
{
   colorSelector_ = new QPushButton(this);
   colorSelector_->setText(tr("cell color"));
   colorSelector_->setMaximumSize(70,50);
   QPalette widgetColor = QPalette(Qt::white);
   colorSelector_->setPalette(widgetColor);

   QCheckBox* colorChecker = new QCheckBox("add to cell");
   colorChecker->setChecked(false);

   colorSelectorGrouper_ = new QGroupBox;
   QHBoxLayout* colorLayout = new QHBoxLayout;
   colorLayout->addWidget(colorChecker);
   colorLayout->addWidget(colorSelector_);
   colorSelectorGrouper_->setLayout(colorLayout);

   connect(colorChecker,
           SIGNAL(stateChanged(int)),
           canvas_,
           SLOT(color_state_changed(int)));

   connect(colorSelector_,
           SIGNAL(clicked()),
           this,
           SLOT(pick_color_()));
}



//-------------------------------------------------------------
// create the main splitter
// 
// NOTE: all Widgets that belong to the splitter have to exist
//       at this point
//-------------------------------------------------------------
void MainWindow::create_property_symbol_layout_()
{
  /* properties layout */
  QVBoxLayout* propertiesLayout = new QVBoxLayout;
  propertiesLayout->addWidget(symbolSelector_);
  propertiesLayout->addWidget(colorSelectorGrouper_);
  propertyBox_ = new QGroupBox(this);
  propertyBox_->setLayout(propertiesLayout);
}


//-------------------------------------------------------------
// create all timers used during exectution
//-------------------------------------------------------------
void MainWindow::create_timers_()
{
  /* this timers clears the status bar every so ofter */
  QTimer* statusBarTimer = new QTimer(this);
  connect(statusBarTimer,
          SIGNAL(timeout()),
          this,
          SLOT(clear_statusBar()));
  statusBarTimer->start(5000);
}


//-------------------------------------------------------------
// open dialog to ask user for the dimensions of the pattern
// grid
//-------------------------------------------------------------
QSize MainWindow::show_grid_dimension_dialog_()
{
  GridDimensionDialog gridDialog; 
  gridDialog.Init();
  return gridDialog.dim();
}


//--------------------------------------------------------------
// save canvas to file
//-------------------------------------------------------------
void MainWindow::save_canvas_(const QString& fileName)
{
  CanvasIOWriter writer(canvas_, fileName);

  /* we need to check if we can open the file for writing */
  if (!writer.Init())
  {
    QMessageBox::critical(0,"Save File",
      QString("Failed to open file\n%1\nfor saving.") 
      .arg(fileName));
    return;
  }
  else
  {
    writer.save();
  }
}


//-------------------------------------------------------------
// load a previously saved canvas from file
//-------------------------------------------------------------
void MainWindow::load_canvas_(const QString& fileName)
{
  CanvasIOReader reader(canvas_, fileName);

  /* we need to make sure that we are able to open the file 
   * for reading */
  if (!reader.Init())
  {
    QMessageBox::critical(0,"Read File",
      QString("Failed to open file\n%1\nfor reading.") 
      .arg(fileName));
    return;
  }
  else
  {
    reader.read();
  }
}


QT_BEGIN_NAMESPACE
