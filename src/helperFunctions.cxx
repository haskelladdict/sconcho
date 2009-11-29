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

/* C++ includes */
#include <float.h>

/* qt includes */
#include <QDebug>
#include <QDir>
#include <QFileDialog>
#include <QFileInfo>
#include <QGraphicsItem>
#include <QGraphicsScene>
#include <QMessageBox>
#include <QObject>
#include <QPainter>
#include <QPrinter>
#include <QPrintDialog>

/* local includes */
#include "graphicsScene.h"
#include "helperFunctions.h"
#include "settings.h"


QT_BEGIN_NAMESPACE


//---------------------------------------------------------------
// this function returns a QFont object with the currently
// selected font
//----------------------------------------------------------------
QFont extract_font_from_settings(const QSettings& settings)
{
  QFont theFont;
  theFont.fromString(get_font_string(settings));

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



//---------------------------------------------------------------
// this functions export the content of a QGraphicsScene to
// a file
//---------------------------------------------------------------
void export_scene(const QString& fileName, GraphicsScene* scene)
{
  /* for now print the image in a fixed resolution 
   * NOTE: We seem to need the 1px buffer region to avoid
   *       the image being cut off */
  QRectF theScene = scene->get_visible_area();
  theScene.adjust(-10,-10,10,10);  // need this to avoid cropping

  QImage finalImage(theScene.width()*3, theScene.height() *3,
      QImage::Format_ARGB32_Premultiplied);
  QPainter painter(&finalImage);
  painter.setRenderHints(QPainter::SmoothPixmapTransform);
  painter.setRenderHints(QPainter::HighQualityAntialiasing);
  painter.setRenderHints(QPainter::TextAntialiasing);

  scene->render(&painter, QRectF(), theScene);
  painter.end();
  finalImage.save(fileName);
}



//---------------------------------------------------------------
// this function prints the content of a QGraphicsScene
//---------------------------------------------------------------
void print_scene(QGraphicsScene* scene)
{
  QPrinter aPrinter(QPrinter::HighResolution);
  QPrintDialog printDialog(&aPrinter);
  if ( printDialog.exec() == QDialog::Accepted )
  {
    /* tell our canvas that we want to print its */
    QPainter painter(&aPrinter);
    painter.setRenderHints(QPainter::SmoothPixmapTransform);
    painter.setRenderHints(QPainter::HighQualityAntialiasing);
    painter.setRenderHints(QPainter::TextAntialiasing);
    scene->render(&painter);
    painter.end();
  }
}


//---------------------------------------------------------------
// given a list of QGraphicsItems returns the maximum y
// coordinate
//---------------------------------------------------------------
qreal get_max_y_coordinate(const QList<QGraphicsItem*> items)
{
  qreal yMax = -DBL_MAX;
  foreach(QGraphicsItem* anItem, items)
  {
    qreal yPos = anItem->scenePos().y();
    if (yMax < yPos)
    {
      yMax = yPos;
    }
  }

  return yMax;
}


//---------------------------------------------------------------
// given a list of QGraphicsItems returns the bounding rectangle
//---------------------------------------------------------------
QRectF get_bounding_rect(const QList<QGraphicsItem*> items)
{
  qreal yMin = DBL_MAX;
  qreal yMax = -DBL_MAX;
  qreal xMin = DBL_MAX;
  qreal xMax = -DBL_MAX;

  foreach(QGraphicsItem* anItem, items)
  {
    QRectF bound(anItem->mapRectToParent(anItem->boundingRect()));

    if (xMin > bound.left())
    {
      xMin = bound.left();
    }

    if (xMax < bound.right())
    {
      xMax = bound.right();
    }
      
    if (yMin > bound.top())
    {
      yMin = bound.top();
    }

    if (yMax < bound.bottom())
    {
      yMax = bound.bottom();
    }
  }

  return QRectF(xMin, yMin, (xMax - xMin), (yMax - yMin));
}




QT_END_NAMESPACE
