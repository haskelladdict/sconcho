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

#ifndef PATTERN_KEY_DIALOG_H
#define PATTERN_KEY_DIALOG_H

/* boost includes */
#include <boost/utility.hpp>

/* QT includes */
#include <QDialog>


QT_BEGIN_NAMESPACE

/* forward declarations */
class PatternKeyCanvas;
class QGraphicsView;
class QSettings;
class QSplitter;


/***************************************************************
 * 
 * This dialog allows the user to configure and export the
 * key/legend for the current pattern grid
 *
 ***************************************************************/
class PatternKeyDialog 
  :
    public QDialog,
    public boost::noncopyable
{
  
  Q_OBJECT

    
public:

  explicit PatternKeyDialog(const QSettings& aSetting, 
    QWidget* myParent = 0);
  bool Init();


private:

  /* some tracking variables */
  int status_;

  /* private data members */
  QFont mainFont_;
  const QSettings& settings_;
  QSplitter* mainSplitter_;
  QGraphicsView* patternKeyView_;
  PatternKeyCanvas* patternKeyCanvas_;
};


QT_END_NAMESPACE

#endif
