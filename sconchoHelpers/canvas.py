# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2010 Markus Dittrich
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License Version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License Version 3 for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
#######################################################################

from PyQt4.QtCore import QPoint, QPointF
import math


def convert_pos_to_row_col(mousePos, cellWidth, cellHeight):
    """
    Converts a mouse position on the canvas into a tuple
    of (column, row).
    Note: This may be outside the actual pattern grid.
    """

    column = int( math.floor( mousePos.x()/cellWidth ) )
    row    = int( math.floor( mousePos.y()/cellHeight ) )

    return (column, row )



def is_click_in_grid(col, row, numCols, numRows):
    """
    Returns true if col and row is within the limits
    set by numCol and numRow.
    """

    if ( col >= 0 and col < numCols ) and ( row >= 0 and row < numRows ):
        return True
    else:
        return False

    

def is_click_on_labels(col, row, numCols, numRows):
    """ Returns true if col and row is inside the grid labels. """

    if (col == numCols) or (row == numRows):
        return True
    else:
        return False

