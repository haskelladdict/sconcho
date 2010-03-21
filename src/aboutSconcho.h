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

#ifndef ABOUT_SCONCHO_H
#define ABOUT_SCONCHO_H

/* boost headers */
#include <boost/utility.hpp>

/* QT headers */
#include <QMessageBox>

QT_BEGIN_NAMESPACE

/*****************************************************************
 *
 * this widget displays sconcho's about and copyright info
 *
 *****************************************************************/

class AboutSconchoWidget
    :
    public QMessageBox,
    public boost::noncopyable
{

public:

  explicit AboutSconchoWidget( QWidget* parent = 0 );


private:

  void setup_contents_();
};


QT_END_NAMESPACE

#endif
