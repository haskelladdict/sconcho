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


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import functools
import random

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QApplication, QCursor)

import sconcho.util.messages as msg

def wait_cursor(func):
    """ Wrapps a function and makes sure the cursor is shown
    as Qt.WaitCursor for the duration.

    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            result = func(*args, **kwargs)
        finally:
            QApplication.restoreOverrideCursor()

        return result

    return wrapper



def get_random_knitting_quote():
    """ This function randomly picks a title from the list
    of available ones. 
    
    """

    num = len(msg.knittingQuotes)
    return (msg.knittingQuotes[random.randint(0, num-1)])

