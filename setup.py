#!/usr/bin/env python
from setuptools import setup
import os
from link.version import version_details, version

dir = os.path.split(os.path.abspath(__file__))[0]


NAME = 'link'
DESCRIPTION = "Easy and consistent access to the objects you care about"
LONG_DESCRIPTION = "Easy and consistent access to the objects you care about"
URL = ''
LICENSE = 'MIT'
DOWNLOAD_URL = ''
CLASSIFIERS = ['Development Status :: 4 - Beta',     
               'Programming Language :: Python',
               'Programming Language :: Python :: 2'
              ]
AUTHOR = ''
EMAIL = ''
SETUP_ARGS = {}
DATA_FILES = [('link/configs', ['link/configs/link.config'])]
REQUIRES = []

try:
    import numpy
    import pandas
except:
    print "We highly suggest you install numpy and Pandas for some functionality" 
    print "easy_install numpy"
    print "easy_install pandas"

# write out the version file so we can keep track on what version the built
# package is

# call setup so it can build the package
setup(name=NAME,
      version=version,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      license=LICENSE,
      maintainer_email=EMAIL,
      maintainer=AUTHOR,
      url=URL,
      packages=['link', 'link.wrappers', 'link.configs'],
      #package_data = {'link.configs': ['link.configs/*config']},
      install_requires = REQUIRES,
      #data_files = DATA_FILES,
      classifiers=CLASSIFIERS,
      **SETUP_ARGS)
