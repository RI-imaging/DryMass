#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import dirname, realpath, exists
from setuptools import setup, find_packages
import sys


author = u"Paul Müller"
authors = [author]
description = 'user-friendly quantitative phase imaging analysis'
name = 'drymass'
year = "2017"

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)
from _version import version

setup(
    name=name,
    author=author,
    author_email='dev@craban.de',
    url='https://github.com/RI-imaging/DryMass',
    version=version,
    packages=find_packages(),
    package_dir={name: name},
    license="MIT",
    description=description,
    long_description=open('README.rst').read() if exists('README.rst') else '',
    install_requires=["matplotlib",
                      "numpy",
                      "qpformat==0.1.1",
                      "qpimage==0.1.3",
                      "qpsphere==0.1.1",
                      "scikit-image>=0.13.1",
                      ],
    setup_requires=['pytest-runner'],
    tests_require=["pytest"],
    entry_points={
       "console_scripts": [
           "dm_analyze_sphere = drymass.__main__:cli_analyze_sphere",
           "dm_convert = drymass.__main__:cli_convert",
           "dm_extract_roi = drymass.__main__:cli_extract_roi",
            ],
       },
    python_requires='>=3.5, <4',
    keywords=["digital holographic microscopy",
              "optics",
              "quantitative phase imaging",
              "refractive index",
              "scattering",
              ],
    classifiers= [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research'
                 ],
    platforms=['ALL'],
    )
