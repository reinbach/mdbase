#!/usr/bin/env python
import os
from distutils.core import setup

requires = [
    'pyzmq (>=13.0.2)',
]

# Utility function to read the README file.
# Used for the long_description. It's nice, because 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a
# raw string in below...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='mdbase',
    version='0.1',
    description='MajorDomo Titanic Pattern implementation',
    author='Greg Reinbach',
    author_email='greg@reinbach.com',
    license='BSD',
    url='https://github.com/reinbach/mdbase',
    packages=['mdbase',],
    long_description=read('README.rst'),
    requires=requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)