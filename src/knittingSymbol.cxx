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
#include <QStringList>

/** local headers */
#include "basicDefs.h"
#include "knittingSymbol.h"


QT_BEGIN_NAMESPACE

/**************************************************************
 *
 * PUBLIC FUNCTIONS 
 *
 **************************************************************/

//-------------------------------------------------------------
// constructor
//-------------------------------------------------------------
KnittingSymbol::KnittingSymbol(const QString& aPath,
  const QString& aPatternName, 
  const QString& aCategory,
  const QSize& dimension, 
  const QString& instruction)
  :
    svgPath_(aPath),
    patternName_(aPatternName),
    category_(aCategory),
    dimensions_(dimension),
    instructions_(instruction)
{
  status_ = SUCCESSFULLY_CONSTRUCTED;
}


//--------------------------------------------------------------
// main initialization routine
//--------------------------------------------------------------
bool KnittingSymbol::Init()
{
  if ( status_ != SUCCESSFULLY_CONSTRUCTED )
  {
    return false;
  }

  return true;
}


QT_END_NAMESPACE
