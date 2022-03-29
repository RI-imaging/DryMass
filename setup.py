from os.path import dirname, realpath, exists
from setuptools import setup, find_packages
import sys


author = u"Paul Müller"
authors = [author]
description = 'manipulation and analysis of phase microscopy data'
name = 'drymass'
year = "2017"

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)
from _version import version  # noqa: E402


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
    install_requires=[
        "appdirs",
        "matplotlib>=2.2.0",
        "numpy>=1.12.0",
        "qpformat>=0.13.1",
        "qpimage>=0.8.5",
        "qpretrieve>=0.2.2",
        "qpsphere>=0.5.9",
        "scikit-image>=0.16.1",  # threshold_li
        "tifffile==2020.5.25",  # TIFF writer
        ],
    python_requires='>=3.9, <4',
    entry_points={
       "console_scripts": [
           "dm_analyze_sphere = drymass.cli:cli_analyze_sphere",
           "dm_convert = drymass.cli:cli_convert",
           "dm_extract_roi = drymass.cli:cli_extract_roi",
           "dm_profile = drymass.cli:cli_profile",
            ],
       },
    keywords=["digital holographic microscopy",
              "optics",
              "quantitative phase imaging",
              "refractive index",
              "scattering",
              ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research'
                 ],
    platforms=['ALL'],
    )
