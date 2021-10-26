#!/usr/bin/env python
from setuptools import setup
import os

dir = os.path.split(os.path.abspath(__file__))[0]

#import all of this version information
__version__ = '2.1.3'
__author__ = 'David Buonasera'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2019 David Buonasera'
__title__ = 'link'


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
REQUIRES = ['requests>=2.0.0', 'requests_oauthlib>=0.4.0', 'xmltodict' , 'six']
EXTRAS_REQUIRE = {
      'pandas': ['pandas>=1.0.0'],
}

# write out the version file so we can keep track on what version the built
# package is

# call setup so it can build the package
setup(name=__title__,
      version=__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      license=__license__,
      maintainer_email=EMAIL,
      maintainer=__author__,
      url=URL,
      packages=['link', 'link.wrappers', 'link.configs'],
      extras_require=EXTRAS_REQUIRE,
      #package_data = {'link.configs': ['link.configs/*config']},
      install_requires=REQUIRES,
      #data_files = DATA_FILES,
      classifiers=CLASSIFIERS,
      **SETUP_ARGS)
