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
#include <QSettings>

/** local headers */
#include "settings.h"


QT_BEGIN_NAMESPACE



/***********************************************************
 * set up the initial state of the settings 
 ***********************************************************/
void initialize_settings(QSettings& settings)
{
  /* font properties for canvas text */
  QString preferenceFont = settings.value("global/font").toString();
  if (preferenceFont == "")
  {
    settings.setValue("global/font","Arial,10,-1,5,50,0,0,0,0,0");
  }

  /* canvas selections for exporting/printing */
  QString exportPatternGrid = 
    settings.value("global/export_pattern_grid").toString();
  if (exportPatternGrid == "")
  {
    settings.setValue("global/export_pattern_grid","true");
  }

  QString exportLegend = 
    settings.value("global/export_legend").toString();
  if (exportLegend == "")
  {
    settings.setValue("global/export_legend","true");
  }
}



QT_END_NAMESPACE
