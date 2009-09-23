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
#include <QColorDialog>
#include <QDebug>
#include <QDir>
#include <QFileDialog>
#include <QGraphicsView>
#include <QGraphicsTextItem>
#include <QGroupBox>
#include <QLabel>
#include <QMenu>
#include <QMenuBar>
#include <QMessageBox>
#include <QPrinter>
#include <QPrintDialog>
#include <QPushButton>
#include <QSplitter>
#include <QStatusBar>
#include <QToolBar>
#include <QToolButton>
#include <QVBoxLayout>

/** local headers */
#include "basicDefs.h"
#include "graphicsScene.h"
#include "gridDimensionDialog.h"
#include "knittingSymbol.h"
#include "mainWindow.h"
#include "symbolSelectorWidget.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
MainWindow::MainWindow() 
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

  /* populate the main interface */
  create_menu_bar_();
  create_file_menu_();
  create_status_bar_();
  create_graphics_scene_();
  create_symbols_widget_();
  create_toolbar_();
  create_property_widget_();
  create_main_splitter_();

  connect(symbolSelector_,
          SIGNAL(selected_symbol_changed(const KnittingSymbolPtr)),
          canvas_,
          SLOT(update_selected_symbol(const KnittingSymbolPtr))
         );

  connect(this,
          SIGNAL(color_changed(QColor)),
          canvas_,
          SLOT(update_current_color(QColor)));

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
// update the status bar message
//-------------------------------------------------------------
void MainWindow::show_statusBar_message(QString aMessage)
{
  statusBarMessages_->setText(aMessage);
}



/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

//-------------------------------------------------------------
// SLOT: show file open menu
//-------------------------------------------------------------
void MainWindow::show_file_open_menu_()
{
  QString currentDirectory = QDir::currentPath();
  QString fileName = QFileDialog::getOpenFileName(this,
    tr("open data file"), currentDirectory,
    tr("data files (*.dat)"));
}



//-------------------------------------------------------------
// SLOT: show file export menu
//-------------------------------------------------------------
void MainWindow::show_file_export_menu_()
{
  QString currentDirectory = QDir::currentPath();
  QString saveFileName = QFileDialog::getSaveFileName(this,
    tr("Export Canvas"), currentDirectory,
    tr("Image Files (*.png *.tif *.jpg *.gif)"));

  if ( saveFileName.isEmpty() )
  {
    return;
  }

  /* extract file extension and make sure it corresponds to
   * a supported format */
  QFileInfo saveFileInfo(saveFileName);
  QString extension = saveFileInfo.completeSuffix();

  if ( extension != "png" && extension != "tif" 
       && extension != "jpg" && extension != "gif" )
  {
    QMessageBox::warning(this, tr("Warning"),
      tr("Unknown file format ") + extension,
      QMessageBox::Ok);
    return;
  }

  /* for now print the image in a fixed resolution 
   * NOTE: We seem to need the 1px buffer region to avoid
   *       the image being cut off */
  QRectF theScene = canvas_->sceneRect();
  theScene.adjust(-10,-10,10,10);  // need this to avoid cropping

  QImage finalImage(theScene.width()*3, theScene.height() *3,
      QImage::Format_ARGB32_Premultiplied);
  QPainter painter(&finalImage);
  painter.setRenderHints(QPainter::SmoothPixmapTransform);
  painter.setRenderHints(QPainter::HighQualityAntialiasing);
  painter.setRenderHints(QPainter::TextAntialiasing);

  canvas_->render(&painter, QRectF(), theScene);
  painter.end();
  finalImage.save(saveFileName); 
}



//------------------------------------------------------------
// SLOT: show the print menu
//------------------------------------------------------------
void MainWindow::show_print_menu_()
{
  /* create printer and fire up print dialog */
  QPrinter aPrinter(QPrinter::HighResolution);
  QPrintDialog printDialog(&aPrinter, this);
  if ( printDialog.exec() == QDialog::Accepted )
  {
    /* tell our canvas that we want to print its */
    QPainter painter(&aPrinter);
    painter.setRenderHints(QPainter::SmoothPixmapTransform);
    painter.setRenderHints(QPainter::HighQualityAntialiasing);
    painter.setRenderHints(QPainter::TextAntialiasing);
    canvas_->render(&painter);
    painter.end();
  }
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

  QPalette selectorColor = QPalette(selection);
  colorSelector_->setPalette(selectorColor);

  emit color_changed(selection);
}



//------------------------------------------------------------
// SLOTS for zooming and paning
//------------------------------------------------------------
void MainWindow::zoom_in_()
{
  canvasView_->scale(1.1,1.1);
}


void MainWindow::zoom_out_()
{
  canvasView_->scale(0.9,0.9);
}


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


void MainWindow::fit_in_view_()
{
  QRectF canvasSize(canvas_->sceneRect());
  canvasSize.adjust(-30,-30,30,30);
  canvasView_->fitInView(canvasSize,Qt::KeepAspectRatio);
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
  connect(openAction, SIGNAL(triggered()), this,
      SLOT(show_file_open_menu_()));

  fileMenu->addSeparator();

  /* export */
  QAction* exportAction =
    new QAction(QIcon(":/icons/fileexport.png"),tr("&Export"), this);
  fileMenu->addAction(exportAction);
  exportAction->setShortcut(tr("Ctrl+E"));
  connect(exportAction, SIGNAL(triggered()), this,
      SLOT(show_file_export_menu_()));

  /* print */
  QAction* printAction =
    new QAction(QIcon(":/icons/fileprint.png"),tr("&Print"), this);
  fileMenu->addAction(printAction);
  printAction->setShortcut(tr("Ctrl+P"));
  connect(printAction, SIGNAL(triggered()), this,
      SLOT(show_print_menu_()));

  fileMenu->addSeparator();

  /* exit */
  QAction* exitAction =
    new QAction(QIcon(":/icons/exit.png"),tr("E&xit"), this);
  fileMenu->addAction(exitAction);
  exitAction->setShortcut(tr("Ctrl+X"));
  connect(exitAction, SIGNAL(triggered()), this,
      SLOT(quit_sconcho_()));
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
// create the main GraphicsScene widget
//-------------------------------------------------------------
void MainWindow::create_graphics_scene_()
{
  canvas_ = new GraphicsScene(this);
  if ( !canvas_->Init() )
  {
    qDebug() << "Failed to initialize canvas";
  }

  canvasView_ = new QGraphicsView(canvas_);
  canvasView_->setDragMode(QGraphicsView::RubberBandDrag);
  canvasView_->setTransformationAnchor(QGraphicsView::NoAnchor); 
  canvasView_->setRenderHints(QPainter::Antialiasing);

  /* ask user for the grid size */
  GridDimensionDialog* gridDialog = new GridDimensionDialog;
  gridDialog->Init();
  QSize gridSize = gridDialog->dim();
  delete gridDialog;

  /* create pattern grid */
  canvas_->create_pattern_grid(QPoint(0,0), gridSize, 30);
  fit_in_view_();
}


//-------------------------------------------------------------
// create the widget showing the available symbols 
//-------------------------------------------------------------
void MainWindow::create_symbols_widget_()
{
  symbolSelector_ = new SymbolSelectorWidget(this);
  symbolSelector_->Init();
}


//-------------------------------------------------------------
// create toolbar
//-------------------------------------------------------------
void MainWindow::create_toolbar_()
{
  QToolBar* toolBar = new QToolBar(this);

  /* FIXME: not implemented yet */
/*  QToolButton* openButton = new QToolButton(this);
  openButton->setIcon(QIcon(":/icons/fileopen.png"));
  openButton->setToolTip(tr("open data file"));
  toolBar->addWidget(openButton);
  connect(openButton,SIGNAL(clicked()),this,
      SLOT(show_file_open_menu_()));
*/

  QToolButton* exportButton = new QToolButton(this);
  exportButton->setIcon(QIcon(":/icons/fileexport.png"));
  exportButton->setToolTip(tr("export canvas"));
  toolBar->addWidget(exportButton);
  connect(exportButton,
          SIGNAL(clicked()),
          this,
          SLOT(show_file_export_menu_()));
 
  QToolButton* printButton = new QToolButton(this);
  printButton->setIcon(QIcon(":/icons/fileprint.png"));
  printButton->setToolTip(tr("print canvas"));
  toolBar->addWidget(printButton);
  connect(printButton,
          SIGNAL(clicked()),
          this,
          SLOT(show_print_menu_()));

  toolBar->addSeparator();

  QToolButton* zoomInButton = new QToolButton(this);
  zoomInButton->setIcon(QIcon(":/icons/viewmag+.png"));
  zoomInButton->setToolTip(tr("zoom in"));
  toolBar->addWidget(zoomInButton);
  connect(zoomInButton,SIGNAL(clicked()),this,SLOT(zoom_in_()));
  
  QToolButton* zoomOutButton = new QToolButton(this);
  zoomOutButton->setIcon(QIcon(":/icons/viewmag-.png"));
  zoomOutButton->setToolTip(tr("zoom out"));
  toolBar->addWidget(zoomOutButton);
  connect(zoomOutButton,SIGNAL(clicked()),this,SLOT(zoom_out_()));

  toolBar->addSeparator();

  QToolButton* resetButton = new QToolButton(this);
  resetButton->setIcon(QIcon(":/icons/gohome.png"));
  resetButton->setToolTip(tr("reset view"));
  toolBar->addWidget(resetButton);
  connect(resetButton,SIGNAL(clicked()),this,SLOT(fit_in_view_()));
  
  toolBar->addSeparator();
 
  QToolButton* leftMoveButton = new QToolButton(this);
  leftMoveButton->setIcon(QIcon(":/icons/left.png"));
  leftMoveButton->setToolTip(tr("move canvas left"));
  toolBar->addWidget(leftMoveButton);
  connect(leftMoveButton,SIGNAL(clicked()),this,SLOT(pan_left_()));
  
  QToolButton* rightMoveButton = new QToolButton(this);
  rightMoveButton->setIcon(QIcon(":/icons/right.png"));
  rightMoveButton->setToolTip(tr("move canvas right"));
  toolBar->addWidget(rightMoveButton);
  connect(rightMoveButton,SIGNAL(clicked()),this,SLOT(pan_right_()));

  QToolButton* upMoveButton = new QToolButton(this);
  upMoveButton->setIcon(QIcon(":/icons/up.png"));
  upMoveButton->setToolTip(tr("move canvas up"));
  toolBar->addWidget(upMoveButton);
  connect(upMoveButton,SIGNAL(clicked()),this,SLOT(pan_up_()));
  
  QToolButton* downMoveButton = new QToolButton(this);
  downMoveButton->setIcon(QIcon(":/icons/down.png"));
  downMoveButton->setToolTip(tr("move canvas down"));
  toolBar->addWidget(downMoveButton);
  connect(downMoveButton,SIGNAL(clicked()),this,SLOT(pan_down_()));
  
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
void MainWindow::create_main_splitter_()
{
  /* properties layout */
  QVBoxLayout* propertiesLayout = new QVBoxLayout;
  propertiesLayout->addWidget(symbolSelector_);
  propertiesLayout->addWidget(colorSelector_);
  QGroupBox* propertyBox = new QGroupBox(this);
  propertyBox->setLayout(propertiesLayout);

  
  mainSplitter_ = new QSplitter(this);
  mainSplitter_->addWidget(canvasView_);
  mainSplitter_->addWidget(propertyBox);
}
