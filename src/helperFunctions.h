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

/****************************************************************
 *
 * this is a collection of useful helper functions
 *
 ***************************************************************/

#ifndef HELPER_FUNCTIONS_H 
#define HELPER_FUNCTIONS_H

/* Qt includes */
#include <QFont>
#include <QSettings>
#include <QString>

QT_BEGIN_NAMESPACE

//---------------------------------------------------------------
// simple integer min max function
//---------------------------------------------------------------
int int_max(int a, int b); 


//---------------------------------------------------------------
// this function returns a QFont object with the currently
// selected font
//---------------------------------------------------------------
QFont extract_font_from_settings(const QSettings& settings);


//---------------------------------------------------------------
// this functions a file export dialog and returns the selected
// filename or an empty string if nothing was selected
//---------------------------------------------------------------
QString show_file_export_dialog();


QT_END_NAMESPACE

#endif
