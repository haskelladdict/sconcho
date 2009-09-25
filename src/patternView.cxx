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

/** local headers */
#include "basicDefs.h"
#include "patternView.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternView::PatternView(QGraphicsScene* aScene, QWidget* myParent)
  :
  QGraphicsView(aScene, myParent),
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
// deal with mouse events and how they translate into rubber
// band geometry changes if one is requested
//-------------------------------------------------------------
void PatternView::mouseReleaseEvent(QMouseEvent* evt)
{
  if (rubberBandOn_)
  {
    qDebug() << "stop rubber band";
    rubberBandOn_ = false;
    rubberBand_->hide();
  }

  QGraphicsView::mouseReleaseEvent(evt);
}



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



void PatternView::mouseMoveEvent(QMouseEvent* evt)
{
  if (rubberBandOn_)
  {
    rubberBand_->setGeometry(QRect(rubberBandOrigin_,evt->pos()).normalized());
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
  rubberBand_ = new QRubberBand(QRubberBand::Line, this);

  /* change colors
   * FIXME: Background coloring does not work for some reason */
  rubberBand_->setAutoFillBackground(true);
  QPalette aPalette = rubberBand_->palette();
  aPalette.setColor(QPalette::Base, Qt::blue);
  aPalette.setColor(QPalette::WindowText, Qt::red);
  rubberBand_->setPalette(aPalette);
}
