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

/* Qt includes */
#include <QFont>
#include <QString>
#include <QSize>


QT_BEGIN_NAMESPACE


/* forward declarations */
class QSettings;


/***********************************************************
 * set up the initial state of the settings
 ***********************************************************/
void initialize_settings( QSettings& settings );



/*******************************************************************
 * accessor function for font settings
 *******************************************************************/
QFont extract_font_from_settings( const QSettings& settings );



/*******************************************************************
 * accessor function for cell dimension settings
 *******************************************************************/
QSize extract_cell_dimensions_from_settings( const QSettings& settings );


/************************************************************
 * set a new font string
 ***********************************************************/
void set_font_string( QSettings& settings, const QString& fontString );



/************************************************************
 * set new cell dimensions
 ***********************************************************/
void set_cell_dimensions( QSettings& settings, const QSize& cellSize );


QT_END_NAMESPACE
