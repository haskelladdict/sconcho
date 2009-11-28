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

#ifndef PREFERENCES_DIALOG_H
#define PREFERENCES_DIALOG_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QDialog>
#include <QSettings>

QT_BEGIN_NAMESPACE


/* forward declarations */
class QComboBox;
class QFont;
class QFontComboBox;
class QTabWidget;
class QLineEdit;


/**************************************************************
 * 
 * this dialog provides all the user interaction to 
 * change sconcho's settings. The settings themselves
 * are being kept track of by the MainWindow via a
 * QSettings instance
 *
 **************************************************************/
class PreferencesDialog 
  :
    public QDialog,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit PreferencesDialog(QSettings& sets, QWidget* myParent = 0);
  bool Init();


private slots:

  void update_font_selectors_(const QFont& newFont);
  void update_current_font_();
  void ok_clicked_();


private:

  /* some tracking variables */
  int status_;

  /* status variables */
  QSettings& settings_;

  /* current selections */
  QFont currentFont_;
  //bool doExportPatternGrid_;
  //bool doExportLegend_;

  /* widgets */
  QTabWidget* tabWidget_;
  QFontComboBox* fontFamilyBox_;
  QComboBox* fontStyleBox_;
  QComboBox* fontSizeBox_;
  QLineEdit* exampleText_;

  /* interface creation functions */
  void create_main_layout_();
  void create_font_tab_();
};


QT_END_NAMESPACE


#endif
