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
#include <QDebug>
#include <QDir>
#include <QFileDialog>
#include <QGraphicsView>
#include <QGraphicsTextItem>
#include <QLabel>
#include <QMenu>
#include <QMenuBar>
#include <QMessageBox>
#include <QPrinter>
#include <QPrintDialog>
#include <QSplitter>
#include <QStatusBar>


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
  create_main_splitter_();

  connect(symbolSelector_,
          SIGNAL(selected_symbol_changed(const KnittingSymbolPtr)),
          canvas_,
          SLOT(update_selected_symbol(const KnittingSymbolPtr))
         );


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
  QImage finalImage(2*canvas_->width()+1, 2*canvas_->height()+1,
      QImage::Format_ARGB32_Premultiplied);
  QPainter painter(&finalImage);
  painter.setRenderHints(QPainter::SmoothPixmapTransform);
  painter.setRenderHints(QPainter::HighQualityAntialiasing);
  painter.setRenderHints(QPainter::TextAntialiasing);
  canvas_->render(&painter);
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

  /* ask user for the grid size */
  GridDimensionDialog* gridDialog = new GridDimensionDialog;
  gridDialog->Init();
  QSize gridSize = gridDialog->dim();
  delete gridDialog;

  /* create grid item */
  canvas_->create_pattern_grid(QPoint(0,0), gridSize, 30);

  //QGraphicsTextItem* key = new QGraphicsTextItem("Key");
  //key->setPos(0, gridSize.height()*30+20);
  //canvas_->addItem(key);
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
// create the main splitter
// 
// NOTE: all Widgets that belong to the splitter have to exist
//       at this point
//-------------------------------------------------------------
void MainWindow::create_main_splitter_()
{
  mainSplitter_ = new QSplitter(this);
  mainSplitter_->addWidget(canvasView_);
  mainSplitter_->addWidget(symbolSelector_);
}
