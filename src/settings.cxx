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

/** Qt headers */
#include <QSettings>

/** local headers */
#include "basicDefs.h"
#include "settings.h"


QT_BEGIN_NAMESPACE



/******************************************************************
 * set up the initial state of the settings
 ******************************************************************/
void initialize_settings( QSettings& settings )
{
  /* font properties for canvas text */
  QString preferenceFont = settings.value( "global/font" ).toString();
  if ( preferenceFont.isEmpty() ) {
    settings.setValue( "global/font", "Arial,10,-1,5,50,0,0,0,0,0" );
  }

  /* canvas selections for exporting/printing */
  QString exportPatternGrid =
    settings.value( "global/export_pattern_grid" ).toString();
  if ( exportPatternGrid.isEmpty() ) {
    settings.setValue( "global/export_pattern_grid", "true" );
  }

  QString exportLegend = settings.value( "global/export_legend" ).toString();
  if ( exportLegend.isEmpty() ) {
    settings.setValue( "global/export_legend", "true" );
  }

  /* default settings for width and height of grid cells */
  QString cellWidth = settings.value( "global/cell_width" ).toString();
  if ( cellWidth.isEmpty() ) {
    QString defaultWidth;
    defaultWidth.setNum( GRID_CELL_WIDTH );
    settings.setValue( "global/cell_width", defaultWidth );
  }

  QString cellHeight = settings.value( "global/cell_height" ).toString();
  if ( cellHeight.isEmpty() ) {
    QString defaultHeight;
    defaultHeight.setNum( GRID_CELL_HEIGHT );
    settings.setValue( "global/cell_height", defaultHeight );
  }
}



/*******************************************************************
 * implementations of accessors for some settings
 *******************************************************************/
QString get_font_string( const QSettings& settings )
{
  QString preferenceFont = settings.value( "global/font" ).toString();
  assert( preferenceFont != "" );
  return preferenceFont;
}



/*******************************************************************
 * implementations of setters for settings
 ******************************************************************/
void set_font_string( QSettings& settings, const QString& fontString )
{
  settings.setValue( "global/font", fontString );
}


QT_END_NAMESPACE
