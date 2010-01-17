/***************************************************************
 *
 * (c) 2009-2010 Markus Dittrich 
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
#include <limits.h>

/* qt includes */
#include <QDebug>
#include <QGraphicsItem>

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
// given a list of QGraphicsItems returns the maximum y
// coordinate
//---------------------------------------------------------------
qreal get_max_y_coordinate(const QList<QGraphicsItem*> items)
{
  qreal yMax = -DBL_MAX;
  foreach(QGraphicsItem* anItem, items)
  {
    qreal yPos = anItem->scenePos().y() 
      + anItem->boundingRect().height();
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


//---------------------------------------------------------------
// this function splits a string of the form
// <string>[:<int>]
// into <string> and <int> and returns them as a QPair.
// if no <int> is present we return INT_MAX instead
//---------------------------------------------------------------
QPair<QString,int> split_into_category_and_position(
  const QString& aParseString)
{
  QStringList result = aParseString.split(":");
  assert(!result.isEmpty());
  
  bool status = false;
  int ordering = result.last().toInt(&status);
  if ( (result.length() < 2) || (status == false) )
  {
    return QPair<QString,int>(aParseString, INT_MAX);
  }
  else
  {
    result.removeLast();
    return QPair<QString,int>(result.join(":"), ordering);
  }
}
  

//---------------------------------------------------------------
// this function takes a string, typically a pattern description
// and tries to format them a bit nicer since they come as one
// long string. We don't want to be fancy here and basically
// just break possible long lines into a bunch of shorter ones.
//---------------------------------------------------------------
QString format_string(const QString& oldString)
{
  int maxLineLength = 40;

  QStringList splitString = oldString.split(" ");
  QString outString;
  int lengthCount = 0;
  foreach(QString item, splitString)
  {
    if (lengthCount > maxLineLength)
    {
      outString += "\n";
      lengthCount = 0;
    }

    outString += item;
    outString += " ";
    lengthCount += (item.length() + 1);
  }

  return outString;
}


QT_END_NAMESPACE
