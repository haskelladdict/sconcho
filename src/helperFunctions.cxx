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

/* qt includes */
#include <QDir>
#include <QFileDialog>
#include <QFileInfo>
#include <QMessageBox>
#include <QObject>


/* local includes */
#include "helperFunctions.h"

QT_BEGIN_NAMESPACE

//---------------------------------------------------------------
// simple integer min max function
//---------------------------------------------------------------
int int_max(int a, int b) 
{ 
  return a > b ? a : b; 
}


//---------------------------------------------------------------
// this function returns a QFont object with the currently
// selected font
//----------------------------------------------------------------
QFont extract_font_from_settings(const QSettings& settings)
{
  QFont theFont;
  theFont.fromString(settings.value("global/font").toString());

  return theFont;
}


//---------------------------------------------------------------
// this functions a file export dialog and returns the selected
// filename or an empty string if nothing was selected
//---------------------------------------------------------------
QString show_file_export_dialog()
{
  QString currentDirectory = QDir::currentPath();
  QString saveFileName = QFileDialog::getSaveFileName(0,
    QObject::tr("Export"), currentDirectory,
    QObject::tr("Image Files (*.png *.tif *.jpg *.gif)"));

  if ( saveFileName.isEmpty() )
  {
    return QString("");
  }

  /* extract file extension and make sure it corresponds to
   * a supported format */
  QFileInfo saveFileInfo(saveFileName);
  QString extension = saveFileInfo.completeSuffix();

  if ( extension != "png" && extension != "tif"
       && extension != "jpg" && extension != "gif" )
  {
    QMessageBox::warning(0, QObject::tr("Warning"),
      QObject::tr("Unknown file format ") + extension,
      QMessageBox::Ok);
    return QString("");
  }

  return saveFileName;
}


QT_END_NAMESPACE
