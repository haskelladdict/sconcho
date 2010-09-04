#!/usr/bin/python
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


from PyQt4.QtCore import QDir


def parse_all_symbols(symbolPaths):
    """ 
    This function reads all available knitting symbols and
    returns a dictionary with them all.
    """

    symbolPaths = get_list_of_symbol_paths(symbolPaths)

    symbols = {}
    symbols['foo'] = "bar"
    
    return symbols



def get_list_of_symbol_paths(symbolPaths):
    """
    Given a list of top level paths to directories containting
    sconcho kitting symbols returns a list of all paths to 
    individual sconcho patterns.
    """

    for path in symbolPaths:
        aDir = QDir(path)
        print(path, aDir.absolutePath())

        

