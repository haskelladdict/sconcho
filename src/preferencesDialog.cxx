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
#include <QFontComboBox>
#include <QFontDialog>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QVBoxLayout>

/** local headers */
#include "basicDefs.h"
#include "preferencesDialog.h"


/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
PreferencesDialog::PreferencesDialog(QSettings& theSettings,
  QWidget* myParent)
    :
      QTabWidget(myParent),
      settings_(theSettings)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool PreferencesDialog::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  qDebug() << "preferences";

  /* call individual initialization routines */
//  setFixedSize(QSize(250,130));
//  setModal(true);
  setWindowTitle(tr("Preferences"));

  /* create the interface */
  create_font_tab_();

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

//------------------------------------------------------------
// create the font widget
//------------------------------------------------------------
void PreferencesDialog::create_font_tab_()
{
  QGroupBox* fontWidget = new QGroupBox(this); 
  QVBoxLayout *mainLayout = new QVBoxLayout(this);

  QHBoxLayout *fontFamilyLayout = new QHBoxLayout(this);
  QLabel* familyLabel = new QLabel(tr("Family"));
  QFontComboBox* fonts = new QFontComboBox; 
  fontFamilyLayout->addWidget(familyLabel);
  fontFamilyLayout->addWidget(fonts);

  mainLayout->addLayout(fontFamilyLayout);
  fontWidget->setLayout(mainLayout);

  addTab(fontWidget, tr("Fonts"));
}
