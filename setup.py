#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import dirname, realpath, exists
from setuptools import setup
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
    packages=[name],
    package_dir={name: name},
    license="MIT",
    description=description,
    long_description=open('README.rst').read() if exists('README.rst') else '',
    install_requires=["numpy",
                      "qpformat",
                      "qpimage",
                      "qpsphere",
                      "scikit-image>=0.13.1",
                      ],
    setup_requires=['pytest-runner'],
    tests_require=["pytest"],
    entry_points={
       "console_scripts": ["dm_convert = drymass.__main__:cli_convert",
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
