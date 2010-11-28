#!/usr/bin/env python

from distutils.core import setup

setup(name='sconcho',
      version='0.1_a5',
      description='Program for Generating Knitting Charts',
      author='Markus Dittrich',
      author_email='haskelladdict@users.sourceforge.net',
      url='http://sconcho.sourceforge.net/',
      license='GNU GPLv3',
      packages=['sconcho', 'sconcho.util', 'sconcho.gui'], 
      scripts=['sconcho/sconcho.pyw']
     )

