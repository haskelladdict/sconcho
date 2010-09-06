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

from PyQt4.QtCore import QSettings, QString, QSize


### some global settings (is there a better way to do this)
GRID_CELL_WIDTH  = "30"
GRID_CELL_HEIGHT = "30"


def initialize(settings):
    """
    Initializes some basic settings if none exist.
    """

    preferenceFont = settings.value( "global/font" ).toString()
    if preferenceFont.isEmpty():
      settings.setValue( "global/font", "Arial,10,-1,5,50,0,0,0,0,0" )

    exportPatternGrid =  \
        settings.value( "global/export_pattern_grid" ).toString()
    if exportPatternGrid.isEmpty():
        settings.setValue( "global/export_pattern_grid", "true" )

    exportLegend = settings.value( "global/export_legend" ).toString()
    if exportLegend.isEmpty():
        settings.setValue( "global/export_legend", "true" )

    cellWidth = settings.value( "global/cell_width" ).toString()
    if cellWidth.isEmpty():
        defaultWidth = QString(GRID_CELL_WIDTH)
        settings.setValue( "global/cell_width", defaultWidth )

    cellHeight = settings.value( "global/cell_height" ).toString()
    if cellHeight.isEmpty():
        defaultHeight = QString(GRID_CELL_HEIGHT)
        settings.setValue( "global/cell_height", defaultHeight )



def get_grid_dimensions(settings):
    """
    Helper function returning a tuple with width and height
    for grid cells.
    """

    (cellWidth, widthStatus) = \
            settings.value( "global/cell_width" ).toString().toInt()
    (cellHeight, heightStatus) = \
            settings.value( "global/cell_height" ).toString().toInt()

    if not widthStatus or not heightStatus:
        print("Error: Failed to retrieve grid dimensions from settings.")

    return QSize(cellWidth, cellHeight)
