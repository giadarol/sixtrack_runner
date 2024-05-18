# copyright ############################### #
# This file is part of the Xpart Package.   #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

from setuptools import setup, find_packages, Extension
from pathlib import Path

#######################################
# Prepare list of compiled extensions #
#######################################

extensions = []


#########
# Setup #
#########

version_file = Path(__file__).parent / 'sixtrack/_version.py'
dd = {}
with open(version_file.absolute(), 'r') as fp:
    exec(fp.read(), dd)
__version__ = dd['__version__']

setup(
    name='sixtrack_runner',
    version=__version__,
    description='sixtrack runner',
    packages=find_packages(),
    ext_modules=extensions,
    include_package_data=True,
    install_requires=[
        'numpy>=1.0',
        'scipy',
        ],
    author='G. Iadarola et al.',
    license='Apache 2.0',
    extras_require={
        'tests': ['cpymad', 'PyHEADTAIL', 'pytest'],
        },
    )
