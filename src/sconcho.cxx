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

/** Qt includes */
#include <QApplication>
#include <QDebug>

/** local includes */
#include "mainWindow.h"


int main(int argc, char** argv)
{
  QApplication app(argc, argv);

  /** done with setup, now enter the mainloop */
  MainWindow mainWin;
  bool status = mainWin.Init();

  if ( status == false )
  {
    qDebug() << "Failed to initialize main window.";
    return EXIT_FAILURE;
  }

  mainWin.show();
  return app.exec();
}
