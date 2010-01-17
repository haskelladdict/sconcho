/***************************************************************
*
* (c) 2009-2010 Markus Dittrich 
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
#include <QGraphicsSceneMouseEvent>
#include <QWheelEvent>

#include <QScrollBar>

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
  setDragMode(QGraphicsView::NoDrag);
  setRenderHints(QPainter::Antialiasing);

  initialize_rubberband_();
  visible_in_view();
  
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

//-------------------------------------------------------------
// slot responsible for making sure all graphics items
// that should be are accesible in the view
//-------------------------------------------------------------
void PatternView::accessible_in_view()
{
  // fix our view on the initial grid size; otherwise items
  // added to the legend (even if inivisible) will cause
  // spurious re-scaling
  QRectF myScene = canvas_->get_visible_area();
  myScene.adjust(-50,-50,100,100);
  setSceneRect(myScene);

  // FIXME: this is a dirty hack; there has to be a better
  // way. The following is happening: If we are in a view with
  // no scrollbar and the above call to setSceneRect forces
  // scrollbars to appear due to the scene growing, Qt will
  // move the scrollbars such that upper left corner of the
  // default view is (0,0) instead of the true upper left 
  // corner of the view. Note that all is well if we already
  // have scrollbars that are set at a given value. Hopefully,
  // the below hack won't mess with these.
  int horizontalScrollMin = horizontalScrollBar()->minimum();
  int horizontalScrollVal = horizontalScrollBar()->value();

  if ((horizontalScrollMin <= 0) && (horizontalScrollVal == 0))
  {
    horizontalScrollBar()->setValue(horizontalScrollMin);
  }

  int verticalScrollMin = verticalScrollBar()->minimum();
  int verticalScrollVal = verticalScrollBar()->value();

  if ((verticalScrollMin <= 0) && (verticalScrollVal == 0))
  {
    verticalScrollBar()->setValue(verticalScrollMin);
  }
}



//-------------------------------------------------------------
// slot responsible for making sure all graphics items
// that should be are visible in the view
//-------------------------------------------------------------
void PatternView::visible_in_view()
{
  accessible_in_view();

  /* center the view on the pattern grid */
  QPoint gridCenter = canvas_->get_grid_center();
  centerOn(mapFromScene(gridCenter));

  setMatrix(QMatrix());
}



//-------------------------------------------------------------
// slot responsible for zooming into the canvas
//-------------------------------------------------------------
void PatternView::zoom_in()
{
  QPointF center(mapToScene(rect()).boundingRect().center());
  scale(1.1,1.1);
  centerOn(center);
}


//-------------------------------------------------------------
// slot responsible for zooming out of the canvas
//-------------------------------------------------------------
void PatternView::zoom_out()
{
  QPointF center(mapToScene(rect()).boundingRect().center());
  scale(0.9,0.9);
  centerOn(center);
}



//------------------------------------------------------------
// SLOTS for paning
//------------------------------------------------------------
void PatternView::pan_down()
{
  translate(0,-30);
}


void PatternView::pan_left()
{
  translate(30,0);
}


void PatternView::pan_right()
{
  translate(-30,0);
}


void PatternView::pan_up()
{
  translate(0,30);
}



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


//--------------------------------------------------------------
// event handler for mouse wheel events
//--------------------------------------------------------------
void PatternView::wheelEvent(QWheelEvent* aWheelEvent)
{
  if (aWheelEvent->modifiers().testFlag(Qt::ControlModifier) 
      && aWheelEvent->delta() > 0)
  {
    zoom_in();
  }
  else if (aWheelEvent->modifiers().testFlag(Qt::ControlModifier)
           && aWheelEvent->delta() < 0)
  {
    zoom_out();
  }
  else
  {
    QGraphicsView::wheelEvent(aWheelEvent);
  }
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
