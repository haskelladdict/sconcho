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
#include <QLineEdit>
#include <QPushButton>
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
      QDialog(myParent),
      settings_(theSettings),
      tabWidget_(new QTabWidget),
      fontFamilyBox_(new QFontComboBox),
      fontStyleBox_(new QComboBox),
      fontSizeBox_(new QComboBox),
      exampleText_(new QLineEdit)
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

  /* get our current font from our settings; if it is empty
   * we choose a default */
  QString preferenceFont = settings_.value("global/font").toString();
  assert( preferenceFont != "");
  currentFont_.fromString(preferenceFont);

  /* call individual initialization routines */
  setModal(true);
  setWindowTitle(tr("Preferences"));

  /* create the interface */
  create_main_layout_();
  create_font_tab_();

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

//-------------------------------------------------------------
// update settings with whatever is selected and then close
// the widget
//-------------------------------------------------------------
void PreferencesDialog::ok_clicked_()
{
  settings_.setValue("global/font",currentFont_.toString());
  close();
}


//-------------------------------------------------------------
// update the currently selected font based on the font
// selectors
//-------------------------------------------------------------
void PreferencesDialog::update_current_font_()
{
  QString fontFamily(fontFamilyBox_->currentFont().family());
  QString fontStyle(fontStyleBox_->currentText());
  int fontSizeSelection = fontSizeBox_->currentIndex();
  int fontSize = fontSizeBox_->itemData(fontSizeSelection).toInt();

  QFontDatabase dataBase;
  currentFont_ = dataBase.font(fontFamily, fontStyle, fontSize);

  qDebug() << currentFont_.toString();
  exampleText_->setFont(currentFont_);
}



//-------------------------------------------------------------
// update the font style, point size and example text widgets
// if the user changes the font family
//-------------------------------------------------------------
void PreferencesDialog::update_font_selectors_(const QFont& newFont)
{
  QString family(newFont.family());
  QFontDatabase database;

  /* update font style */
  QStringList availableStyles(database.styles(family));
  fontStyleBox_->clear();
  QString targetStyle(database.styleString(newFont));
  int targetIndex = 0;
  for (int index = 0; index < availableStyles.size(); ++index)
  {
    if (availableStyles.at(index) == targetStyle)
    {
      targetIndex = index;
    }

    fontStyleBox_->addItem(availableStyles.at(index));
  }
  fontStyleBox_->setCurrentIndex(targetIndex);

 
  /* update font size */
  QList<int> availableSizes(database.pointSizes(family));
  QString helper;
  fontSizeBox_->clear();
  int targetSize(newFont.pointSize());
  targetIndex = 0;
  for (int index = 0; index < availableSizes.size(); ++index)
  {
    if (availableSizes.at(index) == targetSize)
    {
      targetIndex = index;
    }

    fontSizeBox_->addItem(helper.setNum(availableSizes.at(index)),
        QVariant(availableSizes.at(index)));
  }
  fontSizeBox_->setCurrentIndex(targetIndex);
}


/*************************************************************
 *
 * PRIVATE MEMBER FUNCTIONS
 *
 *************************************************************/

//------------------------------------------------------------
// create the main widget layout
//------------------------------------------------------------
void PreferencesDialog::create_main_layout_()
{
  QVBoxLayout* mainLayout = new QVBoxLayout;

  QHBoxLayout* buttonLayout = new QHBoxLayout;
  QPushButton* okButton = new QPushButton(tr("Ok"),this);
  QPushButton* cancelButton = new QPushButton(tr("Cancel"),this);
  buttonLayout->addStretch(1);
  buttonLayout->addWidget(okButton);
  buttonLayout->addWidget(cancelButton);

  connect(okButton,
          SIGNAL(clicked()),
          this,
          SLOT(ok_clicked_()));

  connect(cancelButton,
          SIGNAL(clicked()),
          this,
          SLOT(close()));


  mainLayout->addWidget(tabWidget_);
  mainLayout->addLayout(buttonLayout);

  setLayout(mainLayout);
}


//------------------------------------------------------------
// create the font widget
//------------------------------------------------------------
void PreferencesDialog::create_font_tab_()
{
  QGroupBox* fontWidget = new QGroupBox(this); 
  QVBoxLayout *mainLayout = new QVBoxLayout;

  /* font family selector */
  QHBoxLayout *fontFamilyLayout = new QHBoxLayout;
  QLabel* fontFamilyLabel = new QLabel(tr("Family"));
  fontFamilyBox_->setWritingSystem(QFontDatabase::Latin);
  fontFamilyBox_->setCurrentFont(currentFont_);
  fontFamilyLayout->addWidget(fontFamilyLabel);
  fontFamilyLayout->addWidget(fontFamilyBox_);

  connect(fontFamilyBox_, 
          SIGNAL(currentFontChanged(const QFont&)),
          this,
          SLOT(update_font_selectors_(const QFont&)));

  connect(fontFamilyBox_,
          SIGNAL(currentFontChanged(const QFont&)),
          this,
          SLOT(update_current_font_()));


  /* font style selector */
  QHBoxLayout *fontStyleLayout = new QHBoxLayout;
  QLabel* fontStyleLabel =  new QLabel(tr("Style"));
  fontStyleLayout->addWidget(fontStyleLabel);
  fontStyleLayout->addWidget(fontStyleBox_);

  connect(fontStyleBox_,
          SIGNAL(activated(int)),
          this,
          SLOT(update_current_font_()));


  /* font size selector */
  QHBoxLayout *fontSizeLayout = new QHBoxLayout;
  QLabel* fontSizeLabel =  new QLabel(tr("Point size"));
  fontSizeLayout->addWidget(fontSizeLabel);
  fontSizeLayout->addWidget(fontSizeBox_);

  connect(fontSizeBox_,
          SIGNAL(activated(int)),
          this,
          SLOT(update_current_font_()));


  /* example String */
  exampleText_->setReadOnly(true);
//  exampleText_->setFixedHeight(50);
  exampleText_->setFont(currentFont_);
  exampleText_->setText("Thanks for sharing!");
  
  mainLayout->addLayout(fontFamilyLayout);
  mainLayout->addLayout(fontStyleLayout);  
  mainLayout->addLayout(fontSizeLayout);
  mainLayout->addWidget(exampleText_);
  
  fontWidget->setLayout(mainLayout);
  tabWidget_->addTab(fontWidget, tr("Canvas Font"));

  /* initialize the whole bunch */
  update_font_selectors_(currentFont_);
}




QT_END_NAMESPACE
