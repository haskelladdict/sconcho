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
#include <QTabWidget>
#include <QSettings>

/* a few forward declarations */



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
    public QTabWidget,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit PreferencesDialog(QSettings& sets, QWidget* myParent = 0);
  bool Init();


private:

  /* some tracking variables */
  int status_;

  /* status variables */
  QSettings& settings_;
};



#endif
