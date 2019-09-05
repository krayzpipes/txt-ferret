#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

__version__ = "0.3.0a"
description = "Scan text files for senitive (or non-sensitive) data."

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='txtferret',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=__version__,

    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",

    # The project's main homepage.
    url='https://github.com/krayzpipes/txt-ferret',

    # Author details
    author='Kyle Piper',
    author_email='kylepiper29@gmail.com',

    # Choose your license
    license='License :: OSI Approved :: Apache Software License',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Security",

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # What does your project relate to?
    keywords=["pci", "dlp", "text", "scan", "regex"],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=["src.txtferret"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},


    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #py_modules=["txt_ferret"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['click', 'loguru', 'pyyaml'],

    entry_points={
        'console_scripts': [
            'txtferret=txtferret:main',
        ],
    }
)
