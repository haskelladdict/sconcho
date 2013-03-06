#!/usr/bin/env python

from distutils.core import setup
import os, sys


def check_dependencies():
    """ Make sure we have python and pyQt with their
    proper versions installed.
    """

    # python 
    if sys.version_info < (3, 2, 0):
        print('Sorry, sconcho needs python version 3.2 or later')
        print("Python Version detected: %d.%d.%d" % sys.version_info[:3])
        exit(5)
    print("Python Version: %d.%d.%d" % sys.version_info[:3])
    
    try:
        from PyQt4.QtCore import qVersion
    except ImportError as msg:
        print('Sorry, please install PyQt4.')
        print('Error: %s' % msg)
        exit(1)
    print("Found PyQt")



def get_symbol_files():
    """ get a list of all symbol files. 
    NOTE: This is only one level deep! 
    """

    fileList = []
    for root, subFolders, files in os.walk("sconcho/symbols"):
        newRoot = root.replace("sconcho/","") 
        for aFile in files:
            fileList.append(os.path.join(newRoot, aFile))
   
    return fileList



if __name__ == "__main__":

    check_dependencies()
    dataFiles = get_symbol_files()

    #make sure we copy the manual
    dataFiles.append('doc/manual.html')

    setup(name='sconcho',
        version='0.2.0_b6',
        description='Program for Generating Knitting Charts',
        author='Markus Dittrich',
        author_email='haskelladdict@users.sourceforge.net',
        url='http://sconcho.sourceforge.net/',
        license='GNU GPLv3',
        packages=['sconcho', 'sconcho.util', 'sconcho.gui'], 
        package_data = {'sconcho': dataFiles}, 
        scripts=['sconcho.pyw']
        )
