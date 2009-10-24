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
#include <QGraphicsView>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QSettings>
#include <QSplitter>
#include <QVBoxLayout>


/** local headers */
#include "basicDefs.h"
#include "patternKeyCanvas.h"
#include "patternKeyDialog.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PatternKeyDialog::PatternKeyDialog(const QSettings& aSetting,
  QWidget* myParent)
    :
      QDialog(myParent),
      settings_(aSetting),
      mainSplitter_(new QSplitter)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PatternKeyDialog::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  /* call individual initialization routines */
  setModal(false);
  setWindowTitle(tr("Edit pattern key"));

  /* create interface */
  patternKeyCanvas_ = new PatternKeyCanvas(settings_, this);  
  patternKeyCanvas_->Init();
  patternKeyView_ = new QGraphicsView(patternKeyCanvas_);

  /* generate main layout */
  mainSplitter_->addWidget(patternKeyView_);
  QHBoxLayout* mainLayout = new QHBoxLayout;
  mainLayout->addWidget(mainSplitter_);
  setLayout(mainLayout);
  exec();

  return true;
}


/**************************************************************
 *
 * PUBLIC SLOTS
 *
 *************************************************************/



/**************************************************************
 *
 * PUBLIC MEMBER FUNCTIONS
 *
 *************************************************************/

/**************************************************************
 *
 * PROTECTED MEMBER FUNCTIONS 
 *
 *************************************************************/

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

QT_END_NAMESPACE
