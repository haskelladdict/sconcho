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
#include <QDebug>
#include <QMouseEvent>
#include <QRubberBand>

#include <QCoreApplication>
#include <QApplication>
#include <QMouseEvent>
#include <QGraphicsSceneMouseEvent>

/** local headers */
#include "basicDefs.h"
#include "graphicsScene.h"
#include "patternGridItem.h"
#include "patternView.h"


QT_BEGIN_NAMESPACE


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternView::PatternView(GraphicsScene* aScene, QWidget* myParent)
  :
  QGraphicsView(aScene, myParent),
  canvas_(aScene),
  rubberBandOn_(false)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternView::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* set some basic properties */
  setTransformationAnchor(QGraphicsView::NoAnchor);
  setDragMode(QGraphicsView::NoDrag);
  setRenderHints(QPainter::Antialiasing);
  setViewportUpdateMode(QGraphicsView::FullViewportUpdate);

  initialize_rubberband_();
  
  return true;
}


/**************************************************************
 *
 * PUBLIC FUNCTIONS
 *
 *************************************************************/

/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/

/**************************************************************
 *
 * PROTECTED 
 *
 *************************************************************/

//-------------------------------------------------------------
// deal with mouse release events and rubber band 
// events if requested
//-------------------------------------------------------------
void PatternView::mouseReleaseEvent(QMouseEvent* evt)
{
  if (rubberBandOn_)
  {
    qDebug() << "stop rubber band";

    /* retrieve final rubberBand geometry and pick
     * and select them */
    QRectF finalGeometry(
        mapToScene(rubberBand_->geometry()).boundingRect());
    canvas_->select_region(finalGeometry);

    rubberBandOn_ = false;
    rubberBand_->hide();
  }

  QGraphicsView::mouseReleaseEvent(evt);
}


//-------------------------------------------------------------
// deal with mouse press events and rubber band 
// events if requested
//-------------------------------------------------------------
void PatternView::mousePressEvent(QMouseEvent* evt)
{
  if (evt->modifiers().testFlag(Qt::ControlModifier))
  {
    qDebug() << "start rubber band";
    rubberBandOn_ = true;
    rubberBandOrigin_ = evt->pos();
    rubberBand_->move(evt->pos());
    rubberBand_->resize(0,0);
    rubberBand_->show();
  }
  
  QGraphicsView::mousePressEvent(evt);
}


//-------------------------------------------------------------
// deal with mouse move events and rubber band 
// geometry changes 
//-------------------------------------------------------------
void PatternView::mouseMoveEvent(QMouseEvent* evt)
{
  if (rubberBandOn_)
  {
    rubberBand_->setGeometry(QRect(rubberBandOrigin_,
                                   evt->pos()).normalized());
  }
    
  QGraphicsView::mouseMoveEvent(evt);
}


/**************************************************************
 *
 * PRIVATE SLOTS
 *
 *************************************************************/

/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//-------------------------------------------------------------
// set up the rubber band
//-------------------------------------------------------------
void PatternView::initialize_rubberband_()
{
  rubberBand_ = new QRubberBand(QRubberBand::Rectangle, this);

  /* change colors
   * FIXME: Background coloring does not work for some reason */
  rubberBand_->setAutoFillBackground(true);
  rubberBand_->setWindowOpacity(0.4);
  QPalette aPalette = rubberBand_->palette();
  aPalette.setBrush(QPalette::Base, Qt::blue);
  aPalette.setBrush(QPalette::WindowText, Qt::red);
  rubberBand_->setPalette(aPalette);
}


QT_END_NAMESPACE
