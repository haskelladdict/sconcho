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
#include <QComboBox>
#include <QDebug>
#include <QFontComboBox>
#include <QFontDatabase>
#include <QFontDialog>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QList>
#include <QString>
#include <QStringList>
#include <QVBoxLayout>

/** local headers */
#include "basicDefs.h"
#include "preferencesDialog.h"


QT_BEGIN_NAMESPACE

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

  /* set current font; this should eventually come from the
   * passed in settings */
  currentFont_.fromString("DejaVu Sans,9,-1,5,50,0,0,0,0,0");

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

//-------------------------------------------------------------
// update the font style, point size and example text widgets
// if the user changes the font family
//-------------------------------------------------------------
void PreferencesDialog::update_font_selectors_(const QFont& newFont)
{
  QString family(newFont.family());
  qDebug() << newFont.toString();

  QFontDatabase database;

  QStringList availableStyles(database.styles(family));
  fontStyleBox_->clear();
  foreach(QString entry, availableStyles)
  {
    fontStyleBox_->addItem(entry);
  }

  QList<int> availableSizes(database.pointSizes(family));
  QString helper;
  fontSizeBox_->clear();
  foreach(int entry, availableSizes)
  {
    fontSizeBox_->addItem(helper.setNum(entry), QVariant(entry));
  }

}


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

  /* font family selector */
  QHBoxLayout *fontFamilyLayout = new QHBoxLayout;
  QLabel* fontFamilyLabel = new QLabel(tr("Family"));
  fontFamilyBox_ = new QFontComboBox;
  fontFamilyBox_->setCurrentFont(currentFont_);
  fontFamilyLayout->addWidget(fontFamilyLabel);
  fontFamilyLayout->addWidget(fontFamilyBox_);

  connect(fontFamilyBox_, 
          SIGNAL(currentFontChanged(const QFont&)),
          this,
          SLOT(update_font_selectors_(const QFont&)));

  /* font style selector */
  QHBoxLayout *fontStyleLayout = new QHBoxLayout;
  QLabel* fontStyleLabel =  new QLabel(tr("Style"));
  fontStyleBox_ = new QComboBox(this);
  fontStyleLayout->addWidget(fontStyleLabel);
  fontStyleLayout->addWidget(fontStyleBox_);

  /* font size selector */
  QHBoxLayout *fontSizeLayout = new QHBoxLayout;
  QLabel* fontSizeLabel =  new QLabel(tr("Point size"));
  fontSizeBox_ = new QComboBox(this);
  fontSizeLayout->addWidget(fontSizeLabel);
  fontSizeLayout->addWidget(fontSizeBox_);

  mainLayout->addLayout(fontFamilyLayout);
  mainLayout->addLayout(fontStyleLayout);  
  mainLayout->addLayout(fontSizeLayout);
  
  fontWidget->setLayout(mainLayout);
  addTab(fontWidget, tr("Fonts"));

  /* initialize the whole bunch */
  update_font_selectors_(currentFont_);
}


QT_END_NAMESPACE
