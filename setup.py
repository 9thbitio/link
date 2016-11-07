#!/usr/bin/env python
from setuptools import setup
import os
import link

dir = os.path.split(os.path.abspath(__file__))[0]


DESCRIPTION = "Easy and consistent access to the objects you care about"
LONG_DESCRIPTION = "Easy and consistent access to the objects you care about"
URL = ''
DOWNLOAD_URL = ''
CLASSIFIERS = ['Development Status :: 4 - Beta',     
               'Programming Language :: Python',
               'Programming Language :: Python :: 2',
               'Programming Language :: Python :: 3'
              ]
EMAIL = ''
SETUP_ARGS = {}
DATA_FILES = [('link/configs', ['link/configs/link.config'])]
REQUIRES = ['requests>=2.0.0', 'requests_oauthlib>=0.4.0', 'pandas', 'xmltodict' ]

try:
    import numpy
    import pandas
    import xmltodict
except:
    print("We highly suggest you install numpy and Pandas for some functionality" )
  
# write out the version file so we can keep track on what version the built
# package is

# call setup so it can build the package
setup(name=link.__title__,
      version=link.__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      license=link.__license__,
      maintainer_email=EMAIL,
      maintainer=link.__author__,
      url=URL,
      packages=['link', 'link.wrappers', 'link.configs'],
      #package_data = {'link.configs': ['link.configs/*config']},
      install_requires = REQUIRES,
      #data_files = DATA_FILES,
      classifiers=CLASSIFIERS,
      **SETUP_ARGS)
