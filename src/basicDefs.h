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

/****************************************************************
 *
 * basic_definitions provides definitions such as macros or
 * better const ints to be used be all other files.
 * NOTE: please keep this file leightweight and do not 
 * include any other files unless necessary for the definitions
 * themselves.
 *
 ***************************************************************/

#ifndef BASIC_DEFINITIONS_H 
#define BASIC_DEFINITIONS_H

/* use BOOST_FOREACH */
#include <boost/foreach.hpp>
#define FOREACH BOOST_FOREACH

/** assert for debugging */
#ifndef DEBUG
#define NDEBUG
#endif
#include <cassert>

/* flag that a class object has been successfully 
 * constructed */
const int SUCCESSFULLY_CONSTRUCTED = 0xabe123;

/* types used for identifying custom QGraphicsItems */
const int PATTERN_GRID_ITEM_TYPE = 1;
const int PATTERN_GRID_LABEL_TYPE = 2;
const int PATTERN_GRID_RECTANGLE_TYPE = 3;
const int PATTERN_KEY_CANVAS_TYPE = 4;
const int KNITTING_PATTERN_ITEM_TYPE = 5;
const int LEGEND_LABEL_TYPE = 6;
const int LEGEND_ITEM_TYPE = 7;

/* the size (in pixels) of a grid cell */
const int GRID_CELL_SIZE = 30;


#endif
