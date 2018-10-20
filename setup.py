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

if version.count("dev") or sys.argv.count("test"):
    # specific versions are not desired for
    # - development version
    # - running pytest
    release_deps = ["qpformat",
                    "qpimage",
                    "qpsphere"]
else:
    release_deps = ["qpformat==0.6.0",
                    "qpimage==0.4.3",
                    "qpsphere==0.4.0",
                    ]

setup(
    name=name,
    author=author,
    author_email='dev@craban.de',
    url='https://github.com/RI-imaging/DryMass',
    version=version,
    packages=find_packages(),
    package_dir={name: name},
    include_package_data=True,
    license="MIT",
    description=description,
    long_description=open('README.rst').read() if exists('README.rst') else '',
    install_requires=["matplotlib",
                      "numpy>=1.12.0",
                      "scikit-image>=0.13.1",
                      ] + release_deps,
    setup_requires=['pytest-runner'],
    tests_require=["pytest"],
    python_requires='>=3.6, <4',
    entry_points={
       "console_scripts": [
           "dm_analyze_sphere = drymass.cli:cli_analyze_sphere",
           "dm_convert = drymass.cli:cli_convert",
           "dm_extract_roi = drymass.cli:cli_extract_roi",
            ],
       },
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
